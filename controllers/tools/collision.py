def direction(x0, y0, x1, y1):
    return x1 - x0, y1 - y0

def hit(t, dt):
    return t / dt if dt != 0 else t / 0.0001

def swap(x, y):
    c = x
    x = y
    y = c
    return x, y

def overlapping(bbox1, bbox2):
    x0, y0, x1, y1 = bbox1

    if x1 < x0:
        x0, x1 = swap(x0, x1)
    if y1 < y0:
        y0, y1 = swap(y0, y1)

    rx0, ry0, rx1, ry1 = bbox2

    return x0 <= rx1 and rx0 <= x1 and y0 <= ry1 and y1 >= ry0

def collision_point(x, y, dx, dy, t):
    return x + t * dx, y + t * dy

class DrawingCollision(object):
    def collision_info(self, px, py, dx, dy, bbox):
        rx0, ry0, rx1, ry1 = bbox

        nx = rx0 - px
        ny = ry0 - py

        fx = rx1 - px
        fy = ry1 - py

        nx = hit(nx, dx)
        ny = hit(ny, dy)

        fx = hit(fx, dx)
        fy = hit(fy, dy)

        if nx > fx:
            nx, fx = swap(nx, fx)
        if ny > fy:
            ny, fy = swap(ny, fy)

        # take the smallest collision time outside the rectangle
        if nx >= 0 and ny >= 0:
            nrx, nry = self._normal(nx, ny, dx, dy)
            t = min(nx, ny)
        elif ny < 0 and nx < 0:
            nrx, nry = self._normal(ny, nx, dx, dy)
            t = max(nx, ny)
        elif ny < -10000 or ny > 10000:
            nrx, nry = self._normal(nx, ny, dx, dy)
            t = nx
        elif nx < -10000 or nx > 10000:
            nrx, nry = self._normal(nx, ny, dx, dy)
            t = ny
        else:
            nrx, nry = self._normal(ny, nx, dx, dy)
            t = max(nx, ny)

        if t <= 1:
            return True, t, nrx, nry

        return False, t, nrx, nry

    def overlapping(self, bbox1, bbox2):
        x0, y0, x1, y1 = bbox1

        if x1 < x0:
            x0, x1 = swap(x0, x1)
        if y1 < y0:
            y0, y1 = swap(y0, y1)

        rx0, ry0, rx1, ry1 = bbox2

        return x0 <= rx1 and rx0 <= x1 and y0 <= ry1 and y1 >= ry0

    def _normal(self, nx, ny, dx, dy):
        if ny > nx:
            nry = 0
            if dx > 0:
                nrx = -1
            elif dx < 0:
                nrx = 1
            else:
                nrx = None
        elif ny < nx:
            nrx = 0
            if dy < 0:
                nry = 1
            elif dy > 0:
                nry = -1
            else:
                nry = None
        else:
            nrx = None
            nry = None
        return nrx, nry

class BoxCollision(object):
    def collision_info(self, px, py, dx, dy, bbox):
        rx0, ry0, rx1, ry1 = bbox

        nx = rx0 - px
        ny = ry0 - py

        fx = rx1 - px
        fy = ry1 - py


        nx = hit(nx, dx)
        ny = hit(ny, dy)

        fx = hit(fx, dx)
        fy = hit(fy, dy)

        if nx > fx:
            nx, fx = swap(nx, fx)
        if ny > fy:
            ny, fy = swap(ny, fy)

        t_hit_far = min(fx, fy)
        t = max(nx, ny)

        normal = self._normal(nx, ny, dx, dy)

        if t_hit_far < 0:
            return False, t, *normal

        if nx > fy or ny > fx:
            return False, t, *normal

        if t <= 1:
            return True, t, *normal

        return False, t, *normal

    def overlapping(self, bbox1, bbox2):
        x0, y0, x1, y1 = bbox1
        rx0, ry0, rx1, ry1 = bbox2

        return x0 <= rx1 and rx0 <= x1 and y0 <= ry1 and y1 >= ry0

    def _normal(self, nx, ny, dx, dy):
        if ny < nx:
            nry = 0
            if dx > 0:
                nrx = -1
            elif dx < 0:
                nrx = 1
            else:
                nrx = None
        elif ny > nx:
            nrx = 0
            if dy < 0:
                nry = 1
            elif dy > 0:
                nry = -1
            else:
                nry = None
        else:
            nrx = None
            nry = None
        return nrx, nry

class CollisionView(object):
    def __init__(self, mapper):
        self._mapper = mapper
        self._lines = []
        self._points = []

    def ray(self, x, y, dx, dy):
        self._lines.append(self._mapper.canvas.create_line(x, y, x + 25*dx, y + 25*dy, dash=(6,4)))

    def normal(self, x, y, nrx, nry):
        self._lines.append(self._mapper.canvas.create_line(x, y, x + nrx * 15, y + nry * 15, fill="red"))

    def point(self, x, y):
        self._points.append(self._mapper.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue"))

    def clear(self):
        for l in self._lines:
            self._mapper.canvas.delete(l)

        for p in self._points:
            self._mapper.canvas.delete(p)

        self._lines.clear()
        self._points.clear()