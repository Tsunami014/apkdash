import os
class Files:
    APK_FILE = None
    BASENAME = None
    OUT_FOLDER = None
    PACKAGE = None
    OUT_APK = None
    @classmethod
    def recalculate(cls):
        cls.APK_FILE = cls._getapk()
        if cls.APK_FILE is not None:
            cls.BASENAME = cls.APK_FILE[:cls.APK_FILE.rindex(".")].split('/')[-1]
            cls.OUT_FOLDER = cls.APK_FILE[:cls.APK_FILE.rindex(".")]
            cls.PACKAGE = cls._getPkg()
            cls.OUT_APK = cls.OUT_FOLDER+".out.apk"
        else:
            cls.BASENAME = None
            cls.OUT_FOLDER = None
            cls.PACKAGE = None
            cls.OUT_APK = None
            cls.SIGNED_APK = None

    @classmethod
    def _getapk(cls):
        for i in os.listdir(os.getcwd()):
            if i.endswith(".apk"):
                pth = os.path.join(os.getcwd(), i)
                return os.path.abspath(pth)
        return None
    @classmethod
    def _getPkg(cls):
        manifest = os.path.join(cls.OUT_FOLDER, "AndroidManifest.xml")
        if os.path.exists(manifest):
            import xml.etree.ElementTree as ET
            tree = ET.parse(manifest)
            root = tree.getroot()
            return root.attrib.get("package", None)
        return None

if 'main' not in globals():
    from app import MainApp
    from gui.wind import ScrlWind
    from readchar import key
    main = MainApp()

    class CreateWind(ScrlWind):
        def _init(self):
            self.title = "New window"
            Files.recalculate()
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
            if k == '\x03' or k == key.ESC or k == key.ESC+key.ESC or k == 'Q':
                quit()
            if self.sel == 1 and k in main.apps.keys():
                main.openWind(k)
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
            home = os.path.expanduser("~")
            def display(pth):
                if pth.startswith(home):
                    return pth.replace(home, "~", 1)
                return pth
            self.title = "Config"
            print("- \020bFolder:\n  "+os.getcwd())
            if Files.APK_FILE is None:
                print("- \020b\020crCould not find an avaliable apk file in this folder!")
            else:
                print("- \020bApk file:\n  "+display(Files.APK_FILE))
                if os.path.exists(Files.OUT_FOLDER):
                    print("- \020bOut folder:\n  "+display(Files.OUT_FOLDER))
                    if Files.PACKAGE is not None:
                        print("- \020bPackage:\n  "+display(Files.PACKAGE))
                    else:
                        print("- \020b\020crCould not find the package!")
                    if os.path.exists(Files.OUT_APK):
                        print("- \020bBuilt apk:\n  "+display(Files.OUT_APK))
                    else:
                        print("- \020b\020ccApk file has never been built (Run `Finish`)")
                else:
                    print("- \020b\020ccOut folder does not exist! (Run `Init`)")
            return True

    main._initialise(CreateWind)

