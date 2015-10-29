#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk
from models import QsoVariable

class QsoVariablesEditor(Gtk.TreeView):
    
    def __init__(self, config, variables=None, *args, **kwargs):
        
        self.liststore = Gtk.ListStore(str, str)
        
        
        super(QsoVariablesEditor, self).__init__(model=self.liststore, *args, **kwargs)
        
        self.connect("key-press-event", self.monitor_keypress)   

        renderer_editabletext0 = Gtk.CellRendererText()
        renderer_editabletext0.set_property("editable", True)
        
        renderer_editabletext1 = Gtk.CellRendererText()
        renderer_editabletext1.set_property("editable", True)

        column_editabletext0 = Gtk.TreeViewColumn("VARIABLE NAME",
            renderer_editabletext0, text=0)
        self.append_column(column_editabletext0)
        
        renderer_editabletext0.connect("edited", self.text_edited0)
        
        column_editabletext1 = Gtk.TreeViewColumn("VARIABLE VALUE",
            renderer_editabletext1, text=1)
        self.append_column(column_editabletext1)

        renderer_editabletext1.connect("edited", self.text_edited1)

        self.connect('button-release-event', self.button_release)
        
        # CONTEXT MENU
        self.context_menu = Gtk.Menu()
        menu_item1 = Gtk.MenuItem("Delete")
        menu_item1.connect("activate", self.delete_selected_variable)
        menu_item2 = Gtk.MenuItem("Add new")
        menu_item2.connect("activate", self.add_new_variable)
        
        self.context_menu.append(menu_item1)
        self.context_menu.append(menu_item2)
        menu_item1.show()
        menu_item2.show()
         
    def text_edited0(self, widget, path, text):
        self.liststore[path][0] = text
    
    def text_edited1(self, widget, path, text):
        self.liststore[path][1] = text
        
    def button_release(self, widget, event):
        if event.button == 3:
            # if right click was pressed
            x = int(event.get_root_coords()[0])
            y = int(event.get_root_coords()[1])
            time = event.time
            
            self.context_menu.popup(None, None, lambda menu, user_data: (x, y, True), widget, 3, time)
            
    def add_new_variable(self, widget):
        self.liststore.append(["", ""])
   
    def delete_selected_variable(self, widget):
        selection = self.get_selection()
        model, treeiter = selection.get_selected()
        
        if treeiter is not None:
            model.remove(treeiter)
            
    # EVENTS
    
    # VALUE
    def monitor_keypress(self, widget, event):
        if event.state == Gdk.ModifierType.CONTROL_MASK:
            keyval = Gdk.keyval_name(event.keyval)
            
            if keyval == 'a':
                self.add_new_variable(widget)
            elif keyval == 'x':
                self.delete_selected_variable(widget)
            else:
                pass
    
    @property
    def value(self):
        output = {}
        for i in self.liststore:
            output[i[0]] = QsoVariable(i[0], i[1])
        
        return output
    
    @value.setter
    def value(self, value):
        self.liststore.clear()
        
        for key, val in value.items():
            self.liststore.append([key, val.value])
       
