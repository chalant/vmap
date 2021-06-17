from os import path

from tkinter import *

from gscrap.mapping.tools.detection.sampling import samples
from gscrap.mapping.tools.detection import image_grid

from gscrap.data import paths

class FakeCaptureZone(object):
    def __init__(self, bbox):
        self.width = bbox[2] - bbox[0]
        self.height = bbox[3] - bbox[1]
        self.bbox = bbox

class FakeVideoMetadata(object):
    def __init__(self):
        self.fps = 30
        self.path = path.join(paths.videos(), "0a2b56aa72344a4ebfc73a71b7ba3ba4.mp4")


master = Tk()

img_grid = image_grid.ImageGrid()

spl = samples.Samples(img_grid)

img_grid.render(master)

spl.load_samples(FakeVideoMetadata(), FakeCaptureZone((40,40,70,70)))
spl.draw()

mainloop()