#!/usr/bin/env python
# -*- coding: utf-8 -*-

license = """
Copyright 2014-2015, Jakub Ondrusek, OM1AWS (yak@gmx.co.uk)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


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
from libs import prefix_resolver

class HamLogger(Gtk.Application):

    def __init__(self, config, *args, **kwargs):
        super(HamLogger, self).__init__(*args, **kwargs)

        # config post processing ->
        # change a potentially relative path to absolute path
        config.DB_FILE = os.path.abspath(config.DB_FILE)
        config.PREFIX_FILE = os.path.abspath(config.PREFIX_FILE)
        
        # initialize DXCC prefix resolver
        self.resolver = prefix_resolver.Resolver(config.PREFIX_FILE)
        
        # create a db handle, this will be handled by our intelligent connector
        self.db_handle = data_connector.DataConnector(config.DB_FILE) 

        # save the config as my attribute
        self.config = config
    
    def do_activate(self):
        

        # create the main window and send it a reference to the config module
        window = main_window.MainWindow(application=self, config=self.config, db=self.db_handle, resolver=self.resolver)
        window.set_title(self.config.APPLICATION_NAME)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_icon_from_file('icons/application.png')
        window.show_all()

# INIT APPLICATION
app = HamLogger(config)


# PROCESS COMMAND LINE ARGUMENTS
parser = argparse.ArgumentParser(description='%s - a Ham radio logger application by OM1AWS' % config.APPLICATION_NAME)
parser.add_argument("-l", "--license", dest="license", action="store_true", help="show licensing information")
parser.add_argument("-i", "--import_ods", type=str, help="import log records from an ODS file.", metavar="ODS_FILE")
parser.add_argument("-x", "--export_ods", type=str, help="export log records to an ODS file.", metavar="ODS_FILE")

args = parser.parse_args()

# 1. print licensing information and exit
if args.license:
    print license
    sys.exit()

# 2. import log data from an ods file 
if args.import_ods:
    from libs.tools import import_from_ods
    import_from_ods.execute(ods_file=args.import_ods, db_handle=app.db_handle)
    sys.exit()
    
# 3. export log data to an ods file 
if args.export_ods:
    from libs.tools import export_to_ods
    export_to_ods.execute(ods_file=args.export_ods, db_handle=app.db_handle)
    sys.exit()




# RUN GTK APPLICATION

# capture sigint to close application
signal.signal(signal.SIGINT, signal.SIG_DFL)
status = app.run(sys.argv)
sys.exit(status)

