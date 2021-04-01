#user can choose between, detection models for each label

# note: filtering is decoupled from the detection algorithm
from abc import ABC, abstractmethod
from concurrent import futures

import cv2
import numpy as np

from data import engine

#difference matching detection tolerance
DIFF_MAX = 10 #todo: should let the user setup this

class Detection(object):
    @abstractmethod
    def detect(self, img):
        raise NotImplemented

class NullDetection(Detection):
    def __init__(self):
        pass

    def detect(self, img):
        return "Unknown"

class Detector(object):
    def __init__(self):
        self._detector = NullDetection()

    def detect(self, img):
        self._detector.detect(img)

    def set_detection(self, detector):
        """

        Parameters
        ----------
        detector: Detector

        Returns
        -------

        """
        self._detector = detector

class Tesseract(Detection):
    #todo: detect through tesseract
    def __init__(self):
        self._filters = None

    def initialize(self, capture_zone):
        pass

    def detect(self, img):
        print("Tesseract!")
        #todo
        filtered_img = self._filters.apply(img)

    def set_filters(self, filters):
        self._filters = filters


class DifferenceMatching(Detection):
    def __init__(self):
        self._filters = None
        self._source = None

    def detect(self, img):
        filtered_image = self._filters.apply(img)

        best_match_diff = DIFF_MAX
        name = "Unknown"
        best_match_name = "Unknown"

        for meta in self._source.get_images():
            diff_img = cv2.absdiff(filtered_image, meta.image)
            rank_diff = int(np.sum(diff_img) / 255)

            if rank_diff < best_match_diff:
                best_match_diff = rank_diff
                name = meta.label

        #todo: we need to setup a detection threshold which determines the "tolerance", the lowest
        # the better. Otherwise, we would get false positives (threshold could be set by user)

        if (best_match_diff < DIFF_MAX):
            best_match_name = name

        return best_match_name

    def set_filters(self, filters):
        self._filters = filters

    def set_image_source(self, source):
        self._source = source
