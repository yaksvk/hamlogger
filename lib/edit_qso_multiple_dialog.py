#!/usr/bin/env python

from gi.repository import Gtk
from .widgets.qso_variables_editor import QsoVariablesEditor
from .models import QsoVariable

class EditQsoMultipleDialog(Gtk.Dialog):

    def __init__(self, parent):
        
        
        Gtk.Dialog.__init__(
            self, 
            "Edit Multiple QSOs", 
            parent,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        self.set_default_size(
            parent.config['EDIT_QSO_WIDTH'], 
            parent.config['EDIT_QSO_HEIGHT']
        )
        
        # get QSO to edit
        
        common_variables = {}
        common_variables_count = {}
        
        for qso in parent.editing_qsos:
            for variable in qso.variables.values():
                if variable.name in common_variables:
                    if variable.value == common_variables[variable.name]:
                        common_variables_count[variable.name] += 1
                else:
                    common_variables[variable.name] = variable.value
                    common_variables_count[variable.name] = 1
        
        result_variables = dict(map(lambda x: (x[0], QsoVariable(x[0], x[1])), filter(lambda item: common_variables_count.get(item[0], 0) == len(parent.editing_qsos), common_variables.items())))
        

        # TODO

        # FIRST CHECK IF QSO VARIABLES ARE NOT MESSED UP!!!
        # 1. get all QSOs in selection
        # 2. get the common variable values and cache them (user will be able to delete those)
        box = self.get_content_area()
        vbox = Gtk.VBox(False, 2)
        
        
         # PREPARE FOR ALL THE WIDGETS
        self.widgets = {}
        
        label_h4 = Gtk.Label()
        label_h4.set_markup("<b>QSO VARIABLES:</b>")
        self.qso_variables = QsoVariablesEditor(parent.config)
        self.qso_variables.value = result_variables

        vbox.pack_start(self.qso_variables, True, True, 0)
        #if self.found_qso.variables:
        box.pack_start(vbox, True, True, 0)
        #    self.qso_variables.value = self.found_qso.variables
        
        self.show_all()
        
        
