import lzma

from PIL import Image

import numpy as np

#todo: refactor this... major changes on how the data is stored

def from_bytes(meta, data):
    return np.asarray(Image.frombytes(meta.mode, meta.dimensions, data, "raw"))

class FrameSeeker(object):
    def __init__(self, video_meta):
        """

        Parameters
        ----------
        video_meta: gscrap.data.images.videos.VideoMetadata
        """
        self._meta = video_meta
        self._byte_size = video_meta.byte_size
        self._file = None

    def read(self, cursor):
        file = self._file

        byte_size = self._byte_size

        file.seek(byte_size * cursor)

        data = file.read(byte_size)

        if not data:
            raise EOFError("No Image")

        return from_bytes(self._meta, lzma.decompress(data))

    def open(self):
        if not self._file:
            self._file = open(self._meta.path, "rb")

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

class VideoReader(object):
    def __init__(self, video_meta):
        """

        Parameters
        ----------
        video_meta: gscrap.data.images.videos.VideoMetadata
        """

        self._meta = video_meta
        self._byte_size = video_meta.byte_size
        self._file = None

    def open(self):
        if not self._file:
            self._file = open(self._meta.path, "rb")

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def read(self, from_=0):
        #reads until EOF starting from some point
        file = self._file
        byte_size = self._byte_size

        file.seek(from_ * byte_size)

        while True:
            data = file.read(byte_size)
            if not data:
                break

            yield from_bytes(self._meta, lzma.decompress(data))