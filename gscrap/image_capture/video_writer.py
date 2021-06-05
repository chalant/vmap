import ffmpeg

from PIL import Image

class VideoWriter(object):
    """
    Class for writing a video frame-by-frame
    """
    def __init__(
            self,
            video_metadata,
            lossless=True,
            preset='slow'):

        """
        Args:
            video_metadata: gscrap.data.image
            lossless (bool): Whether to apply lossless encoding.
                Be aware: lossless format is still lossy due to RGB to YUV conversion inaccuracy
            preset (str): H.264 compression preset
        """

        input_params = dict(
            format='rawvideo',
            pix_fmt='rgb24',
            s='{}x{}'.format(*video_metadata.dimensions),
            loglevel='error')

        input_params['framerate'] = float(video_metadata.fps)

        ffmpeg_input = ffmpeg.input('pipe:', **input_params)

        encoding_params = {"c:v": "libx264", "preset": preset}

        if lossless:
            encoding_params['profile:v'] = 'high444'
            encoding_params['crf'] = 0

        stream = ffmpeg_input.output(
            video_metadata.path,
            pix_fmt='yuv444p' if lossless else 'yuv420p',
            **encoding_params)

        self._ffmpeg_process = ffmpeg.run_async(stream, pipe_stdin=True)
        self._dimensions = video_metadata.dimensions

    def write(self, bytes_):
        self._ffmpeg_process.stdin.write(
            Image.frombytes(
                "RGB",
                (1920, 1080),
                bytes_,
                'raw',
                'BGRX').tobytes())

    def close(self):
        """
        Finish video creation process and close video file
        """
        process = self._ffmpeg_process

        process.stdin.close()
        process.wait()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()