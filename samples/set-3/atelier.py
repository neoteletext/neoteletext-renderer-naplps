"""Encoding and geometry tools; pages own their visual design."""
from encoder import Page, xy, Y_SCALE
from pathlib import Path
import math, json, random
ROOT=Path(__file__).resolve().parent
FONT=Path('/Users/andrewstuart/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes')
METRICS={}
section=''
for row in FONT.read_text().splitlines():
    if row.startswith('['): section=row
    elif row and not row.startswith('#') and section=='[primary]':
        a=row.split(); xs=[]
        for seg in a[3:]:
            v=list(map(int,seg.split(',')));xs.extend([v[0],v[2]])
        METRICS[chr(int(a[0],16))]=(max(xs)-min(xs)+2)/8 if xs else 1

def page(name,colours):
    pal=colours.split()
    pal += [pal[-1]]*(16-len(pal))
    return Page(name,pal)

def measure(s,w,prop=True):return sum(METRICS.get(a,1) for a in s)*w if prop else len(s)*w

def type(p,x,y,s,w=24,h=32,c=1,align='left',prop=True):
    if align=='center': x-=measure(s,w,prop)/2
    if align=='right': x-=measure(s,w,prop)
    p.text(x,y,s,w,h,c,prop)

def circle(p,x,y,r,c,fill=True):
    p.color(c).pel(1).cmd(0x2f if fill else 0x2e,xy((x-r)/640,(480-y)/Y_SCALE)+xy(2*r/640,0))

def curve(p,pts,c,width=2):p.line(pts,c,width)
def bez(a,b,c,d,n=22):
    return [((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*d[0],(1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*d[1]) for t in [i/n for i in range(n+1)]]
def star(x,y,r,r2,n=8,angle=-math.pi/2):
    return [(x+(r if i%2==0 else r2)*math.cos(angle+i*math.pi/n), y+(r if i%2==0 else r2)*math.sin(angle+i*math.pi/n)) for i in range(2*n)]
def points(p,pts,c,size=3):
    p.color(c).pel(size).cmd(0x26,b''.join(xy(x/640,(480-y)/Y_SCALE) for x,y in pts))
def finish(p,number,title,purpose,style,techniques,note):
    p.save()
    assert len(p.data)<6144,(p.name,len(p.data))
    info={'number':number,'file':p.name+'.nap','title':title,'purpose':purpose,'style':style,'bytes':len(p.data),'techniques':techniques,'animated':False,'design':note}
    (ROOT/'out'/f'{p.name}.meta.json').write_text(json.dumps(info,indent=2)+'\n')
