from gscrap.labeling import labeling

from gscrap.filtering import filters

from gscrap.samples import source

class Labeler(object):
    def __init__(self):
        self.labeling = labeling.NullLabeling()
        self.filter_pipeline = []

    def set_model(self, labeling_model):
        """

        Parameters
        ----------
        labeling_model: labeling.AbstractLabeling

        Returns
        -------

        """
        self.labeling = labeling_model

    def set_filter_pipeline(self, filter_pipeline):
        self.filter_pipeline = filter_pipeline


def label(labeler, image):
    return labeling.label(
        labeler.labeling,
        filters.apply_filters(
            labeler.filter_pipeline,
            image))

def create_labeler(connection, scene, label, rectangle, filter_pipeline):
    model = Labeler()

    meta = labeling.load_labeling_model_metadata(
        connection,
        label,
        scene.name)

    model_type = meta['model_type']

    if model_type == 'difference_matching':

        labeling_model = labeling.DifferenceMatching().load(
            connection,
            meta['model_name'])


        sample_source = source.SampleSource(
            scene.name,
            label.label_type,
            label.label_name,
            (rectangle.width, rectangle.height),
            filter_pipeline
        )

        labeling_model.set_samples_source(sample_source)
        source.load_samples(sample_source, connection)

    elif model_type == 'tesseract':

        return labeling.get_tesseract(label.label_type)
    else:
        raise ValueError("No labeling model of type {}".format(model_type))


    model.set_model(labeling_model)
    model.set_filter_pipeline(filter_pipeline)

    return model
