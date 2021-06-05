import tkinter as tk

from PIL import Image, ImageTk

from gscrap.image_capture import video_navigators as vn

class NavigationView(object):
    def __init__(self, width, height):
        self.next_frame = None
        self.previous_frame = None

        self.thumbnail = None
        self.canvas = None

        self.width = width
        self.height = height

    def set_thumbnail(self, image):
        return self.canvas.create_image(
            (int(self.width/2), int(self.height/2)),
            image=image,
            anchor=tk.CENTER)

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

        canvas.create_image((0, 0), anchor=tk.NW, image=controller.background)

        return frame

    def set_controller(self, controller):
        self._controller = controller

#todo: we need to know when the reach the end of a video (disable next frame button)
#todo:

class NavigationController(object):
    def __init__(self, callback=None):
        """

        Parameters
        ----------
        callback: function
        """

        self._view = None

        def null_callback(img):
            pass

        self._callback = callback if callback else null_callback

        self._vid_meta = None
        self._video = None

        self._current_frame = None
        self.background = None
        self._meta = None

        self._video_navigator = vn.VideoNavigator()

        self._initialized = False

    def view(self):
        return self._view

    def disable_read(self):
        view = self._view

        view.next_frame["state"] = tk.DISABLED
        view.previous_frame["state"] = tk.DISABLED

    def enable_read(self, video_metadata):
        #initialize reader in case it is a new record
        if not self._initialized:
            self._video_navigator.initialize(video_metadata)

        view = self._view

        view.next_frame["state"] = tk.NORMAL
        view.previous_frame["state"] = tk.NORMAL

    @property
    def current_frame(self):
        return self._video_navigator.current_frame

    def next_frame(self):
        ret, frame = self._video_navigator.next_frame()

        if ret:
            self._callback(frame)

    def prev_frame(self):
        ret, frame = self._video_navigator.previous_frame()

        if ret:
            self._callback(frame)

    def restart(self):
        meta = self._meta

        if meta:
            self._video_navigator.reset()
            self._start(meta)

    def _start(self, video_meta):
        #todo: we should register for any new video write event
        try:
            view = self._view

            # create thumbnail
            self._video_navigator.initialize(video_meta)

            # thumbnail = self.thumbnail


            # image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # image.thumbnail((view.width, view.height))
            #
            # self.thumbnail_image = image
            #
            # if ret:
            #     thumbnail.paste(image)

            view.next_frame["state"] = tk.NORMAL
            view.previous_frame["state"] = tk.NORMAL

            # self._callback(frame)  # update
        except EOFError:
            pass

    def reset(self):
        view = self._view

        #reset everything
        view.next_frame["state"] = tk.DISABLED
        view.previous_frame["state"] = tk.DISABLED

        self._video_navigator.reset()

        self.background.paste(Image.new('RGB', (view.width, view.height)))

    def set_view(self, view):
        self._view = view

        self.background = ImageTk.PhotoImage(
            Image.new('RGB', (view.width, view.height)))

        view.set_controller(self)

    def set_video_metadata(self, video_meta):
        self._meta = video_meta
        self._start(video_meta)

    def set_image_comparator(self, comparator):
        self._video_navigator.set_comparator(comparator)


