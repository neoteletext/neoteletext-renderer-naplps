import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('060-hearth-quilt',palette('f0dfb8','2a4653','d3bd91','ad5544','6f8d7c','c49245','efe7d1'))
p.rect(0,0,640,480,1);p.rect(27,8,586,464,5);p.rect(37,16,566,448,0)
# Two relative macros: a pieced star and a four-stitch cross.
f=Art()
f.relpoly([(56,0),(70,28),(84,28),(84,42),(112,56),(84,70),(84,84),(70,84),(56,112),(42,84),(28,84),(28,70),(0,56),(28,42),(28,28),(42,28)])
f.move(-56,0)
p.macro(0x21,f)
g=Art();g.relpoly([(-2,-8),(2,-8),(2,-2),(8,-2),(8,2),(2,2),(2,8),(-2,8),(-2,2),(-8,2),(-8,-2),(-2,-2)]);g.move(2,8)
p.macro(0x22,g)
for row in range(4):
    for col in range(5):
        x=40+col*112;y=16+row*112
        p.rect(x,y,112,112,0 if (row+col)%2 else 2)
        p.call(0x21,x,y,(1,3,4,3,1)[(col+row)%5])
        p.poly([(x+56,y+34),(x+78,y+56),(x+56,y+78),(x+34,y+56)],0)
        p.call(0x22,x+56,y+56,5)
# Fine seam lines and border stitches make the piece read as textile.
for x in range(40,602,112):p.line([(x,16),(x,464)],6)
for y in range(16,466,112):p.line([(40,y),(600,y)],6)
for y in range(33,465,46):
    p.call(0x22,12,y,0);p.call(0x22,628,y,0)
p.save()
