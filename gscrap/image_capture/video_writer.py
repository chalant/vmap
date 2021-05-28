class VideoWriter(object):
    def __init__(self, video_meta):
        self._meta = video_meta
        self._file = None

    def write(self, bytes_):
        self._file.write(bytes_)

    def open(self):
        self._file = open(self._meta.path, "ab")

    def close(self):
        self._file.close()