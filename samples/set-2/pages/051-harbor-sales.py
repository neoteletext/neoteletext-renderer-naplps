import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('051-harbor-sales',palette('162d48','eceddc','3a9da6','8ad3ce','206371','e8b655','ffe1a0','9a7539','3f546c'))
p.txt(26,58,'HARBOR SALES',34,41,1)
p.txt(28,102,'1988 / QUARTERLY REPORT',23,28,1)
base=380;scale=2.8
for val in (0,20,40,60,80):
    y=base-val*scale
    p.line([(84,y),(610,y)],8)
    p.txt(26,y+8,str(val),20,24,1)
for i,value in enumerate((42,58,53,74)):
    x=121+i*120;y=base-value*scale;front,top,side=(2,3,4) if i<3 else (5,6,7)
    p.rect(x,y,62,base-y,front)
    p.poly([(x,y),(x+21,y-15),(x+83,y-15),(x+62,y)],top)
    p.poly([(x+62,y),(x+83,y-15),(x+83,base-15),(x+62,base)],side)
    p.center(x+38,y-25,str(value),25,29,1)
    p.center(x+35,419,'Q'+str(i+1),24,28,1)
p.rect(29,448,19,19,2);p.txt(61,469,'NET SALES / $000',25,29,1)
p.save()
