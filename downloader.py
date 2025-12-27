from thread import Thread, Progress
import requests
import json
import os

_toolpth = os.path.abspath(__file__+"/../tools/")
if not os.path.exists(_toolpth):
    os.mkdir(_toolpth)

class Download(Thread):
    def __init__(self, wind, fname, url):
        self.pth = _toolpth+"/"+fname
        skip = os.path.exists(self.pth)
        if not skip:
            print(f"\020~Could not find {fname} in tools, downloading from {url}...")
        super().__init__(wind, url, skip=skip)

    def main(self, print, url):
        response = requests.get(url, stream=True)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"\020-Failed downloading {url}!\n  {e}")
            return

        p = Progress(self, int(response.headers.get('Content-Length', 0)))
        with open(self.pth, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                p(len(chunk))
        p.end()

        print("\020+Successfully downloaded!")

class GithubDownload(Download):
    def main(self, print, url):
        print("\020~Downloading latest release from github...")
        asset_ext = self.pth.split(".")[-1]
        resp = requests.get(url)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"\020-Failed loading {url}!\n  {e}")
            return
        release_response = json.loads(resp.content)
        assets_url = release_response["assets_url"]
        resp2 = requests.get(assets_url)
        try:
            resp2.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"\020-Failed loading {url}!\n  {e}")
            return
        assets_response = json.loads(resp2.content)
        for asset in assets_response:
            if asset["name"].endswith(asset_ext):
                print(f"\020~Downloading asset {asset['name']}...")
                super().main(print, asset['browser_download_url'])
                break
        else:
            print("\020-Could not find an avaliable asset!")

