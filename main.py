import readchar
from app import MainApp

main = MainApp()
main.wind.print()
while True:
    main.wind.updprint(readchar.readkey())
    if main.reprint:
        main.wind.print()
        main.reprint = False

