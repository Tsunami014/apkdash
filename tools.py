from thread import Thread, Progress, Lock
import subprocess
import platform
import requests
import builtins
import shutil
import json
import os
import re
import zipfile
import tarfile

_toolpth = os.path.abspath(__file__+"/../.tools")
_dwnldpth = os.path.abspath(_toolpth+"/downloads")

class Runner(Thread):
    def __init__(self, t: '_ToolBase', *args, runTxt=None):
        self.tool = t
        self.ret = None
        self.runTxt = runTxt
        super().__init__(t._wind, *args)
        self.start()
    def main(self, print, *cmd):
        if not self.tool.success:
            self.tool.main(print)
        main = self.tool._run_args(self)
        if main is None:
            print(f"\020-Could not find run args for tool {self.tool.tool['name']}!")
            return
        if self.runTxt is not None:
            print("\020~"+self.runTxt)
        process = subprocess.Popen(
            main+list(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line-buffered
        )

        # Read line by line
        for line in process.stdout:
            print(line, end="")

        process.wait()

        self.ret = process.returncode

class ToolRunner(Runner):
    def __init__(self, wind, name, *args, runTxt=None):
        super().__init__(Tool(wind, name), *args, runTxt=runTxt)

class Tool:
    def __new__(cls, wind, name):
        if name == "java":
            return JavaTool(wind)
        if name == "git":
            return GitTool(wind)
        return RegularTool(wind, name)

class _ToolBase(Thread):
    def _setup_tool(self, name):
        self.success = False
        fpth = f"{_toolpth}/{name}.json"
        if not os.path.exists(fpth):
            print(f"\020-Could not find tool with name {name}!")
            return False
        with open(fpth) as f:
            self.tool = json.load(f)
        return True

    def _find_tool(self):
        pth = shutil.which(self.tool['cmd'])
        if pth is not None:
            self.pth = pth
            skip = True
            print(f"\020+Found {self.tool['name']} in the path, using that.")
            self.success = True
        else:
            self.pth = f"{_dwnldpth}/{self.tool['fname']}"
            skip = os.path.exists(self.pth)
            if skip:
                print("\020+Tool already downloaded:", self.tool['name'])
                self.success = True
            else:
                print(f"\020~Could not find {self.tool['name']}, downloading from {self.tool['url']}...")
        return skip

    @property
    def done(self):
        return self.success and super().done

    def _download(self, print):
        if not os.path.exists(_toolpth):
            os.mkdir(_toolpth)
        if not os.path.exists(_dwnldpth):
            os.mkdir(_dwnldpth)
        if self.tool['url_type'] == "Github":
            print("\020~Downloading latest release from github...")
            params = self.tool['gh_params']
            resp = requests.get(self.tool['url'])
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"\020-Failed loading {self.tool['url']}!\n\t{e}")
                return
            release_response = json.loads(resp.content)
            assets_url = release_response["assets_url"]
            resp2 = requests.get(assets_url)
            try:
                resp2.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"\020-Failed loading {assets_url}!\n\t{e}")
                return
            assets_response = json.loads(resp2.content)
            reg = re.compile(params['matches'])
            for asset in assets_response:
                if reg.fullmatch(asset["name"]):
                    print(f"\020~Downloading asset {asset['name']}...")
                    url = asset['browser_download_url']
                    break
            else:
                print("\020-Could not find an avaliable asset!")
                return
        else:
            url = self.tool['url']

        tmppth = self.pth+".tmp"

        partial = os.path.exists(tmppth)
        if partial:
            print("\020~Found partial download, attempting to continue...")
            downloaded = os.path.getsize(tmppth)
            response = requests.get(url, stream=True, headers={"Range": f"bytes={downloaded}-"}, allow_redirects=True)
            if response.status_code != 206: # Server does not support partial complete downloading
                sze = int(response.headers.get('Content-Range', '/-1').split('/')[-1])
                if downloaded == sze:
                    print("\020+Already fully downloaded!")
                    return tmppth
                else:
                    print("\020*Partial download failed, fully retrying...")
                    os.remove(tmppth)
                    partial = False
            else:
                mode = 'ab'

        if not partial:
            mode = 'wb'
            downloaded = 0
            response = requests.get(url, stream=True, allow_redirects=True)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"\020-Failed downloading {url}!\n  {e}")
                return

        p = Progress(self, print, int(response.headers.get('Content-Length', 0)) + downloaded, downloaded)
        with open(tmppth, mode) as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                p(len(chunk))
        p.end()

        return tmppth


