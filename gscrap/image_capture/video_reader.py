import os

import subprocess

import numpy as np

import ffmpeg

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
        self._meta = video_metadata

    def seek(self, frame_index, crop=None):
        meta = self._meta
        start_time = frame_index / meta.fps

        if crop:
            x0, y0, x1, y1 = crop
            x, y, w, h = (x0, y0, x1 - x0, y1 - y0)

            command = [
                "ffmpeg",
                "-nostdin",
                "-ss", "{}".format(start_time),
                "-i", "{}".format(meta.path),
                "-pix_fmt", "rgb24",
                "-filter:v", "crop={}:{}:{}:{}".format(w, h, x, y),
                "-frames:v", "1",
                "-f", "rawvideo",
                "pipe:"
             ]
        else:
            command = [
                "ffmpeg",
                "-nostdin",
                "-ss", "{}".format(start_time),
                "-i", "{}".format(meta.path),
                "-pix_fmt", "rgb24",
                "-frames:v", "1",
                "-f", "rawvideo",
                "pipe:"
            ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return process.communicate()[0]

def read(video_metadata, from_=0, crop=None):
    meta = video_metadata
    start_time = from_ / meta.fps

    if crop:
        x0, y0, x1, y1 = crop
        x, y, w, h = (x0, y0, x1 - x0, y1 - y0)

        dims = np.array((w, h))

        command = [
            "ffmpeg",
            "-nostdin",
            "-ss", "{}".format(start_time),
            "-i", "{}".format(meta.path),
            "-filter:v", "crop={}:{}:{}:{}".format(w, h, x, y),
            "-pix_fmt", "rgb24",
            "-f", "rawvideo",
            "pipe:"]
    else:
        dims = np.array(meta.dimensions)

        command = [
            "ffmpeg",
            "-nostdin",
            "-ss", "{}".format(start_time),
            "-i", "{}".format(meta.path),
            "-pix_fmt", "rgb24",
            "-f", "rawvideo",
            "pipe:"
        ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    while True:
        bytes_ = process.stdout.read(np.prod(dims) * 3)
        if not bytes_:
            process.terminate()
            break
        else:
            yield bytes_

def get_thumbnail(video_metadata, dimensions):
    command = [
        "ffmpeg",
        "-i", "{}".format(video_metadata.path),
        "-pix_fmt", "rgb24",
        "-filter:v", "scale={}:{}".format(*dimensions),
        "-frames:v", "1",
        "-f", "rawvideo",
        "pipe:"]

    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()[0]

class VideoReader(object):
    def __init__(self, video_metadata):
        """

        Parameters
        ----------
        video_metadata: gscrap.data.images.videos.VideoMetadata
        """
        self._meta = video_metadata

    def read(self, from_=0, crop=None):
        meta = self._meta
        start_time = from_ / meta.fps

        if crop:
            x0, y0, x1, y1 = crop
            x, y, w, h = (x0, y0, x1 - x0, y1 - y0)

            dims = np.array(w, h)

            command = [
                "ffmpeg",
                "-nostdin",
                "-ss", "{}".format(start_time),
                "-i", "{}".format(meta.path),
                "-filter:v", "crop={}:{}:{}:{}".format(w, h, x, y),
                "-pix_fmt", "rgb24",
                "-f", "rawvideo",
                "pipe:"]
        else:
            dims = np.array(meta.dimensions)

            command = [
                "ffmpeg",
                "-nostdin",
                "-ss", "{}".format(start_time),
                "-i", "{}".format(meta.path),
                "-pix_fmt", "rgb24",
                "-f", "rawvideo",
                "pipe:"
            ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        while True:
            bytes_ = process.stdout.read(np.prod(dims) * 3)
            if not bytes_:
                process.terminate()
                break
            else:
                yield bytes_