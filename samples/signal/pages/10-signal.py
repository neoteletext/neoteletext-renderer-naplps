import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page
p=Page('10-signal',['24273e','f2dfb6','de8f82','ac5d80','688e98','9ec5b3','d9bc83','414563','c8757f','335d70','b5c6b2','e8bda0','6e758c','879f9c','d7a179','eee3c7'])
p.text(32,33,'NORTH AMERICAN VIDEOTEX / COLLECTION 01',8,12,1,False)
p.text(28,140,'SIGNAL',100,114,1)
p.rect(538,61,64,68,7,False)
p.text(547,106,'10',24,34,2,False)
p.text(548,125,'PAGES',8,12,5,False)
p.text(33,171,'TEN STUDIES IN LIGHT',16,22,5,False)
p.line([(32,191),(608,191)],7)
# A rainbow portal: native arcs, straight legs, and a receding wire floor.
for i,c in enumerate([3,8,2,6,5,4]):
    inset=i*10;xl=51+inset;xr=275-inset;yy=308
    p.pel(5).arc((xl,yy),(163,196+inset),(xr,yy),c)
    p.line([(xl,yy),(xl,391)],c,5)
    p.line([(xr,yy),(xr,391)],c,5)
p.rect(112,335,102,57,0)
p.ellipse(163,311,28,28,6,n=40)
p.rect(116,312,96,25,0)
for y in[337,346,359,376,398]:p.line([(60,y),(265,y)],7)
for x in[60,95,130,163,196,231,265]:p.line([(163,326),(x,398)],7)
p.text(71,427,'1200 BITS / SECOND',8,12,5,False)
p.text(335,219,'THE PICTURE DIRECTORY',9,13,5,False)
entries=['Tide-clock harbour','Botanical plate','Constellation map','Common ground','Form follows frequency','Two languages','Southern season','Chromatic bloom','The evening room']
for i,s in enumerate(entries):
    y=245+i*21
    p.text(335,y,f'{i+1:02d}',9,13,2,False)
    p.text(371,y,s,10,14,1)
    p.line([(335,y+7),(603,y+7)],7)
p.text(32,460,'VECTOR ART / FINITE COLOURS / OPEN POSSIBILITIES',8,12,1)
p.text(561,460,'10/10',8,12,1,False)
p.save()
