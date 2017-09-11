#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk

class RstEntry(Gtk.Entry):

    default_mode = 'RS'
    default_values = {
        'RS': {'max': 9, 'place': 1, 'default': '59'},
        'RST': {'max': 9, 'place': 1, 'default': '599'}
    }
    
    def __init__(self, *args, **kwargs):
        super(RstEntry, self).__init__(*args, **kwargs)
        self.connect("key-press-event", self.__entry_keypress)
        
        self.mode = kwargs.get('mode', self.default_mode)
        if self.mode not in self.default_values.keys():
            self.mode = self.default_mode

    def __getmax(self):
        return self.default_values[self.mode]['max']
    
    def __getplace(self):
        return self.default_values[self.mode]['place']

    def __value_step(self, increment):
        val = self.get_text()

        if val:
            pos = self.__getplace()
            if len(val) >= pos:
                try:
                    x = int(val[pos])
                except:
                    x = 0
            x += increment 
            if x < 0:
                x = 0
            elif x > self.__getmax():
                x = self.__getmax()

            splat = list(val)
            splat[pos] = str(x)
            val = ''.join(splat)

            self.set_text(val)

    def __entry_keypress(self, widget, event):
        if event.keyval in (65451,65453):
            # prevent text from being entered
            self.emit_stop_by_name("key-press-event")

            if event.keyval == 65451:
                self.__value_step(1)
            elif event.keyval == 65453:
                self.__value_step(-1)

    def set_mode(self, val):
        if val in self.default_values.keys():
            self.default_mode = val
    
    def set_default(self):
        self.set_text(self.default_values[self.default_mode]['default'])
        
         

