import tkinter as tk

from gscrap.data import io
from gscrap.data.rectangles import rectangles as rct_data, rectangle_labels as rct_labels

from gscrap.mapping.mapping import mapping_states as states

from gscrap.rectangles import rectangles, utils as rectangle_utils

from gscrap.utils import generators

class MappingTool(rectangle_utils.RectangleFactory):
    def __init__(self, container):
        """

        Parameters
        ----------
        container
        """
        self._container = container
        self.scene = None
        self._img_item = None
        self._canvas = None
        self._root = None
        self._position = [0, 0]
        self._height = 0
        self._width = 0
        self._aborted = False

        self._photo_image = None

        self.initial = states.Initial(self)
        self.editing = states.Editing(self)
        self.cloning = states.Cloning(self)
        self.drawing = states.Drawing(self)

        self._state = self.initial

        self._rectangles = []

        self._all_instances = {}

        self._labels_per_rectangle = {}

        self.rectangle = None
        self._rid = None
        self.cloned = None

        def null_callback(data):
            pass

        self._close_callback = null_callback

    @property
    def canvas(self):
        return self._canvas

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        value.update()

    @property
    def position(self):
        return tuple(self._position)

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def instances(self):
        """

        Returns
        -------
        typing.Dict[int, controllers.rectangles.utils.RectangleWrapper]
        """
        return self._all_instances

    def get_rectangle_labels(self, rectangle):
        lpr = self._labels_per_rectangle

        if not rectangle.id in lpr:
            lpr[rectangle.id] = lbl = rct_labels.RectangleLabels(rectangle)
            return lbl

        return lpr[rectangle.id]

    def select_rectangle(self, x, y):
        res = rectangles.find_closest_enclosing(self._all_instances, x, y)
        if res:
            return res[0]
        return

    def get_rectangles(self, container=None):
        return rectangles.get_rectangles(self._all_instances, container)

    def find_closest(self, x, y):
        return rectangles.find_closest(self._all_instances, x, y)

    def move(self, rid, dx, dy):
        self._canvas.move(rid, dx, dy)

    def adjust_point(self, x, y, w, h):
        #makes sure that any drawn element is within the canvas
        wd = self._width
        hg = self._height

        if x <= 0:
            x = 1
        elif x + w >= wd:
            x = wd - w - 2

        if y <= 0:
            y = 1
        elif y + h >= hg:
            y = hg - h - 2

        return x, y

    @property
    def selected_rectangle(self):
        return self._rid

    @selected_rectangle.setter
    def selected_rectangle(self, rid):
        self._rid = rid

    def add_component(self, rid, comp_rid):
        rectangles.add_component(self._all_instances, rid, comp_rid)

    def remove_component(self, rid, comp_id):
        rectangles.remove_component(self._all_instances, rid, comp_id)

    def add_rectangle(self, bbox, container_id=None):
        x0, y0, x1, y1 = bbox

        rct = self.scene.create_rectangle(x1 - x0, y1 - y0)

        instances = self._all_instances

        if container_id:
            container = instances[container_id]
            container.rectangle.add_component(rct)

        wrapper = self.create_rectangle(self._create_instance(rct, x0, y0, container_id), x0, y0)

        # self._new_instances[rid] = wrapper
        instances[wrapper.rid] = wrapper

        self._rectangles.append(rct)

        return wrapper.rid

    def copy_rectangle(self, instance, x, y):
        instances = self._all_instances

        wrapper = self.create_rectangle(self._create_instance(instance, x, y), x, y)

        # self._new_instances[rid] = wrapper
        instances[wrapper.rid] = wrapper

        return wrapper.rid

    def _create_instance(self, rct, x, y, container_id=None):
        if container_id:
            instance = rct.create_instance(x, y, self._all_instances[container_id].instance)
        else:
            instance = rct.create_instance(x, y)
        return instance

    def add_instance(self, rid, x, y, container_id=None):
        instance = self._all_instances[rid]

        wrapper = self.create_rectangle(instance, x, y)

        self._all_instances[wrapper.rid] = wrapper

        return wrapper.rid

    def get_rectangle(self, rid):
        return rectangles.get_rectangle(self._all_instances, rid)

    def get_all_rectangles(self):
        return self._all_instances.values()

    def create_rectangle(self, instance, x, y):
        return rectangle_utils.RectangleWrapper(
            instance.rectangle,
            self.canvas.create_rectangle(x, y, x + instance.width, y + instance.height),
            instance)

    def set_scene(self, scene):
        """

        Parameters
        ----------
        project: gscrap.projects.scenes._Scene

        Returns
        -------

        """
        self.scene = scene

    def close(self):
        #todo
        pass

    def set_template(self, image):
        self._photo_image = image

    def start(self, on_close):
        """

        Parameters
        ----------
        image: PIL.Image.Image

        Returns
        -------

        """
        self._root = root = tk.Toplevel(self._container)
        self._close_callback = on_close

        self._canvas = canv = tk.Canvas(root, width=500, height=500)
        root.resizable(False, False)

        canv.pack(fill=tk.BOTH, expand=tk.YES)
        root.update()

        root.bind("<Configure>", self._on_drag)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        canv.bind("<Button-1>", self._on_left_click)
        canv.bind("<Button-3>", self._on_right_click)
        canv.bind("<Motion>", self._on_motion)

        image = self._photo_image

        self._img_item = canv.create_image(0, 0, image=image, anchor=tk.NW)

        canv.config(width=image.width(), height=image.height())

        self._width = image.width()
        self._height = image.height()

        io.load(self._load_rectangles)

    def _load_rectangles(self):
        scene = self.scene

        with scene.connect() as con:
            instances = self._all_instances

            for instance in rectangles.load_rectangle_instances(
                con,
                generators.append_yield(
                    self._rectangles,
                    scene.get_rectangles(con)),
                    self):

                instances[instance.rid] = instance

    def stop(self):
        self._aborted = True

    def remove_rectangle(self, rid):
        all_instances = self._all_instances
        canvas = self.canvas

        # with engine.connect() as connection:
        #     container = self.get_rectangle(rid).container
        #
        #     if container:
        #         ct = self.get_rectangle(container)
        #         ct.components.remove(rid)
        #
        #     for rct in rectangle_utils.tree_iterator(self, rid):
        #         self.canvas.delete(rct.rid)
        #         del all_instances[rct.rid]
        #         rct.delete(connection)

        #todo: don't delete components, just un-map them from the container

        with self.scene.connect() as conn:
            ist = all_instances.pop(rid)
            canvas.delete(rid)
            ist.delete(conn)

            for cid in ist.components:
                all_instances[cid].container = None

            # for rct in rectangles.remove_rectangle(all_instances, rid):
            #     id_ = rct.rid
            #     canvas.delete(id_)
            #     rct.delete(conn)
            #     del all_instances[id_]


            num_instances = 0

            # count the number of instances of a rectangle
            for inst in all_instances.values():
                if inst.rectangle == ist.rectangle:
                    num_instances += 1

            num_instances -= 1

            #delete rectangle, labels and samples if there are no more instances.
            # for rectangle, num_instances in dct.items():
            if num_instances == 0:
                rct_data.delete_rectangle(conn, ist.rectangle)


    def unselect_rectangle(self):
        self._rid = None
        self.rectangle = None

    def on_close(self, callback):
        self._close_callback = callback

    def _on_left_click(self, event):
        pass

    def _on_right_click(self, event):
        self._state.on_right_click(event)

    def _on_motion(self, event):
        self._state.on_motion(event)

    def _on_close(self):
        self._root.destroy()
        self._root = None
        self._canvas = None

        scene = self.scene

        #submit new rectangles and instances
        if not self._aborted:
            all_instances = self._all_instances

            with scene.connect() as con:
                for r in self._rectangles:
                    r.delete(con)

                for wrapper in all_instances.values():
                    wrapper.delete(con)

            with scene.connect() as con:
                for r in self._rectangles:
                    r.submit(con)

                for wrapper in all_instances.values():
                    wrapper.submit(con)

                for labels in self._labels_per_rectangle.values():
                    labels.submit(con)


        self._rectangles.clear()
        self._all_instances.clear()

        self._state = self.initial

        self._close_callback(None)

    def _on_drag(self, event):
        self._position[0] = self._root.winfo_rootx()
        self._position[1] = self._root.winfo_rooty()
        self._width = self._root.winfo_width()
        self._height = self._root.winfo_height()
