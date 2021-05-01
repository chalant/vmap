from abc import ABC, abstractmethod

class Controller(ABC):
    def update(self, event, emitter):
        pass

    def handle_data(self, data, emitter):
        pass
