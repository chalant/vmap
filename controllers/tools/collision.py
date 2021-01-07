def direction(x0, y0, x1, y1):
    return x1 - x0, y1 - y0

class BoxCollision(object):
    def _hit(self, t, dt):
        return t / dt if dt != 0 else t / 0.0001

    def _swap(self, x, y):
        c = x
        x = y
        y = c
        return x, y

    def collision_info(self, px, py, dx, dy, bbox):
        rx0, ry0, rx1, ry1 = bbox

        nx = rx0 - px
        ny = ry0 - py

        fx = rx1 - px
        fy = ry1 - py

        nx = self._hit(nx, dx)
        ny = self._hit(ny, dy)

        fx = self._hit(fx, dx)
        fy = self._hit(fy, dy)

        if nx > fx:
            nx, fx = self._swap(nx, fx)
        if ny > fy:
            ny, fy = self._swap(ny, fy)

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
        return t, nrx, nry

    def collision_point(self, x, y, dx, dy, t):
        return x + t * dx, y + t * dy

    def overlapping(self, bbox1, bbox2):
        x0, y0, x1, y1 = bbox1

        if x1 < x0:
            x0, x1 = self._swap(x0, x1)
        if y1 < y0:
            y0, y1 = self._swap(y0, y1)

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