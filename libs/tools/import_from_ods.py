#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
THIS IS A HELPER FUNCTION TO IMPORT AN OLD ODS-STYLE LOG TO SQLITE
USE THIS AT YOUR OWN RISK - FOR YOUR USE IT MIGHT REQUIRE CONSIDERABLE
TWEAKING :)
"""

import ezodf
from ezodf.timeparser import TimeParser
import datetime
import re

def execute(ods_file, db_handle, pretend=False):
    
    if pretend:
        print "I will only pretend. Nothing will be written. No worries :)"
        
    print "Processing file: %s" % ods_file

    doc = ezodf.opendoc(ods_file)

    if doc.doctype != 'ods':
        print "Not an ODS file. Sorry."
        return
    
    for j, sheet in enumerate(doc.sheets):
        print "Processing sheet: %s" % sheet.name
        if j == 0:
            for i, row in enumerate(sheet.rows()):
                
                if i > 0:
                    
                    dat=None
                    utc=None
                    mode=None
                    band=None
                    callsign=None

                    try:
                        # try other formats before
                        
                        if row[0] is not None:
                            tfields = row[0].value.split('-')
                            if len(tfields) == 3:
                                dat = datetime.date(*map(int, tfields))
                            else:
                                tfields = map(int, row[0].value.split('.'))
                                if len(tfields) == 3:
                                    dat = datetime.date(tfields[2], tfields[1], tfields[0])
                                else:
                                    print "Unable to parse date."            
                        
                        if row[1].value is not None:
                            utc = datetime.time(int(row[1].value[2:4]), int(row[1].value[5:7]))
                        mode = row[2].value
                        band = row[3].value
                        
                        if int(band) == band:
                            band = int(band)
                        
                        callsign = row[4].value
                        
                        if not pretend and None not in (callsign, dat, utc):    
                            datetime_combined=datetime.datetime.combine(dat, utc)
                            
                            found_qso = db_handle.get_first_qso(callsign=unicode(callsign),datetime_utc=datetime_combined)

                            if found_qso:
                                print "Not adding: %04i:  %-10s %-10s %-6s %-6s (already in db)" % (i, mode, dat, utc, band)
                            else:
                                qso = db_handle.create_qso(
                                    callsign=callsign,
                                    mode=mode,
                                    datetime_utc=datetime_combined,
                                    frequency=band,
                                    rst_sent=row[5].value, 
                                    rst_received=row[6].value,
                                    name_received=row[7].value,
                                    qth_received=row[8].value,
                                    country_received=row[9].value,
                                    text_note=row[10].value,
                                )
                                print "Added: %04i:  %-10s %-10s %-6s %-6s" % (i, mode, dat, utc, band)
                        
                        
                        

                    except Exception, e:
                        print "%04i:  Invalid data. (%s)" % (i, str(e))
                        next
                    
                   

