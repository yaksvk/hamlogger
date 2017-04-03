#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import Base, CallsignEntity, QsoType, Qso, QsoVariable, QsoSession
from models import probe_models_and_create_session
from sqlalchemy import func, desc

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
        
    def get_orphan_qsos(self, asc=False):
        return self.session.query(Qso).filter_by(qso_session=None).order_by(Qso.id.asc()).all()

    def get_qsos(self, callsign_filter=None, base_callsign=True, asc=False):
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
            if asc:
                return self.session.query(Qso).order_by(Qso.id.asc()).all()
            else:
                return self.session.query(Qso).order_by(Qso.id.desc()).all()
    
    def get_qsos_sota(self, summit=None, date=None):

        # TODO this is a quick and easy way to make exception for an activation
        # the qsos shoudl be filtered by DATE +- 1d

        if summit is not None and date is not None:
            return self.session.query(Qso).join(QsoVariable) \
                .filter(QsoVariable.name==u'SUMMIT_SENT') \
                .filter(QsoVariable.value==unicode(summit)) \
                .filter(func.date(Qso.datetime_utc)==date).order_by(Qso.id).all()
        else:                        
            return self.session.query(Qso).join(QsoVariable).filter(QsoVariable.name==u'SUMMIT_SENT').order_by(Qso.id).all()

    def get_sota_activations(self):
        
        sota_activations = self.session.query(
            func.count(Qso.id), 
            func.date(Qso.datetime_utc),
            QsoSession.description,
            QsoVariable.value
        ).join(Qso.variables).join(Qso.qso_session).filter(QsoVariable.name==u'SUMMIT_SENT').group_by(QsoVariable.value, func.date(Qso.datetime_utc)).order_by(desc(func.date(Qso.datetime_utc))).all()

        return sota_activations

    def get_qsos_sota_chaser(self):
        
        #  TODO or QsoVariable.name=='SUMMIT_RECEIVED'
        return self.session.query(Qso).join(QsoVariable).filter(QsoVariable.name==u'SUMMIT_RECEIVED').order_by(Qso.id).all()
    
    def get_callsigns(self):
        return self.session.query(CallsignEntity).order_by(CallsignEntity.callsign).all()
    
    def get_qso_sessions(self):
        return self.session.query(QsoSession).order_by(QsoSession.id).all()
    
    def get_callsign(self, call):
        return self.session.query(CallsignEntity).filter(CallsignEntity.callsign==call).first()
    
    def create_qso_session(self, *args, **kwargs):
        qso_session = QsoSession(*args, **kwargs)
        self.session.add(qso_session)
        self.commit()
        return qso_session
    

    def get_first_qso(self, *args, **kwargs):
        return self.session.query(Qso).filter_by(**kwargs).first()
       
    def commit(self):
        self.session.commit()
        
    def rollback(self):
        self.session.rollback()

