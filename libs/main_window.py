#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk
import datetime

class MainWindow(Gtk.Window): 
    def __init__(self, config, db, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.config = config
        self.db = db
        
        self.set_size_request(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # PREPARE FOR ALL THE WIDGETS
        self.widgets = {}
        
        # MENU HEADERS
        
        
        
        
        
        # MAIN CONTENT
        main_vbox = Gtk.VBox(False, 8)
        
        self.widgets['band_combo'] = Gtk.ComboBoxText()
        for band in config.BANDS:
            self.widgets['band_combo'].append_text(band)
        self.widgets['band_combo'].set_active(1)
        
        self.widgets['mode_combo'] = Gtk.ComboBoxText()
        for mode in config.MODES:
            self.widgets['mode_combo'].append_text(mode)
        self.widgets['mode_combo'].set_active(0)

        self.widgets['call_entry'] = Gtk.Entry(max_width_chars=10, width_chars=10)
        self.widgets['call_entry'].connect("changed", self.widget_call_entry_changed) 
        self.widgets['call_entry'].connect("key-press-event", self.widget_call_entry_keypress)   

        self.widgets['input_date'] = Gtk.Entry(max_width_chars=10, width_chars=10)
        self.widgets['input_time'] = Gtk.Entry(max_width_chars=5, width_chars=5)
        
        self.widgets['rst_sent'] = Gtk.Entry(max_width_chars=6, width_chars=6)
        self.widgets['rst_rcvd'] = Gtk.Entry(max_width_chars=6, width_chars=6)

        self.widgets['rst_sent'].connect("key-press-event", self.widget_rst_keypress)   
        self.widgets['rst_rcvd'].connect("key-press-event", self.widget_rst_keypress)   

        self.widgets['input_note'] = Gtk.Entry(max_width_chars=40, width_chars=40)
       
        self.widgets['name'] = Gtk.Entry(max_width_chars=15, width_chars=15)
        self.widgets['qth'] = Gtk.Entry(max_width_chars=20, width_chars=20)
        
        save_button = Gtk.Button(label="Save")
        save_button.connect("button-press-event", self.widget_save_qso)   

        # for some widgets, also add a universal keypress watcher, these will serve for return
        for i in ('call_entry', 'input_date', 'input_time', 'rst_sent', 'rst_rcvd', 'input_note', 'name', 'qth'):
            self.widgets[i].connect("key-press-event", self.widget_guard_for_return)   


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
            ("NOTE", self.widgets['input_note'],4),
            ("", save_button, 1),
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
        
        main_vbox.pack_start(table_label, False, True, 0)
        main_vbox.pack_start(table, False, True, 0)
        
        hbox = Gtk.HBox(False, 3)

        vbox_h_1 = Gtk.VBox(False, 2)
        vbox_h_2 = Gtk.VBox(False, 2)
        vbox_h_3 = Gtk.VBox(False, 2)


        # TODO DXCC info block
        label_h1 = Gtk.Label()
        label_h1.set_markup("<b>DXCC INFO:</b>")
        vbox_h_1.pack_start(label_h1, True, True, 0)

        # TODO callsign info gathethed from the internet
        label_h2 = Gtk.Label()
        label_h2.set_markup("<b>CALLSIGN INFO:</b>")
        vbox_h_2.pack_start(label_h2, True, True, 0)

        label_h3 = Gtk.Label()
        label_h3.set_markup("<b>CALLSIGN NOTE:</b>")
        vbox_h_3.pack_start(label_h3, False, True, 0)

        # TODO - connect this to callsign note
        self.widgets['callsign_note'] = Gtk.TextView()
        vbox_h_3.pack_start(self.widgets['callsign_note'], False, True, 0)

        hbox.pack_start(vbox_h_1, True, True, 0)
        hbox.pack_start(vbox_h_2, True, True, 0)
        hbox.pack_start(vbox_h_3, True, True, 0)
        

        main_vbox.pack_start(hbox, True, True, 0)
       
        # PREVIOUS CONVERSATIONS

        label_previous_log = Gtk.Label()
        label_previous_log.set_markup("<b>PREVIOUS CONVERSATIONS WITH THIS CALLSIGN:</b>")
        main_vbox.pack_start(label_previous_log, False, True, 0)

        swp = Gtk.ScrolledWindow()
        swp.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        swp.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        swp.set_min_content_height(self.config.DUPE_LIST_HEIGHT)
        main_vbox.pack_start(swp, False, True, 0)

        self.dupe_log_store = self.tree_data_create_model()

        treeView_p = Gtk.TreeView(self.dupe_log_store)
        swp.add(treeView_p)

        self.tree_data_create_columns(treeView_p)


        # CURRENT LOG


        label_current_log = Gtk.Label()
        label_current_log.set_markup("<b>CURRENT LOG:</b>")
        main_vbox.pack_start(label_current_log, False, True, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        main_vbox.pack_start(sw, True, True, 0)

        self.current_log_store = self.tree_data_create_model() 

        treeView = Gtk.TreeView(self.current_log_store)
        treeView.set_rules_hint(True)
        sw.add(treeView)

        self.tree_data_create_columns(treeView)


        
        # FOOTER
        self.statusbar = Gtk.Statusbar()
        main_vbox.pack_start(self.statusbar, False, False, 0)
            
        # FINISH OFF
        self.add(main_vbox)

        # reload tree for the first time
        self.tree_data_refresh_main_tree()
        self.widgets['call_entry'].grab_focus()

    
    # EVENT HANDLING FUNCTIONS FOR THE WIDGETS

    def something():
        pass

    def widget_call_entry_changed(self, widget):
        new_text = widget.get_text().upper()
        widget.set_text(new_text)

        if len(new_text) > 1:
            self.tree_data_refresh_dupe_tree()
        else:
            self.dupe_log_store.clear()

        

    def widget_call_entry_keypress(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Tab':
            # get current UTC date and time
            utc = datetime.datetime.utcnow().timetuple()
            self.widgets['input_date'].set_text("%04i-%02i-%02i" % (utc.tm_year , utc.tm_mon, utc.tm_mday))
            self.widgets['input_time'].set_text("%02i:%02i" % (utc.tm_hour, utc.tm_min))
            
            self.widgets['input_time'].grab_focus()
        
    def widget_rst_keypress(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Tab':
            widget.set_text('59')

    def widget_guard_for_return(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Return':
            self.widget_save_qso(widget, event)

    def widget_save_qso(self, widget, event):        
        # check if at least CALL, DATE, TIME and RST SENT and RECEIVED are present and save
        obligatories = ['call_entry', 'input_date', 'input_time', 'rst_sent', 'rst_rcvd']

        freq = self.widgets['band_combo'].get_active_text()
        mode = self.widgets['mode_combo'].get_active_text()

        for i in obligatories:
            if self.widgets[i].get_text() == '':
                print "Not adding. Obligatory fields empty."
                return

        # save
        callsign = self.widgets['call_entry'].get_text()
        dfields = self.widgets['input_date'].get_text().split('-')
        dat = datetime.date(*map(int, dfields))
        tfields = self.widgets['input_time'].get_text().split(':')
        utc = datetime.time(int(tfields[0]), int(tfields[1]))

        datetime_combined=datetime.datetime.combine(dat, utc)
        
        found_qso = self.db.get_first_qso(callsign=unicode(callsign),datetime_utc=datetime_combined)
        if found_qso:
            print "Not adding. Dupe."
        else:
            buf = self.widgets['callsign_note'].get_buffer()
            cs_text_note = buf.get_text(*buf.get_bounds(),include_hidden_chars=False)

            qso = self.db.create_qso(
                callsign=unicode(callsign),
                mode=unicode(mode),
                datetime_utc=datetime_combined,
                frequency=unicode(freq),
                rst_sent=unicode(self.widgets['rst_sent'].get_text()), 
                rst_received=unicode(self.widgets['rst_rcvd'].get_text()),
                name_received=unicode(self.widgets['name'].get_text()),
                qth_received=unicode(self.widgets['qth'].get_text()),
                text_note=unicode(self.widgets['input_note'].get_text()),
                callsign_text_note=unicode(cs_text_note),
            #    country_received=row[9].value,
            # TODO get country from DXCC entity
            )


        # clean fields and grab focus
        for i in obligatories:
            self.widgets[i].set_text('')

        self.widgets['rst_sent'].set_text('')
        self.widgets['rst_rcvd'].set_text('')
        self.widgets['name'].set_text('')
        self.widgets['qth'].set_text('')
        self.widgets['input_note'].set_text('')
        self.widgets['callsign_note'].get_buffer().set_text('')

        self.widgets['call_entry'].grab_focus()
        self.tree_data_refresh_main_tree()
        self.dupe_log_store.clear()

    # TREE LOADING / REFRESHING FUNCTIONS


    def tree_data_create_model(self):
        store = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str, str)

        return store

    def tree_data_refresh_main_tree(self):
        self.current_log_store.clear()

        qsos = self.db.get_qsos()
        for qso in qsos:
            self.current_log_store.append(
                  (
                      qso.id, 
                      qso.datetime_utc.date().isoformat(), 
                      qso.datetime_utc.time().isoformat()[:5], 
                      qso.frequency,
                      qso.mode, 
                      qso.callsign,
                      qso.rst_sent, 
                      qso.rst_received,
                      qso.name_received, 
                      qso.qth_received, 
                      qso.text_note
                  )
            )

    def tree_data_refresh_dupe_tree(self):
        self.dupe_log_store.clear()
        
        qsos = self.db.get_qsos(callsign_filter=self.widgets['call_entry'].get_text())
        for qso in qsos:
            self.dupe_log_store.append(
                (
                    qso.id, 
                    qso.datetime_utc.date().isoformat(), 
                    qso.datetime_utc.time().isoformat()[:5], 
                    qso.frequency, 
                    qso.mode, 
                    qso.callsign, 
                    qso.rst_sent,
                    qso.rst_received,
                    qso.name_received,
                    qso.qth_received,
                    qso.text_note 
                )
            )

        # also try to find if all qsos belong to one callsign - in that case, load their details
        a = set(i.callsign_entity for i in qsos )
        if len(a) == 1:
            self.active_callsign_entity = a.pop()
            if self.active_callsign_entity.text_note is not None:
                self.widgets['callsign_note'].get_buffer().set_text(self.active_callsign_entity.text_note)
            else:
                self.widgets['callsign_note'].get_buffer().set_text('')
            
        else:
            # clear field
            self.active_callsign_entity = None
            self.widgets['callsign_note'].get_buffer().set_text('')

    def tree_data_create_columns(self, treeView):
   
        columns = ['ID','DATE', 'UTC', 'FREQ', 'MODE', 'CALL', 'RST_SENT', 'RST_RCVD', 'NAME', 'QTH', 'NOTE']

        for i, column in enumerate(columns):
            rendererText = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(column, rendererText, text=i)
            col.set_sort_column_id(i)    
            treeView.append_column(col)
        


