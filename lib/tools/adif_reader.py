#!/usr/bin/env python

"""
ADIF reading library

Exports public function read_file which expects a file_name argument. It
reads the file and returns a list of dictionaries.

"""

from typing import TextIO
import re

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


def read_file(adif_file):
    """
    Reads contents of an ADIF file and returns a list of dictionaries
    """
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
            
    return header, qsos