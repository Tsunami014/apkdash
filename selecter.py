from gui.displ import fix, getSze, getSizings
from gui.wind import ScrlWind, Buffer

class SelectWind(ScrlWind):
    @property
    def mainBuffer(self):
        if self.mainScrl is None:
            return super().mainBuffer
        self.buf = fix(self.buf)
        out = self.addSel(self.buf, self.mainScrl)
        sect = 1 if self.sidebuf else None
        return Buffer(out, sect, self.findScrl(out, 1, self.mainScrl))
    @property
    def sideBuffer(self):
        if self.sideScrl is None:
            return super().sideBuffer
        self.sidebuf = fix(self.sidebuf)
        out = self.addSel(self.sidebuf, self.sideScrl)
        return Buffer(out, 0, self.findScrl(out, 0, self.sideScrl))

    def addSel(self, txt, scrl):
        if txt == '':
            return ''
        if scrl == 0:
            nxt = txt.find('\n')
            if nxt == -1:
                return "\020i"+txt
            return "\020i"+txt[:nxt]+txt[nxt:]
        idx = 0
        for _ in range(scrl):
            idx = txt.find('\n', idx+1)
            if idx == -1:
                return txt
        nxt = txt.find('\n', idx+1)
        if nxt == -1:
            nxt = len(txt)
        return txt[:idx+1]+"\020i"+txt[idx+1:nxt]+txt[nxt:]

    def getCurLine(self, side):
        buf = (self.sidebuf, self.buf)[side]
        scrl = (self.sideScrl, self.mainScrl)[side]
        return buf.split('\n')[scrl]

    def getMaxScrl(self):
        _, h, = getSze()
        mx = super().getMaxScrl()
        if mx <= h:
            return mx
        return mx+h-1

    def findScrl(self, txt, sect, scrl):
        _, h, = getSze()
        w, h, wid1, wid2, = getSizings()
        if sect == 0:
            w = wid1
        elif self.sidebuf:
            w = wid2
        hh = h//2
        mx = Buffer(txt).howManyRows(w)
        if mx <= h:
            return 0
        if scrl <= hh:
            return 0
        if scrl >= mx-hh:
            return mx-h
        return scrl-hh

