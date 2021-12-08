from os.path import join
from os import mkdir

_ROOT = ""

_SCENES = "scenes"
_IMAGES = "images"
_TEMPLATES = "templates"
_VIDEOS = "videos"
_TMP = "tmp"
_PROJECT = None

def set_project(project):
    global _PROJECT
    global _ROOT

    _PROJECT = project
    _ROOT = rt = project.working_dir

    try:
        mkdir(rt)
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

def absolute_path(pth):
    return join(_ROOT, pth)

def root():
    return _ROOT

def templates():
    return absolute_path(_TEMPLATES)

def images():
    return join(absolute_path(_SCENES))

def videos():
    return absolute_path(_VIDEOS)

def tmp():
    return absolute_path(_TMP)

def samples():
    return absolute_path(join(tmp(), 'samples'))