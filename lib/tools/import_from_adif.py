#!/usr/bin/env python

"""
This is to import QSOs from an ADIF

./hamlogger.py --import_adif logs/202111171430.adif --summit OE/NO-011

"""

import re
import datetime

from ..models import QsoVariable
from .import_log import ImportLog

from typing import TextIO




from pprint import pprint

def _read_header(fh: TextIO, initial_char: str) -> str:
    """
    Keeps reading characters until it reaches <eoh> tag.
    """
    header = initial_char

    while True:
        char = fh.read(1);
        if not char:
            break

        if char == '<':
            expected_eoh = _read_until(fh, '>')
            if expected_eoh.lower() == 'eoh>':
                break
            else:
                header += expected_eoh

        header += char

    return header

def _read_until(fh: TextIO, until_char: str) -> str:
    """
    Keeps reading characters from filehandle until it reaches
    character <until_char>.
    """
    output = ''
    while True:
        char = fh.read(1)
        if not char:
            break

        output += char
        if char == until_char:
            break
    return output


def execute(adif_file, db_handle, args):

    qsos = []
    first = True
    header = ''

    with open(adif_file, 'r', encoding='utf-8') as fh:
        current_rec = {}
        while True:
            char = fh.read(1)
            last = False
            eor = False

            if first:
                first = False
                if char != '<':
                    header = _read_header(fh, char)
                    continue

            if not char:
                last = True
                eor = True

            if char == '<':
                current_tag = '<' + _read_until(fh, '>')

                if current_tag.lower() == '<eor>':
                    eor = True

                tm = re.match('<(\w+):(\d+)>', current_tag)
                if tm:
                    (var, length) = tm.groups()
                    current_rec[var.upper()] = fh.read(int(length))

            if eor:
                if current_rec:
                    qsos.append(current_rec)
                current_rec = {}

            if last:
                break

    for qso in qsos:
        qso['MY_CALL'] = 'OE/OM1WS/P'
        if args.summit:
            print(f"Adding {args.summit} as SUMMIT_SENT to all QSOs")
            qso['SUMMIT_SENT'] = args.summit

        (year, month, day) = re.match('(\d{4})(\d{2})(\d{2})', qso['QSO_DATE']).groups()
        dat = datetime.date(*map(int, (year, month, day)))

        (hours, minutes) = re.match('(\d{2})(\d{2})', qso['TIME_ON']).groups()
        utc = datetime.time(*map(int, (hours, minutes)))

        qso['datetime_combined']=datetime.datetime.combine(dat, utc)

    qsos.sort(key=lambda x: x['datetime_combined'])
    #pprint(qsos)

    common_vars = { i.strip(): j.strip() for (i, j) in [ i.split('=') for i in header.splitlines() ] }

    for q in qsos:

        qso_variables = common_vars.copy()
        #qso_variables['MY_CALL'] = QsoVariable('MY_CALL', q['MY_CALL'])
        #qso_variables['SUMMIT_SENT'] = QsoVariable('SUMMIT_SENT', q['SUMMIT_SENT'])
        #qso_variables['MY_CALL'] = q['MY_CALL']
        #qso_variables['SUMMIT_SENT'] = q['SUMMIT_SENT'] if 'SUMMIT_SENT' in 
        if 'COMMENT' not in q:
            q['COMMENT'] = ''

        # find something like summit rcvd in comment
        match = re.search(r'\b(\w+\/\w+\-\d+)\b', q['COMMENT'])
        if match:
            qso_variables['SUMMIT_RECEIVED'] = match.group(0).upper()


        # TODO NOTE remote this for real action
        print(f"I would add {q['CALL']} vars: {qso_variables}")

        db_handle.create_qso(
            callsign=q['CALL'],
            mode=q['MODE'],
            datetime_utc=q['datetime_combined'],
            frequency=q['FREQ'],
            rst_sent=q['RST_SENT'],
            rst_received=q['RST_RCVD'],
            text_note=q['COMMENT'],
            variables=qso_variables
        )
