import os

from sqlalchemy import text

from gscrap.data import paths

_GET_VIDEOS_META = text(
    """
    SELECT *
    FROM videos
    """
)

_ADD_VIDEO_META = text(
    """
    INSERT OR REPLACE INTO videos(video_id, project_name, fps, byte_size, width, height, mode, frames, total_time)
    VALUES (:video_id, :project_name, :fps, :byte_size, :width, :height, :mode, :frames, :total_time)
    """
)

_DELETE_VIDEO_META = text(
    """
    DELETE FROM videos
    WHERE video_id=:video_id AND project_name=:project_name
    """
)

_DELETE_ALL_PROJECT_VIDEOS = text(
"""
    DELETE FROM videos
    WHERE project_name=:project_name
    """
)

class VideoMetadata(object):
    __slots__ = (
        'fps',
        'video_id',
        '_path',
        'byte_size',
        'dimensions',
        'mode',
        'frames',
        'time')

    def __init__(
            self,
            video_id,
            fps,
            dimensions,
            byte_size=0,
            mode="RGB",
            frames=0,
            total_time="00:00:00.00"):

        self.video_id = video_id
        self.fps = fps
        self.byte_size = byte_size
        self.mode = mode
        self.dimensions = dimensions
        self.frames = frames
        self.time = total_time

        self._path = os.path.join(
            paths.videos(),
            self.video_id + '.mp4')

    @property
    def path(self):
        return self._path

    def submit(self, connection):
        w, h = self.dimensions
        connection.execute(
            _ADD_VIDEO_META,
            video_id=self.video_id,
            fps=self.fps,
            byte_size=self.byte_size,
            mode=self.mode,
            width=w,
            height=h,
            frames=self.frames,
            total_time=self.time
        )

    def delete(self, connection, project_name):
        connection.execute(
            _DELETE_VIDEO_META,
            video_id=self.video_id,
            project_name=project_name
        )

        try:
            #remove image from disk
            os.remove(self._path)
        except FileNotFoundError:
            pass

def get_metadata(connection):
    for res in connection.execute(_GET_VIDEOS_META):
        yield VideoMetadata(
            res['video_id'],
            res['fps'],
            (res['width'], res['height']),
            res['byte_size'],
            res['mode'],
            res["frames"],
            res["total_time"]
        )

def delete_for_project(connection, project_name):
    connection.execute(
        _DELETE_VIDEO_META,
        project_name=project_name
    )