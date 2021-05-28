from collections import deque
import threading

import cv2

from gscrap.image_capture import capture_loop as ic
from gscrap.image_capture import utils as imu
from gscrap.image_capture import image_comparators as imf
from gscrap.image_capture import video_writer as vw
from gscrap.image_capture import video_reader as vr

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
    def __init__(self, video_meta, xywh, thread_pool, buffer_size=1):
        """

        Parameters
        ----------
        video_meta: gscrap.data.images.videos.VideoMetadata
        xywh
        thread_pool
        buffer_size
        """
        super(VideoRecorder, self).__init__(xywh)

        self._path = video_meta.path

        self._meta = video_meta

        self._image_buffer = im_bfr = ThreadImageBuffer()

        self._frame_buffer = im_bfr.get_buffer()

        self._frame_size = video_meta.byte_size

        self._buffer_size = buffer_size
        self._thread_pool = thread_pool

        self._current_size = 0

        self._writer = None
        self._dimensions = None

        self._lock = threading.Lock()

    def capture_initialize(self, data):
        # xywh = self.xywh
        #
        # self._dimensions = (xywh[2], xywh[3])

        self._writer = writer = vw.VideoWriter(self._meta)

        writer.open()

        # fourcc = cv2.VideoWriter_fourcc(*self._codec)
        #
        # self._writer = cv2.VideoWriter(
        #     self._path,
        #     fourcc,
        #     data.fps,
        #     (dimensions))

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
            # self._thread_pool.submit(self._write_to_file, frame_buffer, image_buffer)

            self._write_to_file(frame_buffer, image_buffer)

            #get a new frame buffer
            self._frame_buffer = image_buffer.get_buffer()
            self._current_size = 0 #reset current bytes

    def capture_stop(self):
        #if capture stops we need to write images that are in the buffer
        frame_buffer = self._frame_buffer
        self._thread_pool.submit(frame_buffer, self._image_buffer)
        frame_buffer.clear()

        self._writer.close()


    def _write_to_file(self, frame_buffer, image_buffer):
        to_np_arr = imu.bytes_to_numpy_array
        dims = self._dimensions

        writer = self._writer

        with self._lock:
            for frame in frame_buffer:
                writer.write(to_np_arr(frame, dims))

        #put back the frame buffer
        image_buffer.put_buffer(frame_buffer)

class VideoNavigator(object):
    def __init__(self, comparator=None):
        """

        Parameters
        ----------
        comparator: gscrap.image_capture.image_comparators.ImageComparator
        """
        self._video = None
        self._comparator = comparator if comparator else imf.NullImageComparator()
        self._indices = []

        self._index = -1
        self._max = 0

        self._current_frame = None

    def initialize(self, video_metadata):
        # if self._video:
        #     self._video.release()

        self._index = 0

        self._video = video = vr.FrameSeeker(video_metadata)

        # self._video = video = cv2.VideoCapture(video_metadata.path)
        self._metadata = video_metadata
        self._indices.clear()

        #todo
        frame = video.read(self._index)

        self._current_frame = frame

        if ret:
            self._indices.append(0)

        return ret, frame

    @property
    def current_frame(self):
        return self._current_frame

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
            ind, ret, frame = self._next_frame(
                video,
                index,
                self._current_frame,
                self._comparator
            )

            if ind != indices[-1]:
                video.set(cv2.CAP_PROP_POS_FRAMES, ind)
                indices.append(ind) #add found index to indices
                index += 1

        self._index = index

        return ret, frame

    def _next_frame(self, video, index, prev_frame, comparator):
        ind = index

        ret, frame = video.read()

        while not comparator.different_image(prev_frame, frame):
            ind += 1
            ret, frame = video.read()

        return ind, ret, frame

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

    def set_comparator(self, comparator):
        self._comparator = comparator