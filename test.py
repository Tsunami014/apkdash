from gui.base import Window
from random import randint

class Test(Window):
    def _init(self):
        print("Random number:\n")
        self._upd()
    def _upd(self):
        print(f"\020<{randint(0,9)}!")
    def _updSide(self):
        print("\020!!Hello!\nThis\nis\na\ntest!")
