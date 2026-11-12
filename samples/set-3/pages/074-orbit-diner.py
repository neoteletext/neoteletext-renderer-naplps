import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('074-orbit-diner','161722 ff8eac 6fe5d3 54303f 282733 ffe2a0 704753')
# Low-contrast brickwork stays behind a freestanding neon sign.
for j,y in enumerate(range(0,481,32)):
    p.line([(0,y),(640,y)],4,2)
    for x in range(-48 if j%2 else 0,641,96):p.line([(x,y),(x,y+32)],4,2)
for off,c in [(0,3),(5,6),(9,1)]:
    p.line([(69+off,121+off),(551-off,121+off),(551-off,349-off),(69+off,349-off),(69+off,121+off)],c,3)
# Three offset stroke impressions make a restrained tube halo.
for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
    type(p,320+dx,219+dy,'ORBIT',59,70,3,'center')
    type(p,320+dx,298+dy,'DINER',55,65,6,'center')
type(p,320,219,'ORBIT',59,70,1,'center')
type(p,320,298,'DINER',55,65,2,'center')
p.line([(144,371),(496,371)],2,3)
type(p,320,419,'OPEN ALL NIGHT',29,36,5,'center')
p.ellipse(320,72,66,22,2,False,n=24);circle(p,320,72,24,1,False)
finish(p,74,'Orbit Diner','Late-night diner sign','Pink and mint neon on dark brick',['stroke overprinting','brick line texture','native arc'], 'A freestanding pink and mint tube sign hangs against subdued charcoal brick. Four offset dark impressions suggest a neon halo, while an orbital badge crowns the sign. The open-all-night line remains fully lit in the final still; no cycling obscures the diner name.')
