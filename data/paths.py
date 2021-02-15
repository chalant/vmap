from os.path import expanduser, join
from os import mkdir

_ROOT = expanduser("~/.gmap")
_IMAGES = "images"
_TEMPLATES = 'templates'

def global_path(pth):
    return join(_ROOT, pth)

def root():
    return _ROOT

def templates():
    return global_path(_TEMPLATES)

def images():
    return global_path(_IMAGES)

try:
    mkdir(_ROOT)
except FileExistsError:
    pass

try:
    mkdir(templates())
except FileExistsError:
    pass

try:
    mkdir(images())
except FileExistsError:
    pass