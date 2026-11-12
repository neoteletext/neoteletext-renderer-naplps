import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('068-odd-room','eebec8 292743 b5ddd0 f2d35d 867bb7 ea7356 faf0d5')
p.rect(0,0,193,480,2);p.poly([(193,0),(640,0),(640,480),(513,480)],4)
# Actual DRCS terrazzo chip: definition uses local unit coordinates.
p.cmd(0x22,b'\x40\x40'+xy(20/640,20/Y_SCALE))
p.data.extend(b'\x1b/\x7b\x1bC!\x0e')
p.cmd(0x37,xy(.1,.1)+xy(.65,.1)+xy(-.25,.65))
p.data.extend(b'\x1bE\x0e')
for x,y in [(26,105),(158,167),(576,55),(603,288),(52,345),(565,412),(325,57),(432,429),(266,392),(555,189)]:
    p.color(5).pos(x,y).data.extend(b'\x1d!')
# A chunky showroom chair in axonometric pastel.
p.poly([(217,292),(413,255),(502,316),(308,355)],1)
p.poly([(229,290),(411,259),(482,307),(307,340)],3)
p.poly([(237,275),(224,131),(385,107),(411,259)],1)
p.poly([(249,257),(239,144),(373,122),(393,247)],6)
p.poly([(242,295),(263,302),(246,403),(228,403)],1)
p.poly([(456,325),(477,321),(504,396),(485,396)],1)
p.poly([(330,349),(348,346),(351,433),(333,433)],1)
for x,y in [(29,247),(504,113)]:
    p.line([(x+i*9,y+10*math.sin(i*1.6)) for i in range(10)],1,4)
p.ellipse(113,408,42,22,3,n=16)
type(p,20,52,'ODD',40,49,1)
type(p,20,97,'ROOM',33,41,1)
p.rect(347,361,270,70,6)
type(p,367,391,'SIT DIFFERENT.',22,27,1)
type(p,367,422,'29 QUAY / 10-6',20,26,1)
finish(p,68,'Odd Room','Furniture showroom advertisement','Memphis pastel furniture and terrazzo',['DRCS','squiggle polylines','axonometric polygons'], 'A lemon-seat chair with a mint-white back floats between pink and lilac diagonals. Native downloadable triangular chips and heavy black squiggles supply the terrazzo setting. A small cream address card balances the oversized off-axis furniture.')
