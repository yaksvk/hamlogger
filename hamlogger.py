#!/usr/bin/env python
# -*- coding: utf-8 -*-

# global libs
import sys
import signal
from gi.repository import Gtk

# application libs
import config 
from libs import main_window
from libs import data_connector

class HamLogger(Gtk.Application):

    def __init__(self, config, *args, **kwargs):
        super(HamLogger, self).__init__(*args, **kwargs)

        self.config = config
    
    def do_activate(self):
        
        # create a db handle, this will be handled by our intelligent connector
        db_handle = data_connector.DataConnector(self.config.DB_FILE) 

        # create the main window and send it a reference to the config module
        window = main_window.MainWindow(application=self, config=self.config, db=db_handle)
        window.set_title(self.config.APPLICATION_NAME)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.show_all()

app = HamLogger(config)
# capture sigint to close application
signal.signal(signal.SIGINT, signal.SIG_DFL)
status = app.run(sys.argv)
sys.exit(status)

