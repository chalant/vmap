import tkinter as tk

from PIL import Image
import cv2

from gscrap.mapping.tools import navigation as nv

class CaptureNavigationView(object):
    def __init__(self, width, height):
        self.navigation_view = nv.NavigationView(width, height)

        self._controller = None

    def render(self, container):
        frame = tk.Frame(container)
        # menu = tk.Menu(frame)

        nav_view = self.navigation_view.render(frame)

        return frame

    def set_controller(self, controller):
        self._controller = controller

    def update_thumbnail(self, image):
        self.navigation_view.thumbnail.paste(image)


class CaptureNavigationController(object):
    def __init__(self):
        self._view = None
        self._navigator = nv.NavigationController(self._frame_update)
        self.thumbnail_image = None

    def _frame_update(self, frame):
        view = self._view

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image.thumbnail((view.width, view.height))

        view.update_thumbnail(image)

        self.thumbnail_image = image

    def disable_read(self):
        self._navigator.disable_read()

    def enable_read(self):
        self._navigator.enable_read()

    def view(self):
        return self._view

    def set_view(self, view):
        view.set_controller(self)

