from models import models
from models.store_managing import POOL

EVENTS = ["new", "open"]

"""
directory
    |database
        |labels (labels of a game (each game has its own label table)
        |games (each game has its own table)
        |parameters (each game has its own parameter table)
        |save_metadata (instance_id, game_type, workdir_id, parameters on the game (max players etc.)
        
    |workspaces
        |workspace_dir
            |metadata_file
            |images_dir
"""

class StoreManager(models.Model):
    def __init__(self, dir_):
        super(StoreManager, self).__init__()
        self._dir = dir_

    def save(self, file_name):
        POOL.submit()

    def _save(self, file_name):
        pass

    def new(self):
        # todo: notify observers => reset there states
        #  we get a new workspace
        pass

    def open_file(self):
        # todo: notify observers => load and display data
        pass

    def _events(self):
        return EVENTS
