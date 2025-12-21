from gui.base import Window
from random import randint

class Test(Window):
    def _init(self):
        print("Random number:")
        self._upd('')
    def _upd(self, char):
        if char == '\x7f':
            print("\020<", end="")
        else:
            print(f"{randint(0,9)}!")
    def _initSide(self):
        self._updSide('')
    def _updSide(self, char):
        print("\020!!Hello!\nThis\nis\na\ntest!")
