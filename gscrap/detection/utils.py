import cv2

import numpy as np

DEFAULT_THRESH = 400

def different_image(im1, im2, threshold):
    return np.sum(cv2.absdiff(im1, im2)) / 255 < threshold

def max_threshold(dimensions, channels=3):
    return np.prod(dimensions) * channels / 255