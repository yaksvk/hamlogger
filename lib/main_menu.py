#!/usr/bin/en vpython

from gi.repository import Gtk, Pango
import sys

from .import_adif_dialog import ImportAdifDialog
from .export_adif_dialog import ExportAdifDialog
from .export_sota_dialog import ExportSotaDialog
from .export_wwff_dialog import ExportWwffDialog
from .session_new_dialog import NewSessionDialog
from .export_sota_chaser_dialog import ExportSotaChaserDialog

class MainMenu(Gtk.MenuBar):
    def __init__(self, app, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.app = app
        self._draw_menu()

    def _draw_menu(self):

        menu_items = [
            {
                'label': 'File',
                'items': [
                    {
                        'label': 'Exit',
                        'action': self.menu_file_exit
                    },
                ]
            },
            {
                'label': 'Import',
                'items': [
                    {
                        'label': 'ADIF',
                        'action': self.import_menu_adif
                    },
                ]
            },
            {
                'label': 'Export',
                'items': [
                    {
                        'label': 'ADIF Session',
                        'action': self.export_menu_adif_session
                    },
                    {
                        'label': 'SOTA CSV Activator',
                        'action': self.export_menu_sota
                    },
                    {
                        'label': 'SOTA CSV Chaser',
                        'action': self.export_menu_sota_chaser
                    },
                    {
                        'label': 'WWFF ADIF Activator',
                        'action': self.export_menu_wwff_activator
                    },
                ]
            },
            {
                'label': 'Sessions',
                'items': [
                    {
                        'label': 'New',
                        'action': self.menu_session_new
                    },
                    {
                        'label': 'Reset',
                        'action': self.menu_session_reset
                    },
                ]
            },
            {
                'label': 'Settings',
                'items': [
                    {
                        'label': 'Application Font',
                        'action': self.set_application_font
                    },
                ]
            },
        ]

        def generate_menu_item(item_data):
            item = Gtk.MenuItem(item_data['label'])

            if 'action' in item_data:
                item.connect("activate", item_data['action'])

            if 'items' in item_data:
                sub_menu = Gtk.Menu()
                for sub_item_data in item_data['items']:
                    sub_menu.append(generate_menu_item(sub_item_data))

                item.set_submenu(sub_menu)
            return item

        for item in menu_items:
            self.append(generate_menu_item(item))



    # Menu Actions

    def menu_file_exit(self, widget):
        sys.exit()


    def import_menu_adif(self, widget):

        dialog = Gtk.FileChooserDialog("Select ADIF file", self.app,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        input_file = None

        if response == Gtk.ResponseType.OK:
            input_file = dialog.get_filename()
        dialog.destroy()

        if input_file is not None:
            import_dialog = ImportAdifDialog(self.app, input_file)
            response = import_dialog.run()
            import_dialog.destroy()


    def export_menu_adif_session(self, widget):
        sessions = self.app.db.get_qso_sessions()
        dialog = ExportAdifDialog(self.app, sessions)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if dialog.selection is not None:
                model, tree_paths = dialog.selection.get_selected_rows()

                output_file = self.display_file_dialog("adi")
                if output_file is not None:
                    qsos = []
                    for path in reversed(tree_paths):
                        session = self.app.db.get_qso_session_by_id(id=model[path][0])
                        qsos.extend(session.qsos)

                    from .tools.export_adif_v2 import create_export_file_from_qsos
                    create_export_file_from_qsos(qsos, adif_file=output_file, config=self.app.config)

        dialog.destroy()


    def export_menu_sota(self, widget):
        # get sota activations
        activations = self.app.db.get_sota_activations()

        dialog = ExportSotaDialog(self.app, activations)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if dialog.selection is not None:
                model, tree_paths = dialog.selection.get_selected_rows()

                sota_qsos = []

                output_file = self.display_file_dialog("csv")

                if output_file is not None:
                    for path in reversed(tree_paths):
                        # model[path][0]       # summit
                        # model[path][2] # date

                        search_results = self.app.db.get_qsos_sota(summit=model[path][0], date=model[path][2])
                        sota_qsos.extend(search_results)

                    from .tools.export_sota import create_export_file_from_qsos
                    create_export_file_from_qsos(sota_qsos, csv_file=output_file, config=self.app.config)

        dialog.destroy()


    def export_menu_sota_chaser(self, widget):
        chaser_qsos = self.app.db.get_qsos_sota_chaser(descending=True)

        dialog = ExportSotaChaserDialog(self.app, chaser_qsos)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if dialog.selection is not None:
                model, tree_paths = dialog.selection.get_selected_rows()

                qso_ids = []

                output_file = self.display_file_dialog("csv")

                if output_file is not None:
                    for path in reversed(tree_paths):
                        qso_ids.append(model[path][0])

                    sota_qsos = self.app.db.get_qsos_sota_chaser(ids=qso_ids)
                    from .tools.export_sota_chaser import create_export_file_from_qsos
                    create_export_file_from_qsos(sota_qsos, csv_file=output_file, config=self.app.config)



        dialog.destroy()


    def export_menu_wwff_activator(self, widget):
        activations = self.app.db.get_wwff_activations()

        dialog = ExportWwffDialog(self.app, activations)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if dialog.selection is not None:
                model, tree_paths = dialog.selection.get_selected_rows()
                wwff_qsos = []

                # for now, it's just the first path, no multiselect
                # enabled
                path = tree_paths[0]

                ref = model[path][0]
                date = model[path][2]

                search_results = self.app.db.get_qsos_wwff(wwff=ref, date=date)
                wwff_qsos.extend(search_results)

                dialog.destroy()

                # for filename: callsign used takes precedense over callsign configured
                my_call = wwff_qsos[0].variables.get('MY_CALL', self.app.config.get('MY_CALLSIGN'))
                new_filename = f'{my_call.replace("/","-")}_{ref}_{date.replace("-","")}.adif'

                output_file = self.display_file_dialog("adif", filename=new_filename)
                from .tools.export_wwff import create_export_file_from_qsos
                create_export_file_from_qsos(
                    wwff_qsos,
                    adif_file=output_file,
                    config=self.app.config
                )

        dialog.destroy()


    def menu_session_new(self, widget):
        dialog = NewSessionDialog(self.app)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:

            locator = dialog.widgets['locator'].get_text()
            description = dialog.widgets['description'].get_text()
            buf = dialog.widgets['text_note'].get_buffer()
            text_note = buf.get_text(*buf.get_bounds(),include_hidden_chars=False)

            qso_session = self.app.db.create_qso_session(
                locator=locator,
                description=description,
                text_note=text_note
            )
            if dialog.widgets['activate_session'].get_active():
                self.app.set_title(self.app.config['APPLICATION_NAME'] + ' Active Session: ' + qso_session.description)
                self.app.active_session = qso_session

        dialog.destroy()


    def menu_session_reset(self, widget):
        self.app.active_session = None
        self.app.set_title(self.app.config['APPLICATION_NAME'])


    def set_application_font(self, widget):
        selector_dialog = Gtk.FontSelectionDialog("Select font name")
        response = selector_dialog.run()

        if response == Gtk.ResponseType.OK:

            font_name = selector_dialog.get_font_name()
            font_desc = Pango.FontDescription(font_name)
            if font_desc:
                self.app.override_font(font_desc)
                self.app.config['GLOBAL_FONT'] = font_name

        selector_dialog.destroy()


    def display_file_dialog(self, extension=None, filename=None):
        dialog = Gtk.FileChooserDialog("Select target file", self.app,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if filename is not None:
            dialog.set_current_name(filename)

        response = dialog.run()
        return_file = None

        if response == Gtk.ResponseType.OK:
            return_file = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

        return return_file
