#user can choose between, detection models for each label

# note: filtering is decoupled from the detection algorithm
from abc import ABC, abstractmethod

import cv2
import numpy as np

import pytesseract

#difference matching detection tolerance
DIFF_MAX = 0 #todo: should let the user setup this

from sqlalchemy import text

from gscrap.samples import source as src

#todo: write query => we need to merge

_GET_MODEL = text(
    '''
    SELECT models.model_name, models.model_type
    FROM models
    LEFT JOIN labels_models 
    ON models.model_name=labels_models.model_name
    WHERE label_type=:label_type AND label_name=:label_name AND project_name=:project_name
    '''
)

_GET_PARAMETERS = '''
    SELECT * 
    FROM {} 
    WHERE model_name=:model_name
    '''

_STORE_LABEL_MODEL = text(
    '''
    INSERT OR REPLACE 
    INTO labels_models (label_name, label_type, model_name, project_name)
    VALUES (:label_name, :label_type, :model_name, :project_name)
    '''
)

class AbstractLabeling(ABC):
    model_type = 'null'

    @abstractmethod
    def label(self, img):
        raise NotImplemented

    def store(self, connection, model_name):
        pass

    def load(self, connection, model_id):
        return self

class NullLabeling(AbstractLabeling):
    def label(self, img):
        return "N/A"

class Tesseract(AbstractLabeling):
    model_type = 'tesseract'

    def label(self, img):
        return pytesseract.image_to_string(img)

class DifferenceMatching(AbstractLabeling):
    model_type = 'difference_matching'

    def __init__(self):
        self._samples_source = None
        self.threshold = DIFF_MAX

    def set_samples_source(self, samples_source):
        self._samples_source = samples_source

    def label(self, img):
        diff_max = self.threshold
        best_match_diff = diff_max
        name = "N/A"
        best_match_name = "N/A"

        for label, image in src.get_samples(self._samples_source):
            diff_img = cv2.absdiff(img, image)

            diff = int(np.sum(diff_img) / 255)

            if diff < best_match_diff:
                best_match_diff = diff
                name = label

        #todo: we need to setup a detection threshold which determines the "tolerance", the lowest
        # the better. Otherwise, we would get false positives (threshold could be set by user)

        if (best_match_diff < diff_max):
            best_match_name = name

        return best_match_name

    def store(self, connection, model_name):
        connection.execute(
            text('''
            INSERT OR REPLACE 
            INTO {} (threshold, model_name) VALUES (:threshold, :model_name) 
            '''.format(self.model_type)),
            threshold=self.threshold,
            model_name=model_name
        )

    def load(self, connection, model_id):
        parameters = connection.execute(
            text(_GET_PARAMETERS.format(self.model_type)),
            model_name=model_id)

        self._threshold = float(parameters['threshold'])

        return self

def label(labeling_model, image):
    return labeling_model.label(image)

def load_labeling_model_metadata(connection, label_group, project_name):
    return connection.execute(
        _GET_MODEL,
        label_type=label_group.label_type,
        label_name=label_group.label_name,
        project_name=project_name).first()

    # return get_labeling_model(model["model_type"]).load(
    #     connection, model["model_name"])

def get_labeling_model(model_type):
    # load parameters
    if model_type == 'difference_matching':
        return DifferenceMatching()
    elif model_type == 'tesseract':
        return Tesseract()
    else:
        raise ValueError("No labeling model of type {}".format(model_type))

def store_label_model(
        connection,
        model_name,
        label_type,
        label_class,
        project_name):

    return connection.execute(
        _STORE_LABEL_MODEL,
        model_name=model_name,
        label_type=label_type,
        label_name=label_class,
        project_name=project_name)
