import math

import tkinter as tk

from PIL import ImageTk, Image

from gscrap.rectangles import rectangles as rt

class ImageRectangle(object):
    def __init__(
            self,
            rid,
            iid,
            width,
            height,
            photo_image,
            image_buffer,
            image_index):

        self.rid = rid
        self.iid = iid
        self._image_index = image_index

        self.width = width
        self.height = height
        self.photo_image = photo_image

        self.dimensions = (width, height)

        self._image_buffer = image_buffer

    @property
    def image(self):
        return self._image_buffer.get_image(self._image_index)

    def paste(self, image):
        self.photo_image.paste(Image.fromarray(image, "RGB"))

    def reset(self):
        self.photo_image.paste(
            Image.frombuffer(
                "RGB",
                self.image,
                self.dimensions,
                "raw"))

class ImageGrid(object):
    def __init__(self, width=None, height=None):
        self._frame = None
        self._canvas = None

        self._x = 1
        self._y = 1
        self._i = 0

        self._images = {}
        self._items = []

        self._width = 0
        self._height = 0

        self._motion_bind = False

        self._prev = None
        self._text = None
        self._f_rid = None

        self._max_row = None
        self._step = None

        self._image_buffer = None

        self._position = 0
        self._image_observers = []

        def null_callback(index, event):
            pass

        self._right_click_callback = null_callback
        self._on_left_click_callback = null_callback

    def clear(self):
        images = self._images
        capture_canvas = self._canvas

        # clear all images
        for k, im in images.items():
            capture_canvas.delete(k)
            capture_canvas.delete(im.iid)

        images.clear()
        self._items.clear()

        self._x = 1
        self._y = 1
        self._i = 0

    @property
    def images(self):
        return self._images.values()

    def render(self, container):
        self._frame = frame = tk.Frame(container)
        self._canvas = canvas = tk.Canvas(frame)

        self._cfv_sb = cfv_sb = tk.Scrollbar(frame, orient=tk.VERTICAL)
        self._cfh_sb = cfh_sb = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        cfv_sb.config(command=canvas.yview)
        cfh_sb.config(command=canvas.xview)

        canvas.config(yscrollcommand=cfv_sb.set)
        canvas.config(xscrollcommand=cfh_sb.set)

        cfv_sb.pack(side=tk.RIGHT, fill=tk.Y)
        cfh_sb.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        canvas.bind("<Button-4>", self._on_mouse_wheel)
        canvas.bind("<Button-5>", self._on_mouse_wheel)

        canvas.bind("<Button-3>", self._on_right_click)
        canvas.bind("<Button-1>", self._on_left_click)

        frame.pack(fill=tk.X)
        canvas.pack(fill=tk.BOTH)

        return frame

    # def samples_update(self, samples):
    #     """
    #
    #     Parameters
    #     ----------
    #     samples: tools.detection.sampling.Samples
    #
    #     Returns
    #     -------
    #
    #     """
    #
    #     with engine.connect() as connection:
    #         self._draw_images(samples.width, samples.get_images(connection))
    #
    #     if not self._motion_bind:
    #         self._canvas.bind("<Motion>", self._on_motion)
    #         self._motion_bind = True

    def draw_images(self, dimensions, image_buffer):
        self._width = dimensions[0]
        self._height = dimensions[1]
        self._image_buffer = image_buffer

        self._draw_images(*dimensions, image_buffer, True)

    def _draw_images(self, width, height, image_buffer, create=True):
        images_dict = self._images
        canvas = self._canvas
        items = self._items

        images_dict.clear() #clear previous data

        w = canvas.winfo_width()

        max_row = math.floor(w / width)
        step = math.floor((w - (width * max_row)) / max_row)

        x = step
        y = 1

        i = 0
        h = 0
        wd = 0

        if create:
            fn = self._create_draw
        else:
            fn = self._update_draw

        xywh = [x, y, width, height]

        for index in image_buffer:
            fn(images_dict,
               items,
               image_buffer,
               canvas,
               index,
               xywh)

            i += 1
            x += width + step

            if i == max_row:
                i = 0
                y += height + 2
                # m = x - step
                x = step

            h = height
            wd = width

            xywh[0] = x
            xywh[1] = y

        self._x = x
        self._y = y
        self._i = i

        mw = canvas.winfo_width()
        mh = canvas.winfo_height()

        if y + h + 1 > mh:
            self._mh = y + h + 1
            canvas.configure(scrollregion=(0, 0, mw, y + h + 1))
        else:
            self._mh = mh
            canvas.configure(scrollregion=(0, 0, mw, mh))

        self._width = wd
        self._height = h
        self._max_row = max_row
        self._step = step

    def add_image(self, image_buffer, index, dimensions):
        canvas = self._canvas

        width, height = dimensions

        w = canvas.winfo_width()

        if not self._max_row:
            self._max_row = math.floor(w / width)

        max_row = self._max_row

        if not self._step:
            self._step = math.floor((w - (w * max_row)) / max_row)

        step = self._step

        i = self._i

        x = self._x
        y = self._y

        self._create_draw(
            self._images,
            self._items,
            image_buffer,
            self._canvas,
            index,
            (x, y, width, height))

        i += 1

        x = self._x + width + step
        y = self._y

        if i == max_row:
            i = 0
            y = self._y + height + 2
            x = step

        self._x = x
        self._y = y
        self._i = i
        self._width = width
        self._height = height

        mw = canvas.winfo_width()
        mh = canvas.winfo_height()
        h = height

        if y + h + 1 > mh:
            self._mh = y + h + 1
            canvas.configure(scrollregion=(0, 0, mw, y + h + 1))
        else:
            self._mh = mh
            canvas.configure(scrollregion=(0, 0, mw, mh))

    def add_image_observer(self, observer):
        self._image_observers.append(observer)

    def _on_motion(self, event):
        canvas = self._canvas
        images = self._images

        # x = event.x + canvas.xview()[0] * (self._x)
        x = event.x
        y = event.y + canvas.yview()[0] * self._mh

        res = rt.find_closest_enclosing(images, x, y)

        if res:
            self._f_rid = rid = res[0]
            self._unbind(canvas)

            rct = rt.get_rectangle(images, rid)
            self._text = canvas.create_text(*rct.center, text=rct.label)
            canvas.itemconfigure(rct.rid, outline="red")
            self._prev = rid
        else:
            self._unbind(canvas)
            self._f_rid = None

    def _unbind(self, canvas):
        prev = self._prev
        text = self._text

        if prev:
            canvas.itemconfigure(prev, outline="black")

        if text:
            canvas.delete(text)

    def _create_draw(self, images, items, image_buffer, canvas, index, xywh):
        width = xywh[2]
        height = xywh[3]

        ph_im = ImageTk.PhotoImage(
            Image.frombuffer(
                "RGB",
                (width, height),
                image_buffer.get_image(index),
                "raw"))

        iid = canvas.create_image(
            xywh[0], xywh[1],
            image=ph_im, anchor=tk.NW)

        bbox = canvas.bbox(iid)
        rid = canvas.create_rectangle(*bbox)

        images[index] = img = ImageRectangle(
            rid, iid, width, height,
            ph_im, image_buffer, index)

        items.append(img)

        return img

    def _update_draw(self, images, items, image_buffer, canvas, index, xywh):
        container = images[index]

        iid = canvas.create_image(
            xywh[0], xywh[1],
            image=container.photo_image,
            anchor=tk.NW)

        bbox = canvas.bbox(iid)
        rid = canvas.create_rectangle(*bbox)

        container.rid = rid
        container.iid = iid
        container.bbox = bbox

        images[index] = container

        return container

    def _on_mouse_wheel(self, event):
        # todo: should create this function as a utility function
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            self._canvas.yview_scroll(1, "units")

        if event.num == 4 or event.delta == 120:
            self._canvas.yview_scroll(-1, "units")

    def on_right_click(self, callback):
        self._right_click_callback = callback

    def on_left_click(self, callback):
        self._left_click_callback = callback

    def _on_left_click(self, event):
        rid = self._f_rid

        if rid:
            self._left_click_callback(rid, event)

    def _on_right_click(self, event):
        rid = self._f_rid

        if rid:
            # menu = tk.Menu(self._frame, tearoff=0)
            # menu.add_command(label="Delete", command=self._delete_image)
            # menu.tk_popup(event.x_root, event.y_root)

            self._right_click_callback(rid, event)

    def delete_image(self, rid):
        #todo: optimize this. avoid deleting everything
        # and redrawing everything.

        items = self._items
        canvas = self._canvas

        canvas.unbind("<Motion>")

        self._f_rid = None
        self._prev = None

        # with engine.connect() as connection:
        rct = self._images.pop(rid)

        self._unbind(canvas)

        self._text = None

        p = rct.position
        k = p - 1

        for item in items[p::]:
            item.position = p
            p += 1

        for item in items:
            canvas.delete(item.rid)
            canvas.delete(item.iid)

        items.pop(k)  # remove item from list

        #redraw everything...
        self._draw_images(self._width, self._height, self._image_buffer, False)

        # rct.delete(connection)

        # with engine.connect() as connection:
        #     for item in items:
        #         item.submit(connection)

            # pos = len(items) - 1

            # self._controller.samples.position = pos if pos > 0 else 0

        canvas.bind("<Motion>", self._on_motion)