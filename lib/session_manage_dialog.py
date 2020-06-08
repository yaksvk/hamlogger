#!/usr/bin/env python

from gi.repository import Gtk

class ManageSessionDialog(Gtk.Dialog):

    def __init__(self, parent):
        
        
        Gtk.Dialog.__init__(
            self, 
            "Create New Session", 
            parent,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        self.set_default_size(
            parent.config['EDIT_QSO_WIDTH'], 
            parent.config['EDIT_QSO_HEIGHT']
        )
        
      

        box = self.get_content_area()
      
        # add elements here - TODO
       
        
        self.show_all()
        
        
