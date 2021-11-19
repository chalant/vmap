from os import path
from os import mkdir

class WorkSpace(object):
    def __init__(self, working_dir, project_name):
        self._working_dir = working_dir
        self._project_dir = project_dir = path.join(working_dir, project_name)
        self.project_name = project_name

        try:
            mkdir(project_dir)
        except FileExistsError:
            pass

    @property
    def working_dir(self):
        return self._working_dir

    @property
    def project_dir(self):
        return self._project_dir