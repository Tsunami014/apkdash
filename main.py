import readchar
from app import MainApp
from gui.displ import printScreen

main = MainApp()
printScreen(main)
while True:
    main.wind.update(readchar.readkey())
    printScreen(main)
