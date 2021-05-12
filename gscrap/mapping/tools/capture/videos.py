import tkinter as tk

#

class VideosView(object):
    def __init__(self, controller, container):
        self._controller = controller

    def render(self, container):
        pass

class VideosController(object):
    def __init__(self, container):
        self._view = VideosView(self, container)