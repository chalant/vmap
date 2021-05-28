from abc import ABC, abstractmethod

import numpy as np

def _as_floats(image0, image1):
    """
    Promote im1, im2 to nearest appropriate floating point precision.
    """
    float_type = np.result_type(image0.dtype, image1.dtype, np.float32)
    image0 = np.asarray(image0, dtype=float_type)
    image1 = np.asarray(image1, dtype=float_type)
    return image0, image1

class ImageComparator(ABC):
    @abstractmethod
    def different_image(self, im1, im2):
        raise NotImplementedError

class NullImageComparator(ImageComparator):
    def different_image(self, im1, im2):
        return True

class MeanSquaredError(ImageComparator):
    def __init__(self, threshold=0.0):
        self._threshold = threshold

    def different_image(self, im1, im2):
        float_type = np.result_type(im1.dtype, im2.dtype, np.float32)

        image0 = np.asarray(im1, dtype=float_type)
        image1 = np.asarray(im2, dtype=float_type)

        #returns true if the msr is above some threshold
        return np.mean((image0 - image1) ** 2, dtype=np.float64) > self._threshold

    def set_threshold(self, value):
        self._threshold = value

class Cropper(ImageComparator):
    def __init__(self, comparator, bbox=None):
        """

        Parameters
        ----------
        comparator: ImageComparator
        bbox
        """
        self._comparator = comparator
        self._bbox = bbox

    def different_image(self, im1, im2):
        x0, y0, x1, y1 = self._bbox

        return self._comparator.different_image(
            im1[y0:y1, x0:x1, :],
            im2[y0:y1, x0:x1, :])

    def set_bbox(self, bbox):
        self._bbox = bbox

class Branching(ImageComparator):
    def __init__(self, comparator1, comparator2):
        """

        Parameters
        ----------
        comparator1: ImageComparator
        comparator2: ImageComparator
        """
        self._cmp1 = comparator1
        self._cmp2 = comparator2

    def different_image(self, im1, im2):

        #return false is the first comparison returns false
        if not self._cmp1.different_image(im1, im2):
            return False

        return self._cmp2.different_image(im1, im2)
