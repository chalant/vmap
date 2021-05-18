import tkinter as tk

from gscrap.data import engine
from gscrap.projects import dialogs


class Interface(object):
    def __init__(self, container, manager, projects):
        """
        Parameters
        ----------
        container
        manager: controllers.main_frame.MainFrame
        projects: models.projects.Projects
        """

        self._container = container

        self._manager = manager
        self._projects = projects

        self._new_btn = None
        self._save_btn = None
        self._load_btn = None

        self._input = None
        self._entry = None

        self._project = None

        self._changed = False

    def save(self):
        pass

    def update_template(self, width, height, img=None):
        pj = self._project

        pj.width = width
        pj.height = height
        pj.store_template(img)

        with engine.connect() as connection:
            pj.save(connection)

        # self._save_btn["state"] = "normal"

    def _on_input(self, t, evt, b):
        ipt = self._input.get()
        slc = self._selection.get()

        if ipt and slc != "n/a":
            self._save_btn["state"] = "normal"
        else:
            self._save_btn["state"] = "disable"

    def _on_new(self):
        # with engine.connect() as connection:
        #     # if self._changed and self._project:
        #     #     # todo: display save message
        #     #     self._project.save(connection)
        #     # self._changed = False
        self._new_project.start(self._initialize)

    def _initialize(self, project):
        self._manager.bind_window(project)

        # self._input.set(project.name)
        # self._selection.set(project.project_type)

        project.on_update(self._update)

        self._project = project

        self._changed = False

    def _update(self, rectangles):
        # self._save_btn["state"] = "normal"
        self._manager.update(rectangles)
        self._changed = True

    def _on_load(self):
        self._open_project.start(self._initialize)

    def _on_save(self):
        #todo: cannot save project with no name
        self._load_btn["state"] = "normal"

class MenuBarController(object):
    def __init__(self, menu_bar, projects):
        self._menu_bar = menu_bar
        self._projects = projects

    def open(self):
        self._menu_bar.open_dialog.start()

    def new(self):
        self._menu_bar.new_dialog.start()

class MenuBar(object):
    def __init__(self, root, controller, projects):

        self.menu_bar = menu = tk.Menu(root, tearoff=False)

        tp = root.winfo_toplevel()
        tp.config(menu=menu)

        self.open_dialog = dialogs.OpenProject(menu, projects)
        self.new_dialog = dialogs.NewProject(menu, projects)

        self.file_menu = file_menu = tk.Menu(menu, tearoff=False)

        menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="New", command=controller.new_project)

        file_menu.add_command(label="Open", command=controller.open_project)
        file_menu.entryconfig("Open", state=tk.DISABLED)

        with engine.connect() as connection:
            if list(projects.get_project_names(connection)):
                file_menu.entryconfig("Open", state=tk.ACTIVE)