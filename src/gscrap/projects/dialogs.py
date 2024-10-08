import tkinter as tk

import threading

class NewScene(object):
    # todo: add Cancel Button
    def __init__(self, container, project):
        """

        Parameters
        ----------
        container
        project: gscrap.projects.projects.Project
        """

        self._project = project
        self._container = container

        self._root = None
        self._scene_name = None
        self._schema_name = None

    def start(self, callback):
        self._callback = callback
        self._root = root = tk.Toplevel(self._container)

        # root.update()
        root.attributes('-topmost', 'true')
        root.grab_set()
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self._close)
        root.wm_title("New Scene")

        rx = self._container.winfo_rootx()
        ry = self._container.winfo_rooty()

        w = 300
        h = 100

        root.geometry("{}x{}+{}+{}".format(w, h, rx + w, ry + h))

        name = tk.Label(root, text="Name")

        self._input = tk.StringVar(root)
        self._scene_name = ipt = tk.Entry(root, textvariable=self._input)

        self._input.trace_add("write", self._on_input)

        # todo: check if input name already exists (also observe user inputs)

        type_ = tk.Label(root, text="Type")

        project = self._project

        self._schema_name = var = tk.Variable(root)
        var.trace_add("write", self._on_input)

        with project.connect() as connection:
            menu = tk.OptionMenu(
                root,
                var,
                *list(project.get_scene_schemas()))

            menu["width"] = 15

            self._scene_names = {
                pj for pj in
                project.get_scene_names(connection)
            }

            self._done_btn = done_btn = tk.Button(
                root,
                text="Done",
                state="disabled",
                command=self._on_done)

            done_btn.grid(row=2, column=1)

            name.grid(row=0, column=0)
            ipt.grid(row=0, column=1)

            type_.grid(row=1, column=0)
            menu.grid(row=1, column=1)

    def _on_input(self, t, evt, b):
        ipt = self._input.get()
        slc = self._schema_name.get()

        if ipt not in self._scene_names:
            if ipt and slc:
                self._done_btn["state"] = "normal"
            else:
                self._done_btn["state"] = "disabled"

    def _close(self):
        root = self._root

        root.grab_release()
        root.destroy()

    def _on_done(self):
        threading.Thread(
            target=self._create_scene,
            args=(self._scene_name.get(), self._schema_name.get())).start()

        self._close()

    def _create_scene(self, scene_name, schema_name):
        self._callback(self._project.create_scene(
            scene_name,
            schema_name))

    def _on_cancel(self):
        self._close()

class OpenScene(object):
    def __init__(self, container, project):
        """

        Parameters
        ----------
        container
        project: gscrap.projects.projects.Project
        """

        self._container = container
        self._project = project

        self._root = None
        self._scene_name = None
        self._callback = None

    def start(self, callback):
        self._callback = callback
        self._root = root = tk.Toplevel(self._container)

        root.attributes('-topmost', 'true')
        root.grab_set()
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.wm_title("Open Scene")

        rx = self._container.winfo_rootx()
        ry = self._container.winfo_rooty()

        w = 300
        h = 100

        root.geometry("{}x{}+{}+{}".format(w, h, rx + w, ry + h))
        project = self._project

        self._scene_name = var = tk.Variable(root)

        var.trace_add("write", self._on_input)

        with project.connect() as connection:
            self._slc_frame = slc_frame = tk.Frame(root)

            # name = tk.Label(slc_frame, text="Project")

            menu = tk.OptionMenu(
                slc_frame,
                var,
                *project.get_scene_names(connection))

            menu["width"] = 15

            self._btn_frame = btn_frame = tk.Frame(root)

            self._done_btn = done_btn = tk.Button(
                btn_frame,
                text="Done",
                state="disabled",
                command=self._on_done)

            self._cancel_btn = cancel_btn = tk.Button(
                btn_frame,
                text="Cancel",
                state="normal",
                command=self._on_close
            )

            slc_frame.pack()

            # name.pack(side=tk.LEFT)
            menu.pack(side=tk.LEFT)

            btn_frame.pack()

            cancel_btn.pack(side=tk.LEFT)
            done_btn.pack(side=tk.LEFT)

    def _on_done(self):
        selection = self._scene_name.get()
        if selection:
            threading.Thread(target=self._load_scene, args=(selection,)).start()

        self._on_close()

    def _load_scene(self, scene_name):
        self._callback(self._project.load_scene(scene_name))

    def _on_close(self):
        self._root.grab_release()
        self._root.destroy()

    def _on_input(self, t, evt, b):
        slc = self._scene_name.get()
        if slc:
            self._done_btn["state"] = "normal"
        else:
            self._done_btn["state"] = "disabled"