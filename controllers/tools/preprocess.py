#module for image pre-process functions.

# will be used for to pre-process elements for number detection, rank detection, suit detection...

import cv2
import numpy as np
from PIL import Image

import tkinter as tk

# Sample known white pixel intensity to determine good threshold level

### Constants ###

# Adaptive threshold levels
BKG_THRESH = 60
CARD_THRESH = 30

# Width and height of card corner, where rank and suit are
CORNER_WIDTH = 32
CORNER_HEIGHT = 84

# Dimensions of rank train images
RANK_WIDTH = 70
RANK_HEIGHT = 125

# Dimensions of suit train images
SUIT_WIDTH = 70
SUIT_HEIGHT = 100

RANK_DIFF_MAX = 2000
SUIT_DIFF_MAX = 700

CARD_MAX_AREA = 120000
CARD_MIN_AREA = 25000

FILTER_TYPES = ["Color", "Resize", "Threshold"]
BLUR_TYPES = ["Gaussian" ,"Average", "Median"]

class ImageWrapper(object):
    def __init__(self, image):
        self.array = np.asarray(image)
        self.mode = image.mode

    def image(self):
        Image.from_array(self.array)

class FilterType(object):
    pass

class Blur(FilterType):
    def __init__(self):
        pass

    def get_types(self):
        return BLUR_TYPES

class Filter(object):
    def __init__(self, position):
        self.position = position

    def apply(self, img):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError

    def __lt__(self, other):
        return other.position < self.position

    def __le__(self, other):
        return other.position <= self.position

    def __eq__(self, other):
        return other.position == self.position

class GaussianBlur(Filter):
    def __init__(self, position, ksizeX, ksizeY, sigmaX, sigmaY=None):
        super(GaussianBlur, self).__init__(position)

        self._kx = ksizeX
        self._ky = ksizeY
        self._sx = sigmaX
        self._sy = sigmaY
        self.position = position

        self._type = "Blur"

    def apply(self, img):
        return cv2.GaussianBlur(img.array, (self._kx, self._ky), self._sx, sigmaY=self._sy)

    def render(self):
        pass

class Grey(Filter):
    def __init__(self, position):
        super(Grey, self).__init__(position)
        self._type = "Color"

    def apply(self, img):
        if img.mode == "RGB":
            return cv2.cvtColor(img.array, cv2.COLOR_BGR2GRAY)
        return img

class FiltersData(object):
    def get_filter_groups(self, connection):
        return

    def get_filters(self, connection, group):
        pass

    def get_filter(self, connection, type_, id_):
        pass

class FilterView(object):
    def __init__(self, container):
        self._frame = frame = tk.Frame(container)

        self._canvas = canvas = tk.Canvas(frame)

        self._vbar = vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        self._hbar = hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        self._filter_tool = FilterTool()

    def render(self):
        self._frame.tkraise()

class FilterTool(object):
    '''
    Filters Interface
    '''

    def __init__(self, filter_data, canvas):
        self._rectangles = {} #rectangles on canvas
        self._pipeline = []

        self._position = 0

        self._canvas = canvas

        self._filter_data = filter_data

    def on_new(self, group_name):
        pass

    def on_import(self, connection, group_name):
        pipeline = self._pipeline
        rectangles = self._rectangles

        if pipeline:
            pipeline.clear()

        if rectangles:
            rectangles.clear()

        for filter_ in self._filter_data.get_filters(connection, group_name):
            pipeline.append(filter_)

    def on_hover(self, event):
        # handles hovering over the filters
        pass

    def clear(self):
        self._pipeline.clear()
        self._rectangles.clear()

    def on_left_click(self, event):
        #todo: return the selected filter
        pass

    def on_right_click(self, event):
        pass

    def add_filter(self, filter_):
        #todo: draw the filter on the canvas
        pass

    def insert_filter(self, position, filter_):
        pass

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