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

def strlen(txt):
    ln = 0
    itr = iter(txt)
    c = None
    for c in itr:
        if c == '\033':
            while c in '\033[0123456789;':
                c = next(itr, 'Z') # So it breaks
        elif c == '\020':
            c = next(itr, 'Z')
            if c in '+-*~':
                ln += 4 # `[c] `
            if c in '!c':
                next(itr)
            elif c == '.':
                if next(itr) == '.' and next(itr) == '.':
                    while c != '\n' and c != '': # Until newline, it has no length (variable as needed)
                        c = next(itr, '')
                    if c != '':
                        ln += 1 # For the newline
            elif c == '%':
                while c != '%':
                    c = next(itr, '%')
        else:
            ln += 1
    return ln

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

_inner = re.compile(r'[\[;](0|39|49|[0-9]|2[1-9]|(?:3|4|9|10)[0-7]|[34]8;(?:5;[0-9]+|2;(?:[0-9]+;){3}))(?=[;m])')
ANSI = re.compile("\033\\[[0-9;]*.")
END = re.compile('\020(?:.|c.)$')
def toPrintable(txt):
    # Get rid of regular \033s but keep ones relating to colour or bold/stuff (for terminal outputs)
    def repl(match):
        txt = match.group(0)
        if txt[-1] != 'm':
            return ''
        params = txt[1:]
        kept = _inner.findall(params)
        if not kept:
            return ''
        return '\033[' + ';'.join(kept) + 'm'
    txt = re.sub(ANSI, repl, txt)

    txt = txt\
        .replace('\020+', '[\033[32;1m+\033[0m] \033[1m')\
        .replace('\020-', '[\033[31;1m-\033[0m] \033[1m')\
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
        .replace('\020cB', '\033[30m')

    # Remove extra sequences at the end of the string
    return re.sub(END, '', txt)\
        .replace('\020', '')

def fixVariable(txt, sect=None):
    w, _, w1, w2 = getSizings()
    if sect is not None:
        w = [w1, w2][sect]

    outs = []
    for ln in txt.split('\n'):
        idx = ln.find("\020=")
        if idx != -1:
            first = ln[:idx]
            ln = first+'═'*(w-strlen(first))

        idx = ln.find("\020...")
        if idx != -1:
            bef, aft = ln[:idx], ln[idx+4:]
        else:
            bef, aft = ln, None
        idx = bef.find("\020%")
        if idx != -1:
            idx2 = bef.find('%', idx+2)
            if idx2 != -1:
                bef1, txt, bef2 = bef[:idx], bef[idx+2:idx2-1], bef[idx2+1:]
                fail = None
                spl = txt.split('/')
                if len(spl) != 2:
                    fail = "No separator found in progress!"
                else:
                    try:
                        progress = int(spl[0])
                        mx = int(spl[1])
                    except ValueError:
                        fail = "Progress values are not numbers!"
                if fail is not None:
                    bef = bef1+fail+bef2
                else:
                    value = min(max(progress / mx, 0), 1)

                    perc = round(value * 100, 3)
                    t1, t2 = "Progress: ", f" {perc}%"
                    lns = len(t1)+len(t2)
                    t1 = f"\020b{t1}\020r"

                    wid = w - (strlen(bef1)+strlen(bef2)+lns)
                    filled = round(value * wid)
                    line = "█"*filled + "░"*(wid-filled)
                    bef = bef1+t1+line+t2+bef2
                    aft = None # No space left, this fills up the whole width
        whole = bef
        if aft is not None:
            left = w - strlen(bef)
            if left > 0:
                aftln = strlen(aft)
                if aftln <= left:
                    whole += aft
                elif left < 3:
                    whole += '.'*left
                else:
                    whole += aft[:-3-(aftln-left)]+'...'
        outs.append(whole)
    return '\n'.join(outs)


def fixTitle(tit, wid, hl, right=False):
    if tit == "":
        return "─"*wid
    if len(tit) > wid-5:
        if right:
            ntit = "..."+tit[-wid+5:]
        else:
            ntit = tit[:wid-5]+"..."
    else:
        ntit = tit
    ntit = " "+ntit+" \020R"
    if hl:
        ntit = "\020i\020b"+ntit
    if right:
        return "─"*(wid-strlen(ntit))+toPrintable(ntit)
    return toPrintable(ntit)+"─"*(wid-strlen(ntit))

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
    out = "\033[0;0H\033[?25l"
    if w <= 15 or h <= 3:
        out += "╭"+"─"*w+"╮\n"
        out += ("│"+" "*w+"│\n")*h
        out += "╰"+"─"*w+"╯"
        print(out, end="", flush=True)
        return 0
    wind = app.wind
    buf = wind.mainBuffer
    mxidx = 0
    if not wind.sidebuf:
        buf.initialFix(w, h)
        out += "╭"+fixTitle(wind.titles[1], w, True)+"╮\n"
        for i in range(h):
            prt = buf.popBuf(w)
            if buf:
                mxidx = i
            out += "│"+prt+"\033[0m│\n"
        c = "─"
        wind.sel = 1
    else:
        sidebuf = wind.sideBuffer
        sidebuf.initialFix(wid1, h)
        buf.initialFix(wid2, h)
        out += "╭"+fixTitle(wind.titles[0], wid1, wind.sel == 0)+"┬"+fixTitle(wind.titles[1], wid2, wind.sel == 1)+"╮\n"
        for i in range(h):
            prt1 = sidebuf.popBuf(wid1)
            prt2 = buf.popBuf(wid2)
            if buf or sidebuf:
                mxidx = i
            out += "│"+prt1+"\033[0m│"+prt2+"\033[0m│\n"
        c = "┴"
    out += "╰"+fixTitle(app.endPref(), wid1, False)+c+fixTitle(app.endSuff(), wid2, False, True)+"╯"
    print(out, end="\033[0;0H", flush=True)
    global lastPrtTime
    lastPrtTime = time.time()
    return mxidx

