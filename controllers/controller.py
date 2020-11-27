from abc import ABC, abstractmethod

class Controller(ABC):
    def __init__(self, id_):
        self._id_ = id_

    def id(self):
        return self._id_

    def update(self, event, emitter):
        pass

    def handle_data(self, data, emitter):
        pass
