#!/usr/bin/env python

"""
EXPORT ADIF (v.2.2.7)
"""

import datetime
import re
import os.path
import io



def execute(adif_file, db_handle, config, pretend=False):
    
    # TODO add some filtering
    output = db_handle.get_qsos(asc=True)
    
    lines = []
    
    for item in output:
        #print "QSO: 21000 PH 2014-03-28 2100 OM1AWS        59     001 VC4D          59     003" 
        sent = '015'
        received = 'XXX'
        
        if item.text_note is not None:
                received = item.text_note 
        
        print "QSO: %05s PH %s %s %-013s %09s %s %-013s %09s %-013s" % (
            str(int(float(item.frequency) * 1000)), item.date_iso, item.time_iso.replace(':', ''), config['MY_CALLSIGN'], item.rst_sent, sent, item.callsign, item.rst_received, received)
    
    
    """
    for item in output:
        export_line = u''
        
        export_line += create_adif_tag('QSO_DATE', item.date_iso.replace('-',''))
        export_line += create_adif_tag('TIME_ON', item.time_iso.replace(':',''))
        
        # use custom callsign if applicable (Portable, etc.)
        if 'MY_CALL' in item.variables:
            export_line += create_adif_tag('STATION_CALLSIGN', item.variables['MY_CALL'].value)

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
    """ 
        
