from gui.wind import Window, ScrlWind, ExitCodes
from gui.displ import printScreen
import log
import importlib
import os

class LogDispl(ScrlWind):
    NAME = "Main App Logs"
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
    __slots__ = ['wind', 'apps', '_createWind']
    def __init__(self):
        self.apps = {'`': LogDispl}

    def _initialise(self, crwind):
        apps = []
        for f in os.listdir(os.path.abspath(__file__+"/../apps/")):
            apps.extend(loadApps(f))
        apps.sort(key=lambda a: a.PRIO)
        for a in apps:
            n = a.NAME
            done = False
            for c in n:
                if c == ' ':
                  continue
                c = c.lower()
                if c not in self.apps:
                    self.apps[c] = a
                    done = True
                    break
                c = c.upper()
                if c not in self.apps:
                    self.apps[c] = a
                    done = True
                    break
            if not done:
                for c in "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    if c not in self.apps:
                        self.apps[c] = a
                        done = True
                        break
            if not done:
                log.error("Too many apps, could not find any characters avaliable!")

        self._createWind = crwind
        self.setWind(crwind)

    def print(self):
        printScreen(self)
                    

    def _onWindDel(self, code):
        if code == ExitCodes.CREATE:
            typ = self._createWind
        self.setWind(typ)

    def endPref(self):
        return ""
    def endSuff(self):
        pth = os.getcwd()
        home = os.path.expanduser("~")
        if pth.startswith(home):
            return os.path.join("~", os.path.relpath(pth, home))
        return pth

    def setWind(self, cls):
        self.wind = cls()
        self.wind.delfn = self._onWindDel

