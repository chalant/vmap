from Xlib import display, X

def snapshot(rt, xywh):
    w = xywh[2]
    h = xywh[3]

    # shift by one pixel to compensate for cz outline width
    return rt.get_image(xywh[0], xywh[1], w, h, X.ZPixmap, 0xffffffff).data

    # return raw.data
    # return Image.frombytes("RGB", (w, h), raw.data, "raw", "BGRX")

class CaptureHandler(object):
    def __init__(self, display):
        self._display = display

    def capture(self, ltwh):
        return snapshot(self._display, ltwh)

class CaptureContext(object):
    def __init__(self):
        self._display = None

    def __enter__(self):
        self._display = dsp = display.Display().screen().root

        return CaptureHandler(dsp)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._display.close()

def capture_context():
    return CaptureContext()