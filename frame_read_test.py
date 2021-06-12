import os
import subprocess

from PIL import Image

from os import path

import numpy as np

from gscrap.image_capture.video_reader import read_video_params

class VideoReader(object):
    def __init__(self, path):
        """

        Parameters
        ----------
        video_metadata: gscrap.data.images.videos.VideoMetadata
        """
        self._path = path

    def read(self, from_=0):
        pth = self._path
        start_time = from_ / 30

        crop = (0, 0, 100, 80)

        x0, y0, x1, y1 = crop
        x, y, w, h = (x0, y0, x1 - x0, y1 - y0)

        command = [
            "ffmpeg",
            "-nostdin",
            "-ss", "{}".format(start_time),
            "-i", "{}".format(pth),
            "-filter:v", "crop={}:{}:{}:{}".format(w, h, x, y),
            "-pix_fmt", "rgb24",
            "-f", "rawvideo",
            "pipe:"]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        res = (crop[2], crop[3])

        im = Image.frombuffer("RGB", res, stdout[9: np.prod(res) * 27], "raw")
        im.show("Image")

        # while True:
        #     bytes_ = process.stdout.read(np.prod(dims) * 3)
        #     if not bytes_:
        #         process.terminate()
        #         break
        #     else:
        #         yield bytes_

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

        dims = (0, 0, 60, 60)

        process = subprocess.Popen(
            ["ffmpeg",
             "-nostdin",
             "-ss", "{}".format(start_time),
             "-i", "{}".format(self._path),
             "-pix_fmt", "rgb24",
             "-filter:v", "crop=60:60:0:0",
             "-frames:v", "1",
             "-f", "rawvideo",
             "pipe:"
             ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        res = (dims[2], dims[3])

        bytes_, err = process.communicate()
        # print(self._params, "PARAMS")

        # in_frame = np.frombuffer(bytes_, np.uint8).reshape(*res[::-1], 3)
        # im = Image.fromarray(in_frame)
        im = Image.frombuffer("RGB", res, bytes_, "raw")
        im.show("Image")

pth = path.expanduser('{}/.gmap/videos/f7ae89f213db4ff38fa878ae92a998b2.mp4'.format(os.environ['HOME']))
print("PATH", pth)

seeker = VideoReader(pth)
seeker.read(0)