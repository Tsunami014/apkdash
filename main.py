import os
import sys

dos = {}
args = sys.argv[1:]
while len(args) > 0:
    a = args.pop(0)
    if a == '-h' or a == '--help':
        willdo = "help"
    else:
        willdo = "setcwd"
    if willdo in dos:
        print(f"Cannot have multiple '{willdo}' arguments!")
        exit(1)
    dos[willdo] = a
if "help" in dos:
    print("""ApkDash

Optional arguments:
    -h - Show this help
    [folder] - An optional folder to start looking in, if not set will use the current directory
"""[:-1])
    exit(0)
if "setcwd" in dos:
    sys.path.insert(0, os.getcwd())
    os.chdir(
        os.path.abspath(dos["setcwd"])
    )

# Because some of these depend on the current directory, we must import after fixing it
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
