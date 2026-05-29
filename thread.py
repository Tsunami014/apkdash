import threading
from _main import main
import ctypes

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


Lock = threading.Lock()
class Thread:
    def __init__(self, wind, *args, skip=False, ignoreErrors=False):
        self._wind = wind
        self.side = wind._cur
        self.ignoreEr = ignoreErrors
        self._prt = print
        if skip:
            self.t = None
        else:
            self.t = threading.Thread(target=self._target, args=args, name=self.__class__.__name__, daemon=True)

    def error(self, msg, e=None):
        if self.ignoreEr:
            return
        self._prt("\020-"+msg)
        if e is not None:
            self._prt("\t"+str(e))
        while True:
            pass

    def waiter(self, onfin=True):
        def wait():
            if self.done:
                return onfin
        return wait

    def start(self):
        if self.t is not None:
            self.t.start()
        else:
            self._end()

    def stop(self):
        if self.done:
            return

        for tid, tobj in threading._active.items():
            if tobj is self.t:
                break
        else:
            raise AssertionError(
                "Could not determine the thread's id!"
            )

        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(KeyboardInterrupt))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # "if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    @property
    def done(self):
        return self.t is None or not self.t.is_alive()

    def _target(self, *args):
        try:
            self.main(self._printLock, *args)
        except KeyboardInterrupt:
            return
        with Lock:
            self.t = None # So self.done is True
            self._end()

    def _end(self):
        oldcur = self._wind._cur
        self._wind._run(1, self._wind._upd)
        self._wind._run(0, self._wind._updSide)
        self._wind._cur = oldcur
        main.print()

    def main(self, print):
        pass

    def _print(self, *args, upd=True, **kwargs):
        self._prt(*args, **kwargs)
        if upd and main.wind is self._wind:
            main.print()
    def _printLock(self, *args, **kwargs):
        with Lock:
            self._print(*args, **kwargs)

