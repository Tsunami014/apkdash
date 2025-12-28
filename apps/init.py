from gui.wind import ScrlWind
from tools import Tool

__apps__ = ['Init']

class Init(ScrlWind):
    NAME = "Init"
    def _init(self):
        self.title = "Initialise"
        self.apktool = Tool(self, "apktool")
        self.apktool.start()
        return True
    def _upd(self, k=None):
        if self.apktool.done:
            print("\020+Finished!")

