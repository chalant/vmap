import tkinter as tk

from gscrap.projects import dialogs

class MenuBarController(object):
    def __init__(self, menu_bar, projects):
        self._menu_bar = menu_bar
        self._projects = projects

    def open(self):
        self._menu_bar.open_dialog.start()

    def new(self):
        self._menu_bar.new_dialog.start()

class MenuBar(object):
    def __init__(self, root, controller, project):

        self.menu_bar = menu = tk.Menu(root, tearoff=False)

        tp = root.winfo_toplevel()
        tp.config(menu=menu)

        self.open_dialog = dialogs.OpenScene(menu, project)
        self.new_dialog = dialogs.NewScene(menu, project)

        self.file_menu = file_menu = tk.Menu(menu, tearoff=False)

        menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="New", command=controller.new_scene)

        file_menu.add_command(label="Open", command=controller.open_scene)
        file_menu.entryconfig("Open", state=tk.DISABLED)

        with project.connect() as connection:
            if list(project.get_scene_names(connection)):
                file_menu.entryconfig("Open", state=tk.ACTIVE)

    def disable_menu(self):
        fm = self.file_menu

        fm.entryconfig("Open", state=tk.DISABLED)
        fm.entryconfig("New", state=tk.DISABLED)

    def enable_menu(self):
        fm = self.file_menu

        fm.entryconfig("Open", state=tk.NORMAL)
        fm.entryconfig("New", state=tk.NORMAL)
