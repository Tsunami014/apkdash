from thread import Thread, Progress
import platform
import requests
import shutil
import json
import os
import zipfile
import tarfile

_toolpth = os.path.abspath(__file__+"/../.tools")
_dwnldpth = os.path.abspath(_toolpth+"/downloads")
if not os.path.exists(_toolpth):
    os.mkdir(_toolpth)
if not os.path.exists(_dwnldpth):
    os.mkdir(_dwnldpth)

class Tool(Thread):
    def __init__(self, wind, name):
        self.success = False
        fpth = f"{_toolpth}/{name}.json"
        if not os.path.exists(fpth):
            print(f"\020-Could not find tool with name {name}!")
            return super().__init__(wind, skip=True)
        with open(fpth) as f:
            self.tool = json.load(f)
        if self.tool['url_type'] == "java":
            s = platform.system()
            if s == "Linux":
                nam = "linux"
            elif s == "Windows":
                nam = "windows"
            elif s == "Darwin":
                nam = "mac"
            else:
                print(f"\020-Unsupported OS: {s}. Please install Java separately and ensure `java` is in the path.")
                return super().__init__(wind, skip=True)
            m = platform.machine().lower()
            if m in ("x86_64", "amd64"):
                arch = "x64"
            elif m in ("arm64", "aarch64"):
                arch = "aarch64"
            else:
                print(f"\020-Unsupported architecture: {m}. Please install Java separately and ensure `java` is in the path.")
                return super().__init__(wind, skip=True)
            
            self.tool['url'] = self.tool['url']\
                .replace("{version}", "21").replace("{os}", nam).replace("{arch}", arch)
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
        super().__init__(wind, skip=skip)

    @property
    def done(self):
        return self.success and super().done

    def main(self, print):
        if self.tool['url_type'] == "Github":
            print("\020~Downloading latest release from github...")
            params = self.tool['gh_params']
            resp = requests.get(self.tool['url'])
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"\020-Failed loading {self.tool['url']}!\n  {e}")
                return
            release_response = json.loads(resp.content)
            assets_url = release_response["assets_url"]
            resp2 = requests.get(assets_url)
            try:
                resp2.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"\020-Failed loading {assets_url}!\n  {e}")
                return
            assets_response = json.loads(resp2.content)
            for asset in assets_response:
                if asset["name"].endswith(params['prefix']):
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
        done = False
        if partial:
            print("\020~Found partial download, attempting to continue...")
            downloaded = os.path.getsize(tmppth)
            response = requests.get(url, stream=True, headers={"Range": f"bytes={downloaded}-"}, allow_redirects=True)
            if response.status_code != 206: # Server does not support partial complete downloading
                sze = int(response.headers.get('Content-Range', '/-1').split('/')[-1])
                if downloaded == sze:
                    print("\020+Already fully downloaded!")
                    done = True
                else:
                    print("\020*Partial download failed, fully retrying...")
                    os.remove(tmppth)
                    partial = False
            else:
                mode = 'ab'

        if not done:
            if not partial:
                mode = 'wb'
                downloaded = 0
                response = requests.get(url, stream=True, allow_redirects=True)
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    print(f"\020-Failed downloading {url}!\n  {e}")
                    return

            p = Progress(self, int(response.headers.get('Content-Length', 0)) + downloaded, downloaded)
            with open(tmppth, mode) as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    p(len(chunk))
            p.end()

        if self.tool['url_type'] == "java":
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
            print("\020+Successfully downloaded and extracted!")
        else:
            shutil.move(tmppth, self.pth)
            print("\020+Successfully downloaded!")
        self.success = True

