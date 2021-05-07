from collections import deque
import threading

import cv2

from gscrap.image_capture import image_capture as ic
from gscrap.image_capture import utils as imu

class ImageBuffer(object):
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

        self._image_buffer = im_bfr = ImageBuffer()

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


