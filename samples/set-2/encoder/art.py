"""Small-screen design helpers. All artwork remains native NAPLPS primitives."""
import math
from . import Page, xy, Y_SCALE


def palette(*colours):
    assert len(colours) <= 16
    return list(colours) + ['000000'] * (16-len(colours))


class Art(Page):
    def __init__(self, name=None, colours=None, background=0):
        self._pel = None
        super().__init__(name, colours, background)
        if name:
            # Explicitly restore the character sets as well as the RESET state.
            self.data[:0] = b'\x18\x1b(B\x1b)W\x1b+}'

    def pel(self, p):
        if p != self._pel:
            super().pel(p)
            self._pel = p
        return self

    def circle(self, x, y, r, c=None, fill=True):
        if c is not None: self.color(c)
        self.pel(1)
        return self.cmd(0x2f if fill else 0x2e,
                        xy((x-r)/640,(480-y)/Y_SCALE)+xy(2*r/640,0))

    def txt(self, x, y, s, w=20, h=26, c=1, prop=False):
        return self.text(x,y,s,w,h,c,prop)

    def center(self, x, y, s, w=20, h=26, c=1):
        # Fixed-pitch letters occupy 6/8 of their field; centre the visible ink.
        return self.txt(x-(len(s)-.25)*w/2,y,s,w,h,c)

    def arrow(self, points, c=1, width=3, head=12):
        self.line(points,c,width)
        a,b=points[-2:]
        ang=math.atan2(b[1]-a[1],b[0]-a[0])
        self.poly([b,(b[0]-head*math.cos(ang-.5),b[1]-head*math.sin(ang-.5)),
                     (b[0]-head*math.cos(ang+.5),b[1]-head*math.sin(ang+.5))],c)
        return self

    def star(self,x,y,r,c=1,n=5,inner=.45,phase=-90):
        return self.poly([(x+r*(1 if i%2==0 else inner)*math.cos(math.radians(phase+i*180/n)),
                           y+r*(1 if i%2==0 else inner)*math.sin(math.radians(phase+i*180/n)))
                          for i in range(2*n)],c)

    def mode2(self, fg, bg):
        return self.cmd(0x3e,bytes([0x40|(fg<<2),0x40|(bg<<2)]))

    def texture_mask(self, fragment, size=12):
        self.cmd(0x23,b'\x40'+xy(size/640,size/Y_SCALE))
        self.data.extend(b'\x1bDA\x0e'+fragment+b'\x1bE\x0e')
        self._pel=None
        return self

    def drcs(self, code, fragment, w=32,h=32):
        self.cmd(0x22,b'\x40\x40'+xy(w/640,h/Y_SCALE))
        self.data.extend(b'\x1bC'+bytes([code])+b'\x0e'+fragment+b'\x1bE\x0e')
        self._pel=None
        return self

    def glyph(self,x,y,code,w,h,c=1):
        self.color(c).cmd(0x22,b'\x40\x40'+xy(w/640,h/Y_SCALE)).pos(x,y)
        self.data.extend(b'\x1b+{\x1d'+bytes([code])+b'\x1b+}\x0e')
        return self

    def supplementary(self,x,y,b,w=20,h=26,c=1):
        self.color(c).cmd(0x22,b'\x40\x40'+xy(w/640,h/Y_SCALE)).pos(x,y)
        self.data.extend(b'\x1b*|\x0f'+b+b'\x0e\x1b*z')
        return self
