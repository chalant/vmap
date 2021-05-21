import tkinter as tk

import cv2

from PIL import Image, ImageTk

class NavigationView(object):
    def __init__(self, width, height):
        self.next_frame = None
        self.previous_frame = None

        self.thumbnail = None
        self.canvas = None

        self.width = width
        self.height = height

    def render(self, container):
        frame = tk.Frame(container)

        controller = self._controller

        self.canvas = canvas = tk.Canvas(
            frame,
            width=self.width,
            height=self.height)

        commands = tk.Frame(frame)

        self.previous_frame = pf = tk.Button(
            commands,
            text="Prev",
            command=controller.prev_frame,
            state=tk.DISABLED
        )

        self.next_frame = nf = tk.Button(
            commands,
            text="Next",
            command=controller.next_frame,
            state=tk.DISABLED
        )

        frame.pack()
        canvas.pack()
        commands.pack(side=tk.BOTTOM)

        pf.pack(side=tk.LEFT)
        nf.pack(side=tk.RIGHT)

        canvas.create_image((0, 0), anchor=tk.NW, image=controller.thumbnail)

        return frame

    def set_controller(self, controller):
        self._controller = controller

class NavigationController(object):
    def __init__(self, video_navigator, callback=None):
        """

        Parameters
        ----------
        video_navigator: gscrap.image_capture.video.VideoNavigator
        callback: function
        """

        self._view = None

        def null_callback(img):
            pass

        self._callback = callback if callback else null_callback

        self._vid_meta = None
        self._video = None

        self._current_frame = None
        self.thumbnail = None

        self._video_navigator = video_navigator

    def view(self):
        return self._view

    def next_frame(self):
        ret, frame = self._video_navigator.next_frame()

        if ret:
            self._callback(frame)

    def prev_frame(self):
        ret, frame = self._video_navigator.previous_frame()

        if ret:
            self._callback(frame)

    def reset(self):
        view = self._view

        #reset everything
        view.next_frame["state"] = tk.DISABLED
        view.previous_frame["state"] = tk.DISABLED

        self._video_navigator.reset()

        self.thumbnail.paste(Image.new('RGB', (view.width, view.height)))

    def set_view(self, view):
        self._view = view
        self.thumbnail = ImageTk.PhotoImage(
            Image.new('RGB', (view.width, view.height)))

        view.set_controller(self)

    def set_video_metadata(self, video_meta):
        view = self._view

        # create thumbnail
        ret, frame = self._video_navigator.initialize(video_meta)

        thumbnail = self.thumbnail


        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image.thumbnail((view.width, view.height))

        if ret:
            thumbnail.paste(image)

        view.next_frame["state"] = tk.NORMAL
        view.previous_frame["state"] = tk.NORMAL

        self._callback(frame) #update


