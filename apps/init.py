from procedure import Procedure, step
from _main import APK_FILE, OUT_FOLDER
import tools
import os

__apps__ = ['Init']

class Init(Procedure):
    NAME = "Init"
    CHAR = "1"
    def _init(self):
        self.title = "Initialising..."
        self.git = None
        if APK_FILE is None:
            self.title = "Initialising failed"
            print("\020-No apk file found in current directory! (See `config` for info)")
            return self.stop()
        return True

    @step(1)
    def sInitial(self):
        if os.path.exists(OUT_FOLDER):
            print("\020+Out folder already exists!")
            return True
        self.title = "Decompiling..."
        print("\020~Initialising", APK_FILE)
        return tools.ToolRunner(self, "apktool", "d", APK_FILE, runTxt="Decompiling apk...").waiter()
    @step(2)
    def sGetGit(self):
        self.title = "Getting git..."
        self.git = tools.GitTool(self)
        return self.git.waiter()
    @step(3)
    def sInitRepo(self):
        if os.path.exists(os.getcwd()+"/.git"):
            print("\020+Git repo already exists!")
            return True
        self.title = "Initialising repo..."
        print("\020~Initialising repo...")
        self.skip() # Skip checking, because there is definately none
        return tools.Runner(self.git, "init").waiter()
    @step(4)
    def sCheckCommits1(self):
        self.title = "Checking commits..."
        print("\020~Checking commits...")
        runner = tools.Runner(self.git, "rev-parse", "--verify", "HEAD")
        return runner.waiter([runner])
    @step(5)
    def sCheckCommits2(self, rnr=None):
        if rnr is not None:
            if rnr.ret == 0:
                print("\020+Found commits!")
                return True
            print("\020*Did not find commits, adding initial commit...")
        else:
            print("\020~Adding initial commit...")
        self.title = "Adding initial commit..."
        return tools.Runner(self.git, "add", "-A").waiter(
            lambda: tools.Runner(self.git, "commit", "-m", "Initial commit").waiter()
        )
    @step(999)
    def sFin(self):
        self.title = "Finished initialising!"
        print("\020+Finished!")
        return True

