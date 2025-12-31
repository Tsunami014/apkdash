from _main import main
from thread import Lock
from threading import Thread
from gui import displ
import readchar
from builtins import print
import atexit

atexit.register(lambda: print("\033[2J\033[?25h", end=""))

def constant_print():
    from time import sleep, time
    while True:
        while time() < displ.lastPrtTime + 1:
            sleep(1)
        with Lock:
            main.print()

main.print()
Thread(target=constant_print, daemon=True).start()
while True:
    try:
        k = readchar.readkey()
    except KeyboardInterrupt:
        k = '\x03'
    with Lock:
        main.wind.update(k)
    main.print()
