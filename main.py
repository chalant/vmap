import tkinter as tk
from tkinter import filedialog

from controllers import main_frame
from controllers import display

from models import images
from models import rectangles

from data import interface as itf

PATH = 'poker_table.png'
FONT = ("Mono", 11)

class WindowManager(object):
    #manages all windows
    def __init__(self):
        self._root = tk.Tk()
        self.image_path = PATH
        # self._right_frame = tk.LabelFrame(self._root, width=500, height=500)
        # self.main_frame.pack()
        self._root.title("Image Mapper")
        self._master = self._root
        self._container = tk.Frame(self._root)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)
        self._main = MainWindow(self)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    @property
    def container(self):
        return self._container

    @property
    def master(self):
        return self._master

    def start(self):
        self._root.mainloop()

    def exit(self):
        self._root.quit()

    def _on_close(self):
        self._main.close()
        self._root.quit()

class MainWindow(object):
    # window for main information about the game
    # contains capture tools, filling forms etc.
    # also handles opening and closing files
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: WindowManager
        """

        self._manager = manager

        self.file_selection = FileSelection(self)

        bar = tk.Menu(manager.master)
        manager.master.config(menu=bar)
        file_menu = tk.Menu(bar)
        bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._new)
        file_menu.add_command(label="Open", command=self._open)
        file_menu.add_command(label="Save", command=self._save)
        file_menu.add_command(label="Exit", command=manager.exit)

        right_frame = tk.LabelFrame(manager.container, text="Data")
        right_frame.grid(row=0, column=1, sticky="wens")

        self._interface = itf.Interface(right_frame, 1, self)

        r = 4/3
        mf = tk.Frame(manager.container, width=800, height=800/r)
        mf.grid(row=0, column=0, sticky="wens")
        mf.grid_propagate(0)

        self._view = main_frame.MainFrame(mf, self._manager.master, rectangles.Rectangles())

        self._updated_dict = {}
        self._updated = False
        # self._img_events.start()

    def _maybe_save(self):
        if self._updated == True:
            #todo: display message box to confirm saving changes
            # wait for user input, then call save or not
            pass

    def on_updated(self, component):
        #tracks components changes
        self._updated = True
        self._updated_dict[component.id] = component

    def update(self):
        # update from buffer
        pass

    def _save(self):
        for c in self._updated_dict.values():
            c.save(self._path)
        self._updated = False #reset updated

    def _new(self):
        self._maybe_save()
        #todo: reset everything

    def _open(self):
        self._maybe_save()
        # todo: open file dialog

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def close(self):
        self._view.close()

class FileSelection(object):
    #when we're main an existing
    # session (image + mappings)
    def __init__(self, manager):
        self._manager = manager

    def update(self):
        #pop file manager and open what we need. => move to TableMapping state
        filedialog.askdirectory()

MANAGER = WindowManager()

if __name__ == '__main__':
    MANAGER.start()