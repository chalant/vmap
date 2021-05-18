import setuptools

from os.path import join, dirname, abspath

def read_requirements(path):
    """
    Read a requirements file, expressed as a path relative to Zipline root.
    """
    real_path = join(dirname(abspath(__file__)), path)

    with open(real_path) as f:
        return f.readlines()

setuptools.setup(
    package_dir={"", "gmap"},
    install_requires=read_requirements("etc/requirements.txt")
)