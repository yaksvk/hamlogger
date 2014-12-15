#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import Base, CallsignEntity, QsoType, Qso, QsoVariable
from models import probe_models_and_create_session

class DataConnector():
    
    def __init__(self, db_file):
        
        self.session = probe_models_and_create_session(db_file)
   
    def create_qso(self, *args, **kwargs):

        qso = Qso(*args, **kwargs)

        # probe for CallsignEntity
        base_callsign_text = CallsignEntity.get_base_callsign(kwargs['callsign'])
        base_callsign_entity = self.session.query(CallsignEntity).filter_by(callsign=base_callsign_text).first()
        if  base_callsign_entity is not None:
            # base callsign found, assign
            qso.callsign_entity = base_callsign_entity 
        else:
            # base callsign not found, create
            base_callsign_entity = CallsignEntity(callsign=unicode(base_callsign_text))
            self.session.add(base_callsign_entity)
            qso.callsign_entity = base_callsign_entity 


        self.session.add(qso)

        self.commit()
        return qso

    def get_qsos(self, callsign_filter=None):
        if callsign_filter is not None:
            return self.session.query(Qso).filter(Qso.callsign.startswith(unicode(callsign_filter))).order_by(Qso.id.desc()).all()
        else:
            return self.session.query(Qso).order_by(Qso.id.desc()).all()

    def get_first_qso(self, *args, **kwargs):
        return self.session.query(Qso).filter_by(**kwargs).first()
       

    def commit(self):
        self.session.commit()

