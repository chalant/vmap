from gscrap.labeling import labeling
from gscrap.filtering import filters

class Labeler(object):
    def __init__(self):
        self._labeling = labeling.NullLabeling()
        self._filter_pipeline = None

    def set_model(self, labeling_model):
        """

        Parameters
        ----------
        labeling_model: AbstractLabeling

        Returns
        -------

        """
        self._labeling = labeling_model

    def set_filter_pipeline(self, filter_pipeline):
        self._filter_pipeline = filter_pipeline


def label(labeler, image):
    return labeling.label(
        labeler.labeling,
        filters.apply_filters(
            labeler.filter_pipeline,
            image))
