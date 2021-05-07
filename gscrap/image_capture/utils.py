from PIL import Image

import numpy as np

def bytes_to_numpy_array(bytes_, dimensions):
    np.asarray(Image.frombytes("RGB", dimensions, bytes_, "raw", "BGRX"))