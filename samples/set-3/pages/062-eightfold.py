import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('062-eightfold','073b43 d9b86e 168b91 9bd4c0 f0e3bb 12535c')
p.rect(19,16,602,448,1);p.rect(25,22,590,436,0)
f=Page()
# Relative macro: eightfold star and its inner rotated square.
f.relpoly(star(0,0,56,31,8),1,False)
f.move(0,56)
f.relpoly([(-22,0),(0,-22),(22,0),(0,22)],2,False)
p.macro(33,f)
for y in [92,196,300]:
    for x in [100,210,320,430,540]:
        p.call(33,x,y,1)
        p.poly([(x-8,y),(x,y-8),(x+8,y),(x,y+8)],3)
for y in [144,248]:
    for x in [155,265,375,485]:p.poly([(x-25,y),(x,y-22),(x+25,y),(x,y+22)],2,False)
p.rect(32,365,577,84,0)
type(p,320,406,'EIGHTFOLD',31,36,4,'center')
type(p,320,440,'NUR COURT / TILE ATELIER',20,25,1,'center')
finish(p,62,'Eightfold','Decorative tile atelier catalogue plate','Turquoise and gold girih geometry',['macro','relative polygons','eightfold symmetry'], 'A reusable eight-point girih star tessellates across deep turquoise, joined by small diamonds. The double gold frame encloses a quiet centered atelier cartouche. Geometry is deliberately large enough to survive the smallest preview.')
