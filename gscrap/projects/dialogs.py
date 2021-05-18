import tkinter as tk

from gscrap.data import engine


class NewProject(object):
    # todo: add Cancel Button
    def __init__(self, container, projects):
        """

        Parameters
        ----------
        container
        projects: models.projects.Projects
        controller
        """
        self._container = container
        self._projects = projects

        self._root = None
        self._project_name = None
        self._project_type = None

    def start(self):
        self._root = root = tk.Toplevel(self._container)

        # root.update()
        root.attributes('-topmost', 'true')
        root.grab_set()
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self._close)
        root.wm_title("New Project")

        rx = self._container.winfo_rootx()
        ry = self._container.winfo_rooty()

        w = 300
        h = 100

        root.geometry("{}x{}+{}+{}".format(w, h, rx + w, ry + h))

        name = tk.Label(root, text="Name")

        self._input = tk.StringVar(root)
        self._project_name = ipt = tk.Entry(root, textvariable=self._input)

        self._input.trace_add("write", self._on_input)

        # todo: check if input name already exists (also observe user inputs)

        type_ = tk.Label(root, text="Type")

        self._project_type = var = tk.Variable(root)
        var.trace_add("write", self._on_input)

        with engine.connect() as connection:
            menu = tk.OptionMenu(
                root,
                var,
                *self._projects.get_project_types(connection))

            menu["width"] = 15

            self._project_names = {
                pj for pj in
                self._projects.get_project_names(connection)
            }

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
        slc = self._project_type.get()

        if ipt not in self._project_names:
            if ipt and slc:
                self._done_btn["state"] = "normal"
            else:
                self._done_btn["state"] = "disabled"

    def _close(self):
        self._root.grab_release()
        self._root.destroy()

    def _on_done(self):
        self._projects.create_project(
            self._project_name.get(),
            self._project_type.get())
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

    def start(self):
        self._root = root = tk.Toplevel(self._container)

        root.attributes('-topmost', 'true')
        root.grab_set()
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.wm_title("Open Project")

        rx = self._container.winfo_rootx()
        ry = self._container.winfo_rooty()

        w = 300
        h = 100

        root.geometry("{}x{}+{}+{}".format(w, h, rx + w, ry + h))

        self._project_name = var = tk.Variable(root)

        var.trace_add("write", self._on_input)

        with engine.connect() as connection:
            self._slc_frame = slc_frame = tk.Frame(root)

            # name = tk.Label(slc_frame, text="Project")

            menu = tk.OptionMenu(
                slc_frame,
                var,
                *self._projects.get_project_names(connection))

            menu["width"] = 15

            self._btn_frame = btn_frame = tk.Frame(root)

            self._done_btn = done_btn = tk.Button(
                btn_frame,
                text="Done",
                state="disabled",
                command=self._on_done)

            self._cancel_btn = cancel_btn = tk.Button(
                btn_frame,
                text="Cancel",
                state="normal",
                command=self._on_close
            )

            slc_frame.pack()

            # name.pack(side=tk.LEFT)
            menu.pack(side=tk.LEFT)

            btn_frame.pack()

            cancel_btn.pack(side=tk.LEFT)
            done_btn.pack(side=tk.LEFT)

    def _on_done(self):
        selection = self._project_name.get()
        if selection:
            self._projects.open_project(selection)
        self._on_close()

    def _on_close(self):
        self._root.grab_release()
        self._root.destroy()

    def _on_input(self, t, evt, b):
        slc = self._project_name.get()
        if slc:
            self._done_btn["state"] = "normal"
        else:
            self._done_btn["state"] = "disabled"