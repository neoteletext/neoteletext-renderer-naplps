import sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('042-birthday-magic',palette('f8e2d0','8e3658','e67068','e1ad48','479b9c','f5f1d6','b85b7b'))
# Airy, offset balloon clusters with loose strings.
for x,y,r,c in [(87,153,45,4),(151,113,36,2),(544,162,43,3),(526,311,31,6)]:
    p.circle(x,y,r,c)
    p.poly([(x,y+r-2),(x-6,y+r+10),(x+6,y+r+10)],c)
    p.line([(x,y+r+9),(x-8,y+r+41),(x+6,y+r+75),(x-4,y+r+104)],1)
    p.arc((x-r*.55,y-5),(x-r*.5,y-r*.5),(x-8,y-r*.68),5)
p.center(324,104,'HAPPY',34,43,1)
for i,ch in enumerate('BIRTHDAY'):
    p.txt(176+i*35,210+(i%3-1)*5,ch,35,49,1 if i%2 else 6)
p.supplementary(238,292,b'Ren\x19Bee',34,43,1)
p.center(320,377,'MAKE A LITTLE',25,31,1)
p.center(320,418,'MAGIC TODAY!',27,34,1)
r=random.Random(42)
for x,y in [(38,47),(203,43),(438,47),(604,78),(57,350),(177,313),(450,325),(594,417),(139,442),(416,457)]:
    if r.randrange(2):p.star(x,y,8,3 if x%2 else 2,4)
    else:p.line([(x-3,y-7),(x+5,y+5)],4,3)
# The ribbon shade is deliberately redefined after the drawing, without a wait.
p.set_palette(6,'b34f79')
p.save()
