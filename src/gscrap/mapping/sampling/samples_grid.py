from gscrap.mapping.sampling import grid
from gscrap.mapping.sampling import image_grid

class DrawInfo(object):
    def __init__(self):
        self.items = []
        self.image_rectangles = {}

class SamplesGrid(object):
    def __init__(self, buffer, width, height):
        self._samples_buffer = buffer

        self._image_grid = grid.Grid(
            image_grid.ImageRectangleFactory(buffer),
            width,
            height)

        self._items = []
        self._image_rectangles = {}

        self._rendered = False

    def render(self, container):
        self._image_grid.render(container)

    def draw(self, draw_info, indices):
        image_rectangles = self._image_rectangles

        grid = self._image_grid

        image_grid.clear_canvas(grid, grid.canvas, image_rectangles.values())

        image_rectangles.clear()

        image_rectangles = draw_info.image_rectangles

        for i, item in zip(indices, draw_info.items):
            image_rectangles[i] = grid.add_item(item)

        grid.update()

    def update(self, draw_info, indices):
        grid = self._image_grid

        image_rectangles = draw_info.image_rectangles

        image_grid.clear_canvas(grid, grid.canvas, image_rectangles.values())

        grid.reload(self._get_elements(
            indices,
            image_rectangles))

    def _get_elements(self, indices, image_rectangles):
        for i in indices:
            yield image_rectangles[i]