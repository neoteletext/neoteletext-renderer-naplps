import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('045-paddock-prices',palette('e2c28a','3f3827','854b2d','998048','f5e3b8'))
p.rect(0,0,189,480,1)
# Woodcut landscape and a sheaf of wheat in the dark vertical panel.
p.circle(93,99,45,3)
p.poly([(0,238),(51,202),(112,225),(189,196),(189,480),(0,480)],2)
p.texture(2);p.rect(0,285,188,194,3);p.texture()
for x,h in [(52,76),(81,111),(111,93),(141,69)]:
    p.line([(95,331),(x,331-h)],4,3)
    for k in range(4):
        y=331-h+12+k*13
        p.poly([(x,y),(x-13,y-12),(x-12,y+2)],4)
        p.poly([(x,y+7),(x+12,y-6),(x+12,y+7)],4)
p.txt(24,390,'FIELD',25,32,4);p.txt(24,429,'NOTES',25,32,4)
p.txt(215,57,'PADDOCK',35,42,1)
p.txt(215,101,'PRICES',35,42,1)
p.txt(216,145,'12 NOV 1988',22,27,2)
for y,name,price,unit in [(206,'WHEAT','$186','/ TONNE'),(301,'WOOL','640c','/ KG'),(396,'CATTLE','128c','/ KG LIVE')]:
    p.line([(216,y-31),(608,y-31)],2,2)
    p.txt(215,y,name,25,30,1)
    p.txt(216,y+41,price,30,37,2)
    p.txt(380,y+39,unit,22,26,1)
p.txt(213,472,'RIVER SALEYARDS',23,26,1)
p.save()
