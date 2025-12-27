from _main import main
from thread import Lock
import readchar

main.print()
try:
    while True:
        k = readchar.readkey()
        with Lock:
            main.wind.update(k)
        main.print()
except KeyboardInterrupt:
    print("\033[2J", end="", flush=True)
