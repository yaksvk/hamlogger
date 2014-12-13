#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

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
        
        # TODO - more widgets
        
        
        items = (
            ("FREQ", self.widgets['band_combo'],1),
            ("MODE", self.widgets['mode_combo'],1),
            # TODO
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
        
        
        # FOOTER
        self.statusbar = Gtk.Statusbar()
        main_vbox.pack_start(self.statusbar, False, False, 0)
            
        # FINISH OFF
        self.add(main_vbox)

    
    # EVENT HANDLING FUNCTIONS FOR THE WIDGETS

    def something():
        pass



    # TREE LOADING / REFRESHING FUNCTIONS


