import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('057-water-molecule',palette('e9f0ed','354956','d9584e','a53e45','b8d4d8','789da8','ffffff','8caaa9'))
p.txt(30,66,'WATER',46,54,1)
p.txt(298,61,'BENT MOLECULE',23,28,1)
p.line([(29,91),(610,91)],7,2)
o=(320,205);dx=145*math.sin(math.radians(52.25));dy=145*math.cos(math.radians(52.25))
for h in [(320-dx,205+dy),(320+dx,205+dy)]:
    p.line([o,h],5,22);p.line([o,h],4,12)
    p.circle(*h,38,5);p.circle(h[0]-5,h[1]-5,32,4);p.circle(h[0]-14,h[1]-16,9,6)
    p.center(h[0]+2,h[1]+13,'H',31,35,1)
p.circle(320,205,62,3);p.circle(313,196,54,2)
p.texture(3);p.arc((271,233),(320,263),(369,233),3,True);p.texture()
p.circle(296,178,13,6);p.center(322,222,'O',39,44,6)
# Bond angle is measured at oxygen, between the two O-H bonds.
a=lambda v:(320+72*math.cos(math.radians(v)),205+72*math.sin(math.radians(v)))
p.arc(a(37.75),a(90),a(142.25),1)
p.supplementary(260,371,b'104.5\x190',23,29,1)
p.txt(30,452,'H',39,45,1);p.txt(63,461,'2',25,28,1);p.txt(90,452,'O',39,45,1)
p.txt(204,450,'TWO COVALENT BONDS',23,28,1)
p.save()
