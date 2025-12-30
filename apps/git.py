from gui.wind import AutoScrlWind, ExitCodes
from builtins import print as _origPrt
from tools import LazygitTool
import subprocess

__apps__ = ['LzyGit']

class LzyGit(AutoScrlWind):
    NAME = "Lazygit"
    CHAR = "g"
    def _init(self):
        self.title = "Lazygit"
        self.lzgit = LazygitTool(self)
        if self.lzgit.success:
            self._upd()
        return True
    def _upd(self, k=None):
        if self.lzgit.success:
            print("\020+Running lazygit...")
            _origPrt("\033[2J")
            res = subprocess.run(
                [self.lzgit.pth],
                check=False
            )
            if res.returncode != 0:
                input(f"Errored with code {res.returncode}! Press enter to continue.")
            _origPrt("\033[2J")
            self.delfn(ExitCodes.CLOSE)

