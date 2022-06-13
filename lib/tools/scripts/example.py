#!/usr/bin/env python

import csv
import json
from ...models import Qso, CallsignEntity, QsoVariable
from sqlalchemy.sql import or_, func, desc
from pprint import pprint

"""
Example of what can be done with scripts.

Run this as hamlogger.py --run example
"""

def execute(db_handle, app, args):

    # Example1: Fix missing country info for QSOs with empty country_received.
    # Use the built-in country prefix resolver to determine country.

    # get all QSOs where contry is NULL
    qsos = db_handle.session.query(Qso).filter(Qso.country_received==None)

    for qso in qsos:
        result = app.resolver.get_entity_for_call(qso.callsign)
        if result is not None:
            country = result['name']
            qso.country_received = country
            # (EXAMPLE) db_handle.session.add(qso)

    # commit session, save changes
    # (EXAMPLE) db_handle.session.commit()
