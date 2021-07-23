from abc import ABC, abstractmethod

class ValueSource(ABC):
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError