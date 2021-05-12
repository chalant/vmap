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
    INSERT OR REPLACE INTO videos(video_id, project_name, fps)
    VALUES (:video_id, :project_name, :fps)
    """
)

_DELETE_VIDEO_META = text(
    """
    DELETE FROM videos
    WHERE video_id=:video_id AND project_name=:project_name
    """
)

class VideoMetadata(object):
    __slots__ = ('fps', 'project_name', 'video_id', '_path', 'codec', 'extension')

    def __init__(
            self,
            project_name,
            video_id,
            fps,
            codec="XVID",
            extension=".avi"):

        self.project_name = project_name
        self.video_id = video_id
        self.fps = fps
        self.codec = codec

        self._path = os.path.join(
            paths.videos(),
            self.video_id + '.' + extension)

    @property
    def path(self):
        return self._path

    def submit(self, connection):
        connection.submit(
            _ADD_VIDEO_META,
            project_name=self.project_name,
            video_id=self.video_id,
            fps=self.fps
        )

    def delete(self, connection):
        connection.execute(
            _DELETE_VIDEO_META,
            video_id=self.video_id
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
            res['codec'],
            res['extension'])