import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('038-same-moment',palette('edece6','292d2e','ce4938','737d79'))
p.txt(35,68,'THE SAME MOMENT',29,36)
p.txt(36,113,'13 NOV / STANDARD TIME',20,25,3)
for x,city,hm,utc in [(86,'LONDON',(6,0),'UTC+0'),(242,'DELHI',(11,30),'UTC+5:30'),(398,'TOKYO',(15,0),'UTC+9'),(554,'PERTH',(14,0),'UTC+8')]:
    cy=242;r=65
    p.circle(x,cy,r,1,False)
    for k in range(12):
        a=math.radians(k*30-90)
        p.line([(x+(r-5)*math.cos(a),cy+(r-5)*math.sin(a)),(x+(r-12)*math.cos(a),cy+(r-12)*math.sin(a))],1,2)
    h,m=hm
    for val,length,c,w in [(h%12+m/60,36,1,4),(m/5,52,2,2)]:
        a=math.radians(val*30-90);p.line([(x,cy),(x+length*math.cos(a),cy+length*math.sin(a))],c,w)
    p.circle(x,cy,4,1)
    p.center(x,159,city,20,26)
    p.center(x,359,f'{h:02}:{m:02}',23,31)
    p.center(x,407,utc,18 if len(utc)>5 else 20,24,3)
p.rect(36,452,568,3,2)
p.save()
