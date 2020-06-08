#!/usr/bin/env python

from sets import Set
import csv
import json

def translate(item, fields):
    output = {}

    for field in fields:
        if field in item:
            output[field] = item[field]
    return output
            

def execute(db_handle, **kwargs):
    qsos = db_handle.get_qsos_sota(**kwargs)
    summits = Set()

    for item in sorted(qsos, key=lambda qso: qso.datetime_utc):
        if 'SUMMIT_SENT' in item.variables:
            summits.add(item.variables['SUMMIT_SENT'].value)

    # now that we have a set of summits, load the global summit database 
    # TODO
    summits_with_details = []

    with open('/home/yak/sources/python/hamlogger/db/summitslist.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'SummitCode' in row:
                if row['SummitCode'] in summits:
                    summits_with_details.append(row)

    exported_fields = [ 'SummitCode', 'Latitude', 'Longitude' ]

    out = map(lambda x: translate(x, exported_fields), summits_with_details)

    print(json.dumps(out, indent=4, separators=(',', ': ')))
    
