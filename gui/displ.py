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
    return len(re.sub(r'\020(?:[+\-*~birR]|c[rgbcmyWGB]|)|\033\[[0-9;]*.', '', txt).replace('\020', ' ').replace('\033', ''))

def toPrintable(txt):
    safe = re.sub('\020(?:.|c.)$', '', txt, 1)

    # Get rid of regular \033s but keep ones relating to colour or bold/stuff (for terminal outputs)
    inner = re.compile(r'[\[;](0|39|49|[0-9]|2[1-9]|(?:3|4|9|10)[0-7]|[34]8;(?:5;[0-9]+|2;(?:[0-9]+;){3}))[;m]')
    def repl(match):
        if match.group(0)[-1] != 'm':
            return ''
        params = match.group(1)
        kept = inner.findall(params)
        if not kept:
            return ''
        return '\033[' + ';'.join(kept) + 'm'
    safe = re.sub(r'\033(\[[0-9;]*.)', repl, safe).replace('\033', '�')

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

def fixTitle(tit, wid, right=False):
    if tit == "":
        return "─"*wid
    if len(tit) > wid-5:
        if right:
            ntit = "..."+tit[-wid+5:]
        else:
            ntit = tit[:wid-5]+"..."
    else:
        ntit = tit
    if right:
        return "─"*(wid-strlen(ntit)-2)+" "+toPrintable(ntit)+"\033[0m "
    return " "+toPrintable(ntit)+"\033[0m "+"─"*(wid-strlen(ntit)-2)

def printScreen(app):
    wind = app.wind
    size = shutil.get_terminal_size()
    buf = wind.mainBuffer
    mxidx = 0
    print("\033[0;0H", end="")
    if not wind.sidebuf:
        wid = size.columns-2
        buf.initialFix(wid)
        print("╭"+fixTitle(wind.titles[1], wid)+"╮")
        for i in range(size.lines-2):
            prt = buf.popBuf(wid)
            if buf:
                mxidx = i
            print("│"+prt+"\033[0m│")
        wid1 = wid//2
        wid2 = wid-wid1
        if wind.titles[1] != "":
            curspos = 3
        else:
            curspos = 2
        print("╰"+fixTitle(app.endPref(), wid1)+fixTitle(app.endSuff(), wid2, True)+"╯", end=f"\033[0;{curspos}H", flush=True)
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
            if wind.titles[0] != "":
                curspos = 3
            else:
                curspos = 2
        else:
            if wind.titles[1] != "":
                curspos = wid1+4
            else:
                curspos = wid1+3
        print("╰"+fixTitle(app.endPref(), wid1)+"┴"+fixTitle(app.endSuff(), wid2, True)+"╯", end=f"\033[0;{curspos}H", flush=True)
    return mxidx

