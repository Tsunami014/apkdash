from readchar import key
from gui.wind import ScrlWind
from downloader import GithubDownload

__apps__ = ['Init']

class Init(ScrlWind):
    NAME = "Init"
    def _init(self):
        self.title = "Initialise"
        self.apktool = GithubDownload(self, "apktool.jar", "https://api.github.com/repos/iBotPeaches/Apktool/releases/latest")
        self.apktool.start()
        return True
    def _upd(self, k=None):
        if self.apktool.done:
            print("\020+Finished!")

