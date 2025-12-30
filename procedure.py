from gui.wind import AutoScrlWind
from itertools import islice

def step(order):
    def decor(fn):
        fn._step = order
        return fn
    return decor

class Procedure(AutoScrlWind):
    def __init__(self, delfn=lambda _: None):
        def check(nam):
            attr = getattr(self, nam, None)
            return attr is not None and callable(attr) and hasattr(attr, "_step")
        self.steps = iter(sorted(
            (getattr(self, name) for name in dir(self) if check(name)),
            key=lambda f: f._step
        ))
        self.step = next(self.steps)
        super().__init__(delfn)

    def _initialise(self):
        super()._initialise()
        self._run(1, self._upd)

    def _upd(self, k=None):
        while True:
            nxt = self.step()
            if nxt is None:
                return
            if callable(nxt):
                self.step = nxt
            elif nxt is True:
                self.step = next(self.steps, self._stopfn)
            else:
                self.step = lambda nxtfn=next(self.steps, self._stopfn): nxtfn(*nxt)

    def _stopfn(self):
        return
    def stop(self):
        self.step = self._stopfn
    def skip(self, amnt=1):
        self.steps = islice(self.steps, amnt, None)

