from threading import Thread as _T, Lock as _L
from gui.displ import getSizings
from _main import main
import builtins

class Progress:
    def __init__(self, t: 'Thread', max):
        self.print = t._print
        self.wind = t._wind
        self.side = t.side
        self.max = max
        self.progress = 0
        self.print(upd=False)
        self()

    def __call__(self, increase=0):
        self.progress += increase
        perc = round(self.progress / self.max * 100, 3)
        t1, t2 = "Progress:", f" {perc}%"
        self.print(f"\020<\020b{t1}\020r{t2}", end="", upd=False)
        if self.max > 0 and 0 <= self.progress < self.max:
            _, __, wid1, wid2 = getSizings()
            if self.wind.sidebuf == "":
                wid = wid1 + wid2
            else:
                wid = [wid1, wid2][self.side]
            wid -= len(t1)+len(t2) + 3
            filled = round(self.progress / self.max * wid)
            line = "█"*filled + "░"*(wid-filled)
            self.print(f"  {line}")
        else:
            self.print()

    def end(self):
        self.progress = self.max
        self()


Lock = _L()
class Thread:
    def __init__(self, wind, *args, skip=False):
        self._wind = wind
        self.side = wind._cur
        self._prt = builtins.print
        if skip:
            self.t = None
        else:
            self.t = _T(target=self._target, args=args, name=self.__class__.__name__, daemon=True)

    def start(self):
        if self.t is not None:
            self.t.start()
        else:
            self._end()

    @property
    def done(self):
        return self.t is None or not self.t.is_alive()

    def _target(self, *args):
        self.main(self._printLock, *args)
        with Lock:
            self.t = None # So self.done is True
            self._end()

    def _end(self):
        oldprt = builtins.print
        oldcur = self._wind._cur
        self._wind._cur = self.side
        builtins.print = self._print
        if self.side == 1:
            self._wind._upd()
        else:
            self._wind._updSide()
        builtins.print = oldprt
        self._wind._cur = oldcur

    def main(self, print):
        pass

    def _print(self, *args, upd=True, **kwargs):
        self._prt(*args, **kwargs)
        if upd and main.wind is self._wind:
            main.print()
    def _printLock(self, *args, **kwargs):
        with Lock:
            self._print(*args, **kwargs)

