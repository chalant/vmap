import tkinter as tk

from tkinter import ttk

class PropertyView(object):
    def __init__(self, controller, model, property_):
        self.property_ = property_

        self._model = model
        self._controller = controller
        self._listbox = None

    def render(self, container):
        #todo: we need a "clear" button to un-map value from the rectangle instance.

        frame = tk.Frame(container)
        input_frame = tk.Frame(frame)
        s_frame = tk.Frame(frame)

        label = tk.Label(input_frame, text=self.property_.property_name)

        self._listbox = listbox = ttk.Combobox(
            input_frame,
            state="readonly"
        )

        # scrollbar = tk.Scrollbar(
        #     s_frame,
        #     command=listbox.yview
        # )
        #
        # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        label.grid(
            column=0,
            row=0,
            sticky=tk.NW
        )

        listbox.grid(
            column=1,
            row=0,
            sticky=tk.NW
        )

        # for idx, value in enumerate(self._model.values):
        #     listbox.insert(idx, value)

        listbox['values'] = list(self._model.values)

        # listbox['yscrollcommand'] = scrollbar.set

        listbox.bind('<<ComboboxSelected>>', self._on_selection)

        s_frame.pack()
        input_frame.pack()

        return frame

    def _on_selection(self, event):
        self._controller.on_value_selection(self._listbox.current())

    def insert(self, index, value):
        self._listbox.insert(index, value)

    def remove(self, index):
        self._listbox.delete(index)

    def clear_value(self):
        self._listbox.set('')

    def set_value(self, value):
        if value is None:
            self._listbox.set('')
        else:
            self._listbox.set(str(value))

    def get_value(self):
        self._listbox.get()