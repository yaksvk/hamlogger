#!/usr/bin/env python
import argparse
import importlib
import sys
import glob
import os

"""
Process command line arguments for the Hamlogger application
and run non-GUI tools/commands.
"""

def process(app, license):

    parser = argparse.ArgumentParser(
        description='%s - a Ham radio logger application by OM1WS' % app.config['APPLICATION_NAME'])

    parser.add_argument("-l", "--license",
        dest="license", action="store_true", help="show licensing information")
    parser.add_argument("-d", "--dump-summits",
        help="dump list of unique activated summits", metavar="SUMMITS_CSV")
    parser.add_argument("-i", "--import_ods",
        type=str, help="import log records from an ODS file.", metavar="ODS_FILE")
    parser.add_argument("-x", "--export_ods",
        type=str, help="export log records to an ODS file.", metavar="ODS_FILE")
    parser.add_argument("-t", "--export_odt",
        type=str, help="export log records to an ODT file (nice document).", metavar="ODT_FILE")
    parser.add_argument("-s", "--export_sota",
        type=str, help="export log records to a SOTA-compatible activator CSV file. "
        "Automatically filters for QSOs with the SUMMIT_SENT meta variable. MY_CALL overrides default callsign.",
        metavar="CSV_FILE")
    parser.add_argument("-r", "--export_sota_chaser",
        type=str, help="export log records to a SOTA-compatible chaser CSV file. "
        "Automatically filters for QSOs with the SUMMIT_SENT meta variable. MY_CALL overrides default callsign.",
        metavar="CSV_FILE")
    parser.add_argument("-a", "--export_adif2",
        type=str, help="export log records to an ADIF v2 file.", metavar="ADIF_FILE")
    parser.add_argument("-c", "--export_cabrillo",
        type=str, help="export log records in cabrillo format", metavar="CABRILLO_FILE")
    parser.add_argument("-b", "--import_sota",
        type=str, help="import log records from sotadata website", metavar="CSV_FILE")
    parser.add_argument("-f", "--import_adif",
        type=str, help="import log records from ADIF", metavar="ADIF_FILE")
    parser.add_argument("-L", "--export_lotw",
        type=str, help="export log records to an ADIF v2 file. The name is used as prefix.", metavar="ADIF_FILE")
    parser.add_argument("-P", "--pa",
        dest="vhf", action="store_true", help="vkv pa summary")
    parser.add_argument("--summit",
        type=str, help="specify summit to append as SUMMIT_SENT (use with --import_adif)")
    parser.add_argument("--run", nargs='?', const='',
        help="Execute a custom script from lib.tools.scripts Run without arguments to see options.")

    args, custom_args = parser.parse_known_args()

    # print licensing information and exit
    if args.license:
        print(license)
        sys.exit()

    # dump all activated summits as JSON with lat/lng coordinants, a summits.csv dumped from
    # sotadata must be provided
    if args.dump_summits:
        from .tools import dump_summits
        dump_summits.execute(db_handle=app.db_handle, summits_db_file=args.dump_summits)
        sys.exit()

    # import log data from an ods file 
    if args.import_ods:
        from lib.tools import import_from_ods
        import_from_ods.execute(ods_file=args.import_ods, db_handle=app.db_handle)
        sys.exit()

    # export log data to an ods file 
    if args.export_ods:
        from lib.tools import export_to_ods
        export_to_ods.execute(ods_file=args.export_ods, db_handle=app.db_handle)
        sys.exit()

    # export log data to an ods file 
    if args.export_odt:
        from lib.tools import export_to_odt
        export_to_odt.execute(odt_file=args.export_odt, db_handle=app.db_handle)
        sys.exit()

    # export sota 
    if args.export_sota:
        from lib.tools import export_sota
        export_sota.execute(csv_file=args.export_sota, db_handle=application.db_handle,
            config=application.config)
        sys.exit()

    # export sota 
    if args.export_sota_chaser:
        from lib.tools import export_sota_chaser
        export_sota_chaser.execute(csv_file=args.export_sota_chaser, db_handle=application.db_handle,
            config=application.config)
        sys.exit()

    # export adif 
    if args.export_adif2:
        from lib.tools import export_adif_v2
        export_adif_v2.execute(adif_file=args.export_adif2, db_handle=app.db_handle,
            config=app.config)
        sys.exit()

    # export cabrillo 
    if args.export_cabrillo:
        from lib.tools import export_cabrillo
        export_cabrillo.execute(adif_file=args.export_cabrillo, db_handle=application.db_handle,
            config=application.config)
        sys.exit()

    # import csv log data from sotadata 
    if args.import_sota:
        from lib.tools import import_from_sota
        import_from_sota.execute(csv_file=args.import_sota, db_handle=application.db_handle)
        sys.exit()

    # export lotw 
    if args.export_lotw:
        from lib.tools import export_lotw
        export_lotw.execute(adif_file_prefix=args.export_lotw, db_handle=app.db_handle,
            config=app.config)
        sys.exit()

    # import adif
    if args.import_adif:
        from lib.tools import import_from_adif
        import_from_adif.execute(adif_file=args.import_adif, db_handle=app.db_handle, args=args)
        sys.exit()

    # modify
    if args.run is not None:
        if args.run == '':
            print(f'No argument specified. Please choose something from lib.tools:')
            script_glob = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools/scripts/*py')
            for filename in [ os.path.basename(f) for f in glob.glob(script_glob)]:
                if filename[0] == '_':
                    continue
                print(filename[:-3])
            sys.exit()

        print(f'Trying to import lib.tools.{args.run}')
        runlib = importlib.import_module(f'lib.tools.scripts.{args.run}')
        runlib.execute(db_handle=app.db_handle, app=app, args=custom_args)
        sys.exit()
