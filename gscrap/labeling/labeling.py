#user can choose between, detection models for each label

# note: filtering is decoupled from the detection algorithm
from abc import ABC, abstractmethod

import cv2
import numpy as np

import pytesseract

#difference matching detection tolerance
DIFF_MAX = 400 #todo: should let the user setup this

from sqlalchemy import text

#todo: write query => we need to merge

_GET_MODEL = text(
    '''
    SELECT models.model_name, models.model_type
    FROM models
    LEFT JOIN labels_models 
    ON models.model_name = labels_models.model_name
    WHERE label_type=:=label_type AND label_name=:label_name AND project_name=:project_name
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
    INTO labels_models 
    VALUES (label_name:=label_name, label_type=:label_type, model_type=:model_type, model_name=:model_name)
    '''
)

class AbstractLabeling(ABC):
    model_type = 'null'

    @abstractmethod
    def label(self, img):
        raise NotImplemented

    def store(self, connection):
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
        source = self._samples_source

        best_match_diff = DIFF_MAX
        name = "N/A"
        best_match_name = "N/A"

        for label, image in source.get_samples():
            diff_img = cv2.absdiff(img, image)

            diff = int(np.sum(diff_img) / 255)

            if diff < best_match_diff:
                best_match_diff = diff
                name = label

        #todo: we need to setup a detection threshold which determines the "tolerance", the lowest
        # the better. Otherwise, we would get false positives (threshold could be set by user)

        if (best_match_diff < DIFF_MAX):
            best_match_name = name

        return best_match_name

    def store(self, connection):
        #todo: should only store if the threshold is different

        #todo: this will only append a row to the table, since there is no primary key

        connection.execute(
            text('''INSERT OR REPLACE INTO {} VALUES (threshold=:threshold) WHERE model_name=:model_name'''.format(
                self.model_type)),
            threshold=self._threshold
        )

    def load(self, connection, model_id):
        parameters = connection.execute(
            text(_GET_PARAMETERS.format(self.model_type)),
            model_name=model_id)

        self._threshold = float(parameters['threshold'])

        return self

def label(labeling_model, image):
    return labeling_model.label(image)

def load_labeling_model_metadata(connection, label_group):
    return connection.execute(
        _GET_MODEL,
        label_type=label_group.label_type,
        label_name=label_group.label_name,
        project_name=label_group.project_name)

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
        model_type,
        model_name,
        label_type,
        label_class):

    return connection.execute(
        _STORE_LABEL_MODEL,
        model_name=model_name,
        model_type=model_type,
        label_type=label_type,
        label_name=label_class)
