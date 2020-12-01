from tkinter import *
import select

from Xlib.display import Display, _BaseDisplay
from Xlib import X
from Xlib.ext.xtest import fake_input
from Xlib.ext import record
from Xlib.protocol import rq
from Xlib.protocol import request, display as dis

"""Rect Tracker class for Python Tkinter Canvas"""
def groups(glist, numPerGroup=2):
    result = []

    i = 0
    cur = []
    for item in glist:
        if not i < numPerGroup:
            result.append(cur)
            cur = []
            i = 0

        cur.append(item)
        i += 1

    if cur:
        result.append(cur)

    return result


def average(points):
    aver = [0, 0]

    for point in points:
        aver[0] += point[0]
        aver[1] += point[1]

    return aver[0] / len(points), aver[1] / len(points)


class RectTracker:
    def __init__(self, canvas, win_id):
        self.canvas = canvas
        self.item = None
        self._entry = None
        self.win_id = win_id

    def draw(self, start, end, **opts):
        """Draw the rectangle"""
        return self.canvas.create_rectangle(*(list(start) + list(end)), **opts)

    def autodraw(self, **opts):
        """Setup automatic drawing; supports command option"""
        self.start = None
        self.canvas.bind("<Button-1>", self.__update, '+')
        self.canvas.bind("<B1-Motion>", self.__update, '+')
        self.canvas.bind("<ButtonRelease-1>", self.__stop, '+')

        self._command = opts.pop('command', lambda *args: None)
        self.rectopts = opts

    def __update(self, event):

        if not self.start:
            self.start = [event.x, event.y]
            return
        if self.item is not None:
            self.canvas.delete(self.item)
        self.item = self.draw(self.start, (event.x, event.y), **self.rectopts)
        self._command(self.start, (event.x, event.y))

    def __stop(self, event):
        self.start = None
        # self.canvas.delete(self.item)
        coords = self.canvas.coords(self.item) # todo: save coordinates and tag
        print("Coords", coords)
        clicked = StringVar()
        self._entry = e1 = OptionMenu(self.canvas, clicked, "Board")
        e1.bind("<Return>", self.evaluate)
        # e1.pack()
        w = self.canvas.create_window(coords[0], coords[1], window=e1)
        print("Bounds", self.canvas.bbox(w))
        self.item = None
        # grab_pointer(self.win_id)

    def evaluate(self, event):
        print("Added:", str(self._entry.get()))
        pass

    def hit_test(self, start, end, tags=None, ignoretags=None, ignore=[]):
        """
        Check to see if there are items between the start and end
        """
        ignore = set(ignore)
        ignore.update([self.item])

        # first filter all of the items in the canvas
        if isinstance(tags, str):
            tags = [tags]

        if tags:
            tocheck = []
            for tag in tags:
                tocheck.extend(self.canvas.find_withtag(tag))
        else:
            tocheck = self.canvas.find_all()
        tocheck = [x for x in tocheck if x != self.item]
        if ignoretags:
            if not hasattr(ignoretags, '__iter__'):
                ignoretags = [ignoretags]
            tocheck = [x for x in tocheck if x not in self.canvas.find_withtag(it) for it in ignoretags]

        self.items = tocheck

        # then figure out the box
        xlow = min(start[0], end[0])
        xhigh = max(start[0], end[0])

        ylow = min(start[1], end[1])
        yhigh = max(start[1], end[1])

        items = []
        for item in tocheck:
            if item not in ignore:
                x, y = average(groups(self.canvas.coords(item)))
                if (xlow < x < xhigh) and (ylow < y < yhigh):
                    items.append(item)

        return items

def grab_pointer(win_id):
    display = Display(':0')

    def handle_event(event):
        data = event.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, display.display, None, None)
            if event.type == X.ButtonPress:
                print("Pressed!")
                raise KeyboardInterrupt

    ctx = display.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.ButtonPressMask, X.ButtonReleaseMask),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }]
    )

    try:
        display.screen().root.grab_pointer(True, X.ButtonPressMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                           X.GrabModeAsync, 0, 0, X.CurrentTime)
        display.record_enable_context(ctx, handle_event)
        display.record_free_context(ctx)
    except KeyboardInterrupt:
        display.record_disable_context(ctx)
        display.ungrab_pointer(X.CurrentTime)
        # display.screen().root.ungrab_button(0, [0])
        display.flush()
        display.close() #important! otherwise os crashes

def main():
    from random import shuffle
    main = Tk()
    # load the .gif image file
    main.title("Table Mapper")
    gif1 = PhotoImage(file='poker_table.png')
    container = Frame(main, width=200, height=100)
    container.pack()

    def click():
        root = Toplevel()
        canv = Canvas(root, width=500, height=500)
        root.resizable(False, False)
        # canv.create_rectangle(50, 50, 250, 150, fill='red')
        canv.pack(fill=BOTH, expand=YES)
        root.update()
        print("ABS", root.winfo_rootx(), root.winfo_rooty())
        def closing():
            print("Closing")
            root.destroy()
        root.protocol("WM_DELETE_WINDOW", closing)

        rect = RectTracker(canv, root.winfo_id())
        # # draw some base requests
        # rect.draw([50, 50], [250, 150], fill='red', tags=('red', 'box'))
        # rect.draw([300, 300], [400, 450], fill='green', tags=('gre', 'box'))

        # put gif image on canvas
        # pic's upper left corner (NW) on the canvas is at x=50 y=10
        canv.create_image(0, 0, image=gif1, anchor=NW)
        canv.config(width=gif1.width(), height=gif1.height())

        # just for fun
        x, y = None, None

        def cool_design(event):
            global x, y
            kill_xy()

            dashes = [3, 2]
            x = canv.create_line(event.x, 0, event.x, 1000, dash=dashes, tags='no')
            y = canv.create_line(0, event.y, 1000, event.y, dash=dashes, tags='no')

        def kill_xy(event=None):
            canv.delete('no')

        canv.bind('<Motion>', cool_design, '+')

        # command
        def onDrag(start, end):
            # global x, y
            # items = rect.hit_test(start, end)
            # for x in rect.items:
            #     if x not in items:
            #         canv.itemconfig(x, fill='grey')
            #     else:
            #         canv.itemconfig(x, fill='blue')
            pass

        rect.autodraw(fill="", width=1, command=onDrag)

    #move to window selection state => deactivate button
    btn = Button(container, text="Select Window", command=click, font=("Mono", 11))
    btn.pack(pady=2, padx=2)
    # btn["state"] = DISABLED

    main.mainloop()


if __name__ == '__main__':
    main()
