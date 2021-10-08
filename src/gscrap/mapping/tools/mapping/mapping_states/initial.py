from collections import defaultdict
from functools import partial

import tkinter as tk

from gscrap.projects import scenes

from gscrap.data.rectangles import rectangle_labels as rct_lbl


class Initial(object):
    def __init__(self, manager):
        '''

        Parameters
        ----------
        manager: gscrap.mapping.tools.mapping.mapping.MappingTool
        '''

        self._mapper = manager

        self._options = m = tk.Menu(manager.canvas, tearoff=False)

        self._rectangle = None
        self._rid = None
        self._clicked_rid = None
        self._text = None

        self._labels = {}

        m.add_command(label="Add Label", command=self._on_set_label)
        m.add_command(label="Remove Label", command=self._on_remove_label)
        m.add_separator()
        m.add_command(label="Edit", command=self._on_edit)
        m.add_command(label="Copy", command=self._on_clone)
        m.add_command(label="Delete", command=self._on_delete)
        m.add_separator()
        m.add_command(label="Draw", command=self._on_draw)

        m.entryconfig("Delete", state="disabled")
        m.entryconfig("Copy", state="disabled")
        m.entryconfig("Edit", state="disabled")
        m.entryconfig("Add Label", state="disabled")
        m.entryconfig("Remove Label", state="disabled")

    def on_right_click(self, event):
        mapper = self._mapper

        res = mapper.select_rectangle(event.x, event.y)
        options = self._options

        if res:
            self._mapper.selected_rectangle = res
            options.entryconfig("Copy", state="normal")
            options.entryconfig("Edit", state="normal")
            options.entryconfig("Delete", state="normal")
            options.entryconfig("Add Label", state="normal")

            if res != self._clicked_rid:
                options.entryconfig("Remove Label", state="disabled")
                rct = mapper.get_rectangle(res)
                # load labels
                labels = mapper.get_rectangle_labels(rct.rectangle)

                dct = defaultdict(list)

                with scenes.connect(self._mapper.scene) as connection:
                    for label in rct_lbl.get_rectangle_labels(connection, rct.rectangle):
                        dct[label.label_type].append(label)

                #add unsaved labels
                for label in labels.get_unsaved_labels():
                    dct[label.label_type].append(label)

                self._labels = dct

                if dct.keys():
                    options.entryconfig("Remove Label", state="normal")

                self._clicked_rid = res

        else:
            options.entryconfig("Copy", state="disabled")
            options.entryconfig("Edit", state="disabled")
            options.entryconfig("Delete", state="disabled")
            options.entryconfig("Add Label", state="disabled")
            options.entryconfig("Remove Label", state="disabled")

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
        mapper = self._mapper

        canvas = mapper.canvas
        res = mapper.select_rectangle(event.x, event.y)

        if res:
            if res != self._rid:
                self._unbind()

            self._rid = res

            canvas.itemconfigure(res, outline="red")

            #todo: display all associated labels

            # rct = self._mapper.get_rectangle(res)

            # if self._text:
            #     canvas.delete(self._text)
            #
            # x0, y0, x1, y1 = rct.bbox
            #
            # x, y = round((x1 + x0)/2), y0
            #
            # self._text = canvas.create_text(x, y, text=rct.label_name)

        else:
            # if self._text:
            #     canvas.delete(self._text)
            self._unbind()

    def _on_close(self):
        pass

    def _selected_label(self, label_name, label_type):
        mapper = self._mapper

        rct = mapper.get_rectangle(mapper.selected_rectangle)

        labels = mapper.get_rectangle_labels(rct.rectangle)

        self._labels[label_type].append(labels.add_label(label_name, label_type))

    def _on_set_label(self):
        scene = self._mapper.scene

        x, y = self._clicked

        self._label_types_menu = types = tk.Menu(self._mapper.canvas, tearoff=False)
        types.tk_popup(x, y)

        selected = self._selected_label

        dct = self._labels

        with scene.connect() as connection:
            for lt in scene.get_label_types(connection):
                lbm = tk.Menu(types, tearoff=False)
                types.add_cascade(label=lt, menu=lbm)

                assigned = set(label.label_name for label in dct[lt])
                names = set(lb["label_name"] for lb in scene.get_labels_of_type(connection, lt))

                #only display unassigned labels
                for lb in names.difference(assigned):
                    lbm.add_command(
                        label=lb,
                        command=partial(selected, lb, lt))

    def _on_remove_label(self):
        mapper = self._mapper
        types_menu = tk.Menu(mapper.canvas, tearoff=False)

        dct = self._labels

        for type_ in dct.keys():
            labels = dct[type_]
            class_menu = tk.Menu(types_menu, tearoff=False)
            if labels:
                types_menu.add_cascade(label=type_, menu=class_menu)

                for label in labels:
                    class_menu.add_command(
                        label=label.label_name,
                        command=partial(self._remove_label, label))

        x, y = self._clicked

        types_menu.tk_popup(x, y)

    def _remove_label(self, label):
        with scenes.connect(self._mapper.scene) as connection:
            label.delete(connection)

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