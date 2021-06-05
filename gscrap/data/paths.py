from os.path import expanduser, join
from os import mkdir

_ROOT = expanduser("~/.gmap")
_IMAGES = "images"
_TEMPLATES = 'templates'
_VIDEOS = 'videos'
_TMP = 'tmp'

def absolute_path(pth):
    return join(_ROOT, pth)

def root():
    return _ROOT

def templates():
    return absolute_path(_TEMPLATES)

def images():
    return absolute_path(_IMAGES)

def videos():
    return absolute_path(_VIDEOS)

def tmp():
    return absolute_path(_TMP)

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

try:
    mkdir(videos())
except FileExistsError:
    pass

try:
    mkdir(tmp())
except FileExistsError:
    pass