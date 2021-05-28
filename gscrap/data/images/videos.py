import os

from sqlalchemy import text

from gscrap.data import paths

_GET_VIDEOS_META = text(
    """
    SELECT *
    FROM videos
    WHERE project_name=:project_name
    """
)

_ADD_VIDEO_META = text(
    """
    INSERT OR REPLACE INTO videos(video_id, project_name, fps, byte_size)
    VALUES (:video_id, :project_name, :fps, byte_size)
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
    __slots__ = ('fps', 'project_name', 'video_id', '_path', 'byte_size', 'mode')

    def __init__(
            self,
            project_name,
            video_id,
            fps,
            byte_size,
            mode="RGB"):

        self.project_name = project_name
        self.video_id = video_id
        self.fps = fps
        self.byte_size = byte_size
        self.mode = mode

        self._path = os.path.join(
            paths.videos(),
            self.video_id)

    @property
    def path(self):
        return self._path

    def submit(self, connection):
        connection.execute(
            _ADD_VIDEO_META,
            project_name=self.project_name,
            video_id=self.video_id,
            fps=self.fps,
            byte_size=self.byte_size
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

def get_metadata(connection, project_name):
    for res in connection.execute(_GET_VIDEOS_META, project_name=project_name):
        yield VideoMetadata(
            project_name,
            res['video_id'],
            res['fps'],
            res['byte_size'])

def delete_for_project(connection, project_name):
    connection.execute(
        _DELETE_VIDEO_META,
        project_name=project_name
    )