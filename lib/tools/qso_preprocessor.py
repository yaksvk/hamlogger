#!/usr/bin/env/python

import re
import datetime

def process_qsos(header, qsos, custom_variables=None):

    common_vars = { i.strip(): j.strip() for (i, j) in [ i.split('=') for i in header.splitlines() ] }
    
    # common vars will be forcibly replaced by custom variables if set
    if custom_variables is None:
        custom_variables = {}

    for key, value in custom_variables.items():
        common_vars[key] = value

    for qso in qsos:
        # date and time
        (year, month, day) = re.match('(\d{4})(\d{2})(\d{2})', qso['QSO_DATE']).groups()
        dat = datetime.date(*map(int, (year, month, day)))

        (hours, minutes) = re.match('(\d{2})(\d{2})', qso['TIME_ON']).groups()
        utc = datetime.time(*map(int, (hours, minutes)))

        qso['datetime_combined']=datetime.datetime.combine(dat, utc)

        # init qso variables
        qso_variables = common_vars.copy()

        # parse additional stuff from note and init variables
        match = re.search(r'\b(\w+\/\w+\-\d+)\b', qso.get('COMMENT',''))
        if match:
            qso_variables['SUMMIT_RECEIVED'] = match.group(0).upper()

        qso['qso_variables'] = qso_variables

    return qsos