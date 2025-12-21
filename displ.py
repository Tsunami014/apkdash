"""
\\020

< go to start of this line (use with 'end="\\020<"')

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

def toPrintable(txt):
    safe = re.sub('\033\\[[0-9;]+.', '', txt)
    return safe\
        .replace('\020<', '\r')\
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
        .replace('\020cB', '\033[30m')

def popBuf(buf: str, wid: int):
    idx = buf.find("\n")
    if idx == -1 or wid < idx:
        return buf[:wid].ljust(wid), buf[wid:]
    return buf[:idx].ljust(wid), buf[idx+1:]

def printScreen(buf, sidebuf=None):
    size = shutil.get_terminal_size()
    if sidebuf is None:
        print("╭"+"─"*(size.columns-2)+"╮")
        for _ in range(size.lines-2):
            prt, buf = popBuf(buf, size.columns-2)
            print("│"+prt+"│")
        print("╰"+"─"*(size.columns-2)+"╯", end="\033[0;0H", flush=True)
    else:
        wid1 = (size.columns-3)//3
        wid2 = (size.columns-3)-wid1
        print("╭"+"─"*wid1+"┬"+"─"*wid2+"╮")
        for _ in range(size.lines-2):
            prt1, sidebuf = popBuf(sidebuf, wid2)
            prt2, buf = popBuf(buf, wid2)
            print("│"+prt1+"│"+prt2+"│")
        print("╰"+"─"*wid1+"┴"+"─"*wid2+"╯", end="\033[0;0H", flush=True)

