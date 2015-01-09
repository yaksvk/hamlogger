#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EXPORT SOTA (TSVv2)
"""

import datetime
import re
import os.path

def execute(csv_file, db_handle, config, pretend=False):
    output = db_handle.get_qsos_sota()
    
    for item in output:
        
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
        
        note = ', '.join(notes)
        note = '"' + note + '"'
        
        fields.append(note)
            
        
        text = ','.join(fields)
        print text
        
        
