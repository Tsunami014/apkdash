from .displ import fix, strlen, strcut, toPrintable, printScreen
from enum import IntEnum
from readchar import key
import builtins

class Buffer:
    __slots__ = ['txt', 'scroll']
    def __init__(self, txt, scroll=0):
        self.txt = txt
        self.scroll = scroll

    def initialFix(self, wid: int):
        while self.txt and self.scroll > 0:
            self.popBuf(wid)
            self.scroll -= 1

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
    EXCEPTION = 0
    """An exception occurred"""
    CREATE = 1
    """Go to app creation screen"""

class Window:
    __slots__ = ['_cur', 'buf', 'sidebuf', 'sel', 'delfn', 'titles']

    NAME: str
    PRIO: int = 0

    def __init__(self):
        self.buf = ""
        self.sidebuf = ""
        self.titles = ["", ""]
        self.sel = 0
        self.delfn = lambda code: None

        _oldprt = builtins.print
        builtins.print = self._bufprt
        self._cur = 1
        self._init()
        builtins.print = self._sideprt
        self._cur = 0
        self._initSide()
        builtins.print = _oldprt
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
        if k == ',':
            self.delfn(ExitCodes.CREATE)
            return
        if k == ' ':
            self.delfn(ExitCodes.PICK)
        _oldprt = builtins.print
        builtins.print = self._bufprt
        self._cur = 1
        self._upd(k if self.sel == 1 else None)
        builtins.print = self._sideprt
        self._cur = 0
        self._updSide(k if self.sel == 0 else None)
        builtins.print = _oldprt
        self.buf = fix(self.buf)
        self.sidebuf = fix(self.sidebuf)

    def _init(self): pass
    def _upd(self, k=None): pass
    def _initSide(self): pass
    def _updSide(self, k=None): pass

    @property
    def mainBuffer(self):
        self.buf = fix(self.buf)
        return Buffer(self.buf)
    @property
    def sideBuffer(self):
        self.sidebuf = fix(self.sidebuf)
        return Buffer(self.sidebuf)

class ScrlWind(Window):
    __slots__ = ['mainScrl', 'sideScrl']

    def __init__(self):
        self.buf = ""
        self.sidebuf = ""
        self.titles = ["", ""]
        self.sel = 0

        _oldprt = builtins.print
        builtins.print = self._bufprt
        self._cur = 1
        if self._init():
            self.mainScrl = 0
        else:
            self.mainScrl = None
        builtins.print = self._sideprt
        self._cur = 0
        if self._initSide():
            self.sideScrl = 0
        else:
            self.sideScrl = None
        builtins.print = _oldprt
        self.buf = fix(self.buf)
        self.sidebuf = fix(self.sidebuf)

    def update(self, k):
        old = (self.sideScrl, self.mainScrl)[self.sel]
        if old is not None:
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
                new = max(old + mod, 0)
                if self.sel == 0:
                    self.sideScrl = new
                else:
                    self.mainScrl = new
                return
        super().update(k)

    def _init(self): return False
    def _initSide(self): return False

    @property
    def mainBuffer(self):
        self.buf = fix(self.buf)
        return Buffer(self.buf, self.mainScrl or 0)
    @property
    def sideBuffer(self):
        self.sidebuf = fix(self.sidebuf)
        return Buffer(self.sidebuf, self.sideScrl or 0)

