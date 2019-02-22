#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EXPORT ADIF (v.2.2.7)
"""

import datetime
import re
import os.path
import io

def create_adif_tag(tag_name, value):
    return u''.join((u'<', tag_name, u':', str(len(value)), u'>', value, u' '))

def create_export_file_from_qsos(qsos, adif_file, config):
    execute(adif_file=adif_file, db_handle=None, pretend=False, config=config, qsos=qsos) 

def execute(adif_file, db_handle, config, pretend=False, qsos=None):
    
    header = u"""
Date of export: %s
Callsign: %s
Locator: %s
<ADIF_VER:5>2.2.7
<EOH>
""" % (datetime.datetime.now().isoformat(), config['MY_CALLSIGN'], config['MY_LOCATOR'])
    
    # TODO add some filtering

    if qsos is not None:
        output = qsos
    else:
        output = db_handle.get_qsos()

    lines = []
    
    for item in output:
        export_line = u''
        
        export_line += create_adif_tag('QSO_DATE', item.date_iso.replace('-',''))
        export_line += create_adif_tag('TIME_ON', item.time_iso.replace(':',''))


        # use custom callsign if applicable (Portable, etc.)
        if 'MY_CALL' in item.variables:
            export_line += create_adif_tag('STATION_CALLSIGN', item.variables['MY_CALL'].value)
            # if callsign used is different than callsign configured, also use the OPERATOR tag
            if item.variables['MY_CALL'].value != config['MY_CALLSIGN']:
                export_line += create_adif_tag('OPERATOR', config['MY_CALLSIGN'])
        
        # fast support for WWFF
        if 'WWFF_SENT' in item.variables:
            export_line += create_adif_tag('MY_SIG', 'WWFF')
            export_line += create_adif_tag('MY_SIG_INFO', item.variables['WWFF_SENT'].value)


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

        lines.append(export_line)
   
    with io.open(adif_file,'w', encoding='utf8') as out_file:
        out_file.write(header)
        out_file.write(u"\n<EOR>\n".join(lines))
        
        
