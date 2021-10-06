from abc import ABC, abstractmethod

class _Element(ABC):
    def __init__(self):
        self._submit_flag = False

    def submit(self, connection):
        if not self._submit_flag:
            self._submit(connection)
            self._submit_flag = True

    @abstractmethod
    def _submit(self, connection):
        raise NotImplementedError

    def clear(self):
        self._submit_flag = True