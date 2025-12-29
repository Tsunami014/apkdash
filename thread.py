from threading import Thread as _T, Lock as _L
from _main import main
import builtins

class Progress:
    def __init__(self, t: 'Thread', print, max, initial=0):
        self.print = print
        self.wind = t._wind
        self.side = t.side
        self.max = max
        self.progress = 0
        print(upd=False)
        self(initial)

    def __call__(self, increase=0):
        self.progress += increase
        self.print(f"\020<\020%{self.progress}/{self.max}%")

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

