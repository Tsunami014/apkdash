from abc import ABC, abstractmethod

class Window(ABC):
    __slots__ = ['_buf']

    @abstractmethod
    def update(self): ...

    def getRow(self, idx):
        return self._buf[idx]

