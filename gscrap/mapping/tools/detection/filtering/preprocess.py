import cv2
import numpy as np
from PIL import Image

import tkinter as tk

from gscrap.rectangles import rectangles as rct

from gscrap.data.filters import filters

class Rectangle(object):
    def __init__(self, rid, tid, rct_idx, txt_idx, bbox, filter_):
        self._rid = rid
        self._bbox = bbox
        self._filter = filter_
        self._tid = tid
        self._rct_idx = rct_idx
        self._txt_idx = txt_idx

    @property
    def rid(self):
        return self._rid

    @property
    def tid(self):
        return self._tid

    @property
    def text_idx(self):
        return self._txt_idx

    @property
    def rectangle_idx(self):
        return self._rct_idx

    @property
    def bbox(self):
        return self._bbox

    def move(self, dx, dy):
        bbox = self._bbox
        bbox[0] += dx
        bbox[1] += dy
        bbox[2] += dx
        bbox[3] += dy

    @bbox.setter
    def bbox(self, value):
        self._bbox = value

    @property
    def position(self):
        return self._filter.position

    @position.setter
    def position(self, value):
        self._filter.position = value

    @property
    def top_left(self):
        bbox = self._bbox
        return bbox[0], bbox[1]

    @property
    def rid(self):
        return self._rid

    def delete(self, connection):
        #todo: delete the filter
        pass

class ImageWrapper(object):
    def __init__(self, image):
        self.array = np.asarray(image)
        self.mode = image.mode

    def image(self):
        Image.from_array(self.array)

class FiltersData(object):
    def get_filter_groups(self, connection):
        return

    def get_filters(self, connection, group):
        pass

    def get_filter(self, connection, type_, id_):
        pass

class AddFilterView(object):
    def __init__(self, container, controller):
        pass

    def render(self):
        pass

class FiltersView(object):
    def __init__(self, container, controller):
        self._controller = controller

        self._frame = frame = tk.Frame(container)
        self._commands = commands = tk.Frame(frame)
        self.canvas = canvas = tk.Canvas(frame)

        self._vbar = vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        self._hbar = hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        self._import_filters = import_ = tk.Button(commands, text="Import", command=controller.import_filters)
        self._add_filter = add_ = tk.Button(commands, text="Add", command=controller.add_filter)

        frame.pack()
        commands.pack()
        import_.pack(side=tk.LEFT)
        add_.pack(side=tk.LEFT)

        canvas.pack()
        vbar.pack(orient=tk.VERTICAL, side=tk.RIGHT)
        hbar.pack(orient=tk.HORIZONTAL, side=tk.BOTTOM)


    def render(self, container):
        self._frame.tkraise(container)

class FiltersTool(object):
    '''
    Filters Interface
    '''

    def __init__(self, filter_factory):
        '''

        Parameters
        ----------
        filter_factory: controllers.tools.preprocess.filters.Filters
        '''

        self._rectangles = {} #rectangles on canvas
        self._pipeline = []

        self._position = 0

        self._items = []
        self._filter_factory = filter_factory

    def on_new(self, group_name):
        #todo:
        pass

    def on_import(self, canvas, connection, group_name):
        pipeline = self._pipeline
        rectangles = self._rectangles
        items = self._items

        pipeline.clear()
        rectangles.clear()

        #clear canvas
        for item in items:
            canvas.delete(item)

        item_idx = 0

        x = 0
        y = 0
        mw = canvas.winfo_width()

        for filter_ in self._load_filters(connection, group_name):
            pipeline.append(filter_)
            tid = canvas.create_text(x + 3, y + 2, text=filter_.type)
            items.append(tid)

            txt_idx = item_idx

            item_idx += 1


            x0, y0, x1, y1 = canvas.bbox(tid)

            x = x1 + 2

            if x >= mw:
                x = 0
                y = y1 + 1

            bbox = (x0 - 2, x, y0 - 1, y)

            rid = canvas.create_rectangle(*bbox)

            items.append(rid)

            rct_idx = item_idx

            item_idx += 1

            rectangles[rid] = Rectangle(rid, tid, rct_idx, txt_idx, bbox, filter_)

        self._position = len(pipeline)
        self._x = x
        self._y = y
        self._item_idx = item_idx

    def _load_filters(self, connection, group_name):
        factory = self._filter_factory

        for res in filters.get_filters(connection, group_name):
            type_ = res["type"]
            name = res["name"]
            position = res["position"]

            flt = factory.create_filter(type_, name, position)
            flt._load_parameters(connection, group_name)

            yield flt

    def get_filter(self, x, y):
        # get the filter at some position on the canvas
        return rct.find_closest_enclosing(self._rectangles, x, y)

    def delete_filter(self, canvas, connection, rid):
        filter_ = self._rectangles.pop(rid)

        pipeline = self._pipeline
        items = self._items

        #replace deleted rectangle with rectangle on the right

        pos = filter_.position

        flt0 = pipeline[pos+1]

        p = flt0.position
        flt0.position = p - 1

        canvas.delete(flt0.rid)
        canvas.delete(flt0.tid) #remove text

        items.pop(flt0.text_idx)
        items.pop(flt0.rectangle_idx)

        pr = pipeline[pos]

        bbox1 = flt0.bbox
        bbox2 = pr.bbox

        dx = bbox1[0] - bbox2[0]
        dy = bbox1[1] - bbox2[1]

        # move drawing
        flt0.move(-dx, -dy)
        canvas.move(flt0.rid, -dx, -dy)
        canvas.move(flt0.tid, -dx, -dy)

        #shift all positions

        mw = canvas.winfo_width()

        for flt in pipeline[pos+2::]:
            bbox0 = flt0.bbox
            bbox = flt.bbox

            x = bbox0[2]
            y = bbox0[1]

            dx = x - bbox[0]
            dy = y - bbox[1]

            #if the rectangle might exceed the canvas width, just move it to the first column and
            # stay on the same row.

            if bbox[2] + dx >= mw:
                dx = 1 - bbox[0]
                dy = 0

            flt.move(dx, dy)
            canvas.move(flt.rid, dx, dy)
            canvas.move(flt.tid, dx, dy)

        pipeline.pop(pos) #remove filter from pipeline
        filter_.delete(connection) #delete filter from database
        self._position = len(pipeline)

    def clear(self, canvas):
        self._pipeline.clear()
        self._rectangles.clear()
        self._position = 0
        self._x = 0
        self._y = 0

        for item in self._items:
            canvas.delete(item)

    def add_filter(self, canvas, filter_type, filter_name):
        rectangles = self._rectangles

        pipeline = self._pipeline
        items = self._items
        item_idx = self._item_idx
        position = self._position

        filter_ = self._filter_factory.create_filter(filter_type, filter_name, position)

        position += 1

        mw = canvas.winfo_width()

        x, y = self._x, self._y

        pipeline.append(filter_)

        tid = canvas.create_text(x + 3, y + 2, text=filter_.type)

        x0, y0, x1, y1 = canvas.bbox(tid)

        x = x1 + 2

        if x >= mw:
            x = 0
            y = y1 + 1

        bbox = (x0 - 2, x, y0 - 1, y)

        rct_idx = item_idx
        item_idx += 1
        txt_idx = item_idx
        item_idx += 1

        rid = canvas.create_rectangle(*bbox)

        rectangles[rid] = Rectangle(rid, tid, rct_idx, txt_idx, bbox, filter_)

        items.append(rid)
        items.append(tid)

        self._position = position

    def filter_image(self, img):
        #applies the sequence of filters to the image
        im = ImageWrapper(img)

        for p in self._pipeline:
            im = p.apply(im)

        return im.image()

