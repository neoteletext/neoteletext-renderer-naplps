import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('053-river-population',palette('342735','f3e9dc','dc9995','96c5c1','69515f','b3a1a8'))
p.txt(24,52,'RIVER COUNTY',33,40,1)
p.txt(26,92,'POPULATION / 1988',23,28,5)
p.center(149,137,'MEN',24,28,2);p.center(495,137,'WOMEN',24,28,3)
left=259;right=380;scale=48
for i,(age,m,w) in enumerate([('60+',1.9,2.5),('45-59',2.8,2.9),('30-44',3.8,3.9),('15-29',4.5,4.3),('0-14',4.0,3.8)]):
    y=159+i*49
    p.rect(left-m*scale,y,m*scale,33,2);p.rect(right,y,w*scale,33,3)
    p.center(320,y+28,age,20,25,1)
    p.txt(left-m*scale+8,y+27,str(m),20,25,0)
    p.txt(right+w*scale-66,y+27,str(w),20,25,0)
for x in (left,right):p.line([(x,151),(x,402)],5)
p.line([(39,405),(259,405)],4);p.line([(380,405),(600,405)],4)
p.txt(28,464,'PEOPLE IN THOUSANDS',28,33,1)
p.save()
