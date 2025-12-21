"""
\\020

< Clear last line
!! Clear screen

+ good
- bad
* warn
~ info

b bold
i invert
r reset colour
R reset all

cr colour red
cg colour green
cb colour blue
cc colour cyan
cm colour magenta
cy colour yellow
cW colour White
cG colour Grey
cB colour Black (invisible)
"""
import shutil
import re

def fix(txt):
    idx = txt.rfind("\020!!")
    if idx != -1:
        txt = txt[idx+3:]
    txt = re.sub('^.*\n?.*\020<', '', txt, flags=re.MULTILINE).lstrip("\n")
    if txt == '':
        return ''
    if txt[-1] == '\n':
        return txt.rstrip("\n")+"\n"
    return txt

def toPrintable(txt):
    safe = re.sub('\033\\[[0-9;]+.', '', txt)
    return safe\
        .replace('\020+', '[\03392m+\033[39m] ')\
        .replace('\020-', '[\03394m-\033[39m] ')\
        .replace('\020*', '[\03393m*\033[39m] ')\
        .replace('\020~', '[\03395m~\033[39m] ')\
        .replace('\020b', '\033[1m')\
        .replace('\020i', '\033[7m')\
        .replace('\020r', '\033[39m')\
        .replace('\020R', '\033[0m')\
        .replace('\020cr', '\033[91m')\
        .replace('\020cg', '\033[92m')\
        .replace('\020cb', '\033[94m')\
        .replace('\020cc', '\033[96m')\
        .replace('\020cm', '\033[95m')\
        .replace('\020cy', '\033[93m')\
        .replace('\020cW', '\033[97m')\
        .replace('\020cG', '\033[90m')\
        .replace('\020cB', '\033[30m')\
        .replace('\020', '�')

def popBuf(buf: str, wid: int):
    idx = buf.find("\n")
    if idx == -1 or wid < idx:
        return buf[:wid].ljust(wid), buf[wid:]
    return buf[:idx].ljust(wid), buf[idx+1:]

def printScreen(wind):
    size = shutil.get_terminal_size()
    buf = toPrintable(wind.buf)
    mxidx = 0
    if not wind.sidebuf:
        print("╭"+"─"*(size.columns-2)+"╮")
        for i in range(size.lines-2):
            prt, buf = popBuf(buf, size.columns-2)
            if buf.strip(" "):
                mxidx = i
            print("│"+prt+"│")
        print("╰"+"─"*(size.columns-2)+"╯", end="\033[0;0H", flush=True)
    else:
        sidebuf = toPrintable(wind.sidebuf)
        wid1 = (size.columns-3)//3
        wid2 = (size.columns-3)-wid1
        print("╭"+"─"*wid1+"┬"+"─"*wid2+"╮")
        for i in range(size.lines-2):
            prt1, sidebuf = popBuf(sidebuf, wid1)
            prt2, buf = popBuf(buf, wid2)
            if buf.strip(" ") or sidebuf.strip(" "):
                mxidx = i
            print("│"+prt1+"│"+prt2+"│")
        print("╰"+"─"*wid1+"┴"+"─"*wid2+"╯", end="\033[0;0H", flush=True)
    return mxidx

