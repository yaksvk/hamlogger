#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import Base, CallsignEntity, QsoType, Qso, QsoVariable
from models import probe_models_and_create_session

class DataConnector():
    
    def __init__(self, db_file):
        
        self.session = probe_models_and_create_session(db_file)
   
    def create_qso(self, *args, **kwargs):

        qso = Qso(*args, **kwargs)
        self.session.add(qso)
        return qso

    def get_qsos(self, callsign_filter=None):
        if callsign_filter is not None:
            return self.session.query(Qso).filter(Qso.callsign.startswith(callsign_filter)).order_by(Qso.id.desc()).all()
        else:
            return self.session.query(Qso).order_by(Qso.id.desc()).all()

    def commit(self):
        self.session.commit()

