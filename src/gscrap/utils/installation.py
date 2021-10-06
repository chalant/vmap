from os import mkdir
from os.path import expanduser

def install():
    #create main directory
    try:
        mkdir(expanduser("/.gmap"))
    except FileExistsError:
        pass


