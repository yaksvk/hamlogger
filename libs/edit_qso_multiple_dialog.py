#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from qso_variables_editor import QsoVariablesEditor

class EditQsoMultipleDialog(Gtk.Dialog):

    def __init__(self, parent):
        
        
        Gtk.Dialog.__init__(
            self, 
            "Edit QSO", 
            parent,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        self.set_default_size(
            parent.config['EDIT_QSO_WIDTH'], 
            parent.config['EDIT_QSO_HEIGHT']
        )
        
        # get QSO to edit
        
        self.found_qsos = parent.db.get_qsos_by_ids(id_list=parent.editing_qso_ids)
        
        self.show_all()
        
        
