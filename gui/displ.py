"""
\\020

< Clear last line
!! Clear screen

+ good
- bad
* warn
~ info

= separator
%<perc>/<max>% Display a percent with a progress bar
...<txt> Display as much of the text as fits on that line

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
from builtins import print # So later stuffing around won't mess up the core printing
import shutil
import time
import re

def fix(txt):
    idx = txt.rfind("\020!!")
    if idx != -1:
        txt = txt[idx+3:]
    txt = re.sub('^.*\n?.*\020<', '', txt, flags=re.MULTILINE).lstrip("\n")
    if txt == '':
        return ''
    txt = txt.replace('\t', '    ')
    if txt[-1] == '\n':
        return txt.rstrip("\n")+"\n"
    return txt

FANCY = re.compile(r'\020[+\-*~]')
REG = re.compile(r'\020(?:[birR]|c[rgbcmyWGB])|\033\[[0-9;]*.')
END = re.compile('\020(?:.|c.)$|\033[0-9;].$')
def strlen(txt):
    return len(
        re.sub(REG, '',
            re.sub(FANCY, '    ', 
                re.sub(END, '', txt)
        )).replace('\020', ' ').replace('\033', ' '))

def strcut(txt, wid):
    if txt == '':
        return '', ''
    out = ''
    i = 0
    while i < len(txt):
        out += txt[i]
        if strlen(out) > wid:
            out = out[:-1]
            break
        i += 1
    return out, txt[len(out):]

_inner = re.compile(r'[\[;](0|39|49|[0-9]|2[1-9]|(?:3|4|9|10)[0-7]|[34]8;(?:5;[0-9]+|2;(?:[0-9]+;){3}))[;m]')
_ansi = re.compile(r'\033(\[[0-9;]*.)')
def toPrintable(txt):
    # Remove extra sequences at the end of the string
    safe = re.sub(END, '', txt)

    # Get rid of regular \033s but keep ones relating to colour or bold/stuff (for terminal outputs)
    def repl(match):
        if match.group(0)[-1] != 'm':
            return ''
        params = match.group(1)
        kept = _inner.findall(params)
        if not kept:
            return ''
        return '\033[' + ';'.join(kept) + 'm'
    safe = re.sub(_ansi, repl, safe).replace('\033', '�')

    return safe\
        .replace('\020+', '[\033[32;1m+\033[0m] \033[1m')\
        .replace('\020-', '[\033[34;1m-\033[0m] \033[1m')\
        .replace('\020*', '[\033[33;1m*\033[0m] \033[1m')\
        .replace('\020~', '[\033[35;1m~\033[0m] \033[1m')\
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

_perc = re.compile(r'\020%(\d+)/(\d+)%')
_dots = re.compile(r'(.*)\020\.\.\.(.*)')
def fixVariable(txt, sect=None):
    w, _, w1, w2 = getSizings()
    if sect is not None:
        w = [w1, w2][sect]

    def handlePerc(match):
        try:
            progress = int(match.group(1))
            max = int(match.group(2))
        except ValueError:
            return 'Unknown percent: '+match.group(0)[1:]
        perc = round(progress / max * 100, 3)
        t1, t2 = "Progress:", f" {perc}%"
        o = f"\020b{t1}\020r{t2}"
        if max > 0 and 0 <= progress < max:
            wid = w -len(t1)-len(t2) - 5
            filled = round(progress / max * wid)
            line = "█"*filled + "░"*(wid-filled)
            o += "  "+line
        return o
    txt = re.sub(_perc, handlePerc, txt)

    def handleDots(match):
        txt1, txt2 = match.group(1), match.group(2)
        tlen = strlen(txt1)
        mxwid = max(w-tlen, 0)
        if mxwid <= 3:
            return txt1+"."*mxwid
        if strlen(txt2) > mxwid:
            return txt1+strcut(txt2, mxwid-3)[0]+"..."
        return txt1+txt2
    txt = re.sub(_dots, handleDots, txt)

    return txt\
        .replace('\020=', '═'*w)


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

def getSizings():
    size = shutil.get_terminal_size()
    wid1 = (size.columns-3)//3
    return size.columns-2, size.lines-2, wid1, (size.columns-3)-wid1
def getSze():
    size = shutil.get_terminal_size()
    return size.columns-2, size.lines-2

lastPrtTime = 0
def printScreen(app):
    w, h, wid1, wid2, = getSizings()
    out = "\033[0;0H"
    if w <= 15 or h <= 3:
        out += "╭"+"─"*w+"╮\n"
        out += ("│"+" "*w+"│\n")*h
        out += "╰"+"─"*w+"╯"
        print(out, end="\033[0;2H", flush=True)
        return 0
    wind = app.wind
    buf = wind.mainBuffer
    mxidx = 0
    if not wind.sidebuf:
        buf.initialFix(w, h)
        out += "╭"+fixTitle(wind.titles[1], w)+"╮\n"
        for i in range(h):
            prt = buf.popBuf(w)
            if buf:
                mxidx = i
            out += "│"+prt+"\033[0m│\n"
        c = "─"
        wind.sel = 1
        if wind.titles[1] != "":
            curspos = 3
        else:
            curspos = 2
    else:
        sidebuf = wind.sideBuffer
        sidebuf.initialFix(wid1, h)
        buf.initialFix(wid2, h)
        out += "╭"+fixTitle(wind.titles[0], wid1)+"┬"+fixTitle(wind.titles[1], wid2)+"╮\n"
        for i in range(h):
            prt1 = sidebuf.popBuf(wid1)
            prt2 = buf.popBuf(wid2)
            if buf or sidebuf:
                mxidx = i
            out += "│"+prt1+"\033[0m│"+prt2+"\033[0m│\n"
        c = "┴"
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
    out += "╰"+fixTitle(app.endPref(), wid1)+c+fixTitle(app.endSuff(), wid2, True)+"╯"
    print(out, end=f"\033[0;{curspos}H", flush=True)
    global lastPrtTime
    lastPrtTime = time.time()
    return mxidx

