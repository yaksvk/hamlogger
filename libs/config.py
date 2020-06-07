#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A singleton persistent config object that probes/creates the application folder
in the users home directory. Also performs a commit on config dictionary 
updates.

In human terms: An auto-saving dictionary (saves on __setitem__) that inits
from a default config file provided by the application and saves to the config
file to users home dir.
"""

import json
import os

class PersistentConfig(dict):
    _instance = None

    def __new__(cls, source_path, *args, **kwargs):
        
        if cls._instance is None:
            cls._instance = super(PersistentConfig, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        
        return cls._instance

    def __init__(self, source_path, *args, **kwargs):
        
        if source_path:
            self.__source_path = source_path
        else:
            self.__source_path = ''
            
        
        if not self._initialized:
            self.__save_file = None
            self.__initialize_from_file()
            self._initialized = True

    # CUSTOM METHODS, LOADING, PROBING DIR, SAVING
    
    def get_absolute_path(self, path):
        """
        """
        if path[0] != '/':
            return os.path.join(self.__source_path, path)
        else:
            return path

    def __probe_home_dir_and_install_config(self):
        """
        determine users home directory, check if ~/.hamlogger exists, and copy a default config file to 
        this location. if possible, load custom config, if not, load default config
        """
        
        # SOME ARBITRARY STUFF, WHICH SHOULD BE FIXED
        my_dir = '.hamlogger'
        my_conf = 'config.json'
        default_config = 'config.json.default'
        
        conf_path = os.environ['HOME'] 
        conf_path = os.path.join(os.environ['HOME'], my_dir, my_conf)
        
        # if a custom user config file exists, load it instead of the default one
        if os.path.isfile(conf_path):
            with open(conf_path) as conf_file:
                input_hash = json.load(conf_file)
                self.__save_file = conf_path
                self.update(**input_hash)
        else:
            if not os.path.isfile(os.path.join(os.environ['HOME'], my_dir)):
                if not os.path.isdir(os.path.join(os.environ['HOME'], my_dir)):
                    os.makedirs(os.path.join(os.environ['HOME'], my_dir))
                
                # load defaults
                default_config = os.path.join(self.__source_path, 'libs', default_config)
                with open(default_config) as conf_file:
                    input_hash = json.load(conf_file)
                    self.update(**input_hash)
                
                with open(conf_path,'w') as out_file:
                    json.dump(input_hash, out_file)
                    self.__save_file = conf_path
        

    def __initialize_from_file(self):
        self.__probe_home_dir_and_install_config()
    
    def __save_to_file(self):
        if self.__save_file is not None:
            with open(self.__save_file,'w') as out_file:
                json.dump(dict(self), out_file, indent=4, sort_keys=True)
            
    # STANDARD DICTIONARY METHODS

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        return val

    def __setitem__(self, key, val):
        
        dict.__setitem__(self, key, val)
        self.__save_to_file()
        
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.__save_to_file()

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            super(PersistentConfig, self).__setitem__(k, v)
    
    
  
