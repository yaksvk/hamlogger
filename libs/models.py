#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, relationship

Base = declarative_base()

# create the necessary models and database session
def probe_models_and_create_session(db_file):
    engine = create_engine('sqlite:///' + db_file)
    Base.metadata.create_all(engine)  

    session = sessionmaker(bind=engine,)()
    return session

# models for tables

class CallsignEntity(Base):                                                                                                                                                                         
    __tablename__ = 'callsigns'                                                                                                                                                               
                                                                                                                                                                                              
    id = Column(Integer, primary_key=True)
    callsign = Column(Unicode(64))
    qsos = relationship("Qso", backref="callsigns")
    text_note = Column(Text)

class QsoType(Base):
    __tablename__ = 'qso_types'

    id = Column(Integer, primary_key=True)
    description = Column(Unicode(64))
    qsos = relationship("Qso", backref="qso_types")
    

class Qso(Base):
    __tablename__ = 'qsos'
    
    id = Column(Integer, primary_key=True)
    callsign_id = Column(Integer, ForeignKey('callsigns.id'), nullable=True)
    type_id = Column(Integer, ForeignKey('qso_types.id'), nullable=True)
    callsign = Column(Unicode(64))
    callsign_entity = relation(CallsignEntity)
    qso_type = relation(QsoType)
    variables = relationship("QsoVariable", backref="qsos")
    date = Column(Date)
    utc_time = Column(Time)
    rst_sent = Column(Unicode(64))
    rst_received = Column(Unicode(64))
    name_received = Column(Unicode(64))                                                                                                                                                         
    qth_received = Column(Unicode(64))                                                                                                                                                          
    text_note = Column(Text)                                                                                                                                                                           
    export = Column(Boolean, default=True)                                                                                                                                                    

class QsoVariable(Base):
    __tablename__ = 'qso_variables'

    id = Column(Integer, primary_key=True)
    qso = relation(Qso)
    qso_id = Column(Integer, ForeignKey('qsos.id'), nullable=False)
    name = Column(Unicode(64))
    value = Column(Unicode(64))