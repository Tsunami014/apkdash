from readchar import key
from gui.wind import ScrlWind
from random import randint

__apps__ = ['Test']

class Test(ScrlWind):
    NAME = "Test"
    def _init(self):
        self.title = "Random number:"
        self._upd('')
        return True
    def _upd(self, k=None):
        if self.selecting:
            return
        if k == key.BACKSPACE:
            print("\020<", end="")
        else:
            print(f"{randint(0,9)}!")
    def _initSide(self):
        self.title = "Random tests:"
        print("\020!!Hello!\nThis\nis\na\ntest!")

