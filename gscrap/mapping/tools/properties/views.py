import tkinter as tk

class ValuesList(object):
    def __init__(self, name, controller):
        self.name = name
        self.controller = controller
        self.listbox = None

    def render(self, container):
        frame = tk.Frame(container)
        input_frame = tk.Frame(frame)

        label = tk.Label(input_frame, text=self.name)

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

        listbox['yscrollcommand'] = scrollbar.set

        listbox.bind('<<ListboxSelect>>', self.controller.on_selection)

        return frame

    def _on_selection(self, event):
        self.controller.on_selection(self.listbox.curselection()[0])

    def insert(self, index, value):
        self.listbox.insert(index, value)

    def remove(self, index):
        self.listbox.delete(index)