#!/usr/bin/env python

from dataclasses import dataclass

class ImportLog:
    def __init__(self):
        self._qsos = []

    def __iter__(self):
        return iter(self._qsos)

@dataclass
class ImportQso:
    CALL: str
    FREQ: str

if __name__ == '__main__':
    log = ImportLog()

    for qso in log:
        print(qso)
