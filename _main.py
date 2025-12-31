import os
def _getapk():
    for i in os.listdir(os.getcwd()):
        if i.endswith(".apk"):
            pth = os.path.join(os.getcwd(), i)
            home = os.path.expanduser("~")
            if pth.startswith(home):
                pth = os.path.join("~", os.path.relpath(pth, home))
            return pth
    return None

APK_FILE = _getapk()
if APK_FILE is not None:
    OUT_FOLDER = APK_FILE[:APK_FILE.rindex(".")]
else:
    OUT_FOLDER = None

if 'main' not in globals():
    from app import MainApp
    from gui.wind import ScrlWind
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
                nam = a.NAME
                if c in main.opens.keys():
                    nam = "\020b*"+nam
                print(f"\020b{c}\020R: {nam}")
            self.sel = 1
            return True
        def update(self, k):
            if k == '\x03' or k == key.ESC or k == key.ESC+key.ESC:
                quit()
            if self.sel == 1 and k in main.apps.keys():
                if k in main.opens.keys():
                    toopen = main.opens[k]
                    idx = main.recents.index(toopen)
                    main.opens.pop(list(main.opens.keys())[idx])
                    main.recents.pop(idx)
                    main.setWind(toopen, int(main.idx < len(main.recents)-1))
                else:
                    main.setWind(main.mkWind(main.apps[k]))
                    main.wind._initialise()
                return
            if k == ' ':
                if main.idx > 0:
                    main.idx -= 0.5
                    main.wind = main.recents[int(main.idx)]
                elif main.idx == 0:
                    main.wind = main.recents[int(main.idx)]
                elif len(main.recents) > 0:
                    main.wind = main.recents[0]
                    main.idx = 0
                return
            super().update(k)

        def _initSide(self):
            self.title = "Config"
            print("- \020bFolder:\n  "+os.getcwd())
            if APK_FILE is None:
                print("- \020bCould not find an avaliable apk file in this folder!")
            else:
                print("- \020bApk file:\n  "+APK_FILE)
                if os.path.exists(OUT_FOLDER):
                    print("- \020bOut folder:\n  "+OUT_FOLDER)
                else:
                    print("- \020bOut folder does not exist! (Try running `Init`)")
            return True

    main._initialise(CreateWind)

