"""Original, standard-library-only NAPLPS writer (ANSI X3.110-1983).

7-bit PDI in G1; four-byte coordinates (11 fraction bits), one-byte
single values, explicit 16-entry colour map. Design API uses a 640x480
canvas; the PP3 viewport is 1 by 25/32 unit-screen coordinates.
"""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parent.parent
Y_SCALE = 480 / (25 / 32)


def xy(x, y, n=4):
    """Interleave signed two's-complement fractions, three bits per axis."""
    scale = 1 << (3*n-1)
    vals = [max(-scale, min(scale-1, round(v*scale))) & ((1 << (3*n))-1) for v in (x,y)]
    return bytes(0x40 | (((vals[0] >> s) & 7) << 3) | ((vals[1] >> s) & 7)
                 for s in range(3*(n-1), -1, -3))


def rgb(colour):
    r,g,b = (int(colour[i:i+2],16) for i in (0,2,4))
    return bytes(0x40 | (((g>>s)&2)<<4) | (((r>>s)&2)<<3) | (((b>>s)&2)<<2)
                 | ((g>>s)&1)<<2 | ((r>>s)&1)<<1 | ((b>>s)&1)
                 for s in (6,4,2,0))


class Page:
    def __init__(self, name=None, palette=None, background=0):
        self.name=name
        self.data=bytearray()
        self.frames=[]
        self.timeline=[]
        self.elapsed=0
        self.palette=palette
        if name:
            # Enter NAPLPS, designate C1, reset all state, define G2 as macros.
            self.data.extend(b'\x1b%A\x18\x1b"F\x1bE\x0e\x20\x7f\x7f\x1b. z')
            self.pel(1)
            for i,c in enumerate(palette): self.set_palette(i,c)
            self.rect(0,0,639.6,479.6,background)

    def cmd(self, op, operand=b''):
        self.data.extend(bytes([op])+operand)
        return self

    def pos(self,x,y): return self.cmd(0x24,xy(x/640,(480-y)/Y_SCALE))
    def move(self,x,y): return self.cmd(0x25,xy(x/640,-y/Y_SCALE))
    def color(self,i): return self.cmd(0x3e,bytes([0x40 | (i<<2)]))
    def set_palette(self,i,c): return self.color(i).cmd(0x3c,rgb(c))
    def pel(self,p): return self.cmd(0x21,b'\x4c'+xy(p/640,p/Y_SCALE))
    def texture(self,fill=0,line=0): return self.cmd(0x23,bytes([0x40 | fill<<3 | line]))
    def line(self,pts,c=None,width=1):
        if c is not None:self.color(c)
        self.pel(width)
        points=[xy(x/640,(480-y)/Y_SCALE) for x,y in pts]
        if len(points)<=2: return self.cmd(0x2a,b''.join(points))
        # SET & LINE pairs its points (T500 5.3.3.2.4); a connected line is POINT SET, then LINE.
        return self.cmd(0x24,points[0]).cmd(0x28,b''.join(points[1:]))
    def poly(self,pts,c=None,fill=True):
        if c is not None:self.color(c)
        self.pel(1)
        first=pts[0]
        data=xy(first[0]/640,(480-first[1])/Y_SCALE)
        for a,b in zip(pts,pts[1:]): data+=xy((b[0]-a[0])/640,(a[1]-b[1])/Y_SCALE)
        return self.cmd(0x37 if fill else 0x36,data)
    def relpoly(self,pts,c=None,fill=True):
        if c is not None:self.color(c)
        self.move(*pts[0])
        data=b''.join(xy((b[0]-a[0])/640,(a[1]-b[1])/Y_SCALE) for a,b in zip(pts,pts[1:]))
        return self.cmd(0x35 if fill else 0x34,data)
    def rect(self,x,y,w,h,c=None,fill=True):
        if c is not None:self.color(c)
        self.pel(1)
        return self.cmd(0x33 if fill else 0x32,xy(x/640,(480-y-h)/Y_SCALE)+xy(w/640,h/Y_SCALE))
    def ellipse(self,x,y,rx,ry,c=None,fill=True,n=48):
        return self.poly([(x+rx*math.cos(i*2*math.pi/n),y+ry*math.sin(i*2*math.pi/n)) for i in range(n)],c,fill)
    def arc(self,start,mid,end,c=None,fill=False):
        if c is not None:self.color(c)
        a,b,d=start,mid,end
        return self.cmd(0x2f if fill else 0x2e,xy(a[0]/640,(480-a[1])/Y_SCALE)+xy((b[0]-a[0])/640,(a[1]-b[1])/Y_SCALE)+xy((d[0]-b[0])/640,(b[1]-d[1])/Y_SCALE))
    def text(self,x,y,s,w=10,h=16,c=None,prop=True,rotation=0):
        if c is not None:self.color(c)
        self.cmd(0x22,bytes([0x70 if prop else 0x40,0x40])+xy(w/640,h/Y_SCALE))
        if rotation:self.cmd(0x22,bytes([(0x70 if prop else 0x40)|rotation,0x40]))
        self.pos(x,y)
        self.data.extend(b'\x0f'+s.encode('ascii')+b'\x0e')
        return self
    def macro(self,num,fragment):
        self.data.extend(b'\x1b@'+bytes([num])+b'\x0e'+fragment.data+b'\x1bE\x0e')
        return self
    def call(self,num,x=None,y=None,c=None):
        if c is not None:self.color(c)
        if x is not None:self.pos(x,y)
        self.data.extend(bytes([0x19,num]))
        return self
    def scribble(self,x,y,dx,dy,codes,c=None):
        """2-bit incremental operations; 0 prefixes sign/draw escapes."""
        if c is not None:self.color(c)
        codes=list(codes)
        # Pad with draw toggles (no movement), never with an extra line.
        while len(codes)%3:codes += [0,0]
        self.pos(x,y).cmd(0x3a,xy(dx/640,-dy/Y_SCALE)+bytes(0x40|(codes[i]<<4)|(codes[i+1]<<2)|codes[i+2] for i in range(0,len(codes),3)))
        return self
    def mosaic(self,x,y,codes,w,h,c):
        self.color(c).cmd(0x22,b'\x40\x40'+xy(w/640,h/Y_SCALE)).pos(x,y)
        for code in codes:self.data.extend(bytes([0x1d,code]))
        return self
    def blink(self,src,dest,on=5,off=10,delay=0):
        return self.color(src).cmd(0x3f,bytes([0x40|(dest<<2),0x40|on,0x40|off,0x40|delay]))
    def wait(self,tenths,label=None):
        self.timeline.append({'tenths':self.elapsed,'duration':tenths,'length':len(self.data)})
        if label:self.frames.append({'tenths':self.elapsed,'label':label,'length':len(self.data)})
        self.cmd(0x3d,bytes([0x5c])+bytes([0x40|min(63,tenths)]))
        if tenths>63:raise ValueError('split waits into <=63 tenths')
        self.elapsed+=tenths
        return self
    def save(self):
        self.data.extend(b'\x0f') # finish the last PDI operand, leave primary text active
        (ROOT/'out').mkdir(exist_ok=True)
        path=ROOT/'out'/f'{self.name}.nap'
        path.write_bytes(self.data)
        meta={'name':self.name,'bytes':len(self.data),'palette':self.palette,'frames':self.frames,'duration_tenths':self.elapsed,'timeline':self.timeline}
        path.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
        print(f'{path.relative_to(ROOT)}: {len(self.data)} bytes')


def polar(x,y,r,a):
    a=math.radians(a)
    return x+r*math.cos(a),y+r*math.sin(a)


def label(p,num,title,c=1):
    p.text(32,33,f'SIGNAL / {num:02d}',8,12,c,False)
    p.text(32,456,title,8,12,c)
    p.text(561,456,f'{num:02d}/10',8,12,c,False)
