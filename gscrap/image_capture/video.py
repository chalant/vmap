from collections import deque
import threading

import cv2

from gscrap.image_capture import image_capture as ic
from gscrap.image_capture import utils as imu
from gscrap.image_capture import image_filters as imf

class ThreadImageBuffer(object):
    def __init__(self, num_buffers=2):
        self._num_buffers = num_buffers

        self._queue = qu = deque()

        for _ in range(num_buffers):
            qu.append([])

        self._lock = threading.Lock()

    def get_buffer(self):
        with self._lock:
            try :
                return self._queue.pop()
            except IndexError:
                #return a new buffer if the queue is empty
                return []

    def put_buffer(self, buffer):
        with self._lock:
            buffer.clear() #clear buffer

            self._queue.appendleft(buffer)

class VideoRecorder(ic.ImageHandler):
    def __init__(self, path, xywh, thread_pool, buffer_size=1):
        super(VideoRecorder, self).__init__(xywh)
        self._path = path

        self._image_buffer = im_bfr = ThreadImageBuffer()

        self._frame_buffer = im_bfr.get_buffer()

        self._buffer_size = buffer_size
        self._thread_pool = thread_pool

        self._current_size = 0

        self._writer = None
        self._dimensions = None

    def capture_initialize(self, data):
        self._frame_size = data.frame_byte_size / 1000

        xywh = self.xywh
        self._dimensions = dimensions = (xywh[2], xywh[3])

        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        self._writer = cv2.VideoWriter(
            self._path + ".avi",
            fourcc,
            data.fps,
            (dimensions))

    def process_image(self, image):
        frame_buffer = self._frame_buffer
        frame_buffer.append(image)

        image_buffer = self._image_buffer

        cbs = self._current_size

        fbs = self._frame_size

        cbs += fbs

        #write to file each time we exceed the threshold
        if cbs >= self._buffer_size:
            #submit a copy of the frame buffer
            self._thread_pool.submit(self._write_to_file, frame_buffer, image_buffer)

            #get a new frame buffer
            self._frame_buffer = image_buffer.get_buffer()
            self._current_size = 0 #reset current bytes

    def capture_stop(self):
        #if capture stops we need to write images that are in the buffer
        frame_buffer = self._frame_buffer
        self._thread_pool.submit(frame_buffer, self._image_buffer)
        frame_buffer.clear()


    def _write_to_file(self, frame_buffer, image_buffer):
        to_np_arr = imu.bytes_to_numpy_array
        dims = self._dimensions

        writer = self._writer

        for frame in frame_buffer:
            to_np_arr(frame, dims)
            writer.write(frame)

        #put back the frame buffer
        image_buffer.put_buffer(frame_buffer)

class VideoNavigator(object):
    def __init__(self, video_reader):
        """

        Parameters
        ----------
        video_reader: VideoReader
        trimmer:
        """
        self._video = None
        self._reader = video_reader
        self._indices = []

        self._index = -1
        self._max = 0

        self._current_frame = None

    def initialize(self, video_metadata):
        if self._video:
            self._video.release()

        self._index = 0

        self._video = video = cv2.VideoCapture(video_metadata.path)
        self._metadata = video_metadata
        self._indices.clear()

        ret, frame = video.read()

        self._current_frame = frame

        if ret:
            self._indices.append(0)

        return ret, frame

    def has_next(self):
        return self._index < self._max

    def has_prev(self):
        return self._index > 0

    def next_frame(self):
        index = self._index
        video = self._video
        indices = self._indices

        if index < self._max - 1:
            index += 1
            video.set(cv2.CAP_PROP_POS_FRAMES, indices[index])
            ret, frame = video.read()
        else:
            ind, ret, frame = self._reader.next_frame(
                video,
                index,
                self._current_frame)

            if ind != indices[-1]:
                video.set(cv2.CAP_PROP_POS_FRAMES, ind)
                indices.append(ind) #add found index to indices
                index += 1

        self._index = index

        return ret, frame

    def previous_frame(self):
        index = self._index

        if index > 0:
            index -= 1

        video = self._video
        video.set(cv2.CAP_PROP_POS_FRAMES, self._indices[index])

        self._index = index

        return video.read()

    def reset(self):
        index = 0

        video = self._video
        video.set(cv2.CAP_PROP_POS_FRAMES, self._indices[index])

        self._index = index

class VideoReader(object):
    def __init__(self, filter_=None):
        self._filter = filter_ if filter_ else imf.NullImageFilter()

    def next_frame(self, video, index, prev_frame):
        filter_ = self._filter
        ind = index

        ret, frame = video.read()

        while not filter_.different(prev_frame, frame):
            ind += 1
            ret, frame = video.read()

        return ind, ret, frame