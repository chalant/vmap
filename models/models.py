from abc import ABC, abstractmethod

class Model(ABC):
    def __init__(self):
        self._observers = {event:{} for event in self._events()}

    def get_observers(self, event):
        return self._observers[event].values()

    def add_observer(self, observer, event):
        if event in self._observers:
            self._observers[event][observer.id] = observer
        else:
            raise NotImplementedError("{} doesn't broadcast {} events".format(type(self), event))

    def remove_observer(self, observer, event):
        if event in self._observers:
            self._observers[event][observer.id] = observer

    @abstractmethod
    def _events(self):
        pass