#!/usr/bin/env python

import os
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from . import prefix_resolver
from . import main_window
from . import data_connector

class HamLogger(Gtk.Application):

    def __init__(self, config, *args, **kwargs):
        super(HamLogger, self).__init__(*args, **kwargs)

        # initialize DXCC prefix resolver
        self.resolver = prefix_resolver.Resolver(config.get_absolute_path(config['PREFIX_FILE']))

        # create a db handle, this will be handled by our intelligent connector
        if not config.get('DB_FILE', ''):
            config['DB_FILE'] = os.path.join(os.environ['HOME'], '.hamlogger', 'log.sqlite')

        self.db_handle = data_connector.DataConnector(config['DB_FILE'])

        # save the config as my attribute
        self.config = config

    def do_activate(self):

        # create the main window and send it a reference to the config module
        window = main_window.MainWindow(application=self, config=self.config, db=self.db_handle, resolver=self.resolver)
        window.set_title(self.config['APPLICATION_NAME'])
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_icon_from_file(self.config.get_absolute_path('icons/application.png'))
        window.show_all()