class RegularTool(_ToolBase):
    def __init__(self, wind, name):
        if not self._setup_tool(name):
            return super().__init__(wind, skip=True)
        super().__init__(wind, skip=self._find_tool())

    def _run_args(self, rn: Runner):
        rt = self.tool['run_type']
        if rt == 'java':
            with Lock: # So other things don't print with this print
                oprt = builtins.print
                builtins.print = rn._print
                javtool = JavaTool(self._wind)
                builtins.print = oprt
            if not javtool.success:
                javtool.main(rn._printLock)
            if javtool.success:
                return [os.path.join(javtool.pth, "bin", "java"), "-jar", self.pth]
            else:
                rn._printLock("\020-Failed to install Java so cannot run command!")
        return None

    def main(self, print):
        tmppth = self._download(print)
        shutil.move(tmppth, self.pth)
        print(f"\020+Successfully downloaded {self.tool['name']}!")
        self.success = True


class JavaTool(_ToolBase):
    def __init__(self, wind):
        if not self._setup_tool("java"):
            return super().__init__(wind, skip=True)
        s = platform.system()
        if s == "Linux":
            nam = "linux"
        elif s == "Windows":
            nam = "windows"
        elif s == "Darwin":
            nam = "mac"
        else:
            print(f"\020-Unsupported OS when installing java: {s}. Please install Java separately and ensure `java` is in the path.")
            return super().__init__(wind, skip=True)
        m = platform.machine().lower()
        if m in ("x86_64", "amd64"):
            arch = "x64"
        elif m in ("arm64", "aarch64"):
            arch = "aarch64"
        else:
            print(f"\020-Unsupported architecture when installing java: {m}. Please install Java separately and ensure `java` is in the path.")
            return super().__init__(wind, skip=True)
        
        self.tool['url'] = self.tool['url']\
            .replace("{version}", "21").replace("{os}", nam).replace("{arch}", arch)

        super().__init__(wind, skip=self._find_tool())

    def _run_args(self, rn):
        return [os.path.join(self.pth, "bin", "java")]

    def main(self, print):
        tmppth = self._download(print)

        tmp_dir = tmppth+".extract"
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        try:
            with zipfile.ZipFile(tmppth) as z:
                z.extractall(tmp_dir)
        except zipfile.BadZipFile:
            try:
                with tarfile.open(tmppth, "r:*") as t:
                    t.extractall(tmp_dir)
            except tarfile.ReadError:
                print("\020-Could not discern archive format!")
                return

        entries = os.listdir(tmp_dir)
        if len(entries) != 1: # There is more than 1 thing in the top level, all should be ok
            shutil.move(tmp_dir, self.pth)
        else: # The folder was wrapped in another folder
            shutil.move(os.path.join(tmp_dir, entries[0]), self.pth)
            shutil.rmtree(tmp_dir)
        os.remove(tmppth)
        print("\020+Successfully downloaded and extracted Java!")
        self.success = True

class GitTool(_ToolBase):
    def __init__(self, wind):
        if not self._setup_tool("git"):
            return super().__init__(wind, skip=True)
        found = self._find_tool()
        s = platform.system()
        if s == "Windows":
            m = platform.machine().lower()
            if m in ("i386", "i486", "i586", "i686", "x86"):
                arch = "32-bit"
            elif m in ("x86_64", "amd64"):
                arch = "64-bit"
            elif m in ("arm64", "aarch64"):
                arch = "arm64" 
            else:
                print(f"\020-Unsupported architecture when installing git: {m}. Please install Git separately and ensure `git` is in the path.")
                return super().__init__(wind, skip=True)
            self.tool['gh_params']['matches'].replace("typ", arch)
            return super().__init__(wind, skip=found)
        if not found:
            print("\020-Autodownload for git only works for Windows, and git was not found in path. Please download git separately.")
        return super().__init__(wind, skip=True)

    def _run_args(self, rn):
        return [self.pth]

