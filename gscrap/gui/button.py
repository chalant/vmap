from abc import abstractmethod, ABC

import tkinter as tk

class ButtonController(ABC):
    def __init__(self, button):
        self._button = button

    def execute(self):
        self._execute(self._button)

    @abstractmethod
    def _execute(self, button):
        raise NotImplementedError

class NullController(ButtonController):
    def _execute(self, button):
        pass

class Button(object):
    def __init__(self, name):
        self._controller = NullController(self)
        self.button = None
        self.name = name

    def render(self, container):
        self.button = button = tk.Button(
            container,
            text=self.name,
            command=self._controller.execute)

        return button

    def set_controller(self, controller):
        self._controller = controller

    def enable_button(self):
        self.button["state"] = tk.NORMAL

    def disable_button(self):
        self.button["state"] = tk.DISABLED