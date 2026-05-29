from gui.selecter import SelectWind
from gui.wind import AutoScrlWind
from _main import Files
import tools
import os

__apps__ = ['ADB']



class ADB(SelectWind):
    NAME = "ADB Tools"
    CHAR = "-"
    PRIO = 0
    def _init(self):
        self.title = "ADB Tools"
        self.run = None
        self.sel = 1
        if Files.OUT_APK is None or not os.path.exists(Files.OUT_APK):
            print("\020-No built apk found! Run `Finish`")
            return True
        if Files.PACKAGE is None:
            print("\020-Package name could not be discerned!")
            return True
        self.CMDS = {
            "- Uninstall existing": [
                ["uninstall", Files.PACKAGE]
            ],
            "- Install new app": [
                ["uninstall", Files.PACKAGE],
                ["install", Files.OUT_APK]
            ],
            "- Launch app": [
                ["shell", "monkey", "-p", Files.PACKAGE, "-c", "android.intent.category.LAUNCHER", "1"]
            ],
            "- View logs (fullscreen)": [None], # Handled separately
        }
        print("\n".join(self.CMDS.keys()))
        #print("- View logs")
        return True
    def _upd(self, k=None):
        if k == '\n':
            ln = self.getCurLine(1)
            if ln not in self.CMDS:
                return
            self._run(0, lambda: print("\020!!") or print(ln))
            if self.run is not None and self.run[2].done:
                adb = self.run[2]
            else:
                adb = self._run(0, lambda: tools.ADBTool(self))
            if self.run is not None:
                self.run[0].stop()
            self.run = [
                adb,
                self.CMDS[ln].copy(),
                adb
            ]
            if not adb.done:
                adb.start()
        if self.run is not None and self.run[0].done and len(self.run[1]) > 0:
            nxt = self.run[1].pop(0)
            if nxt is None:
                adbLoc = ' '.join(self.run[2]._run_args(None))
                os.system(f"printf '\\033[2J\\033[0;0H';{adbLoc} shell 'logcat --pid=$(pidof {Files.PACKAGE} | tr -d '\r')'")
            else:
                self.run[0] = self._run(0, lambda: tools.Runner(self.run[2], *nxt, ignoreErrors=True))

    def _initSide(self):
        return True

    def update(self, k):
        return AutoScrlWind.update(self, k)

    def _sideprt(self, *args, **kwargs):
        super()._sideprt(*args, **kwargs)
        self.sideScrl = -1

    @property
    def sideBuffer(self):
        return super(SelectWind, self).sideBuffer

