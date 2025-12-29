from gui.wind import Window, ScrlWind, ExitCodes
from gui.displ import printScreen
import importlib
import log
import os

class LogDispl(ScrlWind):
    PRIO = -1
    NAME = "Main App Logs"
    CHAR = "~"
    def _init(self):
        self.title = "Main App Logs (not for individual windows)"
        self._upd()
        return True
    def _upd(self, k=None):
        print("\020!!")
        if not log.LOGS:
            print("No logs")
        else:
            for lg in log.LOGS:
                print(lg)

class ConfDispl(Window):
    PRIO = -1
    NAME = "Config"
    CHAR = "`"
    def _init(self):
        import _main
        self.title = "Config"
        print("- Folder:", os.getcwd())
        if _main.APK_FILE is None:
            print("- Could not find an avaliable apk file in this folder!")
        else:
            print("- Apk file:", _main.APK_FILE)
            print("- Out folder:", _main.OUT_FOLDER)

def loadApps(name):
    if name == '__pycache__':
        return []
    modname = name.split(".")[0]
    try:
        mod = importlib.import_module("apps."+modname, __name__)
    except Exception as e:
        log.error("Exception occurred loading module `apps.", modname, "`: ", e)
        return []
    if not hasattr(mod, '__apps__'):
        log.error("Could not find __apps__ in module `apps.", modname, "`")
        return []
    o = []
    for a in mod.__apps__:
        got = getattr(mod, a, None)
        if got is None:
            log.error("Object `", a, "` in module `apps.", modname, "` does not exist!")
        else:
            if issubclass(got, Window):
                o.append(got)
            else:
                log.error("Object `", a, "` in module `apps.", modname, "` is not a Window!")
    return o

class MainApp:
    __slots__ = ['wind', 'apps', 'recents', 'idx', 'opens', '_createWind']
    def __init__(self):
        self.apps = {}
        self.recents = []
        self.opens = {}
        self.idx = 0

    def _initialise(self, crwind):
        apps = [LogDispl, ConfDispl]
        for f in os.listdir(os.path.abspath(__file__+"/../apps/")):
            apps.extend(loadApps(f))
        apps.sort(key=lambda a: a.PRIO)
        for a in apps:
            if a.CHAR in self.apps:
                log.error(f"Multiple apps with same character `{a.CHAR}`")
            else:
                self.apps[a.CHAR] = a

        self._createWind = crwind
        self.wind = self.mkWind(crwind)

    def print(self):
        printScreen(self)
                    

    def _onWindDel(self, code):
        if code in (ExitCodes.CREATE, ExitCodes.CLOSE):
            if code == ExitCodes.CLOSE:
                self.opens.pop(list(self.opens.keys())[self.idx])
                self.recents.pop(self.idx)
            else:
                self.idx += 1
            self.wind = self.mkWind(self._createWind)
        elif code == ExitCodes.FORWARDS:
            if self.idx < len(self.recents)-1:
                self.idx += 1
                self.wind = self.recents[self.idx]
        elif code == ExitCodes.BACK:
            if self.idx > 0:
                self.idx -= 1
                self.wind = self.recents[self.idx]
        else:
            raise ValueError(
                f"Unknown exit code: {code}!"
            )

    def endPref(self):
        if self.idx <= 0:
            st = "─"
            sidx = "─"
        else:
            st = "<"
            if self.idx >= 10:
                sidx = "+"
            else:
                sidx = str(self.idx)
        if self.idx >= len(self.recents)-1:
            nd = "─"
            eidx = "─"
        else:
            nd = ">"
            eidx = str(len(self.recents)-self.idx-1)
            if len(eidx) > 1:
                eidx = "+"
        return sidx+st+nd+eidx
    def endSuff(self):
        pth = os.getcwd()
        home = os.path.expanduser("~")
        if pth.startswith(home):
            return os.path.join("~", os.path.relpath(pth, home))
        return pth

    def setWind(self, wind, updIdx=True):
        self.wind = wind
        self.recents.append(wind)
        self.opens[self.wind.CHAR] = self.wind
        if updIdx:
            self.idx += 1

    def mkWind(self, cls):
        wind = cls()
        wind.delfn = self._onWindDel
        return wind

