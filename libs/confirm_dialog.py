#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class ConfirmDialog(Gtk.Dialog):

    def __init__(self, parent):
        
        
        Gtk.Dialog.__init__(
            self, 
            "Confirm action", 
            parent,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        self.set_default_size(
            400,
            200
        )
        
        box = self.get_content_area()
        
        question_label = Gtk.Label()
        question_label.set_markup("Really do this?")
       
        box.pack_start(question_label, False, True, 0)
        
        self.show_all()