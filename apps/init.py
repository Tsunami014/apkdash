from gui.wind import AutoScrlWind
from tools import ToolRunner
from _main import APK_FILE, OUT_FOLDER
import os

__apps__ = ['Init']

class Init(AutoScrlWind):
    NAME = "Init"
    CHAR = "1"
    def _init(self):
        self.title = "Run the initial programs"
        self.done = False
        self.git = None
        if APK_FILE is None:
            print("\020-No apk file found in current directory! (See `config` for info)")
            return
        if os.path.exists(OUT_FOLDER):
            print("\020+Out folder already exists!")
            self.run = True
            self._upd()
        else:
            self.title = "Initialising"
            print("\020~Initialising", APK_FILE)
            self.run = ToolRunner(self, "apktool", "d", APK_FILE, runTxt="Decompiling apk...")
        return True
    def _upd(self, k=None):
        if self.done:
            return
        if self.run is True or self.run.done:
            if self.git is None:
                if os.path.exists(os.getcwd()+"/.git"):
                    print("\020+Git repo already exists!")
                    self.git = True
                else:
                    self.git = ToolRunner(self, "git", "init")
            if self.git is True or self.git.done:
                print("\020+Finished!")
                self.done = True

