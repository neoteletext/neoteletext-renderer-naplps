import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page,label,polar
p=Page('09-evening-menu',['171f22','d7bd7c','8e7a50','394346','b09b69','f0dfad','6d684e','c6aa68','213031','a48e5b','ddc894','4e5548','bea77a','e0ca94','7f775a','efddb0'])
# Measure the actual primary stroke extents for centred proportional copy.
# Read the supplied font; no font data or other encoder code is copied here.
extents={}
for row in (Path.home()/'devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes').read_text().splitlines()[2:]:
    if row.startswith('['):break
    if not row or row.startswith('#'):continue
    fields=row.split();columns=[]
    for segment in fields[3:]:
        coords=list(map(int,segment.split(',')));columns.extend([coords[0],coords[2]])
    if columns:extents[chr(int(fields[0],16))]=max(columns)-min(columns)
def centre(y,s,w,h,c=1,prop=False):
    if prop:
        width=sum((extents[ch]+2)*w/8 if ch in extents else w for ch in s)-w/4+max(1,round(h/12))
    else:width=len(s)*w
    p.text(320-width/2,y,s,w,h,c,prop)
# Stepped architecture, double rules and a crown of thin filled wedges.
outline=[(28,429),(28,92),(43,92),(43,55),(597,55),(597,92),(612,92),(612,429),(597,429),(597,442),(43,442),(43,429)]
p.poly(outline,2,False)
p.poly([(38,421),(38,101),(53,101),(53,66),(587,66),(587,101),(602,101),(602,421)],1,False)
for k in range(23):
    a=195+k*6.8
    p.poly([polar(320,182,28,a),polar(320,182,113,a-1),polar(320,182,113,a+1)],2 if k%2 else 1)
p.arc((195,204),(320,81),(445,204),1)
p.arc((206,204),(320,93),(434,204),2)
p.rect(191,182,258,49,0)
centre(214,'LUMIERE',30,40,1)
centre(243,'THE EVENING ROOM',10,15,5)
p.line([(111,260),(262,260)],2);p.line([(378,260),(529,260)],2)
p.poly([(314,260),(320,254),(326,260),(320,266)],1)
for y,head,desc in[(290,'FIRST LIGHT','Oyster / cucumber / sea herbs'),(340,'GOLDEN HOUR','Roast pumpkin / sage / beurre noisette'),(390,'AFTERGLOW','Pear / almond / burnt honey')]:
    centre(y,head,12,18,1)
    centre(y+20,desc,10,14,5,True)
# Side ornaments emphasize the central axis without crowding the menu.
for x in (72,568):
    p.line([(x,278),(x,392)],2)
    p.poly([(x,266),(x+4,273),(x,280),(x-4,273)],1)
centre(439,'THREE COURSES / 09',8,12,2)
p.text(32,32,'SIGNAL / 09',8,12,1,False)
p.text(32,466,'AN ART DECO SUPPER',8,12,1,False)
p.text(561,466,'09/10',8,12,1,False)
p.save()
