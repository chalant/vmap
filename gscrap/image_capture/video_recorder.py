import os
from collections import deque
import threading

import subprocess

from datetime import datetime

import ffmpeg

from gscrap.image_capture import capture_loop as ic
from gscrap.image_capture import video_writer as vw

from gscrap.data import paths

def read_video_params(path: str, stream_number: int = 0):
    """
    Read resolution and frame rate of the video
    Args:
        path (str): Path to input file
        stream_number (int): Stream number to extract video parameters from
    Returns:
        dict: Dictionary with height, width and FPS of the video
    """
    if not os.path.isfile(path):
        raise FileNotFoundError("{} does not exist".format(path))
    probe = ffmpeg.probe(path)
    video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
    stream_params = video_streams[stream_number]
    fps_splitted = [int(x) for x in stream_params['avg_frame_rate'].split('/')]
    fps = fps_splitted[0] if fps_splitted[1] == 1 else fps_splitted[0]/float(fps_splitted[1])
    width = stream_params['width']
    height = stream_params['height']
    if 'nb_frames' in stream_params:
        try:
            length = int(stream_params['nb_frames'])
        except ValueError:
            length = None
    else:
        length = None
    if 'rotate' in stream_params['tags']:
        rotation = int(stream_params['tags']['rotate'])
        if rotation%90==0 and rotation%180!=0:
            width = stream_params['height']
            height = stream_params['width']
    params = {'width': width, 'height': height, 'fps': fps}
    if length is not None:
        params['length'] = length
    return params

class FrameSeeker(object):
    def __init__(self, video_metadata):
        self._params = read_video_params(video_metadata.path)
        self._path = video_metadata.path

    def seek(self, frame_index):
        start_time = frame_index - 0.5 / self._params['fps']

        process = subprocess.Popen(
            ["ffmpeg",
             "-nostdin",
             "-ss", "{}".format(start_time),
             "-i", "{}".format(self._path),
             "-frames:v", "1",
             "-f", "rawvideo",
             "pipe:"
             ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        #todo: must decode into a numpy array?
        return process.communicate()[0]

class VideoReader(object):
    def __init__(self, start_frame):
        self._process = subprocess.Popen(
            ["ffmpeg",
             "",
             "",
             ]
        )

    def __iter__(self):
        return self

    def __next__(self):
        pass

class RecordingProcess(object):
    def __init__(self, callback=None):
        self._process = None

        self._concat_path = ''
        self._video_path = ''

        self._thread = None
        self._stop = False

        def null_callback(data):
            pass

        self._callback = callback if callback else null_callback
        self._dict = {}

    def _start_process(self, video_metadata, x_offset, y_offset, preset='slow'):
        self._video_path = video_path = video_metadata.path

        output_file = video_path

        arr = os.path.splitext(video_path)

        if os.path.exists(video_path):
            self._initial_file = initial_file = arr[0] + "0" + arr[1]
            self._output_file = output_file = arr[0] + "1" + arr[1]

            os.rename(video_metadata.path, initial_file)

            self._concat_path = path = os.path.join(paths.videos(), 'concat_files.txt')

            with open(path, "w") as f:
                f.write('file {}\nfile {}'.format(initial_file, output_file))

        self._process = process = subprocess.Popen(
            ["ffmpeg",
             "-nostdin",
             "-video_size", "{}x{}".format(*video_metadata.dimensions),
             "-framerate", "{}".format(int(video_metadata.fps)),
             "-draw_mouse", "0",
             "-f", "x11grab", "-i", ":0.0+{},{}".format(int(x_offset), int(y_offset)),
             "-c:v", "libx264rgb", "-crf", "0",
             "-preset", "{}".format(preset),
             "{}".format(output_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        buffer = b""

        while not self._stop:
            out = process.stderr.read(1)
            # if out == "\":
            # buffer += out
            if out == b"\n":
                buffer = b""
            elif out == b"\r":
                # print("LINE", buffer)
                buff = buffer.decode("utf-8")
                data = self._dict

                data["frames"] = int(buff[0:11].split("=")[1])
                data["fps"] = float(buff[11:19].split("=")[1])
                data["size"] = int(buff[24:41].split("=")[1][:8])
                data["time"] = datetime.strptime(buff[41:58].split("=")[1], "%H:%M:%S.%f")
                bitrate = buff[58:80].split("=")[1][:6]

                res = 0.0

                if bitrate != "N/A sp":
                    res = float(bitrate)

                data["bitrate"] = res

                self._callback(data)

                buffer = b""
            else:
                buffer += out

    def start_recording(self, video_metadata, x_offset, y_offset, preset="slow"):
        self._stop = False

        self._thread = thread = threading.Thread(
            target=self._start_process,
            args=(video_metadata, x_offset, y_offset, preset)
        )

        thread.start()


    def stop_recording(self):
        process = self._process

        if process:
            #merge files into a single video file.

            concat_path = self._concat_path

            #we need to terminate the process before concatenating
            process.terminate()

            self._stop = True

            if concat_path:
                concat_process = subprocess.Popen(
                    ["ffmpeg",
                     "-f", "concat",
                     "-safe", "0",
                     "-i", "{}".format(concat_path),
                     "-c", "copy",
                     "{}".format(self._video_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                concat_process.communicate()
                #wait for process to terminate.

                os.remove(concat_path)
                os.remove(self._output_file)
                os.remove(self._initial_file)

                self._concat_path = ''

            self._process = None


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

        self._xywh = xywh
        self._path = video_meta.path

        self._meta = video_meta

        self._image_buffer = im_bfr = ThreadImageBuffer()

        self._frame_buffer = im_bfr.get_buffer()

        self._frame_byte_size = video_meta.byte_size

        self._buffer_size = buffer_size * 3
        self._thread_pool = thread_pool

        self._current_size = 0

        self._writer = None
        self._dimensions = None

        self._lock = threading.Lock()

    def capture_initialize(self, data):
        # xywh = self.xywh
        #
        # self._dimensions = (xywh[2], xywh[3])

        self._writer = vw.VideoWriter(self._meta)

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

        cbs += self._frame_byte_size

        #write to file each time we exceed the threshold
        if cbs >= self._buffer_size:
            #submit a copy of the frame buffer
            # self._thread_pool.submit(
            #     self._write_to_file,
            #     frame_buffer,
            #     image_buffer)

            self._write_to_file(frame_buffer, image_buffer)

            #get a new frame buffer
            self._frame_buffer = image_buffer.get_buffer()
            self._current_size = 0 #reset current bytes

    def capture_stop(self):
        #write any remaining frames in the current buffer to file
        frame_buffer = self._frame_buffer
        # for frame in frame_buffer:
        self._write_to_file(frame_buffer, self._image_buffer)
        # self._thread_pool.submit(frame_buffer, self._image_buffer)
        frame_buffer.clear()

    def close(self):
        self._writer.close()


    def _write_to_file(self, frame_buffer, image_buffer):
        writer = self._writer

        with self._lock:
            for frame in frame_buffer:
                writer.write(frame)

        #put back the frame buffer
        image_buffer.put_buffer(frame_buffer)