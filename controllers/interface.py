from abc import ABC, abstractmethod

import tkinter as tk

from controllers import controller
from controllers import settings


class State(ABC):
    def __init__(self, manager):
        self._manager = manager

    @abstractmethod
    def game_type_menu(self, x):
        pass

class Initial(State):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: Interface
        """
        super(Initial, self).__init__(manager)
        self._cs = "n/a"

    def game_type_menu(self, x):
        # update metadata only when the game_type changes
        if x != self._cs:
            self._manager.create_metadata()
            self._cs = x


class Resetting(State):
    def __init__(self, manager):
        """

        Parameters
        ----------
        manager: Interface
        """
        super(Resetting, self).__init__(manager)
        # E, W, N, S = tk.E, tk.W, tk.N,tk.S

    def game_type_menu(self, x):
        mw = self._manager
        mw.game_type = "n/a"
        mw.create_metadata()
        mw.state = mw.initial

class Interface(controller.Controller):
    def __init__(self, container, manager, projects):
        self._container = container

        self._manager = manager
        self._projects = projects

        projects.on_load(self._initialize)

        self.initial = Initial(self)
        self.resetting = Resetting(self)
        self._state = self.initial

        self._metadata = None
        self.create_metadata()
        # fr.grid_propagate(0)

        # self._manager.state = self._manager.initial
        # self._manager.update()

        self._save_btn = None
        self._load_btn = None

        self._open_project = settings.OpenProject(container, projects)
        self._new_project = settings.NewProject(container, projects)

    def create_metadata(self):
        if self._metadata != None:
            self._metadata.destroy()
        stg = tk.Frame(self._container)

        self._selection = tk.StringVar(stg)
        self._selection.set("n/a")

        stg.grid(row=1, column=0)
        tk.Label(stg, text="Name").grid(row=0, column=0)
        tk.Label(stg, text="Type").grid(row=1, column=0)
        tk.Entry(stg).grid(row=0, column=1)
        tk.OptionMenu(stg, self._selection, *self._projects.get_project_types()).grid(row=1, column=1)
        self._metadata = stg

        stg.grid(row=0, column=0)

        buttons = tk.Frame(self._container)

        pj = self._projects.get_projects()

        self._load_btn = tk.Button(
            buttons,
            text="Load",
            command=self._on_load,
            state="disabled" if not pj else "normal").grid(row=2, column=0)
        tk.Button(buttons, text="Save", command=self._on_save, state="disabled").grid(row=2, column=1)

        buttons.grid(row=1, column=0)

    def on_window_selected(self):
        self._save_btn["state"] = "normal"

    def _initialize(self, project):
        self._manager.initialize(project)

    def _on_load(self):
        self._open_project.start()

    def _on_save(self):
        #todo: cannot save project with no name
        self._load_btn["state"] = "normal"

    def update(self, event, emitter):
        pass

