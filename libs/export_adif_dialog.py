#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class ExportAdifDialog(Gtk.Dialog):

    def __init__(self, parent, sessions):

        self.sessions = sessions
        
        Gtk.Dialog.__init__(
            self, 
            "Export Adif", 
            parent,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )

        self.set_default_size(
            parent.config['SOTA_EXPORT_WIDTH'], 
            parent.config['SOTA_EXPORT_HEIGHT']
        )

        box = self.get_content_area()
      
        self.widgets = {}
        label1 = Gtk.Label()
        label1.set_markup("<b>Select sesssions</b>")
        
        box.pack_start(label1, False, True, 0)

        swp = Gtk.ScrolledWindow()
        swp.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        swp.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        box.pack_start(swp, True, True, 0)
         
        self.session_store = self.tree_data_create_model()
        
        treeView_p = Gtk.TreeView(self.session_store)
        #treeView_p.connect('button-press-event', self.tree_click)
        #treeView_p.connect('button-release-event', self.current_log_keyrelease)
        
        swp.add(treeView_p)
        
        self.session_scroll_window = swp
        self.session_tree = treeView_p
        
        self.tree_data_create_columns(treeView_p)
        
        self.show_all()

        self.refresh_main_tree()

        self.selection = self.session_tree.get_selection()
	self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)

    def tree_data_create_model(self):
        store = Gtk.ListStore(int, int, str)
        return store
        
    def tree_data_create_columns(self, treeView):
   
        columns = ['ID', 'QSO COUNT', 'DESCRIPTION']

        for i, column in enumerate(columns):
            rendererText = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(column, rendererText, text=i)
            col.set_sort_column_id(i)  
            
            treeView.append_column(col)

    def refresh_main_tree(self):
        

        self.session_store = self.tree_data_create_model()
        self.session_tree.set_model(self.session_store)

        for session in self.sessions:
            #print(''.join(map(lambda x: str(x), activation)))
            self.session_store.append(
                (
                    session.id,
                    len(session.qsos),
                    session.description
                )
            )

