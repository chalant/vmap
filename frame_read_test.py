import os
import subprocess

from gscrap.image_capture.video_recorder import read_video_params

from PIL import Image

from os import path

import numpy as np

class FrameSeeker(object):
    def __init__(self, path):
        self._params = params = read_video_params(path, 0)
        self._path = path
        self.resolution = np.array((params['width'], params['height']))
        print(params)

    def seek(self, frame_index):
        #todo: maybe truncate number.
        start_time = frame_index/self._params['fps']

        print(start_time)

        process = subprocess.Popen(
            ["ffmpeg",
             "-nostdin",
             "-ss", "{}".format(start_time),
             "-i", "{}".format(self._path),
             "-pix_fmt", "rgb24",
             "-frames:v", "1",
             "-f", "rawvideo",
             "pipe:"
             ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        params = self._params
        res = (params['width'], params['height'])

        bytes_, err = process.communicate()

        im = Image.frombytes("RGB", res, bytes_, "raw")
        im.show("Image")

pth = path.expanduser('{}/.gmap/videos/d1dd5fa294f34d46976c9901f44022f1.mp4'.format(os.environ['HOME']))
print("PATH", pth)

seeker = FrameSeeker(pth)
seeker.seek(7706)