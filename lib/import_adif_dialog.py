#!/usr/bin/env python

from gi.repository import Gtk
from .tools.adif_reader import read_file
from .tools.qso_preprocessor import process_qsos
from .widgets.qso_variables_editor import QsoVariablesEditor

class ImportAdifDialog(Gtk.Dialog):
    def __init__(self, parent, input_file):
        
        Gtk.Dialog.__init__(
            self, 
            "Export Sota CSV", 
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

        # build main content area
        box = self.get_content_area()

        self.qso_variables = QsoVariablesEditor(parent.config)
        box.pack_start(self.qso_variables, True, True, 0)

        self.import_button = Gtk.Button(label="Import")
        self.import_button.connect("button-press-event", self.run_import)   
        box.pack_start(self.import_button, True, False, 0)

        self.show_all()

    def run_import(self, widget, event):

        self.header, self.qsos = read_file(self.input_file)
        self.qsos = process_qsos(self.header, self.qsos, custom_variables=self.qso_variables.value)
            
        for q in self.qsos:
            qso_variables = {}

            if 'qso_variables' in q:
                qso_variables = q['qso_variables']
                del q['qso_variables']

            self.parent_app.db.create_qso(
                callsign=q['CALL'],
                mode=q['MODE'],
                datetime_utc=q['datetime_combined'],
                frequency=q['FREQ'],
                rst_sent=q['RST_SENT'],
                rst_received=q['RST_RCVD'],
                text_note=q.get('COMMENT',''),
                variables=qso_variables
            )        
        