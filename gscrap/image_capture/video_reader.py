class FrameSeeker(object):
    def __init__(self, video_meta):
        self._meta = video_meta
        self._byte_size = video_meta.byte_size
        self._file = None

    def read(self, cursor):
        file = self._file

        byte_size = self._byte_size

        file.seek(byte_size * cursor)

        #todo: convert returned value to numpy array
        #todo: what if there is no more data? raise error?

        return file.read(byte_size)

    def open(self):
        if not self._file:
            self._file = open(self._meta.path, "rb")

    def close(self):
        self._file.close()
        self._file = None

class VideoReader(object):
    def __init__(self, video_meta):
        self._meta = video_meta
        self._byte_size = video_meta.byte_size
        self._file = None

    def read(self):
        #reads one frame at a time
        with open(self._meta.path, "rb"):
            file = self._file
            byte_size = self._byte_size

            while True:
                data = file.read(byte_size)
                if not data:
                    break

                #todo: convert bytes to numpy array
                yield data