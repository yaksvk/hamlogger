#!/usr/bin/env python

"""
THIS IS JUST TO PRODUCE A NICE ODT-LOG READY FOR PRINTING
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



def execute(odt_file, db_handle, pretend=False):
    
    print "Processing file: %s" % odt_file

    if odt_file is not None:
        if os.path.isfile(odt_file):
            print "file exists"
            return
        
        export_list = db_handle.get_qsos()
        
        doc = ezodf.newdoc(doctype="odt", filename=odt_file, template=None)
        sessions = db_handle.get_qso_sessions()
        
        properties = "date_iso time_iso mode frequency callsign rst_sent rst_received name_received qth_received country_received text_note".split()

        for session in sessions:

            #tbl = ezodf.Table(name="Table", size=(len(session.qsos), len(properties)))
            tbl = ezodf.Table(name="Table", size=(1, len(properties)))

            doc.body.append(ezodf.Heading(session.description + ' (' + str(len(session.qsos)) + ')'))
            doc.body.append(ezodf.Paragraph(session.text_note))

            # show qsos
            col_gen = column_name_generator(1000)
            columns = list(col_gen)
            variable_columns_source = columns[len(columns)-1:len(properties)-1:-1]

            for j, prop in enumerate(properties):
                tbl[columns[j]+'1'].set_value(prop)

            for i, qso in enumerate(session.qsos):
                for j, prop in enumerate(properties):
                    if getattr(qso, prop) is not None:
                        tbl.append_rows(1)
                        tbl[columns[j]+str(i+2)].set_value(getattr(qso, prop))

            doc.body.append(tbl)

        # orphan qsos
        qsos = db_handle.get_orphan_qsos()
        tbl = ezodf.Table(name="Table", size=(1, len(properties)))
        doc.body.append(ezodf.Heading('Unsorted (' + str(len(qsos)) + ')'))
        col_gen = column_name_generator(1000)
        columns = list(col_gen)
        variable_columns_source = columns[len(columns)-1:len(properties)-1:-1]

        for j, prop in enumerate(properties):
            tbl[columns[j]+'1'].set_value(prop)

        for i, qso in enumerate(qsos):
            for j, prop in enumerate(properties):
                if getattr(qso, prop) is not None:
                    tbl.append_rows(1)
                    tbl[columns[j]+str(i+2)].set_value(getattr(qso, prop))

        doc.body.append(tbl)
            
        doc.save()
        return
        
        qsos = ezodf.Table('QSO Log')
        callsigns= ezodf.Table('Callsigns')
        
        doc.sheets.append(qsos)
        doc.sheets.append(callsigns)
        
        # export qsos
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
        
    
        
