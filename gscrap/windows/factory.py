import tkinter as tk

class WindowFactory(object):
    def create(self, x, y, canvas, element):
        return canvas.create_window(
            x, y,
            window=element.render(canvas),
            anchor=tk.NW)


class Item(object):
    def render(self, container):
        pass
