#!/usr/bin/env python

import csv
import json

def translate(item, fields):
    output = {}

    for field in fields:
        if field in item:
            output[field] = item[field]
    return output
            

def execute(db_handle, summits_db_file, **kwargs):
    qsos = db_handle.get_qsos_sota(**kwargs)
    summits = set()

    for item in sorted(qsos, key=lambda qso: qso.datetime_utc):
        if 'SUMMIT_SENT' in item.variables:
            summits.add(item.variables['SUMMIT_SENT'].value)

    summits_with_details = []

    with open(summits_db_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'SummitCode' in row:
                if row['SummitCode'] in summits:
                    summits_with_details.append(row)

    exported_fields = [ 'SummitCode', 'Latitude', 'Longitude' ]

    out = list(map(lambda x: translate(x, exported_fields), summits_with_details))
    print(json.dumps(out, indent=4, separators=(',', ': ')))
