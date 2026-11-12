import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('071-astor-bridge','146d9b e2f4e8 4697b3 1b7ba5')
# Faint construction grid, white engineering elevation.
for x in range(20,640,40):p.line([(x,0),(x,480)],3)
for y in range(0,481,40):p.line([(0,y),(640,y)],3)
type(p,30,54,'ASTOR RIVER',31,37,1)
type(p,30,88,'PEDESTRIAN BRIDGE / EAST ELEVATION',20,26,1)
p.line([(34,293),(606,293)],1,3);p.line([(34,306),(606,306)],1,2)
p.line([(75,294),(75,252),(565,252),(565,294)],1,3)
for i in range(10):
    x=75+i*49
    p.line([(x,292),(x+24.5,252),(x+49,292)],1,2)
for x in [75,565]:
    p.rect(x-15,307,30,48,1,False);p.line([(x-25,357),(x+25,357)],1,2)
p.line([(75,239),(75,199),(565,199),(565,239)],2)
for x in [75,565]:p.line([(x-7,192),(x+7,206)],1,2)
type(p,320,189,'42.0 m',24,30,1,'center')
p.line([(44,368),(596,368)],2)
p.rect(23,400,594,61,1,False)
p.line([(408,400),(408,461)],1)
type(p,35,429,'MERE ENGINEERING',21,26,1)
type(p,35,453,'A-17 / SCALE 1:200',20,25,1)
type(p,425,438,'REV B',29,35,1)
finish(p,71,'Astor River Bridge','Engineering elevation drawing','Cyan-blue blueprint and technical title block',['polylines','dimension lines','logical pel'], 'A white Warren-truss footbridge spans a faint cyan construction grid. Piers, deck and a single dimension are distinguished by line weight. A conventional bottom-right revision block and measured title make this a technical sheet rather than a decorative landscape.')
