from os import path

class WorkSpace(object):
    def __init__(self, working_dir, project_name):
        self._working_dir = working_dir
        self._project_dir = path.join(working_dir, project_name)

    @property
    def working_dir(self):
        return self._working_dir

    @property
    def project_dir(self):
        return self._project_dir