import Xlib.display

import xdo
from xdo.xdo import libxdo

# xdo = Xdo()
# try:
#     win_id = xdo.select_window_with_click()
# except XdoException:
#     print("Aborted!")
#     raise
# # print(xdo.get_window_location(win_id), xdo.get_window_size(win_id))
# xdo.enable_feature()

def get_active_window(dsp, root):
    win_id = root.get_full_property(dsp.intern_atom('_NET_ACTIVE_WINDOW'),
                                    Xlib.X.AnyPropertyType).value[0]
    try:
        return dsp.create_resource_object('window', win_id)
    except Xlib.error.XError:
        pass

def get_absolute_geometry(root, win):
    """
    Returns the (x, y, height, width) of a window relative to the top-left
    of the screen.
    """
    geom = win.get_geometry()
    x, y = geom.x, geom.y

    while True:
        parent = win.query_tree().parent
        pgeom = parent.get_geometry()
        x += pgeom.x
        y += pgeom.y
        if parent.id == root.id:
            break
        win = parent

    return x, y, geom.width, geom.height

def to_bbox(x, y, w, h):
    """
    Returns (x1, y1, x2, y2) relative to the top-left of the screen.
    """
    return (x, y, x + w, y + h)


class WindowSelectionEvent(object):
    __slots__ = ('xywh', 'window_id', 'width', 'height')

    def __init__(self, xywh, win_id):
        self.xywh = xywh
        self.window_id = win_id

        x, y , w, h  = xywh

        self.width = w
        self.height = h


class WindowSelector(object):
    def __init__(self, container):
        """

        """
        self._container = container

        self._xdo = xdo.Xdo()

        def null_fn():
            pass

        def null_event_fn(event):
            pass

        self._on_abort_callback = null_fn
        self._on_selected_callback = null_event_fn
        self._on_error_callback = null_fn

    def start_selection(self, on_selected, on_abort, on_error=None):
        # view = self._view

        container = self._container

        self._on_abort_callback = on_abort
        self._on_selected_callback = on_selected

        if on_error:
            self._on_error_callback = on_error

        container.grab_set_global()
        container["cursor"] = "target"
        container.bind('<Button-1>', self._on_click)
        container.bind('<Button-3>', self._on_abort)

        # if not self._window_selected:
        #     pass
        # else:
        #     view.capture_button["state"] = "disable"
        #     view.window_selection_button["text"] = "Select Window"

    def resize_window(self, win_id, width, height):
        width = int(width)
        height = int(height)

        xdo_ = self._xdo
        xdo_.set_window_size(win_id, width, height)

        libxdo.xdo_wait_for_window_size(xdo_._xdo, win_id, width, height, 0, 0)

    # def update(self):
    #     self._view.capture_button["state"] = "disabled"
    #     self._view.capture_button["text"] = "Start Capture"

    def _on_abort(self, event):
        container = self._container
        container.grab_release()

        self._on_abort_callback()  # callback if the
        container.config(cursor = "arrow")

    def _on_click(self, event):
        container = self._container

        try:
            win_id = self._xdo.get_window_at_mouse()
            container.grab_release()

            self._xdo.activate_window(win_id)
            self._xdo.wait_for_window_active(win_id)

            dsp = Xlib.display.Display()
            root = dsp.screen().root

            self._on_selected_callback(WindowSelectionEvent(
                get_absolute_geometry(root, get_active_window(dsp, root)),
                win_id))
        except:
            container.grab_release()
            self._on_error_callback()

        container["cursor"] = "arrow"

        container.unbind("<Button-1>")
        container.unbind("<Button-3>")
        # self._manager.display(self._p)