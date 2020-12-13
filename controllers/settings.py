import tkinter as tk

class NewProject(object):
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

    def start(self):
        self._root = root = tk.Toplevel(self._container)
        root.resizable(False, False)

        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.wm_title("New Project")

        name = tk.Label(root, text="Name")
        self._project_name = ipt = tk.Entry(root)
        # todo: check if input name already exists (also observe user inputs)

        type_ = tk.Label(root, text="Type")

        self._project_type = var = tk.Variable(root)
        menu = tk.OptionMenu(root, var, *self._projects.get_project_types())

        name.grid(row=0, column=0)
        ipt.grid(row=0, column=1)

        type_.grid(row=1, column=0)
        menu.grid(row=1, column=1)

    def _on_close(self):
        self._projects.create_project(self._project_name.get(), self._project_type)
        self._root.destroy()

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


    def start(self):
        self._root = root = tk.Toplevel(self._container)
        root.resizable(False, False)

        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.wm_title("Open Project")

        name = tk.Label(root, text="Name")

        self._project_name = var = tk.Variable(root)
        menu = tk.OptionMenu(root, var, *self._projects.get_projects())

        name.grid(row=0, column=0)
        menu.grid(row=0, column=1)


    def _on_close(self):
        self._projects.open_project(self._project_name)
        self._root.destroy()