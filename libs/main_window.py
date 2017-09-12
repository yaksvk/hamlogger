#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk
from rst_entry import RstEntry
from edit_qso_dialog import EditQsoDialog
from edit_qso_multiple_dialog import EditQsoMultipleDialog
from confirm_dialog import ConfirmDialog
from qso_variables_editor import QsoVariablesEditor
from session_manage_dialog import ManageSessionDialog
from session_new_dialog import NewSessionDialog
from export_sota_dialog import ExportSotaDialog
from export_sota_chaser_dialog import ExportSotaChaserDialog
from models import CallsignEntity

import datetime
import sys

HAMCALL_ROOT = 'http://www.hamcall.net/call/'
QRZ_ROOT = 'http://www.qrz.com/db/'
HAMQTH_ROOT = 'http://www.hamqth.com/'

class MainWindow(Gtk.Window): 
    def __init__(self, config, db, resolver, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.config = config
        self.db = db
        self.resolver = resolver
        self.active_session = None
        
        self.logging_mode_standard = True
        self.logging_mode_contest = False

        # manual editing mode (as opposed to clicking-through mode)
        self.editing_mode = False
        
        self.obligatories = ['call_entry', 'input_date', 'input_time', 'rst_sent', 'rst_rcvd']
        
        self.set_size_request(config['WINDOW_WIDTH'], config['WINDOW_HEIGHT'])
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # maximize if configured
        if config['WINDOW_MAXIMIZE']:
            self.maximize()
        
        # PREPARE FOR ALL THE WIDGETS
        self.widgets = {}
        self.locked_widgets = {}
        
        
        # CONNECT KEYPRESS EVENTS
        self.connect('key-press-event', self.window_key_press)
        
        
        
        
        # MAIN CONTENT
        main_vbox = Gtk.VBox(False, 8)
        
        # MENU HEADERS
        
        menu_bar = Gtk.MenuBar()
        menu_bar_file = Gtk.MenuItem("File")
        menu_bar_file_menu = Gtk.Menu()
        menu_bar_file_menu_exit = Gtk.MenuItem("Exit")
        menu_bar_file_menu_exit.connect("activate", self.menu_file_exit)
        
        menu_bar_file_menu.append(menu_bar_file_menu_exit)
        menu_bar_file.set_submenu(menu_bar_file_menu)
        menu_bar.append(menu_bar_file)
        
        menu_bar_export = Gtk.MenuItem("Export")
        menu_bar_export_menu = Gtk.Menu()
        menu_bar_export_menu_ods = Gtk.MenuItem("OpenDocument")
        menu_bar_export_menu_adif = Gtk.MenuItem("ADIF")
        menu_bar_export_menu_sota = Gtk.MenuItem("SOTA CSV Activator")
        menu_bar_export_menu_sota.connect("activate", self.export_menu_sota)
        menu_bar_export_menu_sota_chaser = Gtk.MenuItem("SOTA CSV Chaser")
        menu_bar_export_menu_sota_chaser.connect("activate", self.export_menu_sota_chaser)
        
        # TODO hide these two - we do not have gui functions for these yet
        #menu_bar_export_menu.append(menu_bar_export_menu_ods)
        #menu_bar_export_menu.append(menu_bar_export_menu_adif)
        menu_bar_export_menu.append(menu_bar_export_menu_sota)
        menu_bar_export_menu.append(menu_bar_export_menu_sota_chaser)
        menu_bar_export.set_submenu(menu_bar_export_menu)
        menu_bar.append(menu_bar_export)
        
        
        menu_bar_session = Gtk.MenuItem("Sessions")
        menu_bar_session_menu = Gtk.Menu()
        menu_bar_session_menu_new = Gtk.MenuItem("New")
        menu_bar_session_menu_new.connect("activate", self.menu_session_new)

        # TODO hide session management - not yet available
        #menu_bar_session_menu_manage = Gtk.MenuItem("Manage")
        #menu_bar_session_menu_manage.connect("activate", self.menu_session_manage)
        menu_bar_session_menu_reset = Gtk.MenuItem("Reset")
        menu_bar_session_menu_reset.connect("activate", self.menu_session_reset)
        
        menu_bar_session_menu.append(menu_bar_session_menu_new)
        #menu_bar_session_menu.append(menu_bar_session_menu_manage)
        menu_bar_session_menu.append(menu_bar_session_menu_reset)
        menu_bar_session.set_submenu(menu_bar_session_menu)
        menu_bar.append(menu_bar_session)
        
        menu_bar_mode = Gtk.MenuItem("Mode")

        menu_bar_mode_menu = Gtk.Menu()
        menu_bar_mode_menu_standard = Gtk.MenuItem("Standard")
        menu_bar_mode_menu_standard.connect("activate", self.menu_mode_switch, "standard")
        menu_bar_mode_menu_contest = Gtk.MenuItem("Contest")
        menu_bar_mode_menu_contest.connect("activate", self.menu_mode_switch, "contest")
        menu_bar_mode_menu_qsl = Gtk.MenuItem("QSL Agenda")
        menu_bar_mode_menu_qsl.connect("activate", self.menu_mode_switch, "qsl_agenda")
        menu_bar_mode_menu.append(menu_bar_mode_menu_standard)
        menu_bar_mode_menu.append(menu_bar_mode_menu_contest)
        menu_bar_mode_menu.append(menu_bar_mode_menu_qsl)
        menu_bar_mode.set_submenu(menu_bar_mode_menu)
        menu_bar.append(menu_bar_mode)

        main_vbox.pack_start(menu_bar, False, True, 0)
        
        
        self.widgets['band_combo'] = Gtk.ComboBoxText()
        for band in config['BANDS']:
            self.widgets['band_combo'].append_text(band)
        self.widgets['band_combo'].set_active(1)
        
        self.widgets['mode_combo'] = Gtk.ComboBoxText()
        for mode in config['MODES']:
            self.widgets['mode_combo'].append_text(mode)
        self.widgets['mode_combo'].set_active(0)
        self.widgets['mode_combo'].connect("changed", self.mode_changed)   

        self.widgets['call_entry'] = Gtk.Entry(max_width_chars=10, width_chars=10)
        self.widgets['call_entry'].connect("changed", self.widget_call_entry_changed)   

        self.widgets['input_date'] = Gtk.Entry(max_width_chars=10, width_chars=10)
        
        self.widgets['input_time'] = Gtk.Entry(max_width_chars=5, width_chars=5)
        
        #self.widgets['rst_sent'] = Gtk.Entry(max_width_chars=6, width_chars=6)
        #self.widgets['rst_rcvd'] = Gtk.Entry(max_width_chars=6, width_chars=6)
        
        self.widgets['rst_sent'] = RstEntry(max_width_chars=6, width_chars=6)
        self.widgets['rst_rcvd'] = RstEntry(max_width_chars=6, width_chars=6)

        # CONTEST FIELDS
        self.widgets['contest_sent'] = Gtk.Entry(max_width_chars=6, width_chars=6)
        self.widgets['contest_received'] = Gtk.Entry(max_width_chars=6, width_chars=6)

        self.widgets['input_note'] = Gtk.Entry(max_width_chars=40, width_chars=40)
       
        self.widgets['name'] = Gtk.Entry(max_width_chars=15, width_chars=15)
        self.widgets['qth'] = Gtk.Entry(max_width_chars=20, width_chars=20)
        
        self.save_button = Gtk.Button(label="Save")
        self.save_button.connect("button-press-event", self.widget_save_qso)   

        # for some widgets, also add a universal keypress watcher, these will serve for return
        for i in ('call_entry', 'input_date', 'input_time', 'rst_sent', 'rst_rcvd', 'input_note', 'name', 'qth'):
            self.widgets[i].connect("key-press-event", self.widget_monitor_keypress)   


        table = self.build_qso_variables_table()
        
        table_label = Gtk.Label()
        table_label.set_markup("<b>EDIT QSO:</b>")
        
        main_vbox.pack_start(table_label, False, True, 0)
        main_vbox.pack_start(table, False, True, 0)
        
        hbox = Gtk.HBox(False, 3)

        vbox_h_1 = Gtk.VBox(False, 2)
        vbox_h_2 = Gtk.VBox(False, 2)
        vbox_h_3 = Gtk.VBox(False, 2)


        # TODO DXCC info block
        
        # weblinks
        link_qrz = Gtk.Label()
        link_hamcall = Gtk.Label()
        link_hamqth = Gtk.Label()
        
        self.widgets['links'] = {
            'qrz': Gtk.Label(),
            'hamcall': Gtk.Label(),
            'hamqth': Gtk.Label()
        }
        
        self.widgets['links']['qrz'].set_markup("<b><a href=\"#\">QRZ.com</a></b>")
        self.widgets['links']['hamcall'].set_markup("<b><a href=\"#\">Hamcall.net</a></b>")
        self.widgets['links']['hamqth'].set_markup("<b><a href=\"#\">HamQTH.com</a></b>")
        
        
        hbox_links = Gtk.HBox(False, 2)
        hbox_links.pack_start(self.widgets['links']['qrz'], True, True, 0)
        hbox_links.pack_start(self.widgets['links']['hamcall'], True, True, 0)
        hbox_links.pack_start(self.widgets['links']['hamqth'], True, True, 0)
        
        
        label_h1 = Gtk.Label()
        label_h1.set_markup("<b>DXCC / ITU ENTITY INFO:</b>")
        vbox_h_1.pack_start(label_h1, False, True, 0)
        
        self.widgets['entity_note'] = Gtk.TextView()
        self.widgets['entity_note'].set_editable(False)
        vbox_h_1.pack_start(self.widgets['entity_note'], True, True, 0)
        
        label_h0 = Gtk.Label()
        label_h0.set_markup("<b>WEB LINKS:</b>")
        vbox_h_1.pack_start(label_h0, False, True, 0)
        
        vbox_h_1.pack_start(hbox_links, False, True, 0)

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
        swp.set_min_content_height(self.config['DUPE_LIST_HEIGHT'])
        main_vbox.pack_start(swp, False, True, 0)

        self.dupe_log_store = self.tree_data_create_model()

        treeView_p = Gtk.TreeView(self.dupe_log_store)
        treeView_p.connect('button-press-event', self.tree_click)
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
        self.current_log_tree.connect('button-press-event', self.tree_click)

        selection = self.current_log_tree.get_selection()
        selection.connect("changed", self.main_tree_selection_changed)
	selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        sw.add(self.current_log_tree)

        self.tree_data_create_columns(self.current_log_tree)
        
        
        self.current_log_scroll_window = sw


        # CURRENT LOG CONTEXT MENU
        # this context menu pops up when one row is selected

        self.current_log_context_menu = Gtk.Menu()
        
        # Weblinks
        menu_item_weblinks = Gtk.MenuItem("Weblinks")
        menu_item_weblinks_menu = Gtk.Menu()
        menu_item_weblinks_menu_qrz = Gtk.MenuItem("QRZ.com")
        menu_item_weblinks_menu_qrz.connect("button-press-event", self.open_weblink, QRZ_ROOT)
        menu_item_weblinks_menu_hamcall = Gtk.MenuItem("Hamcall.net")
        menu_item_weblinks_menu_hamcall.connect("button-press-event", self.open_weblink, HAMCALL_ROOT)
        menu_item_weblinks_menu_hamqth = Gtk.MenuItem("HamQTH.com")
        menu_item_weblinks_menu_hamqth.connect("button-press-event", self.open_weblink, HAMQTH_ROOT)
        
        menu_item_weblinks_menu.append(menu_item_weblinks_menu_qrz)
        menu_item_weblinks_menu.append(menu_item_weblinks_menu_hamcall)
        menu_item_weblinks_menu.append(menu_item_weblinks_menu_hamqth)
        menu_item_weblinks.set_submenu(menu_item_weblinks_menu)
        menu_item_weblinks_menu.show()
        menu_item_weblinks_menu_qrz.show()
        menu_item_weblinks_menu_hamcall.show()
        menu_item_weblinks_menu_hamqth.show()
        
        menu_item1 = Gtk.MenuItem("Edit QSO")
        menu_item1.connect("activate", self.current_log_edit_qso)
        
        separator = Gtk.SeparatorMenuItem()

        menu_item2 = Gtk.MenuItem("Delete QSO")
        menu_item2.connect("activate", self.current_log_delete_qso)

        self.current_log_context_menu.append(menu_item_weblinks)
        self.current_log_context_menu.append(menu_item1)
        self.current_log_context_menu.append(separator)
        self.current_log_context_menu.append(menu_item2)
       
        menu_item_weblinks.show()
        menu_item1.show()
        separator.show()
        menu_item2.show()

        # CURRENT LOG CONTEXT MENU - MULTISELECT
        # this context menu pops up when multiple rows are selected
        
        self.current_log_context_menu_multiple = Gtk.Menu()
        multiple_menu_item1 = Gtk.MenuItem("Edit multiple QSOs")
        multiple_menu_item1.connect("activate", self.current_log_edit_qsos_multiple)
        self.current_log_context_menu_multiple.append(multiple_menu_item1);
        multiple_menu_item1.show()

        # FOOTER
        self.statusbar = Gtk.Statusbar()
        main_vbox.pack_start(self.statusbar, False, False, 0)
            
        # FINISH OFF
        self.add(main_vbox)

        # reload tree for the first time
        self.tree_data_refresh_main_tree()
        self.widgets['call_entry'].grab_focus()

    def build_qso_variables_table(self):
        # label, widget, flex int, standard mode boolean, contest mode boolean 

        items = (
            ("FREQ", self.widgets['band_combo'],1, True, True),
            ("MODE", self.widgets['mode_combo'],1, True, True),
            ("CALL", self.widgets['call_entry'],2, True, True),  
            ("DATE", self.widgets['input_date'],1, True, True),
            ("UTC", self.widgets['input_time'],1, True, True),
            ("RST SENT", self.widgets['rst_sent'],1, True, True),
            ("CONTEST SENT", self.widgets['contest_sent'],1, False, True),
            ("RST RCVD", self.widgets['rst_rcvd'],1, True, True),
            ("CONTEST RCVD", self.widgets['contest_received'],1, False, True),
            ("NAME",  self.widgets['name'],2, True, False),
            ("QTH",  self.widgets['qth'],2, True, False),
            ("NOTE", self.widgets['input_note'],4, True, True),
            ("", self.save_button, 1, True, True),
        )
        
        flex_sum = reduce(lambda x,y: x + y, [ i[2] for i in filter(lambda x:(x[3] == True and self.logging_mode_standard == True) or (x[4] == True and self.logging_mode_contest == True), items) ] )

        # create a table with a phantom number of columns (calculated flex sum)
        table = Gtk.Table(rows=2, columns=flex_sum, homogeneous=False)

        flex_cumulative = 0
        for item in filter(lambda x: (x[3] == True and self.logging_mode_standard == True) or (x[4] == True and self.logging_mode_contest == True), items):
            table.attach(Gtk.Label(item[0]), flex_cumulative, flex_cumulative + item[2], 0, 1)
            table.attach(item[1], flex_cumulative, flex_cumulative + item[2], 1, 2)
            flex_cumulative += item[2]
        
        return table
    
    # EVENT HANDLING FUNCTIONS FOR THE WIDGETS

    def something():
        pass

    def update_links(self, callsign):
        base_call = CallsignEntity.get_base_callsign(callsign)
        
        self.widgets['links']['qrz'].set_markup('<b><a href="' + QRZ_ROOT + base_call + '">QRZ.com</a></b>')
        self.widgets['links']['hamcall'].set_markup('<b><a href="'+ HAMCALL_ROOT + base_call + '">HAMCALL.net</a></b>')
        self.widgets['links']['hamqth'].set_markup('<b><a href="'+ HAMQTH_ROOT + base_call + '">HamQTH.com</a></b>')

    def mode_changed(self, widget):
        mode = widget.get_active_text() 
        rst_widgets = ('rst_sent', 'rst_rcvd')
        
        if mode in ('CW', 'RTTY'):
            mode_rst = 'RST'
        else:
            mode_rst = 'RS'
        
        for wgt in rst_widgets:
            self.widgets[wgt].set_mode(mode_rst)

    def widget_call_entry_changed(self, widget):
        self.editing_mode = True

        new_text = widget.get_text().upper()
        widget.set_text(new_text)

        if len(new_text) > 1:
            self.tree_data_refresh_dupe_tree()
            self.update_entity_info(new_text)
            self.update_links(new_text)
        else:
            self.dupe_log_store.clear()
    
    def widget_monitor_keypress(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        
        # guard for lock of this widget
        if event.state == Gdk.ModifierType.CONTROL_MASK and keyname == 'l':
            
            # CTRL-L
            # toggle lock on this widget
            
            # find this widget in the widget list 
            for key, val in self.widgets.items():
                if widget is val:
                    # toggle locked state
                    if key in self.locked_widgets:
                        del self.locked_widgets[key]
                        widget.override_background_color(Gtk.StateFlags.NORMAL, None)
                        widget.override_color(Gtk.StateFlags.NORMAL, None)
                    else:
                        self.locked_widgets[key] = True
                        widget.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.0, 1.0, 0.8, 1.0))
                        widget.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 1.0))
            
        
        # guard for return
        if keyname == 'Return':
            self.widget_save_qso(widget, event)
            return
        
        # guard for TAB
        if keyname == 'Tab':
            
            # complete RST reports 
            #if widget in (self.widgets['rst_sent'], self.widgets['rst_rcvd']):
            #    if not widget.get_text():
            #        mode = self.widgets['mode_combo'].get_active_text()
            #        # TODO: this should be somewhat configurable, but ok for now
            #        if mode in ('CW', 'RTTY'):
            #            widget.set_mode('RST')
            #        else:
            #            widget.set_mode('RS')
            #        widget.set_default()

            if widget == self.widgets['input_time'] and not self.widgets['rst_sent'].get_text():
                self.widgets['rst_sent'].set_default()
            if widget == self.widgets['rst_sent'] and not self.widgets['rst_rcvd'].get_text():
                self.widgets['rst_rcvd'].set_default()

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

    def input_time_inc(self, increment):
        # get current datetime
        iso_datetime = self.widgets['input_date'].get_text() + ' ' + self.widgets['input_time'].get_text()
        
        if iso_datetime != ' ':
            current = datetime.datetime.strptime(iso_datetime, '%Y-%m-%d %H:%M')
            delta = datetime.timedelta(minutes=increment)
            current = current + delta
            
            utc = current.timetuple()
            self.widgets['input_date'].set_text("%04i-%02i-%02i" % (utc.tm_year , utc.tm_mon, utc.tm_mday))
            self.widgets['input_time'].set_text("%02i:%02i" % (utc.tm_hour, utc.tm_min))
                
        

    def window_key_press(self, widget, event):        

        if event.state == Gdk.ModifierType.CONTROL_MASK:
            keyval = Gdk.keyval_name(event.keyval)
            
            #print keyval
            if keyval == 'z':
                # CTRL-Z
                # clear all fields and focus back on callsign
                
                self.clear_fields_and_reset_focus()
            elif keyval == 'a':
                # CTRL-A
                # increment minute
                self.input_time_inc(1)
            elif keyval == 'x':
                # CTRL-X
                # decrement minutes
                self.input_time_inc(-1)
               

    def widget_save_qso(self, widget, event):        
        # check if at least CALL, DATE, TIME and RST SENT and RECEIVED are present and save

        freq = self.widgets['band_combo'].get_active_text()
        mode = self.widgets['mode_combo'].get_active_text()

        for i in self.obligatories:
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
                variables=self.qso_variables.value,
                qso_session=self.active_session
            )
            
        self.clear_fields_and_reset_focus()
        self.tree_data_refresh_main_tree()
        self.dupe_log_store.clear()

    def clear_fields_and_reset_focus(self):
        # clean fields and grab focus
        for i in self.obligatories:
            if i not in self.locked_widgets:
                self.widgets[i].set_text('')

        other_widgets = ['rst_sent','rst_rcvd','name','qth','input_note', 'contest_sent', 'contest_received']
        for i in other_widgets:
            if i not in self.locked_widgets:
                self.widgets[i].set_text('')
        
        self.widgets['callsign_note'].get_buffer().set_text('')

        # grab focus in the callsign box again
        self.widgets['call_entry'].grab_focus()
        
        
      

    def current_log_keyrelease(self, widget, event):
        if event.button == 3:
            # if right click was pressed
            x = int(event.get_root_coords()[0])
            y = int(event.get_root_coords()[1])
            time = event.time
            
            self.last_active_tree = widget

            #  check if selection in single or multiple
            selected_rows = 1

            selection = widget.get_selection()
	    if selection.get_mode() == Gtk.SelectionMode.MULTIPLE:
                model, paths = selection.get_selected_rows()
                selected_rows = len(paths)
            
            if selected_rows == 1:
                self.current_log_context_menu.popup(None, None, lambda menu, user_data: (x, y, True), widget, 3, time)
            else:
                self.current_log_context_menu_multiple.popup(None, None, lambda menu, user_data: (x, y, True), widget, 3, time)
    
    def tree_click(self, widget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.last_active_tree = widget
            self.current_log_edit_qso(widget)

    def main_tree_selection_changed(self, selection):
        # TODO
        # This will probably require something else. Perhaps use onclick and verify for selection. Maybe not onclick, but onselect
        # to cover for situations:
        # - do not fire if nothing is selected (left click fires before seelction takes place)
        # - do not only fire when selection changed, also fire when click is made on the same selection
        # - also change previous conversations when entry is already filled in - but not by user, keep a global memory whether
        #   the entry was changed by typing or by selection DONE
        # when editing a window, the tree refreshes, selection changes and everything goes to hell - probably will be fixed by listering to left click instead of selection
        
        # assume this was to search for previous QSOs
        model, path_list = selection.get_selected_rows()
        
        # only do this when a single row is selected
        if len(path_list) == 1:
            treeiter = path_list[0]
        else:
            return

        if model is not None and treeiter is not None:
            column_callsign = model[treeiter][5]  
            
            # if the callsign editing entry is empty, fill in callsign and refresh previous qso
            if not self.widgets['call_entry'].get_text() or not self.editing_mode:
                self.widgets['call_entry'].set_text(column_callsign)

                self.tree_data_refresh_dupe_tree()
                self.update_entity_info(column_callsign)
                self.update_links(column_callsign)

                self.editing_mode = False

    
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
    
    def current_log_edit_qsos_multiple(self, widget):

        selection = self.last_active_tree.get_selection()
        model, path_list = selection.get_selected_rows()
        self.editing_qsos = self.db.get_qsos_by_ids(id_list=[ model[path][0] for path in path_list ])
        
        edit_dialog = EditQsoMultipleDialog(self)
        response = edit_dialog.run()
        
        if response == Gtk.ResponseType.OK:
            for qso in self.editing_qsos:
                self.db.update_qso_attrs(qso, variables=edit_dialog.qso_variables.value)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        else:
            pass

        edit_dialog.destroy()

    def current_log_edit_qso(self, widget):
        
        selection = self.last_active_tree.get_selection()
        model, path_list = selection.get_selected_rows()
        
        # only do this when a single row is selected
        if len(path_list) == 1:
            path = path_list[0]
        else:
            return
            
        column_id = model[path][0]  
        #path = model.get_path(treeiter)
        
        self.editing_qso_id = column_id
        
        edit_dialog = EditQsoDialog(self)
        response = edit_dialog.run()
        
        if response == Gtk.ResponseType.OK:

            freq = edit_dialog.widgets['band_combo'].get_active_text()
            mode = edit_dialog.widgets['mode_combo'].get_active_text()
            
            qso_session = None
            if edit_dialog.widgets['qso_session_combo'].get_active() != -1:
                qso_session = edit_dialog.qso_sessions[edit_dialog.widgets['qso_session_combo'].get_active()]
            
            callsign = edit_dialog.widgets['call_entry'].get_text()
            dfields = edit_dialog.widgets['input_date'].get_text().split('-')
            dat = datetime.date(*map(int, dfields))
            tfields = edit_dialog.widgets['input_time'].get_text().split(':')
            utc = datetime.time(int(tfields[0]), int(tfields[1]))
            
            datetime_combined=datetime.datetime.combine(dat, utc)
            buf = edit_dialog.widgets['callsign_note'].get_buffer()
            cs_text_note = buf.get_text(*buf.get_bounds(),include_hidden_chars=False)
            
            text_note = edit_dialog.widgets['input_note'].get_text()
            
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
                qsl_sent=edit_dialog.widgets['qsl_sent'].get_active(),
                qsl_received=edit_dialog.widgets['qsl_received'].get_active(),
                qso_session=qso_session,
                variables=edit_dialog.qso_variables.value,
            )
            
            
            current_tree = self.current_log_tree.get_vadjustment().get_value()
            
              
            # dupe_tree = self.dupe_log_tree.get_vadjustment().get_value()
            
            self.tree_data_refresh_main_tree()
            self.tree_data_refresh_dupe_tree()
            
            # self.current_log_tree.get_vadjustment().set_value(current_tree)
            # self.current_log_scroll_window.get_vadjustment().set_value(current_win)
            
                        
            self.current_log_tree.scroll_to_cell(path)
            selection.select_path(path)
            
            
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
        
        # for some reason, for now, we only support current log tree delete:
        if self.current_log_tree is not self.last_active_tree:
            return

        selection = self.last_active_tree.get_selection()
        model, path_list = selection.get_selected_rows()
        
        # only do this when a single row is selected
        if len(path_list) == 1:
            treeiter = path_list[0]
        else:
            return
            
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
        store = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str, str, str, str)

        return store

    def tree_data_refresh_main_tree(self):
        
        # self.current_log_store.clear()
        # Clearing the log by using .clear() is very slow. a faster  approch that works is to create a new ListStore, throw away
        # the old liststore and point the tree to it - set_model

        self.current_log_store = self.tree_data_create_model()
        self.current_log_tree.set_model(self.current_log_store)

        qsos = self.db.get_qsos()
        for qso in qsos:
            
            check = ''
            if qso.qsl_sent:
                check = '✔'
            elif qso.qsl_received:
                check = '✗'
                
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
                      check,
                      qso.text_note
                  )
            )

    def tree_data_refresh_dupe_tree(self):

        self.dupe_log_store = self.tree_data_create_model()
        self.dupe_log_tree.set_model(self.dupe_log_store)
        
        qsos = self.db.get_qsos(callsign_filter=self.widgets['call_entry'].get_text())

        for qso in qsos:
            check = ''
            if qso.qsl_sent:
                check = '✔'
            elif qso.qsl_received:
                check = '✗'
                
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
                    check,
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
   
        columns = ['ID','DATE', 'UTC', 'FREQ', 'MODE', 'CALL', 'RST_SENT', 'RST_RCVD', 'NAME', 'QTH', 'COUNTRY', 'Q', 'NOTE']

        for i, column in enumerate(columns):
            rendererText = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(column, rendererText, text=i)
            col.set_sort_column_id(i)  
            
            # QSL info - TODO this appears not to work FTM
            if i == 11:
                col.sizing = Gtk.TreeViewColumnSizing.FIXED
                col.set_fixed_width(10)
            
            treeView.append_column(col)
    
    # Context menu actions
    def open_weblink(self, widget, event, *params):
        selection = self.last_active_tree.get_selection()
        model, path_list = selection.get_selected_rows()
        
        # only do this when a single row is selected
        if len(path_list) == 1:
            treeiter = path_list[0]
        else:
            return
            
        column_call = model[treeiter][5]  
        base_call = CallsignEntity.get_base_callsign(column_call)
        
        Gtk.show_uri(None, params[0] + base_call, Gdk.CURRENT_TIME)
           
           
    # FILE MENU ACTIONS
    def menu_file_exit(self, widget):
        sys.exit()

    def menu_session_new(self, widget):
        
        dialog = NewSessionDialog(self)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            
            locator = dialog.widgets['locator'].get_text()
            description = dialog.widgets['description'].get_text()
            buf = dialog.widgets['text_note'].get_buffer()
            text_note = buf.get_text(*buf.get_bounds(),include_hidden_chars=False)
            
            qso_session = self.db.create_qso_session(
                locator=locator,
                description=description,
                text_note=text_note
            )
            
            if dialog.widgets['activate_session'].get_active():
                self.set_title(self.config['APPLICATION_NAME'] + ' Active Session: ' + qso_session.description)
                self.active_session = qso_session
            
        dialog.destroy()
    
    def menu_session_reset(self, widget):
        self.active_session = None
        self.set_title(self.config['APPLICATION_NAME'])
                       
    def menu_session_manage(self, widget):
        pass

    def menu_mode_switch(self, widget, mode):
        if mode == "standard":
            self.logging_mode_standard = True
            self.logging_mode_contest = False

        elif mode == "contest":
            self.logging_mode_standard = False
            self.logging_mode_contest = True

    def export_menu_sota_chaser(self, widget):
        chaser_qsos = self.db.get_qsos_sota_chaser(descending=True)

        dialog = ExportSotaChaserDialog(self, chaser_qsos)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            if dialog.selection is not None:
                model, tree_paths = dialog.selection.get_selected_rows()

                qso_ids = []

                output_file = self.display_file_dialog("csv")

                if output_file is not None:
                    for path in reversed(tree_paths):
                        qso_ids.append(model[path][0])
                    
                    sota_qsos = self.db.get_qsos_sota_chaser(ids=qso_ids)
                    from tools.export_sota_chaser import create_export_file_from_qsos
                    create_export_file_from_qsos(sota_qsos, csv_file=output_file, config=self.config)

                        

        dialog.destroy()


    def export_menu_sota(self, widget):
        # get sota activations
        activations = self.db.get_sota_activations()

        dialog = ExportSotaDialog(self, activations)
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

                        search_results = self.db.get_qsos_sota(summit=model[path][0], date=model[path][2]) 
                        sota_qsos.extend(search_results)

                    from tools.export_sota import create_export_file_from_qsos
                    create_export_file_from_qsos(sota_qsos, csv_file=output_file, config=self.config)
            
        dialog.destroy()

        
    # STANDARD FILE CHOOSER
    def display_file_dialog(self, extension=None):
        dialog = Gtk.FileChooserDialog("Select target file", self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        return_file = None
        
        if response == Gtk.ResponseType.OK:
            return_file = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()
        
        return return_file
    

