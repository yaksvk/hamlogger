#!/usr/bin/env python

import csv
import json
from ...models import Qso, CallsignEntity, QsoVariable
from sqlalchemy.sql import or_, func, desc

"""
Example of what can be done with scripts.

Run this as hamlogger.py --run example
"""

def execute(db_handle, app, **kwargs):
    # get all QSOs where contry is NULL or country is 'Slovakia'
    qsos = db_handle.session.query(Qso).filter(or_(Qso.country_received==None, Qso.country_received=='Slovakia'))


    # commit session, save changes
    db_handle.session.commit()
