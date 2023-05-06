#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy import *
from sqlalchemy.orm import relation, sessionmaker, relationship

import re
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
    qsos = relationship("Qso", backref="callsigns", viewonly=True)
    text_note = Column(UnicodeText)

    @classmethod
    def get_base_callsign(myclass, callsign_text):
        """get base callsign for complicated types like mobile, portable or CEPT calls"""
        clean_sign = re.sub('(/p|/m|/mm|/am|/qrp|/\d)?$', '', callsign_text, flags=re.IGNORECASE)
        clean_sign = re.sub('(/p|/m|/mm|/am|/qrp|/\d)?$', '', clean_sign, flags=re.IGNORECASE)
        clean_sign = re.sub('^[^/]+/', '', clean_sign, flags=re.IGNORECASE)

        return clean_sign

    def __repr__(self):
        return ''.join((str(self.id), ':', self.callsign))

    @property
    def qso_count(self):
        return len(self.qsos)


class QsoType(Base):
    __tablename__ = 'qso_types'

    id = Column(Integer, primary_key=True)
    description = Column(Unicode(64))
    qsos = relationship("Qso", backref="qso_types", viewonly=True)


class QsoSession(Base):
    __tablename__ = 'qso_sessions'

    id = Column(Integer, primary_key=True)
    description = Column(Unicode(64))
    text_note = Column(UnicodeText)
    locator = Column(Unicode(8))
    qsos = relationship("Qso", backref="qso_sessions", viewonly=True)


class Qso(Base):
    __tablename__ = 'qsos'

    id = Column(Integer, primary_key=True)
    callsign_id = Column(Integer, ForeignKey('callsigns.id'), nullable=True)
    type_id = Column(Integer, ForeignKey('qso_types.id'), nullable=True)
    session_id = Column(Integer, ForeignKey('qso_sessions.id'), nullable=True)
    callsign = Column(Unicode(64))
    callsign_entity = relation(CallsignEntity)
    qso_type = relation(QsoType)
    qso_session = relation(QsoSession)
    _variables = relationship("QsoVariable",
        collection_class=attribute_mapped_collection('name'),
        cascade="all, delete-orphan",
        backref="qsos")

    # use variables as a proxy so that it behaves transparently as a hash
    variables = association_proxy('_variables','value',
        creator=lambda k, v: QsoVariable(name=k, value=v))
    datetime_utc = Column(DateTime)
    frequency = Column(Unicode(8))
    mode = Column(Unicode(8))
    rst_sent = Column(Unicode(64))
    rst_received = Column(Unicode(64))
    name_received = Column(Unicode(64))
    qth_received = Column(Unicode(64))
    country_received = Column(Unicode(64))
    text_note = Column(UnicodeText)
    export = Column(Boolean, default=True)
    qsl_sent = Column(Boolean, default=False)
    qsl_received = Column(Boolean, default=False)

    def __repr__(self):
        return ''.join((self.callsign, ' ', self.datetime_utc.isoformat()))

    @property
    def time_iso(self):
        if self.datetime_utc is not None:
            return self.datetime_utc.time().isoformat()[:5]
        else:
            return None
    @property
    def date_iso(self):
        if self.datetime_utc is not None:
            return self.datetime_utc.date().isoformat()
        else:
            return None


class QsoVariable(Base):
    __tablename__ = 'qso_variables'

    id = Column(Integer, primary_key=True)
    qso = relation(Qso, viewonly=True)
    qso_id = Column(Integer, ForeignKey('qsos.id'), nullable=False)
    name = Column(Unicode(64))
    value = Column(Unicode(64))

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return ''.join(('QsoVariable(\'', self.name, '\', \'', self.value, '\')'))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.name == other.name ) and (self.value == other.value)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not (self == other)
        return NotImplemented

    def __hash__(self):
        return hash(self.name)
