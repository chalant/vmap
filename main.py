import tkinter as tk

from gscrap.mapping import controller as ctl

from gscrap.projects import projects as pj

from gscrap.data import data

data.build() #build data

# FONT = ("Mono", 11)

class WindowManager(object):
    #manages all windows
    def __init__(self):
        self._root = root = tk.Tk()
        # self._right_frame = tk.LabelFrame(self._root, width=500, height=500)
        # self._main_frame.pack()
        root.title("GMAP")

        self._container = container = tk.Frame(root)

        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._main = MainWindow(self)
        # self._root.wm_minsize(800, 500)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    @property
    def container(self):
        return self._container

    @property
    def root(self):
        return self._root

    def start(self):
        self._root.mainloop()

    def exit(self):
        self._root.quit()

    def _on_close(self):
        self._main.close()
        self._root.quit()

class MainWindow(object):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: WindowManager
        """



        self._manager = manager

        root = manager.container
        self._projects = projects = pj.Projects()
        self._mapping_controller = ctl.MappingController(projects, root)

    def _on_exit(self):
        self._manager.exit()

    def close(self):
        self._mapping_controller.stop()

#todo: add a cli so that we can run the application in either logging mode, or
# mapping mode.

MANAGER = WindowManager()

if __name__ == '__main__':
    MANAGER.start()