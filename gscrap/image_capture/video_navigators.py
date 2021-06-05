from gscrap.image_capture import video_reader as vr
from gscrap.image_capture import image_comparators as imf

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

        self._seeker = seeker = vr.FrameSeeker(video_metadata)
        self._video = video = vr.VideoReader(video_metadata)

        # seeker.open()
        # video.open()

        # self._video = video = cv2.VideoCapture(video_metadata.path)
        self._metadata = video_metadata
        self._indices.clear()

        # frame = seeker.read(self._index)
        #
        # self._current_frame = frame
        #
        # self._indices.append(0)
        #
        # self._index += 1
        #
        # self._max = 1

        # return frame

    @property
    def current_frame(self):
        return self._current_frame

    def has_next(self):
        return self._index < self._max

    def has_prev(self):
        return self._index > self._max

    def next_frame(self):
        index = self._index
        video = self._video
        indices = self._indices

        # if index < self._max - 1:
        #     index += 1
        #     video.set(cv2.CAP_PROP_POS_FRAMES, indices[index])
        #     video.read()
        #     ret, frame = video.read()
        # else:

        ind, frame = self._next_frame(
            video,
            index,
            self._current_frame,
            self._comparator
        )

        if ind != indices[-1]:
            indices.append(ind) #add found index to indices
            index += 1

            self._index = index
            self._max = index

            return True, frame

        return False, frame

    def _next_frame(self, video, index, prev_frame, comparator):
        ind = index

        for frame in video.read(index):
            ind += 1
            if comparator.different_image(prev_frame, frame):
                return ind, frame

        #return same index if no different image was found
        return ind, prev_frame

    def previous_frame(self):
        index = self._index

        if index > 0:
            index -= 1
            self._index = index
            return True, self._seeker.read(self._indices[index])
        else:
            return False, self._current_frame

    def reset(self):
        self._index = 0

    def set_comparator(self, comparator):
        self._comparator = comparator