from .displ import fix, strlen, strcut, toPrintable, fixVariable, getSizings
from enum import IntEnum
from readchar import key
import builtins

class Buffer:
    __slots__ = ['txt', 'scroll']
    def __init__(self, txt, sect=None, scroll=0):
        self.txt = fixVariable(txt, sect)
        self.scroll = scroll

    def initialFix(self, wid: int, hei: int):
        if self.scroll is None:
            return
        if self.scroll == -1:
            self.scroll = max(Buffer(self.txt).howManyRows(wid) - hei, 0)
        while self.txt and self.scroll > 0:
            self.popBuf(wid)
            self.scroll -= 1

    def howManyRows(self, wid: int):
        i = 0
        while self.txt:
            self.popBuf(wid)
            i += 1
        return i

    def __bool__(self):
        return self.txt != ''

    def popBuf(self, wid: int):
        idx = self.txt.find("\n")
        ridx = strlen(self.txt[:idx])
        if idx == -1 or wid < ridx:
            out, self.txt = strcut(self.txt, wid)
        else:
            out = self.txt[:idx]
            self.txt = self.txt[idx+1:]
        return toPrintable(out) + " "*(wid-strlen(out))

class ExitCodes(IntEnum):
    CREATE = 1
    """Go to app creation screen"""
    CLOSE = 2
    """Close the running instance and go to app creation screen"""
    BACK = 3
    """Go to prev app in recent list"""
    FORWARDS = 4
    """Go to next app in recent list"""

class Window:
    NAME: str
    PRIO: int
    CHAR: str

    def __init__(self, delfn = lambda code: None):
        self.buf = ""
        self.sidebuf = ""
        self.titles = ["", ""]
        self.sel = 0
        self.delfn = delfn

    def _run(self, cur, fn, *args):
        _oldprt = builtins.print
        builtins.print = (self._sideprt, self._bufprt)[cur]
        self._cur = cur
        ret = fn(*args)
        builtins.print = _oldprt
        return ret

    def _initialise(self):
        self._run(1, self._init)
        self._run(0, self._initSide)
        self.buf = fix(self.buf)
        self.sidebuf = fix(self.sidebuf)

    def _bufprt(self, *args, sep=" ", end="\n"):
        self.buf += sep.join(str(i) for i in args)+end
    def _sideprt(self, *args, sep=" ", end="\n"):
        self.sidebuf += sep.join(str(i) for i in args)+end

    @property
    def title(self):
        return self.titles[self._cur]
    @title.setter
    def title(self, new):
        self.titles[self._cur] = new
    @property
    def selecting(self):
        return self.sel == self._cur

    def update(self, k):
        if k == key.TAB or k == '\033[Z': # Shift+tab
            self.sel = 1 - self.sel
            return
        if k == ' ':
            self.delfn(ExitCodes.CREATE)
            return
        if k == '\x03' or k == key.ESC or k == key.ESC+key.ESC:
            self.delfn(ExitCodes.CLOSE)
            return
        if k == ',':
            self.delfn(ExitCodes.BACK)
            return
        if k == '.':
            self.delfn(ExitCodes.FORWARDS)
        self._run(1, self._upd, k if self.sel == 1 else None)
        self._run(0, self._updSide, k if self.sel == 0 else None)

    def _init(self): pass
    def _upd(self, k=None): pass
    def _initSide(self): pass
    def _updSide(self, k=None): pass

    @property
    def mainBuffer(self):
        self.buf = fix(self.buf)
        sect = 1 if self.sidebuf else None
        return Buffer(self.buf, sect)
    @property
    def sideBuffer(self):
        self.sidebuf = fix(self.sidebuf)
        return Buffer(self.sidebuf, 0)

class ScrlWind(Window):
    def _initialise(self):
        if self._run(1, self._init):
            self.mainScrl = 0
        else:
            self.mainScrl = None
        if self._run(0, self._initSide):
            self.sideScrl = 0
        else:
            self.sideScrl = None

    @property
    def _scrl(self):
        return (self.sideScrl, self.mainScrl)[self.sel]
    @_scrl.setter
    def _scrl(self, new):
        if self.sel == 0:
            self.sideScrl = new
        else:
            self.mainScrl = new

    def update(self, k):
        scrl = self._scrl
        if scrl is not None:
            mod = None
            if k == key.UP:
                mod = -1
            elif k == key.DOWN:
                mod = 1
            elif k == key.PAGE_UP:
                mod = -5
            elif k == key.PAGE_DOWN:
                mod = 5
            if mod is not None:
                scrl = max(scrl + mod, 0)
                if scrl > 0:
                    scrl = min(scrl, self.getMaxScrl())
                self._scrl = scrl
                return
        super().update(k)

    def _init(self): return False
    def _initSide(self): return False

    @property
    def mainBuffer(self):
        self.buf = fix(self.buf)
        sect = 1 if self.sidebuf else None
        return Buffer(self.buf, sect, self.mainScrl or 0)
    @property
    def sideBuffer(self):
        self.sidebuf = fix(self.sidebuf)
        return Buffer(self.sidebuf, 0, self.sideScrl or 0)
    
    def getMaxScrl(self):
        if self.sel == 0:
            buf = self.sideBuffer
        else:
            buf = self.mainBuffer
        w, h, wid1, wid2, = getSizings()
        if self.sel == 0:
            w = wid1
        elif self.sidebuf:
            w = wid2
        return max(buf.howManyRows(w)-h, 0)

class AutoScrlWind(ScrlWind):
    def _bufprt(self, *args, **kwargs):
        super()._bufprt(*args, **kwargs)
        self.mainScrl = -1
    def _sideprt(self, *args, **kwargs):
        super()._bufprt(*args, **kwargs)
        self.sideScrl = -1
    def update(self, k):
        if self._scrl == -1:
            if k in (key.UP, key.DOWN, key.PAGE_UP, key.PAGE_DOWN):
                self._scrl = self.getMaxScrl()
        super().update(k)

