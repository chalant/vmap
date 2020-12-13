from os.path import expanduser, join
from os import mkdir

_ROOT = expanduser("~/.gmap")
_IMAGES = join(_ROOT, "images")

try:
    mkdir(_ROOT)
except FileExistsError:
    pass

try:
    mkdir(_IMAGES)
except FileExistsError:
    pass

def root():
    return _ROOT