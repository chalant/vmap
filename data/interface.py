from abc import ABC, abstractmethod

import tkinter as tk

from controllers import controller


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
    def __init__(self, container, id_, main_window):
        super(Interface, self).__init__(id_)

        self._container = container

        self.initial = Initial(self)
        self.resetting = Resetting(self)
        self._state = self.initial

        self._game_type = tk.LabelFrame(container)
        self._game_type.config(text="Game Type")
        self._game_type.grid(pady=5, row=0, column=0)
        # fr.grid_propagate(0)

        self._metadata = None
        self.create_metadata()

        self._game_type = tk.LabelFrame(container)
        self._game_type.config(text="Game Type")
        self._game_type.grid(pady=5, row=0, column=0)
        # fr.grid_propagate(0)

        self._selection = tk.StringVar()
        self._selection.set("n/a")
        # todo: load types from database and display them => handled by the model
        selection = self._selection
        self._game_types = tk.OptionMenu(
            self._game_type,
            selection, "Poker", "Solitaire",
            command=self._state.game_type_menu)
        self._game_types.pack()

        # self._manager.state = self._manager.initial
        # self._manager.update()

    def create_metadata(self):
        if self._metadata != None:
            self._metadata.destroy()
        fr = tk.LabelFrame(self._container)
        # todo: load metadata parameters from data-base
        fr.config(text="Metadata")
        fr.grid(row=1, column=0)
        tk.Label(fr, text="Name").grid(row=0, column=0)
        tk.Label(fr, text="Entry").grid(row=1, column=0)
        tk.Entry(fr).grid(row=0, column=1)
        tk.Entry(fr).grid(row=1, column=1)
        self._metadata = fr

    def update(self, event, emitter):
        pass

