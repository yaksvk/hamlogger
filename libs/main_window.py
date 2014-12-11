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
