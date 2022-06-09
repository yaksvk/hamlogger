#!/usr/bin/env python

from gi.repository import Gtk, Gdk

class QsoVariablesEditor(Gtk.TreeView):

    def __init__(self, config, variables=None, *args, **kwargs):

        self.liststore = Gtk.ListStore(str, str, str)
        self.option_store = Gtk.ListStore(str)

        self.combo_values = config.get('QSO_VARIABLES', [])

        for combo_val in self.combo_values:
            self.option_store.append([combo_val])

        super(QsoVariablesEditor, self).__init__(model=self.liststore, *args, **kwargs)

        self.connect("key-press-event", self.monitor_keypress)

        renderer_editabletext0 = Gtk.CellRendererCombo()
        renderer_editabletext0.set_property("editable", True)
        renderer_editabletext0.set_property("model", self.option_store)
        renderer_editabletext0.set_property("text-column", 0)
        renderer_editabletext0.set_property("has-entry", True)

         # user picks a value from combo
        renderer_editabletext0.connect("changed", self.combo_changed)
        # user enters a text into box
        renderer_editabletext0.connect("edited", self.combo_edited)

        renderer_editabletext1 = Gtk.CellRendererText()
        renderer_editabletext1.set_property("editable", True)

        column_editabletext0 = Gtk.TreeViewColumn("VARIABLE NAME",
            renderer_editabletext0, text=0)
            # TODO
            #column_combo.pack_start(renderer_combo, False)
            #column_combo.add_attribute(renderer_combo, "text", 1)
        self.append_column(column_editabletext0)

        # obsolete

        column_editabletext1 = Gtk.TreeViewColumn("VARIABLE VALUE",
            renderer_editabletext1, text=1)
        renderer_editabletext1.connect("edited", self.text_edited)

        column_editabletext1.set_expand(True);
        self.append_column(column_editabletext1)

        renderer_delete_click = Gtk.CellRendererText()
        self.column_delete_click = Gtk.TreeViewColumn("",
            renderer_delete_click, text=2)

        self.column_delete_click.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.column_delete_click.set_fixed_width(20)
        self.column_delete_click.set_expand(False)

        self.append_column(self.column_delete_click)

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

    def combo_edited(self, cellrenderercombo, path, newtext):
        self.liststore[path][0] = newtext

        if newtext not in self.combo_values:
            self.combo_values.append(newtext)
            self.option_store.clear()
            for item in self.combo_values:
                self.option_store.append([item])

    def combo_changed(self, cellrenderercombo, path, treeiter):
        self.liststore[path][0] = self.option_store[treeiter][0]

    def text_edited(self, widget, path, text):
        self.liststore[path][1] = text

    def button_release(self, widget, event):
        if event.button == 1:
            # capture left button click

            # check if the delete (X) button (third column) was clicked. if yes, delete row
            selection = self.get_selection()
            model, treeiter = selection.get_selected()

            if treeiter is not None:
                res = self.get_path_at_pos(int(event.x), int(event.y))
                if res:
                    path, column = res[:2]
                    if column is self.column_delete_click:
                        model.remove(treeiter)

        if event.button == 3:
            # if right click was pressed
            x = int(event.get_root_coords()[0])
            y = int(event.get_root_coords()[1])
            time = event.time

            #self.context_menu.popup(None, None, lambda menu, user_data: (x, y, True), widget, 3, time)
            self.context_menu.popup_at_pointer()

    def add_new_variable(self, widget):
        self.liststore.append(["", "", "✗"])

    def delete_selected_variable(self, widget):
        selection = self.get_selection()
        model, treeiter = selection.get_selected()

        if treeiter is not None:
            model.remove(treeiter)

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
            output[i[0]] = i[1]

        return output

    @value.setter
    def value(self, value):
        self.liststore.clear()

        for key, val in value.items():
            self.liststore.append([key, val, "✗"])

