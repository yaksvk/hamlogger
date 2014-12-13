#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
THIS IS A HELPER FUNCTION TO IMPORT AN OLD ODS-STYLE LOG TO SQLITE
USE THIS AT YOUR OWN RISK - FOR YOUR USE IT MIGHT REQUIRE CONSIDERABLE
TWEAKING :)
"""

import ezodf
from ezodf.timeparser import TimeParser

def execute(ods_file, db_handle):
    print "Processing file: %s" % ods_file

    doc = ezodf.opendoc(ods_file)

    if doc.doctype != 'ods':
        print "Not an ODS file. Sorry."
        return
    
    for j, sheet in enumerate(doc.sheets):
        print "Processing sheet: %s" % sheet.name
        if j == 0:
            for i, row in enumerate(sheet.rows()):

                try:
                    date = row[0].value
                    utc = row[1].value
                    mode = row[2].value
                    band = row[3].value
                    callsign = row[4].value
                    

                except Exception, e:
                    print "%04i:  Invalid data. (%s)" % (i, str(e))
                    next
                
                qso = db_handle.create_qso(
                    callsign=callsign,
                    mode=mode,
                    frequency=band,
                    rst_sent=row[5].value, 
                    rst_received=row[6].value,
                    name_received=row[7].value,
                    qth_received=row[8].value,
                    country_received=row[9].value,
                    text_note=row[10].value,
                )
                db_handle.commit()
                print "Added: %04i:  %-10s %-10s %-6s %-6s" % (i, date, utc, mode, band)

