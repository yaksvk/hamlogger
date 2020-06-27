#!/usr/bin/env python

from gi.repository import Gtk

class ExportSotaChaserDialog(Gtk.Dialog):

    def __init__(self, parent, chase_qsos):

        self.chase_qsos = chase_qsos
        
        
        Gtk.Dialog.__init__(
            self, 
            "Export SOTA Chaser CSV", 
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
        label1.set_markup("<b>Select chase QSOs</b>")
        
        box.pack_start(label1, False, True, 0)

        swp = Gtk.ScrolledWindow()
        swp.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        swp.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        box.pack_start(swp, True, True, 0)
         
        self.sota_activation_store = self.tree_data_create_model()
        
        treeView_p = Gtk.TreeView(self.sota_activation_store)
        #treeView_p.connect('button-press-event', self.tree_click)
        #treeView_p.connect('button-release-event', self.current_log_keyrelease)
        
        swp.add(treeView_p)
        
        self.sota_activation_scroll_window = swp
        self.sota_activation_tree = treeView_p
        
        self.tree_data_create_columns(treeView_p)
        
        self.show_all()

        self.refresh_main_tree()

        self.selection = self.sota_activation_tree.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)

    def tree_data_create_model(self):
        store = Gtk.ListStore(int, str, str, str, str, str, str, str)
        return store
        
    def tree_data_create_columns(self, treeView):
   
        columns = ['ID', 'DATE', 'UTC', 'FREQ', 'MODE', 'CALL', 'SUMMIT_RECEIVED', 'SUMMIT_SENT']

        for i, column in enumerate(columns):
            rendererText = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(column, rendererText, text=i)
            col.set_sort_column_id(i)  
            
            treeView.append_column(col)

    def refresh_main_tree(self):
        

        self.sota_activation_store = self.tree_data_create_model()
        self.sota_activation_tree.set_model(self.sota_activation_store)

        for qso in self.chase_qsos:
            #print(''.join(map(lambda x: str(x), activation)))
            summit_received = qso.variables['SUMMIT_RECEIVED'] if 'SUMMIT_RECEIVED' in qso.variables else ''
            summit_sent = qso.variables['SUMMIT_RECEIVED'] if 'SUMMIT_RECEIVED' in qso.variables else ''

            self.sota_activation_store.append(
                  (
                      qso.id,
                      qso.datetime_utc.date().isoformat(), 
                      qso.datetime_utc.time().isoformat()[:5], 
                      qso.frequency,
                      qso.mode, 
                      qso.callsign,
                      summit_received[:15],
                      summit_sent[:15]
                  )
            )

