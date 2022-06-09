#!/usr/bin/env python

from gi.repository import Gtk
from .widgets.qso_variables_editor import QsoVariablesEditor
from functools import reduce

class EditQsoDialog(Gtk.Dialog):

    def __init__(self, parent):


        Gtk.Dialog.__init__(
            self,
            "Edit QSO",
            parent,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        self.set_default_size(
            parent.config['EDIT_QSO_WIDTH'],
            parent.config['EDIT_QSO_HEIGHT']
        )

        # get QSO to edit

        self.found_qso = parent.db.get_first_qso(id=parent.editing_qso_id)
        # TODO handle case: found_qso is None: self.response(Gtk.ResponseType.CANCEL)



        box = self.get_content_area()


         # PREPARE FOR ALL THE WIDGETS
        self.widgets = {}

        self.widgets['qso_session_combo'] = Gtk.ComboBoxText()
        self.qso_sessions = parent.db.get_qso_sessions()

        for session in self.qso_sessions:
            self.widgets['qso_session_combo'].append_text(str(session.id) + ' ' + session.description)
        self.widgets['qso_session_combo'].append_text("No session")
        self.qso_sessions.append(None)

        if self.found_qso.qso_session:
            self.widgets['qso_session_combo'].set_active(self.qso_sessions.index(self.found_qso.qso_session))


        self.widgets['band_combo'] = Gtk.ComboBoxText()
        for band in parent.config['BANDS']:
            self.widgets['band_combo'].append_text(band)

        try:
            self.widgets['band_combo'].set_active(parent.config['BANDS'].index(self.found_qso.frequency))
        except Exception as e:
            pass


        self.widgets['mode_combo'] = Gtk.ComboBoxText()
        for mode in parent.config['MODES']:
            self.widgets['mode_combo'].append_text(mode)

        try:
            self.widgets['mode_combo'].set_active(parent.config['MODES'].index(self.found_qso.mode))
        except Exception as e:
            pass

        self.widgets['call_entry'] = Gtk.Entry(max_width_chars=10, width_chars=10)
        if self.found_qso.callsign is not None:
            self.widgets['call_entry'].set_text(self.found_qso.callsign)

        self.widgets['input_date'] = Gtk.Entry(max_width_chars=10, width_chars=10)
        self.widgets['input_time'] = Gtk.Entry(max_width_chars=5, width_chars=5)

        utc = self.found_qso.datetime_utc.timetuple()
        self.widgets['input_date'].set_text("%04i-%02i-%02i" % (utc.tm_year , utc.tm_mon, utc.tm_mday))
        self.widgets['input_time'].set_text("%02i:%02i" % (utc.tm_hour, utc.tm_min))

        self.widgets['rst_sent'] = Gtk.Entry(max_width_chars=6, width_chars=6)
        self.widgets['rst_rcvd'] = Gtk.Entry(max_width_chars=6, width_chars=6)

        if self.found_qso.rst_sent is not None:
            self.widgets['rst_sent'].set_text(self.found_qso.rst_sent)

        if self.found_qso.rst_received is not None:
            self.widgets['rst_rcvd'].set_text(self.found_qso.rst_received)

        self.widgets['country_received'] = Gtk.Entry(max_width_chars=14, width_chars=14)
        if self.found_qso.country_received is not None:
            self.widgets['country_received'].set_text(self.found_qso.country_received)


        self.widgets['input_note'] = Gtk.Entry(max_width_chars=40, width_chars=40)

        self.widgets['name'] = Gtk.Entry(max_width_chars=15, width_chars=15)
        self.widgets['qth'] = Gtk.Entry(max_width_chars=20, width_chars=20)


        if self.found_qso.name_received is not None:
            self.widgets['name'].set_text(self.found_qso.name_received)
        if self.found_qso.qth_received is not None:
            self.widgets['qth'].set_text(self.found_qso.qth_received)

        self.widgets['qsl_sent'] =  Gtk.CheckButton(label="sent")
        self.widgets['qsl_received'] =  Gtk.CheckButton(label="received")

        self.widgets['qsl_sent'].set_active(self.found_qso.qsl_sent == True)
        self.widgets['qsl_received'].set_active(self.found_qso.qsl_received == True)




        #save_button.connect("button-press-event", self.widget_save_qso)   

        items = (
            ("FREQ", self.widgets['band_combo'],1),
            ("MODE", self.widgets['mode_combo'],1),
            ("CALL", self.widgets['call_entry'],2),
            ("DATE", self.widgets['input_date'],1),
            ("UTC", self.widgets['input_time'],1),
            ("RST SENT", self.widgets['rst_sent'],1),
            ("RST RCVD", self.widgets['rst_rcvd'],1),
            ("NAME",  self.widgets['name'],2),
            ("QTH",  self.widgets['qth'],2),
            ("COUNTRY",  self.widgets['country_received'],2),
        )

        flex_sum = reduce(lambda x,y: x + y, [ i[2] for i in items ] )

        # create a table with a phantom number of columns (calculated flex sum)
        table = Gtk.Table(rows=2, columns=flex_sum, homogeneous=False)

        flex_cumulative = 0
        for item in items:
            table.attach(Gtk.Label(item[0]), flex_cumulative, flex_cumulative + item[2], 0, 1)
            table.attach(item[1], flex_cumulative, flex_cumulative + item[2], 1, 2)
            flex_cumulative += item[2]

        table_label = Gtk.Label()
        table_label.set_markup("<b>EDIT QSO:</b>")

        box.pack_start(table_label, False, True, 0)
        box.pack_start(table, False, True, 0)

        note_label = Gtk.Label()
        note_label.set_markup("<b>QSO NOTE:</b>")

        box.pack_start(note_label, False, True, 0)
        box.pack_start(self.widgets['input_note'], False, True, 0)

        if self.found_qso.text_note is not None:
            self.widgets['input_note'].set_text(self.found_qso.text_note)

        session_label = Gtk.Label()
        session_label.set_markup("<b>QSO SESSION:</b>")

        box.pack_start(session_label, False, True, 0)
        box.pack_start(self.widgets['qso_session_combo'], False, True, 0)


        hbox = Gtk.HBox(False, 2)
        vbox_h_1 = Gtk.VBox(False, 2)
        vbox_h_2 = Gtk.VBox(False, 4)


        label_h3 = Gtk.Label()
        label_h3.set_markup("<b>CALLSIGN NOTE:</b>")
        self.widgets['callsign_note'] = Gtk.TextView()
        if self.found_qso.callsign_entity.text_note is not None:
            self.widgets['callsign_note'].get_buffer().set_text(self.found_qso.callsign_entity.text_note)
        vbox_h_1.pack_start(label_h3, False, True, 0)
        vbox_h_1.pack_start(self.widgets['callsign_note'], True, True, 0)

        label_h4 = Gtk.Label()
        label_h4.set_markup("<b>QSO VARIABLES:</b>")
        self.qso_variables = QsoVariablesEditor(parent.config)

        if self.found_qso.variables:
            self.qso_variables.value = self.found_qso.variables

        vbox_h_2.pack_start(label_h4, False, True, 0)
        vbox_h_2.pack_start(self.qso_variables, True, True, 0)

        label_h5 = Gtk.Label()
        label_h5.set_markup("<b>QSL DETAILS:</b>")
        vbox_h_2.pack_start(label_h5, False, True, 0)


        hbox_qsl = Gtk.HBox(False, 2)

        hbox_qsl.pack_start(self.widgets['qsl_sent'], True, True, 0)
        hbox_qsl.pack_start(self.widgets['qsl_received'], True, True, 0)


        vbox_h_2.pack_start(hbox_qsl, False, True, 0)


        hbox.pack_start(vbox_h_1, True, True, 0)
        hbox.pack_start(vbox_h_2, True, True, 0)

        box.pack_start(hbox, True, True, 0)

        self.show_all()


