#!/usr/bin/env python

"""
EXPORT WWFF (ADIF with special params)
"""

import datetime
import re
import os.path
import io

def tag(tag_name, value):
    if value is None:
        value = ''

    return u''.join((u'<', tag_name, u':', str(len(value)), u'>', value, u' '))

def create_export_file_from_qsos(qsos, adif_file, config):

    with io.open(adif_file,'w', encoding='utf8') as out_file:
        for item in qsos:
            line = (
                tag('QSO_DATE', item.date_iso.replace('-','')),
                tag('TIME_ON', item.time_iso.replace(':','')),
                tag('CALL', item.callsign),
                tag('FREQ', item.frequency),
                tag('MODE', item.mode),
                tag('RST_SENT', re.sub('^(\d+).*$', u'\\1', item.rst_sent)),
                tag('RST_RCVD', re.sub('^(\d+).*$', u'\\1', item.rst_received)),
                tag('STATION_CALLSIGN', item.variables.get('MY_CALL', config.get('MY_CALLSIGN'))),
                tag('OPERATOR', config.get('MY_CALLSIGN')),
                tag('MY_SIG', item.variables.get('WWFF_SENT')),
                "<EOR>\n",
            )
            out_file.write(''.join(line))
