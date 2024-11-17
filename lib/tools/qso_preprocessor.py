#!/usr/bin/env/python

"""
This pre-processes QSOs before importing them to our log. This is
usually to recognize SOTA, WWFF or other references from comments.
"""

import re
import datetime
from lib.prefix_resolver import Resolver

def process_qsos(header, qsos, custom_variables=None):

    common_vars = {}

    try:
        common_vars = { i.strip(): j.strip() for (i, j) in [ i.split('=') for i in header.splitlines() ] }
    except ValueError:
        print('Unable to process ADIF header')

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
        comment = qso.get('COMMENT','')

        # QSO ADIF vars mapping:
        mapping_table = {
            'SOTA_REF': 'SUMMIT_RECEIVED',
            'MY_SOTA_REF': 'SUMMIT_SENT',
            'STATION_CALLSIGN': 'MY_CALL',
        }
        for adif_var, local_var in mapping_table.items():
            if adif_var in qso:
                qso_variables[local_var] = qso[adif_var]


        # SOTA ref from ADIF vars (SOTA_REF
        if 'SOTA_REF' in qso:
            qso_variables['SUMMIT_RECEIVED'] = qso['SOTA_REF']

        # SOTA summit ref
        match = re.search(r'\b(\w+\/\w+\-\d+)\b', comment)
        if match:
            qso_variables['SUMMIT_RECEIVED'] = match.group(0).upper()

        # WWFF ref
        match = re.search(r'\b(\w+-\d{4})\b', comment)
        if match:
            qso_variables['WWFF_RECEIVED'] = match.group(0).upper()


        qso['qso_variables'] = qso_variables

    return qsos
