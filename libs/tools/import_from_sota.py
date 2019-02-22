#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is to import QSOs from a Sotadata website
"""

import ezodf
import datetime
import re
import csv
import unicodecsv
from ..models import QsoVariable
#from libs import prefix_resolver

def execute(csv_file, db_handle, pretend=False):
    with open(csv_file, 'rb') as fh:
        csv_reader = unicodecsv.reader(fh, delimiter=',', quotechar='"', encoding='utf-8')
        for i, row in enumerate(csv_reader):
            meta_variables = {}
            
            dat=None
            utc=None
            mode=row[5]
            name=None
            country=None
            qth=None
            band=row[4][:-3]
            callsign = row[6]
            note = row[7]
            
            # get country
            #result = self.resolver.get_entity_for_call(callsign)
            #if result:
            #    country = result['name'].decode('utf-8')
            
            (day, month, year) = row[1].split('/')
            dat = datetime.date(*map(int, (year, month, day)))
            utc = datetime.time(*map(int, row[2].split(':')))
            datetime_combined=datetime.datetime.combine(dat, utc)
            
            # QSO variables
            qso_variables = {}
            qso_variables['MY_CALL'] = QsoVariable('MY_CALL', row[0])
            qso_variables['SUMMIT_SENT'] = QsoVariable('SUMMIT_SENT', row[3])
            
            #summit_recvd = re.sub('^.*s2s: ([^, ]+).*$', '\\1', note)
            #if summit_recvd:
             #   qso_variables['SUMMIT_RECEIVED'] = QsoVariable('SUMMIT_RECEIVED', summit_recvd)
           
            #print datetime_combined
            
            #print note
            
            
            #match_result = re.match(r'^(?P<rst_sent>\d+) (?P<rst_received>\d+)', note)
            match_result = re.match(r'^(?P<rst_sent>\d+) (?P<rst_received>\d+),? ?(?P<name>[^,]*),? ?(?P<qth>[^,]*)', note)

            rst_sent = match_result.group('rst_sent')
            rst_received = match_result.group('rst_received')
            
            results = match_result.groupdict()
            name = results.get('name', None)
            qth = results.get('qth', None)
            
            found_qso = db_handle.get_first_qso(callsign=unicode(callsign),datetime_utc=datetime_combined)  
            if found_qso:
                print "sorry, QSO found."
            else:
                qso = db_handle.create_qso(
                callsign=callsign,
                mode=mode,
                datetime_utc=datetime_combined,
                frequency=band,
                rst_sent=rst_sent, 
                rst_received=rst_received,
                name_received=name,
                qth_received=qth,
                country_received=country,
                #text_note=note,
                variables=qso_variables
            )
            #rst_received = match_result.group('name')
            
            #print "Added: %04i:  %-10s %-10s %-6s %-6s" % (i, qso_variables['MY_CALL'], qso_variables['SUMMIT_SENT'], rst_sent, rst_received )




