import abc

import tkinter as tk

from sqlalchemy import text
import cv2

from tools.detection.data import interface

FILTER_TYPES = ["Color", "Resize", "Threshold", "Blur"]
BLUR_TYPES = ["Gaussian" ,"Average", "Median"]

_THRESHOLD_TYPES = {
    "BINARY":cv2.THRESH_BINARY,
    "BINARY_INV":cv2.THRESH_BINARY_INV,
    "TRUNC":cv2.THRESH_TRUNC,
    "TO_ZERO":cv2.THRESH_TOZERO,
    "TO_ZERO_INV":cv2.THRESH_TOZERO_INV
}

FILTERS_BY_TYPE = {
    "Color":["Grey"],
    "Blur": BLUR_TYPES,
    "Threshold":list(_THRESHOLD_TYPES.keys())
}

class Filters(object):
    def get_filter_types(self):
        return FILTER_TYPES

    def get_filters(self, filter_type):
        return FILTERS_BY_TYPE[filter_type]

    def create_filter(self, filter_type, filter_name, position):
        """

        Parameters
        ----------
        filter_type
        filter_name
        position

        Returns
        -------
        Filter
        """
        if filter_type == "Blur":
            if filter_name == "Gaussian":
                return GaussianBlur(position)
            elif filter_name == "Average":
                return AverageBlur(position)
            elif filter_name == "Median":
                return MedianBlur(position)
            else:
                raise ValueError("Unknown filter: {} {}".format(filter_name, filter_type))

        elif filter_type == "Threshold":
            if filter_name not in _THRESHOLD_TYPES:
                raise ValueError("Unknown filter: {} {}".format(filter_name, filter_type))
            return Threshold(position, filter_name)
        elif filter_type == "Color":
            if filter_name == "Grey":
                return Grey(position)
            else:
                raise ValueError("Unknown filter: {} {}".format(filter_name, filter_type))
        else:
            raise  ValueError("Unknown filter type: {}")

class Filter(abc.ABC):
    def __init__(self, position):
        self.position = position

    @property
    @abc.abstractmethod
    def type(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self):
        raise NotImplementedError

    @abc.abstractmethod
    def apply(self, img):
        raise NotImplementedError

    @abc.abstractmethod
    def render(self, container):
        raise NotImplementedError

    @abc.abstractmethod
    def load_parameters(self, connection, group):
        raise NotImplementedError

    @abc.abstractmethod
    def store_parameters(self, connection, group):
        raise NotImplementedError

    def __lt__(self, other):
        return other.position < self.position

    def __le__(self, other):
        return other.position <= self.position

    def __eq__(self, other):
        return other.position == self.position

class Threshold(Filter):
    def __init__(self, position, thresh_type, thresh_value=127, max_value=255):
        super(Threshold, self).__init__(position)

        self._thresh_type = thresh_type
        self._thresh_value = thresh_value
        self._max_value = max_value

    def type(self):
        return "Threshold"

    def name(self):
        return self._thresh_type

    def apply(self, img):
        return cv2.threshold(
            img,
            self._thresh_value,
            self._max_value,
            _THRESHOLD_TYPES[self._thresh_type])[1]

    def render(self, container):
        pass

    def load_parameters(self, connection, group):
        data = interface.get_parameters(connection, self, group)

        self._thresh_type = data["type"]
        self._max_value = data["max_value"]
        self._thresh_value  = data["thresh_value"]

    def store_parameters(self, connection, group):
        connection.execute(
            text(
                """
                INSERT OR REPLACE INTO threshold (group, position, thresh_value, max_value, type)
                VALUES (:group, :position, :thresh_value, :max_value, :type)
                """),
            group=group,
            position=self.position,
            thresh_value=self._thresh_value,
            max_value=self._max_value,
            type=self._thresh_type
        )

class GaussianBlur(Filter):
    def __init__(self, position, ksizeX=5, ksizeY=5, sigmaX=0, sigmaY=None):
        super(GaussianBlur, self).__init__(position)

        self._kx = ksizeX
        self._ky = ksizeY
        self._sx = sigmaX
        self._sy = sigmaY

    @property
    def type(self):
        return "Blur"

    @property
    def name(self):
        return "Gaussian"

    @property
    def ksizeX(self):
        return self._kx

    @property
    def ksizeY(self):
        return self._ky

    @ksizeX.setter
    def ksizeX(self, value):
        self._kx = value

    @ksizeY.setter
    def ksizeY(self, value):
        self._ky = value

    def apply(self, img):
        return cv2.GaussianBlur(img.array, (self._kx, self._ky), self._sx, sigmaY=self._sy)

    def render(self, container):
        # todo
        self._ksize = tk.Label(container)

    def load_parameters(self, connection, group):
        data = interface.get_parameters(connection, self, group)

        self._kx = data["ksizeX"]
        self._ky = data["ksizeY"]
        self._sx = data["sigmaX"]
        self._sy = data["sigmaY"]

    def store_parameters(self, connection, group):
        connection.execute(
            text(
                """
                INSERT OR REPLACE INTO gaussian_blur (group, position, ksizeX, ksizeY, sigmaX, sigmaY) 
                VALUES (:group, :position, :ksizeX, :ksizeY, :sigmaX, :sigmaY) 
                """),
            group=group,
            position=self.position,
            ksizeX=self.ksizeX,
            ksizeY=self.ksizeY,
            sigmaX=self._sx,
            sigmaY=self._sy
        )

class AverageBlur(Filter):
    def __init__(self, position, ksizeX=5, ksizeY=5):
        super(AverageBlur, self).__init__(position)
        self._kx = ksizeX
        self._ky = ksizeY

        self._type = "Blur"

    @property
    def type(self):
        return "Blur"

    @property
    def name(self):
        return "Average"

    @property
    def ksizeX(self):
        return self._kx

    @property
    def ksizeY(self):
        return self._ky

    @ksizeX.setter
    def ksizeX(self, value):
        self._kx = value

    @ksizeY.setter
    def ksizeY(self, value):
        self._ky = value

    def apply(self, img):
        return cv2.blur(img, (self._kx, self._ky))

    def render(self, container):
        pass

class MedianBlur(Filter):
    def __init__(self, position, ksize=5):
        super(MedianBlur, self).__init__(position)
        self._k = ksize

    @property
    def type(self):
        return "Blur"

    @property
    def name(self):
        return "Gaussian"

    @property
    def ksize(self):
        return self._kx

    @ksize.setter
    def ksize(self, value):
        self._kx = value

    def apply(self, img):
        return cv2.medianBlur(img, self._k)

    def render(self, container):
        pass

class Grey(Filter):
    def __init__(self, position):
        super(Grey, self).__init__(position)
        self._type = "Color"

    @property
    def type(self):
        return "Color"

    @property
    def name(self):
        return "Grey"

    def apply(self, img):
        if img.mode == "RGB":
            return cv2.cvtColor(img.array, cv2.COLOR_BGR2GRAY)
        return img