def preprocess_image(image):
    # blur = cv2.GaussianBlur(cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2GRAY), (5, 5), 0)
    # The best threshold level depends on the ambient lighting conditions.
    # For bright lighting, a high threshold must be used to isolate the cards
    # from the background. For dim lighting, a low threshold must be used.
    # To make the card detector independent of lighting conditions, the
    # following adaptive threshold method is used.
    #
    # A background pixel in the center top of the image is sampled to determine
    # its intensity. The adaptive threshold is set at 50 (THRESH_ADDER) higher
    # than that. This allows the threshold to adapt to the lighting conditions.
    # img_w, img_h = np.shape(image)[:2]
    # bkg_level = gray[int(img_h / 100)][int(img_w / 2)]
    # # thresh_level = bkg_level + BKG_THRESH
    # thresh_level = 127
    #
    # retval, thresh = cv2.threshold(blur, thresh_level, 255, cv2.THRESH_BINARY)


    # sample known white pixel intensity to determine good threshold level
    # white_level = thresh[1,1]

    # thresh_level = white_level - CARD_THRESH
    # thresh_level = 127
    #
    # if (thresh_level <= 0):
    #     thresh_level = 1

    retval, query_thresh = cv2.threshold(
        cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2GRAY),
        0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # # Split in to top and bottom half (top shows rank, bottom shows suit)
    # Qrank = query_thresh[20:185, 0:128]
    # Qsuit = query_thresh[186:336, 0:128]
    #
    # # Find rank contour and bounding rectangle, isolate and find largest contour
    # dummy, Qrank_cnts, hier = cv2.findContours(Qrank, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Qrank_cnts = sorted(Qrank_cnts, key=cv2.contourArea, reverse=True)
    #
    # # Find bounding rectangle for largest contour, use it to resize query rank
    # # image to match dimensions of the train rank image
    # if len(Qrank_cnts) != 0:
    #     x1, y1, w1, h1 = cv2.boundingRect(Qrank_cnts[0])
    #     Qrank_roi = Qrank[y1:y1 + h1, x1:x1 + w1]
    #     Qrank_sized = cv2.resize(Qrank_roi, (RANK_WIDTH, RANK_HEIGHT), 0, 0)
    #     qCard.rank_img = Qrank_sized
    #
    # # Find suit contour and bounding rectangle, isolate and find largest contour
    # dummy, Qsuit_cnts, hier = cv2.findContours(Qsuit, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Qsuit_cnts = sorted(Qsuit_cnts, key=cv2.contourArea, reverse=True)
    #
    # # Find bounding rectangle for largest contour, use it to resize query suit
    # # image to match dimensions of the train suit image
    # if len(Qsuit_cnts) != 0:
    #     x2, y2, w2, h2 = cv2.boundingRect(Qsuit_cnts[0])
    #     Qsuit_roi = Qsuit[y2:y2 + h2, x2:x2 + w2]
    #     Qsuit_sized = cv2.resize(Qsuit_roi, (SUIT_WIDTH, SUIT_HEIGHT), 0, 0)
    #     qCard.suit_img = Qsuit_sized
    #
    # return qCard

    return Image.fromarray(query_thresh)