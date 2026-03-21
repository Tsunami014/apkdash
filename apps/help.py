from gui.wind import ScrlWind

__apps__ = ['Help']

class Help(ScrlWind):
    NAME = "Help"
    CHAR = "?"
    PRIO = -1
    def _init(self):
        print("""
\020b\020ccHelp!
\020b\020cyNavigation
- Up or down to scroll
- Tab to toggle which panel you are looking at (if multiple), you will be able to see at the top which one is highlighted
- Space to go to the apps screen
- , or . to switch between open screens (indicator in bottom left)
- Ctrl+c or Q (capital) or Esc (may have to press twice to work) to exit the current screen, \020ior if on choose apps screen, will quit the app.\020R
"""[1:-1])

