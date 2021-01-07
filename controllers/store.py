import tkinter as tk

class NewProject(object):
    # todo: add Done button and Cancel Button
    def __init__(self, container, projects):
        """

        Parameters
        ----------
        container
        projects: models.projects.Projects
        """
        self._container = container
        self._projects = projects

        self._root = None
        self._project_name = None
        self._project_type = None
        self._callback = None

    def start(self, callback):
        #todo: the window must always be displayed at the middle of the main window
        self._root = root = tk.Toplevel(self._container)
        self._callback = callback
        # root.update()
        root.attributes('-topmost', 'true')
        root.grab_set()
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self._close)
        root.wm_title("New Project")

        rx = self._container.winfo_rootx()
        ry = self._container.winfo_rooty()

        scr_w = self._container.winfo_width()

        w = 300
        h = 100

        root.geometry("{}x{}+{}+{}".format(w, h, rx - w - scr_w, ry + h))

        name = tk.Label(root, text="Name")

        self._input = tk.StringVar(root)
        self._project_name = ipt = tk.Entry(root, textvariable=self._input)

        self._input.trace_add("write", self._on_input)

        # todo: check if input name already exists (also observe user inputs)

        type_ = tk.Label(root, text="Type")

        self._project_type = var = tk.Variable(root)
        menu = tk.OptionMenu(root, var, *self._projects.get_project_types())
        menu["width"] = 15

        self._done_btn = done_btn = tk.Button(
            root,
            text="Done",
            state="disabled",
            command=self._on_done)

        done_btn.grid(row=2, column=1)

        name.grid(row=0, column=0)
        ipt.grid(row=0, column=1)

        type_.grid(row=1, column=0)
        menu.grid(row=1, column=1)

    def _on_input(self, t, evt, b):
        ipt = self._input.get()
        slc = self._project_name.get()

        if ipt and slc:
            self._done_btn["state"] = "normal"
        else:
            self._done_btn["state"] = "disable"

    def _close(self):
        self._root.grab_release()
        self._root.destroy()

    def _on_done(self):
        self._callback(self._projects.create_project(self._project_name.get(), self._project_type.get()))
        self._close()

    def _on_cancel(self):
        self._close()

class OpenProject(object):
    def __init__(self, container, projects):
        """

        Parameters
        ----------
        container
        projects: models.projects.Projects
        """
        self._container = container
        self._projects = projects

        self._root = None
        self._project_name = None
        self._callback = None

    def start(self, callback):
        self._callback = callback
        self._root = root = tk.Toplevel(self._container)
        root.resizable(False, False)

        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.wm_title("Open Project")

        name = tk.Label(root, text="Name")

        self._project_name = var = tk.Variable(root)
        menu = tk.OptionMenu(root, var, *self._projects.get_project_names())

        name.grid(row=0, column=0)
        menu.grid(row=0, column=1)

    def _on_close(self):
        self._callback(self._projects.open_project(self._project_name.get()))
        self._root.destroy()
