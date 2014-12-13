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

    for sheet in doc.sheets:
        print "Processing sheet: %s" % sheet.name

        for i, row in enumerate(sheet.rows()):

            try:
                date = row[0].value
                utc = row[1].value
                mode = row[2].value
                band = row[3].value

                print "%04i:  %-10s %-10s %-6s %-6s" % (i, date, utc, mode, band)

            except Exception, e:
                print "%04i:  Invalid data. (%s)" % (i, str(e))

