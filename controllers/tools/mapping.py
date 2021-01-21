import math

import tkinter as tk

import colorutils

from PIL import ImageTk

from data import engine
from data import io

from controllers.tools import mapping_utils
from controllers.tools import mapping_states as states

class MappingTool(object):
    def __init__(self, container, project):
        """

        Parameters
        ----------
        container
        project: models.projects.Project
        """
        self._container = container
        self.project = project
        self._img_item = None
        self._canvas = None
        self._root = None
        self._position = [0, 0]
        self._height = 0
        self._width = 0
        self._aborted = False

        self.initial = states.Initial(self)
        self.editing = states.Editing(self)
        self.cloning = states.Cloning(self)
        self.drawing = states.Drawing(self)

        self._state = self.initial

        self._rectangles = []
        self._new_rectangles = []

        self._new_instances = {}
        self._all_instances = {}

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

    def select_rectangle(self, x, y):
        res = self._find_closest_enclosing(x, y)
        if res:
            return res[0]
        return

    def _smallest(self, per, p):
        return per <= p

    def _biggest(self, per, p):
        return per >= p

    def _find_closest_enclosing(self, x, y):
        m_dist = None
        p = (x, y)

        results = []

        #find smallest distance
        instances = self._all_instances

        for r in instances.values():
            x0, y0, x1, y1 = r.bbox

            if m_dist is None:
                if x0 < x and y0 < y and x1 > x and y1 > y:
                    m_dist = math.dist(p, r.top_left)
                continue

            dst = math.dist(p, r.top_left)

            if dst < m_dist and x0 < x and y0 < y and x1 > x and y1 > y:
                m_dist = dst

        for rid, r in instances.items():
            if m_dist == math.dist(p, r.top_left):
                results.append(rid)

        return results

    def get_rectangles(self, container=None):
        instances = self._all_instances
        if container:
            for c in container.components:
                yield instances[c]
        else:
            for r in instances.values():
                if not r.container:
                    yield r

    def find_closest(self, x, y):
        m_dist = None
        p = (x, y)

        results = []

        # find smallest distance
        all_instances = self._all_instances

        for r in all_instances.values():
            if m_dist is None:
                m_dist = min((math.dist(p, r.top_left), math.dist(p, r.bottom_right)))
                continue

            dst = min((math.dist(p, r.top_left), math.dist(p, r.bottom_right)))

            if dst < m_dist:
                m_dist = dst

        for rid, r in all_instances.items():
            if m_dist == min((math.dist(p, r.top_left), math.dist(p, r.bottom_right))):
                results.append(rid)

        return results

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
        instances = self._all_instances
        comp = instances[comp_rid]
        comp.container = rid
        cont = instances[rid]
        cont.add_component(comp_rid)
        comp.instance.container_id = cont.instance.id

    def add_rectangle(self, bbox, container_id=None):
        x0, y0, x1, y1 = bbox

        rct = self.project.create_rectangle(x1 - x0, y1 - y0)
        rid = self.canvas.create_rectangle(*bbox)

        instances = self._all_instances

        wrapper = mapping_utils.RectangleWrapper(
            rct,
            rid,
            self._create_instance(rct, x0, y0, container_id),
            container_id)

        # self._new_instances[rid] = wrapper
        instances[rid] = wrapper

        self._new_rectangles.append(rct)
        self._rectangles.append(rct)

        return rid

    def _create_instance(self, rct, x, y, container_id=None):
        if container_id:
            instance = rct.create_instance(x, y, self._all_instances[container_id].instance)
        else:
            instance = rct.create_instance(x, y)
        return instance

    def add_instance(self, rid, x, y, container_id=None):
        instance = self._all_instances[rid]

        nid = self.canvas.create_rectangle(x, y, x + instance.width, y + instance.height)

        wrapper = mapping_utils.RectangleWrapper(
            instance.rectangle,
            nid,
            self._create_instance(instance.rectangle, x, y, container_id),
            container_id)

        self._new_instances[nid] = wrapper
        self._all_instances[nid] = wrapper

        return nid

    def get_rectangle(self, rid):
        """

        Parameters
        ----------
        rid

        Returns
        -------
        mapping_utils.RectangleWrapper
        """
        instances = self._all_instances
        if rid in instances:
            return instances[rid]
        return

    def get_root_container(self, rct):
        r = self.get_rectangle(rct)
        if r:
            container = r.container

            while container is not None:
                r = self.get_rectangle(container)
                container = r.container

            if r:
                return r.rid
            return
        return

    def get_components(self, rct):
        if isinstance(rct, mapping_utils.RectangleWrapper):
            return rct.components
        return self._new_instances[rct].components

    def create_rectangle(self, x0, y0, x1, y1):
        return self.canvas.create_rectangle(x0, y0, x1, y1)

    def start(self, image):
        """

        Parameters
        ----------
        image: PIL.Image.Image

        Returns
        -------

        """
        # todo: need absolute coordinates of the main window...

        # todo: highlight un-labeled project

        self._root = root = tk.Toplevel(self._container)

        self._canvas = canv = tk.Canvas(root, width=500, height=500)
        root.resizable(False, False)

        canv.pack(fill=tk.BOTH, expand=tk.YES)
        root.update()

        root.bind("<Configure>", self._on_drag)
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        canv.bind("<Button-1>", self._on_left_click)
        canv.bind("<Button-3>", self._on_right_click)
        canv.bind("<Motion>", self._on_motion)

        self._image = image
        self._photo_image = ImageTk.PhotoImage(image)

        self._img_item = canv.create_image(0, 0, image=self._photo_image, anchor=tk.NW)
        canv.config(width=image.width, height=image.height)

        self._width = image.width
        self._height = image.height

        io.load(self._load_rectangles)

    def _load_rectangles(self):
        # print(mapping_utils.colorInvert(self._canvas["background"][1:]))
        # print(self._canvas["background"])

        # black = colorutils.Color(web="black", arithmetic=colorutils.ArithmeticModel.BLEND)

        with engine.connect() as con:
            cmp_to_rid = {}

            instances = self._all_instances
            rectangles = self._rectangles

            for rct in self.project.get_rectangles(con):
                rectangles.append(rct)

                for instance in rct.get_instances(con):
                #draw all instances
                    rid = self._canvas.create_rectangle(*instance.bbox)
                    # tl = colorutils.Color(rgb=self._image.getpixel(instance.top_left),
                    #                       arithmetic=colorutils.ArithmeticModel.LIGHT)
                    # # br = colorutils.Color(rgb=self._image.getpixel(instance.bottom_right))
                    # outline = tl
                    # r, g, b = outline.rgb
                    # print(outline.rgb)

                    # colorutils.Color(hsv=outline.hsv).hex
                    self._canvas.itemconfigure(rid)

                    wrapper = mapping_utils.RectangleWrapper(
                        instance.rectangle,
                        rid,
                        instance)

                    instances[rid] = wrapper
                    cmp_to_rid[instance.id] = rid

            #build relations
            for k, w in instances.items():
                wrapper = instances[k]
                for cmp in wrapper.instance.get_components():
                    rid = cmp_to_rid[cmp]
                    component = instances[rid]
                    component.container = k
                    w.add_component(rid)

    def stop(self):
        self._aborted = True

    def remove_rectangle(self, rid):
        all_instances = self._all_instances

        with engine.connect() as connection:
            container = self.get_rectangle(rid).container

            if container:
                ct = self.get_rectangle(container)
                ct.components.remove(rid)

            for rct in mapping_utils.tree_iterator(self, rid):
                self.canvas.delete(rct.rid)
                del all_instances[rct.rid]
                rct.delete(connection)

    def unselect_rectangle(self):
        self._rid = None
        self.rectangle = None

    def on_close(self, callback):
        self._close_callback = callback

    def _add_instance(self, rectangle, instance):
        return rectangle.add_instance(instance)

    def _add_component(self, rectangle, component):
        rectangle.add_component(component)

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

        #submit new rectangles and instances
        if not self._aborted:
            with engine.connect() as con:
                # todo: only delete updated rectangles
                for r in self._rectangles:
                    r.delete(con)

                for wrapper in self._all_instances.values():
                    wrapper.delete(con)

            with engine.connect() as con:
                #todo: check if all rectangles have been labeled
                # note: we can resume a mapping session from where we left off
                for r in self._rectangles:
                    r.submit(con)

                for wrapper in self._all_instances.values():
                    wrapper.submit(con)

        self._rectangles.clear()
        self._new_instances.clear()
        self._all_instances.clear()
        self._new_rectangles.clear()

        self._state = self.initial
        self.project.update()
        self._close_callback(None)

    def _on_drag(self, event):
        self._position[0] = self._root.winfo_rootx()
        self._position[1] = self._root.winfo_rooty()
        self._width = self._root.winfo_width()
        self._height = self._root.winfo_height()
