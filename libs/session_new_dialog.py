#!/usr/bin/env python

from gi.repository import Gtk

class NewSessionDialog(Gtk.Dialog):

    def __init__(self, parent):
        
        
        Gtk.Dialog.__init__(
            self, 
            "Create New Session", 
            parent,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        self.set_default_size(
            parent.config['EDIT_QSO_SESSION_WIDTH'], 
            parent.config['EDIT_QSO_SESSION_HEIGHT']
        )
        
      

        box = self.get_content_area()
      
        self.widgets = {}
        label1 = Gtk.Label()
        label1.set_markup("<b>Description (short):</b>")
        self.widgets['description'] = Gtk.Entry(max_width_chars=64, width_chars=64)
        
        box.pack_start(label1, False, True, 0)
        box.pack_start(self.widgets['description'], False, True, 0)
         
        label2 = Gtk.Label()
        label2.set_markup("<b>Locator:</b>")
        self.widgets['locator'] = Gtk.Entry(max_width_chars=8, width_chars=8)
        
        box.pack_start(label2, False, True, 0)
        box.pack_start(self.widgets['locator'], False, True, 0)
        
        label3 = Gtk.Label()
        label3.set_markup("<b>About Session (Note):</b>")
        self.widgets['text_note'] = Gtk.TextView()
       
        box.pack_start(label3, False, True, 0)
        box.pack_start(self.widgets['text_note'], True, True, 0)
        
        self.widgets['activate_session'] =  Gtk.CheckButton(label="activate session",active=True)
        box.pack_start(self.widgets['activate_session'], False, True, 0)
        
        self.show_all()
        
        
