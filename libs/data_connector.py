#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import Base, CallsignEntity, QsoType, Qso, QsoVariable
from models import probe_models_and_create_session

class DataConnector():
    
    def __init__(self, db_file):
        
        self.session = probe_models_and_create_session(db_file)
   
    def create_qso(self, *args, **kwargs):
        
        if 'callsign_text_note' in kwargs:
            callsign_note = kwargs['callsign_text_note']
            del(kwargs['callsign_text_note'])
        else:
            callsign_note = None

        qso = Qso(*args, **kwargs)

        # probe for CallsignEntity
        base_callsign_text = CallsignEntity.get_base_callsign(kwargs['callsign'])
        base_callsign_entity = self.session.query(CallsignEntity).filter_by(callsign=base_callsign_text).first()
        if  base_callsign_entity is not None:
            # base callsign found, assign
            qso.callsign_entity = base_callsign_entity 
            if callsign_note is not None:
                qso.callsign_entity.text_note = callsign_note
        else:
            # base callsign not found, create
            base_callsign_entity = CallsignEntity(callsign=base_callsign_text)
            if callsign_note is not None:
                base_callsign_entity.text_note = callsign_note
            self.session.add(base_callsign_entity)
            qso.callsign_entity = base_callsign_entity 


        self.session.add(qso)

        self.commit()
        return qso
    
    def update_qso(self, qso, *args, **kwargs):
        
        if 'callsign_text_note' in kwargs:
            callsign_note = kwargs['callsign_text_note']
            del(kwargs['callsign_text_note'])
        else:
            callsign_note = None
        
        for i in kwargs.keys():
            setattr(qso, i, kwargs[i])
            
        # TODO - unify settings callsign with create qso
        base_callsign_text = CallsignEntity.get_base_callsign(kwargs['callsign'])
        base_callsign_entity = self.session.query(CallsignEntity).filter_by(callsign=base_callsign_text).first()
        
        if  base_callsign_entity is not None:
            # base callsign found, assign
            qso.callsign_entity = base_callsign_entity 
            if callsign_note is not None:
                qso.callsign_entity.text_note = callsign_note
        else:
            # base callsign not found, create
            base_callsign_entity = CallsignEntity(callsign=base_callsign_text)
            if callsign_note is not None:
                base_callsign_entity.text_note = callsign_note
            self.session.add(base_callsign_entity)
            qso.callsign_entity = base_callsign_entity 
        
        self.session.add(qso)
        self.commit()
    
    def delete_qso(self, qso):
        
        self.session.delete(qso)
        self.session.flush()
        self.session.commit()
        
    def get_qsos(self, callsign_filter=None, base_callsign=True):
        if callsign_filter is not None:

            if base_callsign:
                # first get basic callsign and then get matching qsos
                callsign_filter = CallsignEntity.get_base_callsign(callsign_filter)
                if len(callsign_filter) > 1:
                    return self.session.query(Qso).join(CallsignEntity).filter(CallsignEntity.callsign.startswith(unicode(callsign_filter))).order_by(Qso.id.desc()).all()
                else:
                    return []
            else:
                # just return a list matching the given callsign
                return self.session.query(Qso).filter(Qso.callsign.startswith(unicode(callsign_filter))).order_by(Qso.id.desc()).all()
        else:
            return self.session.query(Qso).order_by(Qso.id.desc()).all()

    def get_first_qso(self, *args, **kwargs):
        return self.session.query(Qso).filter_by(**kwargs).first()
       
    def commit(self):
        self.session.commit()
        
    def rollback(self):
        self.session.rollback()

