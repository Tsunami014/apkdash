from procedure import Procedure, step
from _main import main, BUILT_APK, OUT_FOLDER, KEYSTORE, KEYSTORE_PASSWORD
import tools
import os

__apps__ = ['Finish']

class Finish(Procedure):
    NAME = "Finish"
    CHAR = "0"
    PRIO = 0
    def _init(self):
        if OUT_FOLDER is None or not os.path.exists(OUT_FOLDER):
            self.title = "Finishing failed"
            print("\020-No out folder found! Run `Init`")
            return self.stop()
        self.pwd = None
        self.title = "Finishing..."
        return True

    @step(1)
    def sRecompile(self):
        self.title = "Recompiling..."
        print("\020~Recompiling")
        return tools.ToolRunner(self, "apktool", "b", OUT_FOLDER, runTxt="Recompiling into apk...").waiter()
    @step(2)
    def sGetKey(self):
        self.title = "Signing..."
        if os.path.exists(KEYSTORE_PASSWORD):
            with open(KEYSTORE_PASSWORD) as f:
                self.pwd = f.readline()

        if os.path.exists(KEYSTORE):
            if self.pwd is None:
                print("\020+Keystore already exists!")
            else:
                print("\020-Keystore already exists, but no password file was found!")
                self.stop()
            return True
        if self.pwd is None:
            self.pwd = "test1234"
            with open(KEYSTORE_PASSWORD, "w+") as f:
                f.writelines([
                    self.pwd, f"The first line contains the password for '{os.path.relpath(KEYSTORE, os.path.dirname(KEYSTORE_PASSWORD))}'"
                ])
        print(f"\020~Generating a keystore with password `{self.pwd}`")
        return tools.ToolRunner(self, "keytool",
            "-genkey", "-v",
            "-keystore", KEYSTORE,
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-alias", "app",
            "-storepass", self.pwd,
            "-dname", "CN=Testy, OU=Test, O=Test, L=None, ST=None, C=None",
        runTxt="Generating keystore...").waiter()

    @step(3)
    def sSign(self):
        return tools.ToolRunner(self, "apksigner", "sign", "--ks", KEYSTORE, "--ks-pass" "pass:"+self.pwd, BUILT_APK)

    @step(999)
    def sFin(self):
        self.title = "Finished!"
        print("\020+Finished! The output apk file is in", BUILT_APK)
        print("\020*Press - to open the adb reinstaller")
        return True
    
    def _upd(self, k=None):
        if k == '-':
            main.openNew('-')
        super().update(k)

