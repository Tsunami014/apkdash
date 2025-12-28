from gui.wind import ScrlWind
from tools import ToolRunner
from _main import APK_FILE, OUT_FOLDER
import os

__apps__ = ['Init']

class Init(ScrlWind):
    NAME = "Init"
    CHAR = "1"
    def _init(self):
        if APK_FILE is None:
            print("\020-No apk file found in current directory!")
            return
        if os.path.exists(OUT_FOLDER):
            print("\020+Out folder already exists!")
        else:
            self.title = "Initialising"
            print("\020~Initialising", APK_FILE)
            self.run = ToolRunner(self, "apktool", "d", APK_FILE)
        return True
    def _upd(self, k=None):
        if self.run.done:
            print("\020+Finished!")

