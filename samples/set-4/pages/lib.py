"""Shared encoding tools; layouts and visual language belong to individual pages."""
import sys, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from encoder import Page as BasePage, xy, Y_SCALE

FONT=Path('/Users/andrewstuart/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes')
METRICS={}
section=''
for line in FONT.read_text().splitlines():
    if line.startswith('['): section=line
    if section=='[primary]' and line and not line.startswith(('#','[')):
        a=line.split()
        try:
            xs=[int(v) for seg in a[3:] for v in seg.split(',')[::2]]
            METRICS[chr(int(a[0],16))]=(max(xs)-min(xs)+2)/8 if xs else 1
        except ValueError: pass

def measure(s,w,prop=True): return sum(METRICS.get(c,1)*w if prop else w for c in s)

class Page(BasePage):
    def __init__(self,name,palette):
        self._color=None;self._pel=None;self._text=None
        pal=palette+[palette[-1]]*(16-len(palette))
        # Begin with SO RESET, independently of all preceding drawing state.
        super().__init__(None)
        self.name=name;self.palette=pal
        self.data.extend(b'\x1b)W\x0e\x20\x7f\x7f\x1b(B\x1b*z\x1b+}')
        self.pel(1)
        for i,c in enumerate(pal):self.set_palette(i,c)
        self.rect(0,0,639.6,479.6,0)
    def color(self,i):
        if i!=self._color:
            self._color=i;super().color(i)
        return self
    def pel(self,p):
        if p!=self._pel:
            self._pel=p;super().pel(p)
        return self
    def text(self,x,y,s,w=20,h=24,c=1,prop=True,rotation=0):
        self.color(c)
        spec=(w,h,prop,rotation)
        if spec!=self._text:
            self.cmd(0x22,bytes([(0x70 if prop else 0x40)|rotation,0x40])+xy(w/640,h/Y_SCALE));self._text=spec
        self.pos(x,y)
        self.data.extend(b'\x0f'+s.encode('ascii')+b'\x0e')
        return self
    def center(self,y,s,w=20,h=24,c=1,x=320,prop=True):
        return self.text(x-measure(s,w,prop)/2,y,s,w,h,c,prop)
    def circle(self,x,y,r,c,fill=True):
        self.color(c).pel(1)
        return self.cmd(0x2f if fill else 0x2e,xy((x-r)/640,(480-y)/Y_SCALE)+xy(2*r/640,0))
    def ellipse(self,x,y,rx,ry,c=None,fill=True,n=24):return super().ellipse(x,y,rx,ry,c,fill,n)
    def call(self,*a,**kw):
        super().call(*a,**kw);self._color=None;self._pel=None;self._text=None
        return self
    def rawtext(self,x,y,b,w=20,h=24,c=1):
        self.text(x,y,'',w,h,c)
        self.data.extend(b'\x0f'+b+b'\x0e');return self
    def drcs(self,code,body):
        self.cmd(0x22,b'\x40\x40'+xy(.09,.09))
        self.data.extend(b'\x1b/\x7b\x1bC'+bytes([code])+b'\x0e'+body+b'\x1bE\x0e')
        self._text=None;self._color=None;self._pel=None
        return self
    def glyph(self,x,y,code,w,h,c):
        self.text(x,y,'',w,h,c)
        self.data.extend(bytes([0x1d,code]));return self
    def mode2(self,fg,bg):
        self.cmd(0x3e,bytes([0x40|fg<<2,0x40|bg<<2]));self._color=None;return self
    def pattern(self,body,size=12):
        self.cmd(0x23,b'\x40'+xy(size/640,size/Y_SCALE))
        self.data.extend(b'\x1bDA\x0e'+body+b'\x1bE\x0e')
        self._pel=None;self._color=None;return self
    def save(self):
        self.data.extend(b'\x0f')
        if len(self.data)>=6144:raise ValueError(f'{self.name}: {len(self.data)} bytes exceeds 6 KB')
        if max(self.data)>127:raise ValueError('8-bit data')
        (ROOT/'out'/f'{self.name}.nap').write_bytes(self.data)
        print(f'{self.name}: {len(self.data)} bytes')

def heart(p,x,y,s,c=2,flip=False):
    pts=[(-.5,-.12),(-.46,-.4),(-.25,-.5),(0,-.28),(.25,-.5),(.46,-.4),(.5,-.12),(0,.55)]
    sign=-1 if flip else 1
    p.poly([(x+a*s,y+b*s*sign) for a,b in pts],c)

def arrow(p,a,b,c=1,width=3,head=12):
    p.line([a,b],c,width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    p.poly([b,(b[0]-head*math.cos(ang-.45),b[1]-head*math.sin(ang-.45)),(b[0]-head*math.cos(ang+.45),b[1]-head*math.sin(ang+.45))],c)

def human(p,x,y,s,c):
    p.circle(x,y-7*s,s,c)
    p.poly([(x-.65*s,y-5.5*s),(x+.65*s,y-5.5*s),(x+s,y-3*s),(x+.5*s,y-3*s),(x+.65*s,y),(x-.05*s,y),(x-.2*s,y-2.5*s),(x-.5*s,y),(x-1.1*s,y),(x-.8*s,y-3*s),(x-1.2*s,y-3*s)],c)
