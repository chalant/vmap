import tkinter as tk

import click

from gscrap.mapping import controller as ctl

from gscrap.projects import projects

from gscrap.data import paths

from gscrap.tools import window_selection as ws

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

        self._main = None
        # self._root.wm_minsize(800, 500)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    @property
    def container(self):
        return self._container

    @property
    def root(self):
        return self._root

    def start(self, working_dir):
        self._main = MainWindow(self, working_dir)
        self._root.mainloop()

    def exit(self):
        self._root.quit()

    def _on_close(self):
        self._main.close()
        self._root.quit()

class MainWindow(object):
    def __init__(self, manager, working_dir):
        """
        Parameters
        ----------
        manager: WindowManager
        """

        self._manager = manager

        root = manager.container

        projects.set_project(working_dir)
        project = projects.get_project()

        paths.set_project(project)

        self._mapping_controller = ctl.MappingController(
            project,
            root,
            ws.WindowSelector(manager.root))

    def _on_exit(self):
        self._manager.exit()

    def close(self):
        self._mapping_controller.stop()

MANAGER = WindowManager()

@click.group()
def cli():
    pass

@cli.command()
@click.argument("directory")
def run(directory):
    MANAGER.start(directory)

if __name__ == '__main__':
    cli()