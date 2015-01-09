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

def column_name_generator(n):
    C = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    X = C[0]
    i = 0

    while i < n:
        yield X
        
        chars = list(X)
        for k, j in enumerate(reversed(chars)):
            if C.index(j) < len(C) - 1:
                chars[(len(chars)-1) -k] = C[C.index(j)+1]
                for l in range(len(chars)-k, len(chars)):
                    chars[l] = C[0]
                break
        else:
            chars = list(C[0] * (len(chars) + 1))

        X = ''.join(chars)

        i += 1


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
        properties = "id date_iso time_iso mode frequency callsign rst_sent rst_received name_received qth_received country_received text_note".split()
        col_gen = column_name_generator(1000)
        columns = list(col_gen)
        variable_columns_source = columns[len(columns)-1:len(properties)-1:-1]
        
        qsos.append_columns(len(properties))
        qsos.append_rows(1)
        
        variable_columns = {}
        
        # header property row
        for j, prop in enumerate(properties):
            qsos[columns[j]+'1'].set_value(prop)
            
        for i, qso in enumerate(export_list):
            for j, prop in enumerate(properties):
                if getattr(qso, prop) is not None:
                    qsos.append_rows(1)
                    qsos[columns[j]+str(i+2)].set_value(getattr(qso, prop))
            
            # process variables
            for key, var in qso.variables.items():
                if key not in variable_columns:
                    variable_columns[key] = variable_columns_source.pop()
                    qsos[variable_columns[key]+'1'].set_value(key)
                
                qsos[variable_columns[key]+str(i+2)].set_value(var.value)
        
        # export callsigns
        callsign_list = db_handle.get_callsigns()
        properties = "id callsign qso_count text_note".split()
        
        callsigns.append_columns(len(properties))
        callsigns.append_rows(1)
        
        # header property row
        for j, prop in enumerate(properties):
            callsigns[columns[j]+'1'].set_value(prop)
        
        for i, call in enumerate(callsign_list):
            for j, prop in enumerate(properties):
                if getattr(call, prop) is not None:
                    callsigns.append_rows(1)
                    callsigns[columns[j]+str(i+2)].set_value(getattr(call, prop))
        
        doc.save()
    
    
        