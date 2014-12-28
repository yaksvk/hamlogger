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
import os.path

def execute(ods_file, db_handle, pretend=False):
    
    print "Processing file: %s" % ods_file

    if ods_file is not None:
        if os.path.isfile(ods_file):
            print "file exists"
            return
        
        export_list = reversed(db_handle.get_qsos())
        
        doc = ezodf.newdoc(doctype="ods", filename=ods_file, template=None)
        
        qsos = ezodf.Table('QSO Log')
        callsigns= ezodf.Table('Callsigns')
        
        doc.sheets.append(qsos)
        doc.sheets.append(callsigns)
        
        # export qsos
        properties = "id date_iso time_iso mode frequency callsign rst_sent rst_received name_received qth_received text_note".split()
        columns = "ABCDEFGHIJKLMNO"
        
        qsos.append_columns(len(properties))
        
        qsos.append_rows(1)
        # property property row
        for j, prop in enumerate(properties):
            qsos[columns[j]+'1'].set_value(prop)
        # export callsigns
        for i, qso in enumerate(export_list):
            for j, prop in enumerate(properties):
                if getattr(qso, prop) is not None:
                    qsos.append_rows(1)
                    qsos[columns[j]+str(i+2)].set_value(getattr(qso, prop))
        
        doc.save()
    
    
        