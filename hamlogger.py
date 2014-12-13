#!/usr/bin/env python
# -*- coding: utf-8 -*-

# global libs
import argparse
import os
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

        # config post processing ->
        # change a potentially relative path to absolute path
        config.DB_FILE = os.path.abspath(config.DB_FILE)

        self.config = config
    
    def do_activate(self):
        
        # create a db handle, this will be handled by our intelligent connector
        db_handle = data_connector.DataConnector(self.config.DB_FILE) 

        # create the main window and send it a reference to the config module
        window = main_window.MainWindow(application=self, config=self.config, db=db_handle)
        window.set_title(self.config.APPLICATION_NAME)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.show_all()

# PROCESS COMMAND LINE ARGUMENTS
parser = argparse.ArgumentParser(description='%s - a Ham radio logger application' % config.APPLICATION_NAME)
parser.add_argument("--import_ods", type=str, help="Import log records from an ODS file.", metavar="ODS_FILE")
args = parser.parse_args()

if args.import_ods:
    from libs.tools import import_from_ods
    import_from_ods.execute(args.import_ods)
    sys.exit()


# RUN GTK APPLICATION

app = HamLogger(config)
# capture sigint to close application
signal.signal(signal.SIGINT, signal.SIG_DFL)
status = app.run(sys.argv)
sys.exit(status)

