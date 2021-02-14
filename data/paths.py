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
    return _TEMPLATES

def images():
    return _IMAGES

try:
    mkdir(_ROOT)
except FileExistsError:
    pass

try:
    mkdir(global_path(templates()))
except FileExistsError:
    pass

try:
    mkdir(global_path(images()))
except FileExistsError:
    pass