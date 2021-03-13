import tkinter as tk

from controllers import main_frame

FONT = ("Mono", 11)

class WindowManager(object):
    #manages all windows
    def __init__(self):
        self._root = tk.Tk()
        # self._right_frame = tk.LabelFrame(self._root, width=500, height=500)
        # self._main_frame.pack()
        self._root.title("GMAP")
        self._container = tk.Frame(self._root)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)
        self._main = MainWindow(self)
        # self._root.wm_minsize(800, 500)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    @property
    def container(self):
        return self._container

    @property
    def master(self):
        return self._root

    def start(self):
        self._root.mainloop()

    def exit(self):
        self._root.quit()

    def _on_close(self):
        self._main.close()
        self._root.quit()

#todo: need a better approach for handling saving when changes occurs...
# pass-in a callback?
class MainWindow(object):
    # window for main information about the game
    # contains capture states, filling forms etc.
    # also handles opening and closing files
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: WindowManager
        """

        self._manager = manager

        self._main_frame = main_frame.MainFrame(manager, self._manager.master)

        self._updated = False
        # self._img_events.start()

    def _on_exit(self):
        self._manager.exit()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def height(self):
        return self._main_frame.w_height

    def close(self):
        self._main_frame.stop()

MANAGER = WindowManager()

if __name__ == '__main__':
    MANAGER.start()