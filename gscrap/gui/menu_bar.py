import tkinter as tk

class MenuBar(object):
    def __init__(self):
        self._buttons = []

    def add_button(self, button):
        self._buttons.append(button)

    def render(self, container):
        frame = tk.Frame(container)

        menu_bar = tk.Frame(frame)

        for button in self._buttons:
            button.render(menu_bar).pack(side=tk.LEFT)
            self._config(button.button)

        menu_bar.pack(side=tk.TOP, anchor=tk.NW)

        return frame

    def _config(self, button):
        button.config(bd=0)