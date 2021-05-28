from gscrap.image_capture import image_comparators as ic


class UnknownLabel(ic.ImageComparator):
    def __init__(self, detector=None):
        self._detector = detector

    def different_image(self, im1, im2):
        #crop the next frame and apply detection model
        if self._detector.detect(im2) == 'Unknown':
            # return true if the element is unlabeled
            return True

    def set_detector(self, detector):
        self._detector = detector

class DifferentLabel(ic.ImageComparator):
    def __init__(self, detector=None):
        self._detector = detector

    def different_image(self, im1, im2):
        detector = self._detector

        lb1 = detector.detect(im1)
        lb2 = detector.detect(im2)

        #return next frame with different labels
        return lb1 != lb2

    def set_detector(self, detector):
        self._detector = detector
