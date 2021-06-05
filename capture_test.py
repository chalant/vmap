from gscrap.image_capture import capture_loop as ic
from Xlib import display, X
import time

from PIL import Image
import numpy as np

import zlib
import lzma


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

frame = ic.snapshot(dsp, (0, 0, 1920, 1080))

im = Image.frombytes("RGB", (1920, 1080), frame, 'raw', 'BGRX')

im.show("IMAGE")

# print(type(frame))
#
# print("BYTE SIZE", len(frame))
# compressed = lzma.compress(frame)
# print("COMPRESSED BYTE SIZE", len(compressed))
#
# compressor = lzma.LZMACompressor()
#
# cmp = b''
# t = 0
#
# array_data = []
# for i in range(5):
#     c = compressor.compress(ic.snapshot(dsp, (i * 10, i * 10, 800, 800)))
#     cmp = cmp + c
#     t += len(c)
#     print("Partial!!", len(c))
#     array_data.append(c)
#
#
#
# y = compressor.flush()
# cmp = cmp + y
#
# t += len(y)
#
# print("TOTAL!", t)
# print("FLUSH!!!", len(y))
#
# print("IN MEMORY", len(cmp))
#
#
# print("DECOMPRESSED", len(lzma.decompress(compressed)))
# print("IN MEMORY", len(lzma.decompress(cmp)))
#
# decompressor = lzma.LZMADecompressor()
# print("DECOMPRESS!!!", len(decompressor.decompress(array_data[0]+array_data[1])))
#
# print(time.time() - t0)

# frames = []
# dsp = display.Display().screen().root
#
# t0 = time.time()
#
# for _ in range(100):
#     frames.append(ic.snapshot(dsp, (0, 0, 8, 8)))
#
# print(time.time() - t0)