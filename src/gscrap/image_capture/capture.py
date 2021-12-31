from Xlib import display, X

import numpy as np

from PIL import Image


def snapshot(rt, xywh):
    w = xywh[2]
    h = xywh[3]

    return rt.get_image(xywh[0], xywh[1], w, h, X.ZPixmap, 0xffffffff).data

    # return raw.data
    # return Image.frombytes("RGB", (w, h), raw.data, "raw", "BGRX")


class CaptureHandler(object):
    def __init__(self, display, window):
        self._display = display
        self._window = window

    def capture(self, bbox):
        l, t = bbox[0], bbox[1]
        w, h = bbox[2] - l, bbox[3] - t

        window = self._window

        ltwh = l + window.xywh[0], t + window.xywh[1], w, h

        return np.array(Image.frombytes(
            "RGB",
            (w, h),
            snapshot(self._display, ltwh),
            "raw",
            "BGRX"))


class CaptureContext(object):
    def __init__(self, window):
        self._display = None
        self._window = window

    def __enter__(self):
        self._display = dsp = display.Display().screen().root

        return CaptureHandler(dsp, self._window)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._display = None


def capture_context(window):
    return CaptureContext(window)