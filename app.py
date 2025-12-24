from gui.wind import Window, ScrlWind, ExitCodes
from readchar import key
from log import log
import importlib
import os

def loadApps(name):
    if name == '__pycache__':
        return []
    modname = name.split(".")[0]
    try:
        mod = importlib.import_module("apps."+modname, __name__)
    except Exception as e:
        log("Exception occurred loading module `apps.", modname, "`: ", e)
        return []
    if not hasattr(mod, '__apps__'):
        log("Could not find __apps__ in module `apps.", modname, "`")
        return []
    o = []
    for a in mod.__apps__:
        got = getattr(mod, a, None)
        if got is None:
            log("Object `", a, "` in module `apps.", modname, "` does not exist!")
        else:
            if issubclass(got, Window):
                o.append(got)
            else:
                log("Object `", a, "` in module `apps.", modname, "` is not a Window!")
    return o

class MainApp:
    __slots__ = ['wind', 'apps', 'reprint']
    def __init__(self):
        self.reprint = False
        self.apps = {}
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
                log("Too many apps, could not find any characters avaliable!")

        self._setMainWind(CreateWind)
                    

    def _onWindDel(self, code):
        if code == ExitCodes.PICK:
            typ = None
        else:
            typ = CreateWind
        self._setMainWind(typ)

    def setWind(self, cls):
        self.wind = cls()
        self.wind.delfn = self._onWindDel
        self.reprint = True
    def _setMainWind(self, cls):
        self.wind = cls(self)
        self.wind.delfn = self._onWindDel
        self.reprint = True

class MainWind(ScrlWind):
    __slots__ = ['mapp']
    def __init__(self, mapp):
        self.mapp = mapp
        super().__init__()

class CreateWind(MainWind):
    def _init(self):
        for c, a in self.mapp.apps.items():
            print(f"\020b{c}\020R: {a.NAME}")
        return True
    def _upd(self, k=None):
        if k in self.mapp.apps.keys():
            self.mapp.setWind(self.mapp.apps[k])
            return
        super()._upd(k)

