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

def strlen(txt):
    return len(re.sub('\020(?:[+\\-*~birR]|c[rgbcmyWGB]|)', '', txt))

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

def fixTitle(tit, wid):
    if tit == "":
        return "─"*wid
    ntit = tit[:wid-2]
    return " "+toPrintable(ntit)+"\033[0m "+"─"*(wid-strlen(ntit))

def printScreen(wind):
    size = shutil.get_terminal_size()
    buf = wind.mainBuffer
    mxidx = 0
    print("\033[0;0H", end="")
    if not wind.sidebuf:
        buf.initialFix(size.columns-2)
        print("╭"+fixTitle(wind.titles[1], size.columns-4)+"╮")
        for i in range(size.lines-2):
            prt = buf.popBuf(size.columns-2)
            if buf:
                mxidx = i
            print("│"+prt+"\033[0m│")
        print("╰"+"─"*(size.columns-2)+"╯", end="\033[0;2H", flush=True)
        wind.sel = 1
    else:
        wid1 = (size.columns-3)//3
        wid2 = (size.columns-3)-wid1
        sidebuf = wind.sideBuffer
        sidebuf.initialFix(wid1)
        buf.initialFix(wid2)
        print("╭"+fixTitle(wind.titles[0], wid1)+"┬"+fixTitle(wind.titles[1], wid2)+"╮")
        for i in range(size.lines-2):
            prt1 = sidebuf.popBuf(wid1)
            prt2 = buf.popBuf(wid2)
            if buf or sidebuf:
                mxidx = i
            print("│"+prt1+"\033[0m│"+prt2+"\033[0m│")
        if wind.sel == 0:
            curspos = 2
        else:
            curspos = wid1+3
        print("╰"+"─"*wid1+"┴"+"─"*wid2+"╯", end=f"\033[0;{curspos}H", flush=True)
    return mxidx

