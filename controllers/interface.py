from abc import ABC, abstractmethod

import tkinter as tk

from controllers import controller
from controllers import store

# class State(ABC):
#     def __init__(self, manager):
#         self._mapper = manager
#
#     @abstractmethod
#     def game_type_menu(self, x):
#         pass
#
# class Initial(State):
#     def __init__(self, manager):
#         """
#
#         Parameters
#         ----------
#         manager: Interface
#         """
#         super(Initial, self).__init__(manager)
#         self._cs = "n/a"
#
#     def game_type_menu(self, x):
#         # update metadata only when the game_type changes
#         if x != self._cs:
#             self._mapper._create_metadata()
#             self._cs = x
#
# class Resetting(State):
#     def __init__(self, manager):
#         """
#
#         Parameters
#         ----------
#         manager: Interface
#         """
#         super(Resetting, self).__init__(manager)
#
#     def game_type_menu(self, x):
#         mw = self._mapper
#         mw.game_type = "n/a"
#         mw._create_metadata()
#         mw.state = mw.initial

class Interface(controller.Controller):
    def __init__(self, container, manager, projects):
        """

        Parameters
        ----------
        container
        manager
        projects: models.projects.Projects
        """
        self._container = container

        self._manager = manager
        self._projects = projects

        # self.initial = Initial(self)
        # self.resetting = Resetting(self)
        # self._state = self.initial

        self._metadata = None

        self._new_btn = None
        self._save_btn = None
        self._load_btn = None

        self._input = None
        self._entry = None

        self._project = None

        self._changed = False

        self._create_metadata()

        self._open_project = store.OpenProject(container, projects)
        self._new_project = store.NewProject(container, projects)

    def _create_metadata(self):
        if self._metadata != None:
            self._metadata.destroy()
        stg = tk.Frame(self._container)

        self._selection = slc = tk.StringVar(stg)
        self._input = ipt = tk.StringVar(stg)
        self._selection.set("n/a")

        ipt.trace_add("write", self._on_input)
        slc.trace_add("write", self._on_input)

        stg.grid(row=1, column=0)
        tk.Label(stg, text="Name").grid(row=0, column=0)
        tk.Label(stg, text="Type").grid(row=1, column=0)

        self._entry = etr = tk.Entry(stg, textvariable=self._input)
        etr.grid(row=0, column=1)
        etr["state"] = "disabled"

        tk.OptionMenu(
            stg,
            self._selection,
            *self._projects.get_project_types()).grid(row=1, column=1)

        self._metadata = stg

        stg.grid(row=0, column=0)

        buttons = tk.Frame(self._container)

        pj = self._projects.get_project_names()

        self._new_btn = nb = tk.Button(
            buttons,
            text="New",
            command=self._on_new
        )

        self._load_btn = lb = tk.Button(
            buttons,
            text="Load",
            command=self._on_load,
            state="disabled" if not pj else "normal")

        self._save_btn = sb = tk.Button(
            buttons,
            text="Save",
            command=self._on_save,
            state="disabled")

        nb.grid(row=2, column=0)
        lb.grid(row=2, column=1)
        sb.grid(row=2, column=2)

        buttons.grid(row=1, column=0)

    def on_window_selected(self, width, height, img=None):
        pj = self._project

        pj.width = width
        pj.height = height
        pj.store_template(img)

        self._save_btn["state"] = "normal"

    def _on_input(self, t, evt, b):
        ipt = self._input.get()
        slc = self._selection.get()

        if ipt and slc != "n/a":
            self._save_btn["state"] = "normal"
        else:
            self._save_btn["state"] = "disable"

    def _on_new(self):
        if self._changed and self._project:
            # todo: display save message
            self._project.save()
        self._changed = False
        self._new_project.start(self._initialize)

    def _initialize(self, project):
        self._manager.initialize(project)

        self._input.set(project.name)
        self._selection.set(project.project_type)
        project.on_update(self._update)

        self._project = project

        self._changed = False

    def _update(self, rectangles):
        self._save_btn["state"] = "normal"
        self._manager.update(rectangles)
        self._changed = True

    def _on_load(self):
        self._open_project.start(self._initialize)

    def _on_save(self):
        #todo: cannot save project with no name
        self._load_btn["state"] = "normal"