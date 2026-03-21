from procedure import Procedure, step
from _main import main, Files
import tools
import os
import shutil

__apps__ = ['Finish', 'ADB']

class ADB(Procedure):
    NAME = "ADB Reinstaller"
    CHAR = "-"
    PRIO = 0
    def _init(self):
        self.adb = None
        if Files.OUT_APK is None or not os.path.exists(Files.OUT_APK):
            self.title = "Reinstalling failed"
            print("\020-No built apk found! Run `Finish`")
            return self.stop()
        if Files.PACKAGE is None:
            self.title = "Reinstalling failed"
            print("\020-Package name could not be discerned!")
            return self.stop()
        self.title = "Reinstalling..."
        return True

    @step(1)
    def sGetAdb(self):
        self.title = "Getting adb..."
        if self.adb is None:
            self.adb = tools.ADBTool(self)
            self.adb.start()
        return self.adb.waiter()
    @step(2)
    def sUninstallExisting(self):
        self.title = "Uninstalling existing app..."
        print("\020~Uninstalling existing app (if exists)")
        return tools.Runner(self.adb, "uninstall", Files.PACKAGE, ignoreErrors=True).waiter()
    @step(3)
    def sInstallNew(self):
        self.title = "Installing new app..."
        print("\020~Installing new app")
        return tools.Runner(self.adb, "install", Files.OUT_APK).waiter()
    @step(4)
    def sLaunch(self):
        self.title = "Launching app..."
        print("\020~Launching app")
        return tools.Runner(self.adb, "shell", "monkey", "-p", Files.PACKAGE, "-c", "android.intent.category.LAUNCHER", "1").waiter()

    @step(999)
    def sFin(self):
        self.title = "Reinstalled!"
        print("\020+The built app should now be reinstalled onto your device!")
        return True

class Finish(Procedure):
    NAME = "Finish"
    CHAR = "0"
    PRIO = 0
    def _init(self):
        if Files.OUT_FOLDER is None or not os.path.exists(Files.OUT_FOLDER):
            self.title = "Finishing failed"
            print("\020-No out folder found! Run `Init`")
            return self.stop()
        self.pwd = None
        self.title = "Finishing..."
        self.BUILT_APK = os.path.join(Files.OUT_FOLDER, "dist", Files.BASENAME+".apk")
        self.SIGNED_APK = self.BUILT_APK[:-4]+"-aligned-debugSigned.apk"
        return True

    @step(1)
    def sRecompile(self):
        self.title = "Recompiling..."
        print("\020~Recompiling")
        return tools.ToolRunner(self, "apktool", "b", Files.OUT_FOLDER, runTxt="Recompiling into apk...").waiter()
    @step(2)
    def sSign(self):
        if not os.path.exists(self.BUILT_APK):
            self.title = "Finishing failed"
            print("\020-Could not find built file!")
            return self.stop()
        self.title = "Signing..."
        return tools.ToolRunner(self, "apksigner", "-a", self.BUILT_APK).waiter()
    @step(3)
    def sCopy(self):
        if not os.path.exists(self.SIGNED_APK):
            self.title = "Finishing failed"
            print("\020-Could not find signed file!")
            return self.stop()
        if os.path.exists(Files.OUT_APK):
            os.remove(Files.OUT_APK)
        shutil.copy2(self.SIGNED_APK, Files.OUT_APK)
        return True

    @step(999)
    def sFin(self):
        self.title = "Finished!"
        print("\020+Finished! The output apk file is in", self.BUILT_APK)
        return True
    
    def _upd(self, k=None):
        if k == '-':
            main.openWind('-')
        super()._upd(k)

