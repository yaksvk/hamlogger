#!/usr/bin/env python

from gi.repository import Gtk

class ExportWwffDialog(Gtk.Dialog):

    def __init__(self, parent, activations):

        self.activations = activations

        Gtk.Dialog.__init__(
            self,
            "Export WWFF ADIF",
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
        label1.set_markup("<b>Select activations</b>")

        box.pack_start(label1, False, True, 0)

        swp = Gtk.ScrolledWindow()
        swp.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        swp.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        box.pack_start(swp, True, True, 0)

        self.wwff_activation_store = self.tree_data_create_model()

        treeView_p = Gtk.TreeView(self.wwff_activation_store)

        swp.add(treeView_p)

        self.wwff_activation_scroll_window = swp
        self.wwff_activation_tree = treeView_p

        self.tree_data_create_columns(treeView_p)

        self.show_all()

        self.refresh_main_tree()

        self.selection = self.wwff_activation_tree.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)

    def tree_data_create_model(self):
        store = Gtk.ListStore(str, int, str)
        return store

    def tree_data_create_columns(self, treeView):

        columns = ['REFERENCE', 'COUNT', 'DATE']

        for i, column in enumerate(columns):
            rendererText = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(column, rendererText, text=i)
            col.set_sort_column_id(i)
            treeView.append_column(col)

    def refresh_main_tree(self):

        self.wwff_activation_store = self.tree_data_create_model()
        self.wwff_activation_tree.set_model(self.wwff_activation_store)

        for activation in self.activations:
            self.wwff_activation_store.append(
                (
                    activation[2],
                    activation[0],
                    activation[1]
                )
            )
