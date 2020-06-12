#!/usr/bin/env python

"""
EXPORT SOTA (TSVv2)
"""

import datetime
import re
import os.path
import io

def create_export_file_from_qsos(qsos, csv_file, config):
    with io.open(csv_file,'w', encoding='utf8') as out_file:
        # make sure we sort the QSOs by date and time - sotadata will refuse the file otherwise
        for item in sorted(qsos, key=lambda qso: qso.datetime_utc):
            
            fields = ['V2']
            
            # my callsign
            if 'MY_CALL' in item.variables:
                fields.append(item.variables['MY_CALL'].value)
            else:
                fields.append(config['MY_CALLSIGN'])
                
            
            # my summit
            fields.append(item.variables.get('SUMMIT_SENT').value)
            
            # date = Use of International date format (DD/MM/YY) is recommended
            # The time in UTC. Either HHMM or HH:MM will work. Use the 24 hour clock!
            
            utc = item.datetime_utc.timetuple()
            fields.append('%02i/%02i/%02i' % (utc.tm_mday, utc.tm_mon, int(str(utc.tm_year)[-2:])))
            fields.append(("%02i:%02i" % (utc.tm_hour, utc.tm_min)))
            fields.append(item.frequency+'MHz')
            fields.append(item.mode)
            fields.append(item.callsign)
            
            if 'SUMMIT_RECEIVED' in item.variables:
                fields.append(item.variables['SUMMIT_RECEIVED'].value)
            else:
                fields.append('')
            
            notes = [ item.rst_sent + ' ' + item.rst_received ]
            if item.name_received:
                notes.append(item.name_received)
                
            if item.qth_received:
                notes.append(item.qth_received)

            if 'SUMMIT_SENT' in item.variables and 'SUMMIT_RECEIVED' in item.variables:
                notes.append('s2s: ' + item.variables['SUMMIT_RECEIVED'].value)
            
            note = ', '.join(notes)
            note = '"' + note + '"'
            
            fields.append(note)
                
            
            text = ','.join(fields)
            out_file.write(text + "\n")
        

def execute(csv_file, db_handle, config, pretend=False, **kwargs):
    qsos = db_handle.get_qsos_sota(**kwargs)
    create_export_file_from_qsos(qsos, csv_file, config)

    
