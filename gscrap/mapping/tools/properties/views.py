import tkinter as tk

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

        label = tk.Label(input_frame, text=self.property_.property_name)

        self.listbox = listbox = tk.Listbox(
            frame)

        scrollbar = tk.Scrollbar(
            input_frame,
            command=listbox.yview
        )

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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

        for idx, value in enumerate(self._model.values):
            listbox.insert(idx, value)

        listbox['yscrollcommand'] = scrollbar.set

        listbox.bind('<<ListboxSelect>>', self._on_selection)

        return frame

    def _on_selection(self, event):
        self._controller.on_value_selection(self._listbox.curselection()[0])

    def insert(self, index, value):
        self._listbox.insert(index, value)

    def remove(self, index):
        self._listbox.delete(index)