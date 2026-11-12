import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('043-pips-market',palette('d92526','fff04b','fff8e4','242329','f59429','a1131d'))
p.rect(0,0,640,72,1)
p.poly([(480,0),(640,0),(640,72)],0)
p.txt(20,48,"PIP'S MARKET",29,36,3)
p.rect(0,72,640,91,1)
p.txt(27,143,'WEEKLY WOW!',48,59,0)
p.txt(38,200,'7 - 13 NOVEMBER',23,29,2)
for i,(name,unit,price) in enumerate([('EGGS','12 PACK','$2.40'),('APPLES','PER KG','$1.20'),('MILK','2 LITRE','$1.85')]):
    x=10+i*211
    p.rect(x+5,224,202,193,5);p.rect(x,217,202,193,2)
    p.center(x+101,251,name,26,31,3)
    p.center(x+101,285,unit,20,25,3)
    pts=[]
    for k in range(24):
        a=k*math.pi/12;r=94 if k%2==0 else 78
        pts.append((x+101+r*math.cos(a),347+48*r/94*math.sin(a)))
    p.poly(pts,1)
    p.center(x+102,364,price,35,46,0)
p.txt(20,459,'FRESH DEALS. ALL WEEK.',28,33,1,True)
p.save()
