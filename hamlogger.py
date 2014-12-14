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

        # create a db handle, this will be handled by our intelligent connector
        self.db_handle = data_connector.DataConnector(config.DB_FILE) 

        # save the config as my attribute
        self.config = config
    
    def do_activate(self):
        

        # create the main window and send it a reference to the config module
        window = main_window.MainWindow(application=self, config=self.config, db=self.db_handle)
        window.set_title(self.config.APPLICATION_NAME)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.show_all()

# INIT APPLICATION
app = HamLogger(config)


# PROCESS COMMAND LINE ARGUMENTS
parser = argparse.ArgumentParser(description='%s - a Ham radio logger application' % config.APPLICATION_NAME)
parser.add_argument("-i", "--import_ods", type=str, help="Import log records from an ODS file.", metavar="ODS_FILE")
args = parser.parse_args()

# 1. import log data from an ods file 
if args.import_ods:
    from libs.tools import import_from_ods
    import_from_ods.execute(ods_file=args.import_ods, db_handle=app.db_handle)
    sys.exit()


# RUN GTK APPLICATION

# capture sigint to close application
signal.signal(signal.SIGINT, signal.SIG_DFL)
status = app.run(sys.argv)
sys.exit(status)

