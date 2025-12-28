from thread import Thread, Progress
import requests
import shutil
import json
import os

_toolpth = os.path.abspath(__file__+"/../.tools")
_dwnldpth = os.path.abspath(_toolpth+"/downloads")
if not os.path.exists(_toolpth):
    os.mkdir(_toolpth)
if not os.path.exists(_dwnldpth):
    os.mkdir(_dwnldpth)

class Tool(Thread):
    def __init__(self, wind, name):
        fpth = f"{_toolpth}/{name}.json"
        if os.path.exists(fpth):
            with open(fpth) as f:
                self.tool = json.load(f)
            pth = shutil.which(self.tool['cmd'])
            if pth is not None:
                self.pth = pth
                skip = True
                print(f"\020+Found {self.tool['name']} in the path, using that.")
            else:
                self.pth = f"{_dwnldpth}/{self.tool['fname']}"
                skip = os.path.exists(self.pth)
                if skip:
                    print("\020+Tool already downloaded:", self.tool['name'])
                else:
                    print(f"\020~Could not find {self.tool['name']} in tools, downloading from {self.tool['url']}...")
        else:
            print(f"\020-Could not find tool with name {name}!")
            skip = True
        super().__init__(wind, skip=skip)

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

        headers = {}
        mode = 'wb'
        downloaded = 0

        if os.path.exists(self.pth+".tmp"):
            print("\020~Found partial download, attempting to continue...")
            downloaded = os.path.getsize(self.pth + ".tmp")
            headers['Range'] = f"bytes={downloaded}-"
            mode = 'ab'
        response = requests.get(url, stream=True, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"\020-Failed downloading {url}!\n  {e}")
            return
        if mode == 'ab' and response.status_code != 206: # Server does not support partial complete downloading
            print("\020*Server does not support partial downloading, fully retrying...")
            os.remove(self.pth+".tmp")
            mode = 'wb'
            downloaded = 0

        p = Progress(self, int(response.headers.get('Content-Length', 0)) + downloaded, downloaded)
        with open(self.pth+".tmp", mode) as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                p(len(chunk))
        p.end()

        shutil.move(self.pth+".tmp", self.pth)
        print("\020+Successfully downloaded!")

