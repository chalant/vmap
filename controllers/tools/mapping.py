import math

import tkinter as tk

from data import engine

from controllers.tools import mapping_utils
from controllers.tools import mapping_states as states
from controllers.tools import collision as col

from data import io

class MappingTool(object):
    # area capture state (use for capturing positional rectangle)
    def __init__(self, container, rectangles):
        """

        Parameters
        ----------
        container
        rectangles: models.rectangles.Rectangles
        """
        self._img = None
        self._container = container
        self.rectangles = rectangles
        self._img_item = None
        self._canvas = None
        self._root = None
        self._position = [0, 0]
        self._height = 0
        self._width = 0
        self._aborted = False

        self._collision = collision = col.BoxCollision()

        self.initial = states.Initial(self)
        self.editing = states.Editing(self, collision)
        self.cloning = states.Cloning(self, collision)
        self.drawing = states.Drawing(self, collision)

        self._state = self.initial
        self.previous_state = None

        self._rectangles = []
        self._new_rectangles = []

        self._new_instances = {}
        self._all_instances = {}

        self.rectangle = None
        self._rid = None
        self.cloned = None

        self._items = {}

        self._points = []

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
        if x <= 0:
            x = 1
        elif x + w >= self._width:
            x = self._width - w - 2

        if y <= 0:
            y = 1
        elif y + h >= self._height:
            y = self._height - h - 2

        return x, y

    @property
    def selected_rectangle(self):
        return self._rid

    @selected_rectangle.setter
    def selected_rectangle(self, rid):
        self._rid = rid

    def add_item(self, item):
        self._items[item] = item

    def add_component(self, rid, comp_rid):
        instances = self._all_instances
        comp = instances[comp_rid]
        comp.container = rid
        cont = instances[rid]
        cont.add_component(comp_rid)
        comp.instance.container_id = cont.instance.id

    def add_rectangle(self, bbox, container_id=None):
        x0, y0, x1, y1 = bbox

        rct = self.rectangles.create_rectangle(x1 - x0, y1 - y0)
        rid = self.canvas.create_rectangle(*bbox)

        instances = self._all_instances

        wrapper = mapping_utils.RectangleWrapper(
            rct,
            rid,
            self._create_instance(rct, x0, y0, container_id),
            container_id)

        self._new_instances[rid] = wrapper
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
        instance = self._new_instances[rid]

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
        # todo: need absolute coordinates of the main window...

        # todo: highlight un-labeled rectangles

        self._root = root = tk.Toplevel(self._container)
        # root = self._mapper._main_frame
        self._canvas = canv = tk.Canvas(root, width=500, height=500)
        root.resizable(False, False)
        # canv.create_rectangle(50, 50, 250, 150, fill='red')
        canv.pack(fill=tk.BOTH, expand=tk.YES)
        root.update()

        root.bind("<Configure>", self._on_drag)
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        canv.bind("<Button-1>", self._on_left_click)
        canv.bind("<Button-3>", self._on_right_click)

        self._img_item = canv.create_image(0, 0, image=image, anchor=tk.NW)
        canv.config(width=image.width(), height=image.height())

        self._width = image.width()
        self._height = image.height()
        # canv.create_rectangle(0, 0, image.width(), image.height())
        io.load(self._load_rectangles)

    def _load_rectangles(self):

        rectangles = self.rectangles.get_rectangles()

        cmp_to_rid = {}

        instances = self._all_instances

        for rct in rectangles:
            self._rectangles.append(rct)

            for instance in rct.get_instances():
            #draw all instances
                rid = self._canvas.create_rectangle(*instance.bbox)

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

        # for ist in instances.values():
        #     ct = self.get_root_container(ist.rid)
        #     if ct:
        #         for rct in mapping_utils.tree_iterator(self, ct):
        #             x, y = rct.bbox[0], rct.bbox[1]
        #             self._canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill = "blue")

        # for ist in instances.values():
        #     ct = self.get_root_container(ist.rid)
        #
        #     print("ROOT", ct)
        #     if ct:
        #         ct = self.get_rectangle(ct)
        #         x, y = ct.bbox[0], ct.bbox[1]
        #
        #         self._canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill = "blue")
        #
        # print("DRAWN!!!")

    def stop(self):
        self._aborted = True
        # todo: submit changes is any

    def remove_rectangle(self, rid):
        self.canvas.delete(rid)

        all_instances = self._all_instances
        new_instances = self._new_instances

        if rid in new_instances:
            del new_instances[rid]
            wrapper = all_instances.pop(rid)
            for c in wrapper.components:
                del new_instances[c]
                self.canvas.delete(c)
        else:
            with engine.connect() as connection:
                wrapper = all_instances.pop(rid)
                for c in wrapper.components:
                    self.canvas.delete(c)
                    w = all_instances.pop(c)
                    w.delete(connection) #delete components of the instance
                wrapper.delete(connection) #deletes instance from database

    def unselect_rectangle(self):
        self._rid = None
        self.rectangle = None

    def _add_instance(self, rectangle, instance):
        return rectangle.add_instance(instance)

    def _add_component(self, rectangle, component):
        rectangle.add_component(component)

    def _on_left_click(self, event):
        pass

    def _on_right_click(self, event):
        self._state.on_right_click(event)

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

            with engine.connect() as connection:
                #todo: check if all rectangles have been labeled
                # note: we can resume a mapping session from where we left off
                for r in self._rectangles:
                    r.submit(connection)

                for wrapper in self._all_instances.values():
                    wrapper.submit(connection)

        self._rectangles.clear()
        self._new_instances.clear()
        self._all_instances.clear()
        self._new_rectangles.clear()

        self._state = self.initial

    def _on_drag(self, event):
        self._position[0] = self._root.winfo_rootx()
        self._position[1] = self._root.winfo_rooty()
        self._width = self._root.winfo_width()
        self._height = self._root.winfo_height()
