import xml.etree.ElementTree as ET
from selecter import SelectWind
from _main import OUT_FOLDER
from thread import Thread
import os

class GetValues(Thread):
    values = {}
    ids = {}
    unuseds = {}
    def __init__(self, wind):
        super().__init__(wind, skip=GetValues.values)
    def main(self, print):
        print("\020~Finding all values...")
        self.iterFold(print, os.path.join(OUT_FOLDER, "res"))
        print("\020~Updating ids...")
        for i in self.ids:
            if i in self.values:
                self.values[i]['id'] = self.ids[i]
        print("\020~Sorting...")
        self.values = dict(sorted(self.values.items()))
        self.ids = dict(sorted(self.ids.items()))
        print("\020~Finding unused ids...")
        for i in self.ids:
            if i not in self.values:
                self.unuseds[i] = self.ids[i]
        print("\020!!")
    def iterFold(self, print, pth):
        for i in os.listdir(pth):
            full = os.path.join(pth, i)
            if os.path.isdir(full):
                self.iterFold(print, full)
            elif i.endswith(".xml"):
                self.parse_xml(print, full)
    def parse_xml(self, print, f):
        tree = ET.parse(f)
        root = tree.getroot()
        if not root.tag == 'resources':
            return
        print("- Found resource file: "+os.path.basename(f))
        for rs in root:
            if rs.tag in ('public', 'item'):
                val = f"@{rs.attrib['type']}/{rs.attrib['name']}"
                if val in self.ids and self.ids[val] is not None:
                    raise ValueError(
                        f"Multiple id definitions for {val}!"
                    )
                self.ids[val] = rs.attrib.get('id', None)
            else:
                val = f"@{rs.tag}/{rs.attrib['name']}"
                self.values[val] = {
                    "text": rs.text,
                    "id": None,
                    **rs.attrib
                }


__apps__ = ['ValueEditor']

class ValueEditor(SelectWind):
    NAME = "Value Editor"
    CHAR = "v"
    PRIO = 1
    def _init(self):
        self.title = "Value editor"
        self.vs = GetValues(self)
        self.vs.start()
        self.printed = False
        return True
    def _upd(self, k=None):
        if not self.printed and self.vs.done:
            if self.vs.values:
                for nam, rs in self.vs.values.items():
                    if rs['id'] is None:
                        typtxt = ""
                    else:
                        typtxt = f" ({rs['id']})"
                    print(f"- \020b{nam}\020R{typtxt}\020... {rs['text']}")
                if self.vs.unuseds:
                    print("\n\020=\n")
            if self.vs.unuseds:
                for nam, id in self.vs.unuseds.items():
                    if id is None:
                        xtra = ""
                    else:
                        xtra = f" ({id})"
                    print(f"- \020b{nam}\020R{xtra}")
            self.printed = True
    def _initSide(self):
        return True
    def _updSide(self, k=None):
        ln = self.getCurLine(1)
        print("\020!!")
        if len(ln) > 0 and ln[0] == '-':
            print(ln)

