#!/usr/bin/env python

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
import pathlib
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# application libs

from libs import main_window
from libs import data_connector
from libs import prefix_resolver
from libs import config as cfg

class HamLogger(Gtk.Application):

    def __init__(self, config, *args, **kwargs):
        super(HamLogger, self).__init__(*args, **kwargs)
        
        # initialize DXCC prefix resolver
        self.resolver = prefix_resolver.Resolver(config.get_absolute_path(config['PREFIX_FILE']))
        
        # create a db handle, this will be handled by our intelligent connector
        if not config.get('DB_FILE', ''):
            config['DB_FILE'] = os.path.join(os.environ['HOME'], '.hamlogger', 'log.sqlite')

        self.db_handle = data_connector.DataConnector(config['DB_FILE']) 

        # save the config as my attribute
        self.config = config
    
    def do_activate(self):
        

        # create the main window and send it a reference to the config module
        window = main_window.MainWindow(application=self, config=self.config, db=self.db_handle, resolver=self.resolver)
        window.set_title(self.config['APPLICATION_NAME'])
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_icon_from_file(config.get_absolute_path('icons/application.png'))
        window.show_all()

# INIT APPLICATION
absolute_script_path = pathlib.Path(__file__).parent.resolve()
config = cfg.PersistentConfig(source_path=absolute_script_path)

app = HamLogger(config)


# PROCESS COMMAND LINE ARGUMENTS
parser = argparse.ArgumentParser(description='%s - a Ham radio logger application by OM1AWS' % config['APPLICATION_NAME'])
parser.add_argument("-l", "--license", dest="license", action="store_true", help="show licensing information")
parser.add_argument("-d", "--dump_summits", dest="summits", action="store_true", help="dump list of unique activated summits")
parser.add_argument("-i", "--import_ods", type=str, help="import log records from an ODS file.", metavar="ODS_FILE")
parser.add_argument("-x", "--export_ods", type=str, help="export log records to an ODS file.", metavar="ODS_FILE")
parser.add_argument("-t", "--export_odt", type=str, help="export log records to an ODT file (nice document).", metavar="ODT_FILE")
parser.add_argument("-s", "--export_sota", type=str, help="export log records to a SOTA-compatible activator CSV file. "
    "Automatically filters for QSOs with the SUMMIT_SENT meta variable. MY_CALL overrides default callsign.", metavar="CSV_FILE")
parser.add_argument("-r", "--export_sota_chaser", type=str, help="export log records to a SOTA-compatible chaser CSV file. "
    "Automatically filters for QSOs with the SUMMIT_SENT meta variable. MY_CALL overrides default callsign.", metavar="CSV_FILE")
parser.add_argument("-a", "--export_adif2", type=str, help="export log records to an ADIF v2 file.", metavar="ADIF_FILE")
parser.add_argument("--export_adif", type=str, help="export log records to an ADIF v3 file.", metavar="ADIF_FILE")
parser.add_argument("-c", "--export_cabrillo", type=str, help="export log records in cabrillo format", metavar="CABRILLO_FILE")
parser.add_argument("-b", "--import_sota", type=str, help="import log records from sotadata website", metavar="CSV_FILE")
parser.add_argument("-f", "--import_adif", type=str, help="import log records from ADIF", metavar="ADIF_FILE")
parser.add_argument("-L", "--export_lotw", type=str, help="export log records to an ADIF v2 file. The name is used as prefix.", metavar="ADIF_FILE")
parser.add_argument("-P", "--pa", dest="vhf", action="store_true", help="vkv pa summary")

# TODO experimental feature
parser.add_argument("-u", "--upload_sota", dest="upload_sota", action="store_true", help="upload sota log to sotadata")

args = parser.parse_args()

# 1. print licensing information and exit
if args.license:
    print(license)
    sys.exit()

if args.summits:
    from libs.tools import dump_summits
    dump_summits.execute(db_handle=app.db_handle)
    sys.exit()

if args.vhf:
    from libs.tools import vhf
    vhf.execute(db_handle=app.db_handle)
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
    
# 4. export log data to an ods file 
if args.export_odt:
    from libs.tools import export_to_odt
    export_to_odt.execute(odt_file=args.export_odt, db_handle=app.db_handle)
    sys.exit()
    
# 5. export sota 
if args.export_sota:
    from libs.tools import export_sota
    export_sota.execute(csv_file=args.export_sota, db_handle=app.db_handle, config=app.config)
    sys.exit()

# 6. export sota 
if args.export_sota_chaser:
    from libs.tools import export_sota_chaser
    export_sota_chaser.execute(csv_file=args.export_sota_chaser, db_handle=app.db_handle, config=app.config)
    sys.exit()

# 7. export adif 
if args.export_adif2:
    from libs.tools import export_adif_v2
    export_adif_v2.execute(adif_file=args.export_adif2, db_handle=app.db_handle, config=app.config)
    sys.exit()

# 8. export cabrillo 
if args.export_cabrillo:
    from libs.tools import export_cabrillo
    export_cabrillo.execute(adif_file=args.export_cabrillo, db_handle=app.db_handle, config=app.config)
    sys.exit()

# 9. import csv log data from sotadata 
if args.import_sota:
    from libs.tools import import_from_sota
    import_from_sota.execute(csv_file=args.import_sota, db_handle=app.db_handle)
    sys.exit()

# 10. export lotw 
if args.export_lotw:
    from libs.tools import export_lotw
    export_lotw.execute(adif_file_prefix=args.export_lotw, db_handle=app.db_handle, config=app.config)
    sys.exit()

# 11. import adif
if args.import_adif:
    from libs.tools import import_from_adif
    import_from_adif.execute(adif_file=args.import_adif, db_handle=app.db_handle)
    sys.exit()



# RUN GTK APPLICATION

# capture sigint to close application
signal.signal(signal.SIGINT, signal.SIG_DFL)
status = app.run(sys.argv)
sys.exit(status)

