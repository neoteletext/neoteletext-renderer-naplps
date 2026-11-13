"""Small-screen design helpers. All artwork is encoded as native NAPLPS."""
from . import Page as OriginalPage, xy, rgb, ROOT, Y_SCALE
import math
import json
import unicodedata

FONT = '/Users/andrewstuart/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes'
METRICS = {}
section = ''
for ln in open(FONT):
    if ln.startswith('['): section = ln.strip()
    elif section == '[primary]' and ln.strip() and not ln.startswith('#'):
        a = ln.split()
        xs = [int(v) for s in a[3:] for v in s.split(',')[::2]]
        if xs: METRICS[chr(int(a[0],16))] = (max(xs)-min(xs)+2)/8

def ascii_accents(s):
    out = bytearray()
    accents = {'\u0300':0x41, '\u0301':0x42, '\u0302':0x43,
               '\u0308':0x48, '\u0327':0x4b, '\u0303':0x44}
    symbols = {'ß':0x7b, '£':0x23, '¥':0x25, '¢':0x22,
               '¼':0x3c, '½':0x3d, '¾':0x3e, '°':0x30,
               '←':0x2c, '↑':0x2d, '→':0x2e, '↓':0x2f}
    for c in s:
        if c in symbols:
            out.extend([0x19,symbols[c]])
            continue
        d = unicodedata.normalize('NFD',c)
        if len(d)>1 and d[1] in accents:
            out.extend([0x19, accents[d[1]], ord(d[0])])
        else: out.extend(c.encode('ascii'))
    return bytes(out)

class Page(OriginalPage):
    def __init__(self, name=None, colours=None):
        super().__init__()
        self.name = name
        self.text_boxes = []
        self.palette = list(colours or [])
        if not name: return
        # RESET first; explicitly restore the sets too, since RESET does not.
        self.data.extend(b'\x0e\x20\x7f\x7f\x1b"F\x1b(B\x1b)W\x1b*|\x1b+}\x0e')
        self.pel(1)
        while len(self.palette)<16: self.palette.append(self.palette[0])
        assert len(self.palette)==16
        for i,c in enumerate(self.palette): self.set_palette(i,c)
        self.rect(0,0,639.7,479.7,0)

    def t(self,x,y,s,w=20,h=28,c=1,prop=True,align='left',bg=None):
        """Text with a top-left design origin; y is the field's top."""
        n = unicodedata.normalize('NFD',s)
        base = ''.join(ch for ch in n if not unicodedata.combining(ch))
        width = sum((METRICS.get(ch,1) if prop else 1)*w for ch in base)
        if align=='center': x -= width/2
        elif align=='right': x -= width
        assert x>=-0.5 and x+width<=641, (self.name,s,x,width)
        assert y>=-1 and y+h<=482, (self.name,s,y,h)
        self.text_boxes.append(dict(text=s,x=round(x,2),y=y,width=round(width,2),field_width=w,field_height=h))
        if bg is None: self.color(c)
        else: self.cmd(0x3e,bytes([0x40|(c<<2),0x40|(bg<<2)]))
        self.cmd(0x22,bytes([0x70 if prop else 0x40,0x40])+xy(w/640,h/Y_SCALE))
        self.pos(x,y+h)
        self.data.extend(b'\x0f'+ascii_accents(s)+b'\x0e')
        return self

    def circle(self,x,y,r,c=1,fill=True,width=1):
        self.color(c).pel(width)
        return self.cmd(0x2f if fill else 0x2e,xy((x-r)/640,(480-y)/Y_SCALE)+xy(2*r/640,0))

    def arrow(self,pts,c=1,width=4,head=12):
        self.line(pts,c,width)
        a,b=pts[-2:]
        angle=math.atan2(b[1]-a[1],b[0]-a[0])
        return self.poly([b,(b[0]-head*math.cos(angle-.55),b[1]-head*math.sin(angle-.55)),
                             (b[0]-head*math.cos(angle+.55),b[1]-head*math.sin(angle+.55))],c)

    def macro(self,num,fragment):
        self.data.extend(b'\x1b+z\x1b@'+bytes([num])+b'\x0e'+fragment.data+b'\x1bE\x0e')
        return self

    def call(self,num,x=None,y=None,c=None):
        if c is not None:self.color(c)
        if x is not None:self.pos(x,y)
        self.data.extend(bytes([0x1d,num]))
        return self

    def star(self,x,y,r,c=1,n=4,inner=.30):
        return self.poly([(x+(r if i%2==0 else r*inner)*math.cos(-math.pi/2+i*math.pi/n),
                           y+(r if i%2==0 else r*inner)*math.sin(-math.pi/2+i*math.pi/n)) for i in range(n*2)],c)

    def save(self):
        self.data.extend(b'\x0f')
        assert len(self.data)<6144,(self.name,len(self.data))
        assert all(b<128 for b in self.data)
        path=ROOT/'out'/f'{self.name}.nap'
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(self.data)
        path.with_suffix('.layout.json').write_text(json.dumps(self.text_boxes,indent=2)+'\n')
        print(f'{self.name}: {len(self.data)} bytes')
        return path

def run(build):
    build().save()

def sun(p,x,y,r=22,c=2,rays=True):
    p.circle(x,y,r,c)
    if rays:
        for a in range(0,360,45):
            t=math.radians(a)
            p.line([(x+(r+8)*math.cos(t),y+(r+8)*math.sin(t)),
                    (x+(r+16)*math.cos(t),y+(r+16)*math.sin(t))],c,3)

def cloud(p,x,y,c=1,s=1):
    for dx,dy,r in [(-23,0,20),(0,-12,27),(26,0,21)]:p.circle(x+dx*s,y+dy*s,r*s,c)
    p.rect(x-24*s,y,51*s,18*s,c)

def burst(p,x,y,rx,ry,c,n=12):
    p.poly([(x+rx*(1 if i%2==0 else .83)*math.cos(i*math.pi/n),
             y+ry*(1 if i%2==0 else .83)*math.sin(i*math.pi/n)) for i in range(n*2)],c)
