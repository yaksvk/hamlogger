#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk
from edit_qso_dialog import EditQsoDialog
from confirm_dialog import ConfirmDialog
from qso_variables_editor import QsoVariablesEditor

import datetime

class MainWindow(Gtk.Window): 
    def __init__(self, config, db, resolver, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.config = config
        self.db = db
        self.resolver = resolver
        
        self.set_size_request(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # maximize if configured
        if config.WINDOW_MAXIMIZE:
            self.maximize()
        
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

        self.widgets['input_date'] = Gtk.Entry(max_width_chars=10, width_chars=10)
        
        self.widgets['input_time'] = Gtk.Entry(max_width_chars=5, width_chars=5)
        
        self.widgets['rst_sent'] = Gtk.Entry(max_width_chars=6, width_chars=6)
        self.widgets['rst_rcvd'] = Gtk.Entry(max_width_chars=6, width_chars=6)

        self.widgets['input_note'] = Gtk.Entry(max_width_chars=40, width_chars=40)
       
        self.widgets['name'] = Gtk.Entry(max_width_chars=15, width_chars=15)
        self.widgets['qth'] = Gtk.Entry(max_width_chars=20, width_chars=20)
        
        save_button = Gtk.Button(label="Save")
        save_button.connect("button-press-event", self.widget_save_qso)   

        # for some widgets, also add a universal keypress watcher, these will serve for return
        for i in ('call_entry', 'input_date', 'input_time', 'rst_sent', 'rst_rcvd', 'input_note', 'name', 'qth'):
            self.widgets[i].connect("key-press-event", self.widget_monitor_keypress)   


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
        label_h1.set_markup("<b>DXCC / ITU ENTITY INFO:</b>")
        vbox_h_1.pack_start(label_h1, False, True, 0)
        
        self.widgets['entity_note'] = Gtk.TextView()
        self.widgets['entity_note'].set_editable(False)
        vbox_h_1.pack_start(self.widgets['entity_note'], True, True, 0)
       

        # TODO callsign info gathethed from the internet
        label_h2 = Gtk.Label()
        label_h2.set_markup("<b>QSO VARIABLES:</b>")
        vbox_h_2.pack_start(label_h2, False, True, 0)
        self.qso_variables = QsoVariablesEditor(self.config)
        
        vbox_h_2.pack_start(self.qso_variables, True, True, 0)
        

        label_h3 = Gtk.Label()
        label_h3.set_markup("<b>CALLSIGN NOTE:</b>")
        vbox_h_3.pack_start(label_h3, False, True, 0)

        # TODO - connect this to callsign note
        self.widgets['callsign_note'] = Gtk.TextView()
        vbox_h_3.pack_start(self.widgets['callsign_note'], True, True, 0)

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
        treeView_p.connect('button-release-event', self.current_log_keyrelease)
        
        swp.add(treeView_p)
        
        self.dupe_log_scroll_window = swp
        self.dupe_log_tree = treeView_p
        
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

        self.current_log_tree = Gtk.TreeView(self.current_log_store)
        self.current_log_tree.set_rules_hint(True)
        self.current_log_tree.connect('button-release-event', self.current_log_keyrelease)
        sw.add(self.current_log_tree)

        self.tree_data_create_columns(self.current_log_tree)
        
        self.current_log_scroll_window = sw

        # CURRENT LOG CONTEXT MENU
        self.current_log_context_menu = Gtk.Menu()
        menu_item1 = Gtk.MenuItem("Edit QSO")
        menu_item1.connect("activate", self.current_log_edit_qso)
        
        separator = Gtk.SeparatorMenuItem()

        menu_item2 = Gtk.MenuItem("Delete QSO")
        menu_item2.connect("activate", self.current_log_delete_qso)

        self.current_log_context_menu.append(menu_item1)
        self.current_log_context_menu.append(separator)
        self.current_log_context_menu.append(menu_item2)
        menu_item1.show()
        separator.show()
        menu_item2.show()
        
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
            self.update_entity_info(new_text)
        else:
            self.dupe_log_store.clear()
    
    def widget_monitor_keypress(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        
        # guard for return
        if keyname == 'Return':
            self.widget_save_qso(widget, event)
            return
        
        # guard for TAB
        if keyname == 'Tab':
            
            # complete RST reports 
            if widget in (self.widgets['rst_sent'], self.widgets['rst_rcvd']):
                if not widget.get_text():
                    mode = self.widgets['mode_combo'].get_active_text()
                    # TODO: this should be somewhat configurable, but ok for now
                    if mode in ('CW', 'RTTY'):
                        widget.set_text('599')
                    else:
                        widget.set_text('59')

            # TODO enable auto-jump mode here, so that one tab fills in date and time and focuses on RST 
            
            # complete date (when focused on CALL and call not empty or when focused on date and date not empty)
            if (widget == self.widgets['call_entry'] and self.widgets['call_entry'].get_text()) or widget == self.widgets['input_date']:
                if not self.widgets['input_date'].get_text():
                    utc = datetime.datetime.utcnow().timetuple()
                    self.widgets['input_date'].set_text("%04i-%02i-%02i" % (utc.tm_year , utc.tm_mon, utc.tm_mday))
            
            # complete time when focused on date or time
            if (widget == self.widgets['input_date'] and self.widgets['input_date'].get_text()) or widget == self.widgets['input_time']:
                if not self.widgets['input_time'].get_text():
                    utc = datetime.datetime.utcnow().timetuple()
                    self.widgets['input_time'].set_text("%02i:%02i" % (utc.tm_hour, utc.tm_min))

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
                callsign=callsign.decode('utf-8'),
                mode=mode.decode('utf-8'),
                datetime_utc=datetime_combined,
                frequency=freq.decode('utf-8'),
                rst_sent=self.widgets['rst_sent'].get_text().decode('utf-8'), 
                rst_received=self.widgets['rst_rcvd'].get_text().decode('utf-8'),
                name_received=self.widgets['name'].get_text().decode('utf-8'),
                qth_received=self.widgets['qth'].get_text().decode('utf-8'),
                text_note=self.widgets['input_note'].get_text().decode('utf-8'),
                callsign_text_note=cs_text_note.decode('utf-8'),
                country_received=self.country,
                variables=self.qso_variables.value
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
        self.dupe_log_store.clear(
        )

    def current_log_keyrelease(self, widget, event):
        if event.button == 3:
            # if right click was pressed
            x = int(event.get_root_coords()[0])
            y = int(event.get_root_coords()[1])
            time = event.time
            
            self.last_active_tree = widget
            self.current_log_context_menu.popup(None, None, lambda menu, user_data: (x, y, True), widget, 3, time)
    
    def update_entity_info(self, callsign):
        # TODO also, if many subsequent searches are made, i.e. OM, OM1, OM1AWS, do not re-do the search, unless
        # we're deleting some chars
        
        result = self.resolver.get_entity_for_call(callsign)
        if result is not None:
            text = ("Country: %s\nITU zone: %s\nCQ zone: %s\nLat / Long: %s / %s\nUTC offset: %s" %
                (result['name'], result['itu_zone'], result['cq_zone'], result['lat'], result['long'], result['utc']))
            self.widgets['entity_note'].get_buffer().set_text(text)
            self.country = result['name'].decode('utf-8')
        else:
            self.widgets['entity_note'].get_buffer().set_text('')
            self.country = None
    
    def current_log_edit_qso(self, widget):
        
        
        selection = self.last_active_tree.get_selection()
        model, treeiter = selection.get_selected()
            
        column_id = model[treeiter][0]  
        path = model.get_path(treeiter)
        
        self.editing_qso_id = column_id
        
        edit_dialog = EditQsoDialog(self)
        response = edit_dialog.run()
        
        if response == Gtk.ResponseType.OK:
           
            freq = edit_dialog.widgets['band_combo'].get_active_text()
            mode = edit_dialog.widgets['mode_combo'].get_active_text()
            
            callsign = edit_dialog.widgets['call_entry'].get_text()
            dfields = edit_dialog.widgets['input_date'].get_text().split('-')
            dat = datetime.date(*map(int, dfields))
            tfields = edit_dialog.widgets['input_time'].get_text().split(':')
            utc = datetime.time(int(tfields[0]), int(tfields[1]))
            
            datetime_combined=datetime.datetime.combine(dat, utc)
            buf = edit_dialog.widgets['callsign_note'].get_buffer()
            cs_text_note = buf.get_text(*buf.get_bounds(),include_hidden_chars=False)
            
            
            text_note = edit_dialog.widgets['input_note'].get_text()
            #print edit_dialog.qso_variables.value
            
            self.db.update_qso(
                
                edit_dialog.found_qso,
                
                callsign=callsign.decode('utf-8'),
                mode=mode.decode('utf-8'),
                datetime_utc=datetime_combined,
                frequency=freq.decode('utf-8'),
                rst_sent=edit_dialog.widgets['rst_sent'].get_text().decode('utf-8'), 
                rst_received=edit_dialog.widgets['rst_rcvd'].get_text().decode('utf-8'),
                name_received=edit_dialog.widgets['name'].get_text().decode('utf-8'),
                qth_received=edit_dialog.widgets['qth'].get_text().decode('utf-8'),
                country_received=edit_dialog.widgets['country_received'].get_text().decode('utf-8'),
                callsign_text_note=cs_text_note.decode('utf-8'),
                text_note=text_note.decode('utf-8'),
                variables=edit_dialog.qso_variables.value,
            )
            
            
            current_tree = self.current_log_tree.get_vadjustment().get_value()
            
              
            # dupe_tree = self.dupe_log_tree.get_vadjustment().get_value()
            
            
            self.tree_data_refresh_main_tree()
            self.tree_data_refresh_dupe_tree()
            
            # self.current_log_tree.get_vadjustment().set_value(current_tree)
            # self.current_log_scroll_window.get_vadjustment().set_value(current_win)
            
                        
            self.current_log_tree.scroll_to_cell(path)
            
            
            if edit_dialog.found_qso.callsign_entity.text_note is not None:
                self.widgets['callsign_note'].get_buffer().set_text(edit_dialog.found_qso.callsign_entity.text_note)
            else:
                self.widgets['callsign_note'].get_buffer().set_text('')
                
            self.widgets['call_entry'].grab_focus()
       
        
        elif response == Gtk.ResponseType.CANCEL:
            pass
        else:
            pass

        edit_dialog.destroy()
        
        
    def current_log_delete_qso(self, widget):
        selection = self.last_active_tree.get_selection()
        model, treeiter = selection.get_selected()
            
        column_id = model[treeiter][0]   
        self.editing_qso_id = column_id # TODO refactor get active Id, we have it too many times here
        found_qso = self.db.get_first_qso(id=self.editing_qso_id)
        
        # open a yes-no dialog to confirm action
        confirm_dialog = ConfirmDialog(self)
        response = confirm_dialog.run()
        
        if response == Gtk.ResponseType.OK:
            self.db.delete_qso(found_qso)
            
            self.tree_data_refresh_main_tree()
            self.tree_data_refresh_dupe_tree()
        
        confirm_dialog.destroy()
        
    # TREE LOADING / REFRESHING FUNCTIONS


    def tree_data_create_model(self):
        store = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str, str, str)

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
                      qso.country_received,
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
                    qso.country_received,
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
   
        columns = ['ID','DATE', 'UTC', 'FREQ', 'MODE', 'CALL', 'RST_SENT', 'RST_RCVD', 'NAME', 'QTH', 'COUNTRY', 'NOTE']

        for i, column in enumerate(columns):
            rendererText = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(column, rendererText, text=i)
            col.set_sort_column_id(i)    
            treeView.append_column(col)
    

