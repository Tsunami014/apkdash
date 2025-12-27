from _main import main
from thread import Lock
import readchar

main.print()
while True:
    try:
        k = readchar.readkey()
    except KeyboardInterrupt:
        k = '\x03'
    with Lock:
        main.wind.update(k)
    main.print()
