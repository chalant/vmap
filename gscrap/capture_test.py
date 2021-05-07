from image_capture import image_capture as ic
from Xlib import display, X
import time

from PIL import Image
import numpy as np


# dsp = display.Display().screen().root
#
# t0 = time.time()
# #
# # for i in range(100):
# np.asarray(Image.frombytes("RGB", (800, 800), ic.snapshot(dsp, (0, 0, 800, 800)), "raw", "BGRX"))
#
# print(time.time() - t0)
#
dsp = display.Display().screen().root

t0 = time.time()

frame = ic.snapshot(dsp, (0, 0, 800, 800))

print(time.time() - t0)

# frames = []
# dsp = display.Display().screen().root
#
# t0 = time.time()
#
# for _ in range(100):
#     frames.append(ic.snapshot(dsp, (0, 0, 8, 8)))
#
# print(time.time() - t0)