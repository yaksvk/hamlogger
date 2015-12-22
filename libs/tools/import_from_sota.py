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
            
            summit_recvd = re.sub('^.*s2s: ([^, ]+).*$', '\\1', note)
            if summit_recvd:
                qso_variables['SUMMIT_RECEIVED'] = QsoVariable('SUMMIT_RECEIVED', summit_recvd)
           
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
                text_note=note,
                variables=qso_variables
            )
            #rst_received = match_result.group('name')
            
            #print "Added: %04i:  %-10s %-10s %-6s %-6s" % (i, qso_variables['MY_CALL'], qso_variables['SUMMIT_SENT'], rst_sent, rst_received )





 will only pretend. Nothing will be written. No worries :)"

ssing file: %s" % ods_file

opendoc(ods_file)

pe != 'ods':
ot an ODS file. Sorry."


 in enumerate(doc.sheets):
rocessing sheet: %s" % sheet.name
0:

_variables = {}

i, row in enumerate(sheet.rows()):

if i == 0:
    pass
    # process QSO variables here
    if len(row) > 12:
        for k in range(12, len(row)):
            if row[k].value:
                meta_variables[row[k].value] = k

if i > 0:
    
    dat=None
    utc=None
    mode=None
    band=None
    callsign=None

    try:
        if row[1] is not None:
            tfields = row[1].value.split('-')
            if len(tfields) == 3:
                dat = datetime.date(*map(int, tfields))
            else:
                print "Unable to parse date."            
        
        if row[2].value is not None:
            utc = datetime.time(*map(int, row[2].value.split(':')))
        mode = row[3].value
        band = row[4].value
        
        try:
            if int(band) == band:
                band = int(band)
        except:
            pass
        
        rst_received = str(row[7].value).replace('.0', '')
        rst_sent = str(row[6].value).replace('.0', '')
        
        callsign = row[5].value
        
        # QSO variables
        qso_variables = {}
        for key, val in meta_variables.items():
            if row[val].value is not None and len(row[val].value):
                qso_variables[key] = QsoVariable(key, row[val].value)
        
        if not pretend and None not in (callsign, dat, utc):    
            datetime_combined=datetime.datetime.combine(dat, utc)
            
            found_qso = db_handle.get_first_qso(callsign=unicode(callsign),datetime_utc=datetime_combined)

            if found_qso:
                print "Not adding: %04i:  %-10s %-10s %-6s %-6s (already in db)" % (i, mode, dat, utc, band)
            else:
                qso = db_handle.create_qso(
                    callsign=callsign,
                    mode=mode,
                    datetime_utc=datetime_combined,
                    frequency=band,
                    rst_sent=rst_sent, 
                    rst_received=rst_received,
                    name_received=row[8].value,
                    qth_received=row[9].value,
                    country_received=row[10].value,
                    text_note=row[11].value,
                    variables=qso_variables
                )
                print "Added: %04i:  %-10s %-10s %-6s %-6s" % (i, mode, dat, utc, band)
        
        
        

    except Exception, e:
        print "%04i:  Invalid data. (%s)" % (i, str(e))
        next
    
1:
t "Processing callsign data..."
i, row in enumerate(sheet.rows()):
if len(row) >= 4:
    if row[1].value:
        entity = db_handle.get_callsign(row[1].value)
        if entity:
            if row[3].value is not None:
                print "Updating note for %s to: %s" % (row[1].value, row[3].value)
                db_handle.session.add(entity)
                entity.text_note = row[3].value
                db_handle.session.commit()
            
               

