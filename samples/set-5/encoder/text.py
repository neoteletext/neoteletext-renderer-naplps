"""Text-oriented NAPLPS helpers. Design coordinates are 640 x 480 pixels.

Only the Python standard library is needed to encode a page. All letters are
native primary/supplementary stroke characters, except explicitly defined DRCS.
"""
from .design import Page as DesignPage, ascii_accents
from . import xy, Y_SCALE, ROOT
import json

ESC = b'\x1b'
SO, SI = b'\x0e', b'\x0f'
SMALL, MEDIUM, NORMAL, TALL, DOUBLE = (ESC + bytes([v]) for v in (0x4a, 0x4b, 0x4c, 0x4d, 0x4f))
UNDER, NOUNDER = ESC+b'Y', ESC+b'Z'
REVERSE, NOREVERSE = ESC+b'H', ESC+b'I'
SCROLL, NOSCROLL = ESC+b'W', ESC+b'X'


class Page(DesignPage):
    def __init__(self, name, palette):
        super().__init__(name, palette)
        self.evidence = []

    def raw(self, data):
        self.data.extend(data)
        return self

    def write(self, data):
        return self.raw(SI + (ascii_accents(data) if isinstance(data,str) else data) + SO)

    def style(self, w=16, h=24, spacing=0, rows=0, path=0, rotation=0, motion=0):
        return self.cmd(0x22, bytes([0x40|spacing<<4|path<<2|rotation, 0x40|motion<<2|rows])+xy(w/640,h/Y_SCALE))

    def field(self,x=None,y=None,w=None,h=None):
        return self.cmd(0x38, b'' if x is None else xy(x/640,(480-y-h)/Y_SCALE)+xy(w/640,h/Y_SCALE))

    def at(self,x,y,s,w=16,h=24,c=1,spacing=0,rows=0,path=0,rotation=0,motion=0,bg=None):
        # x,y is the cursor origin (baseline for ordinary text).
        self.style(w,h,spacing,rows,path,rotation,motion)
        self.color(c) if bg is None else self.cmd(0x3e,bytes([0x40|c<<2,0x40|bg<<2]))
        return self.pos(x,y).write(s)

    def preset(self,x,y,s,preset,c=1):
        self.style().color(c).raw(SI+preset+SO).pos(x,y).write(s)
        return self

    def repeat(self,n):
        assert 0 <= n <= 63
        return self.raw(ESC+b'F'+bytes([0x40|n]))

    def eol(self): return self.raw(ESC+b'G')

    def evidence_note(self,kind,start,**extra):
        self.evidence.append(dict(kind=kind,offset=start,length=len(self.data)-start,**extra))

    def save(self):
        self.raw(ESC+b'E'+SO) # flush pending operands, known final set
        assert self.data[:4] == b'\x0e\x20\x7f\x7f'
        assert len(self.data) < 6000, (self.name,len(self.data))
        assert max(self.data)<128
        path=ROOT/'out'/f'{self.name}.nap'
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(self.data)
        path.with_suffix('.evidence.json').write_text(json.dumps(self.evidence,indent=2)+'\n')
        return path


def footer(p,number,left,c=1):
    p.t(32,447,left,11,15,c)
    p.t(608,447,f'{number}',11,15,c,align='right')


def rule(p,y,c=1,x=32,w=576):
    p.line([(x,y),(x+w,y)],c,1)


def finish(build,meta):
    page=build()
    path=page.save()
    print(f"{meta['number']} | {meta['title']} | {path.stat().st_size} bytes | covers {meta['covers']}")
