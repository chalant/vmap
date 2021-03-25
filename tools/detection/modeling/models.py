#user can choose between, detection models for each label

# note: filtering is decoupled from the detection algorithm

from concurrent import futures

import cv2
import numpy as np

from data import engine

#difference matching detection tolerance
DIFF_MAX = 10 #todo: should let the user setup this

class Tesseract(object):
    #todo: detect through tesseract
    def __init__(self, filters):
        self._filters = filters

    def initialize(self, capture_zone):
        pass

    def detect(self, img):
        print("Tesseract!")
        #todo
        filtered_img = self._filters.apply(img)


class DifferenceMatching(object):
    def __init__(self, filters):

        self._filters = filters
        self._pairs = []

    def detect(self, img):
        filtered_image = self._filters.apply(img)

        best_match_diff = DIFF_MAX
        name = "Unknown"
        best_match_name = "Unknown"

        for label, img in self._pairs:
            diff_img = cv2.absdiff(filtered_image, img)
            rank_diff = int(np.sum(diff_img) / 255)

            if rank_diff < best_match_diff:
                best_match_diff = rank_diff
                name = label

        #todo: we need to setup a detection threshold which determines the "tolerance", the lowest
        # the better. Otherwise, we would get false positives

        if (best_match_diff < DIFF_MAX):
            best_match_name = name

        return best_match_name

    def initialize(self, capture_zone):
        pool = futures.ThreadPoolExecutor(1)
        pairs = []
        pool.submit(self._load, pairs, capture_zone, self._filters)
        self._pairs = pairs

    def clear(self):
        #clear data
        self._pairs.clear()

    def _load(self, pairs, capture_zone, filters):
        #load and filter captured images.
        with engine.connect() as connection:
            for img in capture_zone.get_images(connection):
                pairs.append((img.label, filters.apply(img.get_image())))

        return pairs
