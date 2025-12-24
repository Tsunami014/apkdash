from readchar import key
from gui.wind import ScrlWind
from random import randint

__apps__ = ['Test']

class Test(ScrlWind):
    NAME = "Test"
    def _init(self):
        print("Random number:")
        self._upd('')
        return True
    def _upd(self, k=None):
        if k is None:
            return
        if k == key.BACKSPACE:
            print("\020<", end="")
        else:
            print(f"{randint(0,9)}!")
    def _initSide(self):
        self._updSide()
    def _updSide(self, k=None):
        print("\020!!Hello!\nThis\nis\na\ntest!")
