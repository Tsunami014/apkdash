import os
def _getapk():
    for i in os.listdir(os.getcwd()):
        if i.endswith(".apk"):
            return os.path.join(os.getcwd(), i)
    return None

APK_FILE = _getapk()
if APK_FILE is not None:
    OUT_FOLDER = APK_FILE[:APK_FILE.rindex(".")]

if 'main' not in globals():
    from app import MainApp
    from gui.wind import ScrlWind
    from builtins import print as origPrt
    from readchar import key
    main = MainApp()

    class CreateWind(ScrlWind):
        def _init(self):
            self.title = "New window"
            lstpri = -1
            for c, a in main.apps.items():
                if a.PRIO != lstpri:
                    print("\020=")
                    lstpri = a.PRIO
                print(f"\020b{c}\020R: {a.NAME}")
            return True
        def _upd(self, k=None):
            if k == '\x03' or k == key.ESC or k == key.ESC+key.ESC:
                origPrt("\033[2J", end="", flush=True)
                quit()
            if k in main.apps.keys():
                main.setWind(main.apps[k])
                return
            super()._upd(k)

    main._initialise(CreateWind)

