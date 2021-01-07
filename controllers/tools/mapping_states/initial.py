from functools import partial

import tkinter as tk

class Initial(object):
    def __init__(self, manager):
        '''

        Parameters
        ----------
        manager: controllers.tools.mapping.MappingTool
        '''

        self._manager = manager

        self._options = m = tk.Menu(self._manager.canvas, tearoff=False)

        self._rectangle = None

        m.add_command(label="Set Label", command=self._on_set_label)
        m.add_command(label="Edit", command=self._on_edit)
        m.add_command(label="Copy", command=self._on_clone)
        m.add_command(label="Delete", command=self._on_delete)
        m.add_separator()
        m.add_command(label="Draw", command=self._on_draw)

        m.entryconfig("Delete", state="disabled")
        m.entryconfig("Copy", state="disabled")
        m.entryconfig("Edit", state="disabled")
        m.entryconfig("Set Label", state="disabled")

    def on_right_click(self, event):
        #todo:
        # when we clone a rectangle, we also clone its components.
        # components positions can be updated
        res = self._manager.select_rectangle(event.x, event.y)
        options = self._options

        if res:
            options.entryconfig("Copy", state="normal")
            options.entryconfig("Edit", state="normal")
            options.entryconfig("Delete", state="normal")
            options.entryconfig("Set Label", state="normal")
        else:
            options.entryconfig("Copy", state="disabled")
            options.entryconfig("Edit", state="disabled")
            options.entryconfig("Delete", state="disabled")
            options.entryconfig("Set Label", state="disabled")

        options.tk_popup(event.x_root, event.y_root)

    def _on_close(self):
        self._root.destroy()

    def _selected_label(self, label_id):
        # set label id
        self._manager.rectangle.label_id = label_id

    def _on_set_label(self):
        self._root = root = tk.Toplevel(self._manager.canvas)
        root.wm_title("Set Label")

        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._label_menu = types = tk.Menu(root)
        self._selected = selected = tk.Label(root)

        lbt = tk.Menu(root)

        types.add_cascade(label="Label Types", menu=lbt)

        rectangles = self._manager.rectangles

        for lt in rectangles.get_label_types():
            lbm = tk.Menu(root)
            lbt.add_cascade(label=lt, menu=lbm)

            for lb in rectangles.get_labels_of_type(lt):
                lbm.add_command(
                    label=lb["label_name"],
                    command=partial(self._selected_label, lb["label_id"]))

        selected.grid(column=0, row=0)
        types.grid(column=1, row=0)

    def _on_draw(self):
        self._manager.state = self._manager.drawing

    def _on_edit(self):
        self._manager.state = self._manager.editing

    def _on_clone(self):
        self._manager.state = self._manager.cloning
        self._manager.cloned = self._manager.selected_rectangle()

    def _on_delete(self):
        self._manager.remove_rectangle(self._manager.selected_rectangle())

    def update(self):
        # self._mapper.canvas.bind("Button-1")
        options = self._options
        options.entryconfig("Delete", state="disabled")
        options.entryconfig("Copy", state="disabled")
        options.entryconfig("Edit", state="disabled")