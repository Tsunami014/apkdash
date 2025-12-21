from abc import ABC, abstractmethod

class Window(ABC):
    __slots__ = ['buf']

    @abstractmethod
    def update(self): ...

