#user can choose between, detection models for each label

# note: filtering is decoupled from the detection algorithm
from abc import ABC, abstractmethod
from concurrent import futures

import cv2
import numpy as np

from data import engine

#difference matching detection tolerance
DIFF_MAX = 10 #todo: should let the user setup this

class AbstractDetection(object):
    @abstractmethod
    def detect(self, img):
        raise NotImplemented


class NullDetection(AbstractDetection):
    def detect(self, img):
        return "Unknown"

class Detector(object):
    def __init__(self):
        self._detection = NullDetection()

    def detect(self, img):
        return self._detection.detect(img)

    def set_detection(self, detection):
        """

        Parameters
        ----------
        detector: Detector

        Returns
        -------

        """
        self._detection = detection

class Tesseract(AbstractDetection): #todo
    def detect(self, img):
        print("Tesseract!")
        #todo


class DifferenceMatching(AbstractDetection):
    def __init__(self, image_source):
        self._image_source = image_source

    def detect(self, img):
        best_match_diff = DIFF_MAX
        name = "Unknown"
        best_match_name = "Unknown"

        for label, image in self._image_source.get_images():
            diff_img = cv2.absdiff(img, image)
            rank_diff = int(np.sum(diff_img) / 255)

            if rank_diff < best_match_diff:
                best_match_diff = rank_diff
                name = label

        #todo: we need to setup a detection threshold which determines the "tolerance", the lowest
        # the better. Otherwise, we would get false positives (threshold could be set by user)

        if (best_match_diff < DIFF_MAX):
            best_match_name = name

        return best_match_name
