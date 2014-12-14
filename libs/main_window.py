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
        
        
        save_button = Gtk.Button(label="Save")
        save_button.connect("button-press-event", self.widget_save_qso)   
        
        items = (
            ("FREQ", self.widgets['band_combo'],1),
            ("MODE", self.widgets['mode_combo'],1),
            ("CALL", self.widgets['call_entry'],2),  
            ("DATE", self.widgets['input_date'],1),
            ("UTC", self.widgets['input_time'],1),
            ("RST SENT", self.widgets['rst_sent'],1),
            ("RST RCVD", self.widgets['rst_rcvd'],1),
            ("NAME", Gtk.Entry(max_width_chars=15, width_chars=15),2),
            ("QTH", Gtk.Entry(max_width_chars=20, width_chars=20),2),
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
        text_field = Gtk.TextView()
        vbox_h_3.pack_start(text_field, True, True, 0)

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
        main_vbox.pack_start(swp, True, True, 0)

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

    def widget_save_qso(self, widget, event):
        pass
        #print "testing event, cleaning test store"
        #self.store_previous.clear()

        self.tree_data_refresh_main_tree();

    # TREE LOADING / REFRESHING FUNCTIONS


    def tree_data_create_model(self):
        store = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str, str)

        return store

    def tree_data_refresh_main_tree(self):
        self.current_log_store.clear()

        qsos = self.db.get_qsos()
        for qso in qsos:
            self.current_log_store.append(
                  (qso.id, qso.date.isoformat(), qso.utc_time.isoformat()[:5], qso.frequency, qso.mode, qso.callsign, qso.rst_sent, qso.rst_received, qso.name_received, qso.qth_received, qso.text_note )
            )

    def tree_data_refresh_dupe_tree(self):
        self.dupe_log_store.clear()
        
        qsos = self.db.get_qsos(callsign_filter=self.widgets['call_entry'].get_text())
        for qso in qsos:
            self.dupe_log_store.append(
                (qso.id, qso.date.isoformat(), qso.utc_time.isoformat()[:5], qso.frequency, qso.mode, qso.callsign, qso.rst_sent, qso.rst_received, qso.name_received, qso.qth_received, qso.text_note )
            )
       


    def tree_data_create_columns(self, treeView):
   
        columns = ['ID','DATE', 'UTC', 'FREQ', 'MODE', 'CALL', 'RST_SENT', 'RST_RCVD', 'NAME', 'QTH', 'NOTE']

        for i, column in enumerate(columns):
            rendererText = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(column, rendererText, text=i)
            col.set_sort_column_id(i)    
            treeView.append_column(col)
        


