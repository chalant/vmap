#user can choose between, detection models for each label

# note: filtering is decoupled from the detection algorithm
from abc import ABC, abstractmethod

import cv2
import numpy as np

import pytesseract

from sqlalchemy import text

from gscrap.samples import source as src
from gscrap.filtering import filters

_ADD_MODEL = text(
    '''
    INSERT OR REPLACE
    INTO models (model_name, model_type)
    VALUES (:model_name, :model_type)
    '''
)

_GET_MODEL = text(
    '''
    SELECT models.model_name, models.model_type
    FROM models
    JOIN labels_models 
        ON models.model_name=labels_models.model_name
    WHERE labels_models.label_type=:label_type 
        AND labels_models.label_name=:label_name 
        AND labels_models.scene_name=:scene_name
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
    INTO labels_models (label_name, label_type, model_name, scene_name)
    VALUES (:label_name, :label_type, :model_name, :scene_name)
    '''
)

_STORE_DIFFERENCE_MATCHING = text(
    '''
    INSERT OR REPLACE 
    INTO difference_matching (threshold, model_name) 
    VALUES (:threshold, :model_name) 
    '''
)

_UPDATE_DIFFERENCE_MATCHING = text(
    '''
    UPDATE difference_matching
    SET threshold=:threshold
    WHERE model_name=:model_name
    '''
)

_ALL_CHARACTERS = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
_NUMBERS = set('0123456789')

#difference matching detection tolerance
DIFF_MAX = 0

class AbstractLabeling(ABC):
    model_type = 'null'

    @abstractmethod
    def label(self, img):
        raise NotImplemented

    def store(self, connection, model_name):
        pass

    def update(self, connection, model_name):
        pass

    def load(self, connection, model_id):
        return self

class NullLabeling(AbstractLabeling):
    def label(self, img):
        return ''

class Tesseract(AbstractLabeling):
    model_type = 'tesseract'

    def __init__(self, character_set):
        self._character_set = character_set

    def label(self, img):
        text = pytesseract.image_to_string(
            cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC),
            config='--psm 6 --oem 1')

        characters = self._character_set
        res = ''

        for i in text:
            if i in characters:
                res += i

        return res

class DifferenceMatching(AbstractLabeling):
    model_type = 'difference_matching'

    def __init__(self):
        self._samples_source = None
        self.threshold = DIFF_MAX
        self._filter_pipeline = []

    def set_samples_source(self, samples_source):
        self._samples_source = samples_source

    def label(self, img):
        diff_max = self.threshold
        best_match_diff = diff_max
        name = ""
        best_match_name = ""

        for label, image in src.get_samples(self._samples_source):
            diff_img = cv2.absdiff(img, image)

            diff = int(np.sum(diff_img) / 255)

            if diff <= best_match_diff:
                best_match_diff = diff
                name = label

        if (best_match_diff <= diff_max):
            best_match_name = name

        return best_match_name

    def store(self, connection, model_name):
        connection.execute(
            _STORE_DIFFERENCE_MATCHING,
            threshold=self.threshold,
            model_name=model_name
        )

    def update(self, connection, model_name):
        connection.execute(
            _UPDATE_DIFFERENCE_MATCHING,
            threshold=self.threshold,
            model_name=model_name
        )

    def load(self, connection, model_id):
        parameters = connection.execute(
            text(_GET_PARAMETERS.format(self.model_type)),
            model_name=model_id).first()

        self.threshold = float(parameters['threshold'])

        return self

def add_model(connection, model_name, model_type):
    connection.execute(
        _ADD_MODEL,
        model_name=model_name,
        model_type=model_type
    )

def label(labeling_model, image):
    return labeling_model.label(image)

def load_labeling_model_metadata(connection, label_group, scene_name):
    return connection.execute(
        _GET_MODEL,
        label_type=label_group.label_type,
        label_name=label_group.label_name,
        scene_name=scene_name).first()

def get_labeling_model(model_type, label_type):
    # load parameters
    if model_type == 'difference_matching':
        return DifferenceMatching()
    elif model_type == 'tesseract':
        characters = _ALL_CHARACTERS

        if label_type == 'Number':
            characters = _NUMBERS

        return Tesseract(characters)
    else:
        raise ValueError("No labeling model of type {}".format(model_type))

def get_tesseract(label_type):
    characters = _ALL_CHARACTERS

    if label_type == 'Number':
        characters = _NUMBERS

    return Tesseract(characters)

def store_label_model(
        connection,
        model_name,
        label_type,
        label_class,
        scene_name):

    return connection.execute(
        _STORE_LABEL_MODEL,
        model_name=model_name,
        label_type=label_type,
        label_name=label_class,
        scene_name=scene_name)
