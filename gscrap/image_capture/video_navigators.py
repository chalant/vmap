import numpy as np

from gscrap.image_capture import video_reader as vr
from gscrap.image_capture import image_comparators as imf

class VideoNavigator(object):
    def __init__(self, comparator=None, crop=None):
        """

        Parameters
        ----------
        comparator: gscrap.image_capture.image_comparators.ImageComparator
        """
        self._video = None
        self._comparator = comparator if comparator else imf.NullImageComparator()
        self._indices = []

        self._index = -1

        self._current_frame = b''

        self._frame_seeker = None
        self._video_reader = None
        self._crop = crop

    def initialize(self, video_metadata):

        self._frame_seeker = vr.FrameSeeker(video_metadata)
        self._video_reader = vr.VideoReader(video_metadata)

        self._metadata = video_metadata
        self._indices.clear()

        # if video_metadata.frames > 0:
        #     self._indices.append(0)

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

    @property
    def has_next(self):
        return self._index < self._metadata.frames

    @property
    def has_prev(self):
        return self._index > 0

    def next_frame(self):
        index = self._index
        video = self._video_reader
        indices = self._indices

        # if index < self._max - 1:
        #     index += 1
        #     video.set(cv2.CAP_PROP_POS_FRAMES, indices[index])
        #     video.read()
        #     ret, frame = video.read()
        # else:

        if not self._current_frame:
            self._index += 1
            self._indices.append(0)

            current_frame = self._frame_seeker.seek(0)
            self._current_frame = current_frame

            return current_frame

        try:
            self._index = index + 1

            frame = self._frame_seeker.seek(indices[index + 1])
            self._current_frame = frame

            return frame

        except IndexError:
            li = indices[-1]

            ind, frame = self._next_frame(
                video,
                li,
                self._current_frame,
                self._comparator
            )

            #advance the index if we found a new frame.

            if ind != li:
                indices.append(ind) #add found index to indices
                self._index = index + 1

            self._current_frame = frame
            return frame

    def _next_frame(self, video, index, prev_frame, comparator):
        ind = index

        crop = self._crop

        if crop:
            x0, y0, x1, y1 = crop
            dims = (x1 - x0, y1 - y0)
        else:
            dims = self._metadata.dimensions

        res = np.array(dims)

        for frame in video.read(index + 1, crop):
            ind += 1

            #skip identical bytes
            if frame == prev_frame:
                #apply additional comparisons to the frames
                continue

            #skip identical frames using some comparator
            if not comparator.different_image(
                    np.frombuffer(prev_frame, np.uint8).reshape(*res[::-1], 3),
                    np.frombuffer(frame, np.uint8).reshape(*res[::1], 3)):
                continue

            return ind, frame

        #return same index if no different image was found
        return ind, prev_frame

    def previous_frame(self):
        index = self._index

        if index > 0:
            index -= 1
            self._index = index
            return self._frame_seeker.seek(self._indices[index])
        else:
            return self._current_frame

    def reset(self):
        self._index = 0

    def set_comparator(self, comparator):
        self._comparator = comparator