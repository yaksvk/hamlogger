#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EXPORT ADIF - LOTW: report used callsign as station callsign (v.2.2.7)
"""

import datetime
import re
import os.path
import io

def create_adif_tag(tag_name, value):
    return u''.join((u'<', tag_name, u':', str(len(value)), u'>', value, u' '))

def execute(adif_file_prefix, db_handle, config, pretend=False):
    
    
    # TODO add some filtering
    output = db_handle.get_qsos()
    
    callsign_dict = {}
    lines = []
     
    for item in output:
        export_line = u''
        
        export_line += create_adif_tag('QSO_DATE', item.date_iso.replace('-',''))
        export_line += create_adif_tag('TIME_ON', item.time_iso.replace(':',''))
        
        current_call = None
        # use custom callsign if applicable (Portable, etc.)
        if 'MY_CALL' in item.variables:
            export_line += create_adif_tag('STATION_CALLSIGN', item.variables['MY_CALL'].value)
            current_call = item.variables['MY_CALL'].value
        else:
            current_call = config['MY_CALLSIGN']

        note = u''            
        # put sota variables into note
        if 'SUMMIT_SENT' in item.variables:
            note += u'SOTA summit sent: ' + item.variables.get('SUMMIT_SENT').value
        if 'SUMMIT_RECEIVED' in item.variables:
            note += u'SOTA summit received: ' + item.variables.get('SUMMIT_RECEIVED').value
        if note != u'':
            export_line += create_adif_tag('NOTES', note)
        
        export_line += create_adif_tag('CALL', item.callsign)
        export_line += create_adif_tag('FREQ', item.frequency)
        export_line += create_adif_tag('MODE', item.mode)
        export_line += create_adif_tag('RST_SENT', re.sub('^(\d+).*$', u'\\1', item.rst_sent))
        export_line += create_adif_tag('RST_RCVD', re.sub('^(\d+).*$', u'\\1', item.rst_received))
        
        if item.name_received:
            export_line += create_adif_tag('NAME', item.name_received)
        if item.qth_received:
            export_line += create_adif_tag('QTH', item.qth_received)

        # add this to the apropriate hash
        if current_call not in callsign_dict:
            callsign_dict[current_call] = []
        
        callsign_dict[current_call].append(export_line)
   
    for call, lines in callsign_dict.items():
        header = u"""
Date of export: %s
Callsign: %s
Locator: %s
<ADIF_VER:5>2.2.7
<EOH>
""" % (datetime.datetime.now().isoformat(), call, '')
        with io.open(adif_file_prefix + '_' + call.replace('/', '_') + '.adif','w', encoding='utf8') as out_file:
            out_file.write(header)
            out_file.write(u"\n<EOR>\n".join(lines))
        
        
