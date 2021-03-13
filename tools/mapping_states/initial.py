from functools import partial

import tkinter as tk

from data import engine

class Initial(object):
    def __init__(self, manager):
        '''

        Parameters
        ----------
        manager: controllers.tools.mapping.MappingTool
        '''

        self._mapper = manager

        self._options = m = tk.Menu(self._mapper.canvas, tearoff=False)

        self._rectangle = None
        self._rid = None
        self._text = None

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
        res = self._mapper.select_rectangle(event.x, event.y)
        options = self._options

        if res:
            self._mapper.selected_rectangle = res
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

        self._clicked = event.x_root, event.y_root

        if self._text:
            self._mapper.canvas.delete(self._text)

    def _unbind(self):
        prev = self._rid

        if prev:
            canvas = self._mapper.canvas
            canvas.itemconfigure(prev, outline="black")

            self._rid = None

    def on_motion(self, event):
        canvas = self._mapper.canvas
        res = self._mapper.select_rectangle(event.x, event.y)

        if res:
            if res != self._rid:
                self._unbind()

            self._rid = res

            canvas.itemconfigure(res, outline="red")
            rct = self._mapper.get_rectangle(res)

            if self._text:
                canvas.delete(self._text)

            x0, y0, x1, y1 = rct.bbox

            x, y = round((x1 + x0)/2), y0

            self._text = canvas.create_text(x, y, text=rct.label_name)

        else:
            if self._text:
                canvas.delete(self._text)
            self._unbind()

    def _on_close(self):
        pass

    def _selected_label(self, label):
        rct = self._mapper.get_rectangle(self._mapper.selected_rectangle)

        rct.label_name = label["label_name"]
        rct.label_type = label["label_type"]

    def _on_set_label(self):
        project = self._mapper.project

        self._label_types_menu = types = tk.Menu(self._mapper.canvas, tearoff=False)
        types.tk_popup(self._clicked[0], self._clicked[1])

        with engine.connect() as connection:
            for lt in project.get_label_types(connection):
                lbm = tk.Menu(types, tearoff=False)
                types.add_cascade(label=lt, menu=lbm)

                for lb in project.get_labels_of_type(connection, lt):
                    name = lb["label_name"]
                    lbm.add_command(
                        label=name,
                        command=partial(self._selected_label, lb))

    def _on_draw(self):
        self._mapper.state = self._mapper.drawing

    def _on_edit(self):
        self._mapper.state = self._mapper.editing

    def _on_clone(self):
        self._mapper.state = self._mapper.cloning

    def _on_delete(self):
        self._mapper.remove_rectangle(self._mapper.selected_rectangle)

    def update(self):
        # self._mapper.canvas.bind("Button-1")
        options = self._options
        options.entryconfig("Delete", state="disabled")
        options.entryconfig("Copy", state="disabled")
        options.entryconfig("Edit", state="disabled")