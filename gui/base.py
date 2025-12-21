from .displ import fix, printScreen
import builtins

class Window:
    __slots__ = ['buf', 'sidebuf']

    def __init__(self):
        self.buf = ""
        self.sidebuf = ""

        _oldprt = builtins.print
        builtins.print = self._bufprt
        self._init()
        builtins.print = self._sideprt
        self._initSide()
        builtins.print = _oldprt
        self.buf = fix(self.buf)
        self.sidebuf = fix(self.sidebuf)

    def _bufprt(self, *args, sep=" ", end="\n"):
        self.buf += sep.join(args)+end
    def _sideprt(self, *args, sep=" ", end="\n"):
        self.sidebuf += sep.join(args)+end

    def update(self, char):
        _oldprt = builtins.print
        builtins.print = self._bufprt
        self._upd(char)
        builtins.print = self._sideprt
        self._updSide(char)
        builtins.print = _oldprt
        self.buf = fix(self.buf)
        self.sidebuf = fix(self.sidebuf)

    def _init(self): pass
    def _initSide(self): pass
    def _upd(self, char): pass
    def _updSide(self, char): pass

    def updprint(self, char):
        self.update(char)
        self.print()

    def print(self):
        printScreen(self)

