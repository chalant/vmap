import os

import tkinter as tk

from gscrap.mapping import controller as ctl

from gscrap.tools import window_selection as ws


# FONT = ("Mono", 11)

class WindowManager(object):
    #manages all windows
    def __init__(self):
        self._root = None
        self._main = None
        self._container = None

    @property
    def container(self):
        return self._container

    @property
    def root(self):
        return self._root

    def start(self, project):
        self._root = root = tk.Tk()
        root.title("GMAP")

        self._container = container = tk.Frame(root)

        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # self._root.wm_minsize(800, 500)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._main = MainWindow(self, project)
        self._root.mainloop()

    def exit(self):
        self._root.quit()

    def _on_close(self):
        self._main.close()
        self._root.quit()
        self._root.destroy()

class MainWindow(object):
    def __init__(self, manager, project):
        """
        Parameters
        ----------
        manager: WindowManager
        """

        self._manager = manager

        root = manager.container

        self._mapping_controller = ctl.MappingController(
            project,
            root,
            ws.WindowSelector(manager.root))

    def _on_exit(self):
        self._manager.exit()

    def close(self):
        self._mapping_controller.stop()

MANAGER = WindowManager()