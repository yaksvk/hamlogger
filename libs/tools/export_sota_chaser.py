#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EXPORT SOTA (TSVv2)
"""

import datetime
import re
import os.path
import io

def execute(csv_file, db_handle, config, pretend=False):
    output = db_handle.get_qsos_sota_chaser()
    create_export_file_from_qsos(output, csv_file, config)
    

def create_export_file_from_qsos(output, csv_file, config):
    with io.open(csv_file,'w', encoding='utf8') as out_file:
        for item in output:
            
            fields = ['V2']
            
            # my callsign
            if 'MY_CALL' in item.variables:
                fields.append(item.variables['MY_CALL'].value)
            else:
                fields.append(config['MY_CALLSIGN'])
                
            
            # my summit)
            if 'SUMMIT_SENT' in item.variables:
                fields.append(item.variables['SUMMIT_SENT'].value)
            else:
                fields.append('')
            
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
     
    

    
        
