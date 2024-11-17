#!/usr/bin/env python

from gi.repository import Gtk
from .tools.adif_reader import read_file
from .tools.qso_preprocessor import process_qsos
from .widgets.qso_variables_editor import QsoVariablesEditor
import os

class ImportAdifDialog(Gtk.Dialog):
    def __init__(self, parent, input_file):

        Gtk.Dialog.__init__(
            self,
            "Import ADIF",
            parent,
            Gtk.DialogFlags.MODAL,
        )

        self.parent_app = parent
        self.add_buttons('Close', Gtk.ResponseType.CANCEL)

        self.set_default_size(
            parent.config['SOTA_EXPORT_WIDTH'],
            parent.config['SOTA_EXPORT_HEIGHT']
        )

        self.input_file = input_file
        self.set_title(self.get_title() + ' from: <' + os.path.basename(input_file) + '>')

        # build main content area
        box = self.get_content_area()

        self.qso_variables = QsoVariablesEditor(parent.config)
        box.pack_start(self.qso_variables, True, True, 0)


        self.session = {}
        label_session_desc = Gtk.Label()
        label_session_desc.set_markup("<b>Description (short):</b>")
        self.session['description'] = Gtk.Entry(max_width_chars=64, width_chars=64)

        label_session_note = Gtk.Label()
        label_session_note.set_markup("<b>About Session (Note):</b>")
        self.session['text_note'] = Gtk.TextView()

        box.pack_start(label_session_desc, False, False, 0)
        box.pack_start(self.session['description'], True, False, 0)

        box.pack_start(label_session_note, False, False, 0)
        box.pack_start(self.session['text_note'] , True, False, 0)


        self.import_button = Gtk.Button(label="Import")
        self.import_button.connect("button-press-event", self.run_import)
        box.pack_start(self.import_button, True, False, 0)

        self.show_all()

    def run_import(self, widget, event):

        self.header, self.qsos = read_file(self.input_file)
        self.qsos = process_qsos(self.header, self.qsos, custom_variables=self.qso_variables.value)

        session_desc = self.session['description'].get_text()

        buf = self.session['text_note'].get_buffer()
        session_note = buf.get_text(*buf.get_bounds(),include_hidden_chars=False)

        qso_session = self.parent_app.db.create_qso_session(
            description=session_desc,
            text_note=session_note
        )

        for q in self.qsos:
            qso_variables = {}

            country = ''
            country_result = self.parent_app.resolver.get_entity_for_call(q['CALL'])

            if country_result and 'name' in country_result:
                country = country_result['name']

            if 'qso_variables' in q:
                qso_variables = q['qso_variables']
                del q['qso_variables']

            # mapped variables (do not use all ADIF fields)
            mapping = {
                'callsign': 'CALL',
                'mode': 'MODE',
                'datetime_utc': 'datetime_combined',
                'name_received': 'NAME',
                'qth_received': 'QTH',
                'frequency': 'FREQ',
                'rst_sent': 'RST_SENT',
                'rst_received': 'RST_RCVD',
                'text_note': 'COMMENT',
            }

            kwargs = {native_var: q[adif_var] for native_var, adif_var in mapping.items() if adif_var in q}
            if 'text_note' not in kwargs or kwargs['text_note'] is None:
                kwargs['text_note'] = ''

            kwargs['country_received'] = country
            kwargs['variables'] = qso_variables
            kwargs['qso_session'] = qso_session




            self.parent_app.db.create_qso(
                **kwargs
            )

        self.parent_app.tree_data_refresh_main_tree()
