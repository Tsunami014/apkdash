from procedure import Procedure, step
from _main import Files
import tools
import os

__apps__ = ['Init']

class Init(Procedure):
    NAME = "Init"
    CHAR = "1"
    PRIO = 0
    def _init(self):
        self.title = "Initialising..."
        self.git = None
        if Files.APK_FILE is None:
            self.title = "Initialising failed"
            print("\020-No apk file found!")
            return self.stop()
        return True

    @step(1)
    def sInitial(self):
        if os.path.exists(Files.OUT_FOLDER):
            print("\020+Out folder already exists!")
            return True
        self.title = "Decompiling..."
        print("\020~Decompiling", Files.APK_FILE)
        return tools.ToolRunner(self, "apktool", "d", Files.APK_FILE, runTxt="Decompiling apk...").waiter()
    @step(2)
    def sGetGit(self):
        self.title = "Getting git..."
        if self.git is None:
            self.git = tools.GitTool(self)
            self.git.start()
        return self.git.waiter()
    @step(3)
    def sInitRepo(self):
        if os.path.exists(os.getcwd()+"/.git"):
            print("\020+Git repo already exists!")
            return True
        self.title = "Initialising repo..."
        print("\020~Initialising repo...")
        self.skip() # Skip next step (checking commits), because there are definately none
        return tools.Runner(self.git, "init", "--initial-branch=main").waiter()
    @step(4)
    def sCheckCommits1(self):
        self.title = "Checking commits..."
        print("\020~Checking commits...")
        runner = tools.Runner(self.git, "rev-parse", "--verify", "HEAD", quiet=True, ignoreErrors=True)
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
            lambda: tools.Runner(self.git, "commit", "-m", "Initial commit", quiet=True).waiter()
        )
    @step(999)
    def sFin(self):
        self.title = "Finished initialising!"
        print("\020+Finished!")
        return True

