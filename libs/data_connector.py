#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import Base, CallsignEntity, QsoType, Qso, QsoVariable
from models import probe_models_and_create_session

class DataConnector():
    
    def __init__(self, db_file):
        
        self.session = probe_models_and_create_session(db_file)
    
    def commit(self):
        self.session.commit()

