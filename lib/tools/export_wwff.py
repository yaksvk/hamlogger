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

def header():
    return "\n".join((
        'ADIF export for WWFF',
        tag('PROGRAMID', 'Hamlogger'),
        tag('ADIF_VER', '3.0.6'),
        "<EOH>\n",
    ))

def freq_to_band(freq):

    bands = (
        ('2190m',.136,.137),
        ('560m',.501,.504),
        ('160m',1.8,2.0),
        ('80m',3.5,4.0),
        ('60m',5.102,5.404),
        ('40m',7.0,7.3),
        ('30m',10.0,10.15),
        ('20m',14.0,14.35),
        ('17m',18.068,18.168),
        ('15m',21.0,21.45),
        ('12m',24.890,24.99),
        ('10m',28.0,29.7),
        ('6m',50,54),
        ('4m',70,71),
        ('2m',144,148),
        ('1.25m',222,225),
        ('70cm',420,450),
        ('33cm',902,928),
        ('23cm',1240,1300),
        ('13cm',2300,2450),
        ('9cm',3300,3500),
        ('6cm',5650,5925),
        ('3cm',10000,10500),
        ('1.25cm',24000,24250),
        ('6mm',47000,47200),
        ('4mm',75500,81000),
        ('2.5mm',119980,120020),
        ('2mm',142000,149000),
        ('1mm',241000,250000),
    );

    freq = int(freq)
    for index, value in enumerate(bands):
        if freq >= value[1] and freq <= value[2]:
            return value[0]

def create_export_file_from_qsos(qsos, adif_file, config):

    with io.open(adif_file,'w', encoding='utf8') as out_file:

        # header
        out_file.write(header())

        # log qso items
        for item in qsos:
            line = (
                tag('QSO_DATE', item.date_iso.replace('-','')),
                tag('TIME_ON', item.time_iso.replace(':','')),
                tag('CALL', item.callsign),
                tag('BAND', freq_to_band(item.frequency)),
                tag('MODE', item.mode),
                tag('RST_SENT', re.sub('^(\d+).*$', u'\\1', item.rst_sent)),
                tag('RST_RCVD', re.sub('^(\d+).*$', u'\\1', item.rst_received)),
                tag('STATION_CALLSIGN', item.variables.get('MY_CALL', config.get('MY_CALLSIGN'))),
                tag('OPERATOR', config.get('MY_CALLSIGN')),
                tag('MY_SIG', 'WWFF'),
                tag('MY_SIG_INFO', item.variables.get('WWFF_SENT')),
                "<EOR>\n",
            )
            out_file.write(''.join(line))
