from lib import *
p=Page('105-election-night',['19254B','FFF2D2','D44F58','62BDC2','E5B75D','36456D','A8B7CE'])
p.rect(0,0,640,83,5)
p.text(23,58,'VALE VOTES',37,45,1)
p.text(445,55,'1986',27,33,4)
p.text(26,125,'CIVIC MAJORITY',26,32,1)
seats=[]
for r,n in [(65,9),(105,13),(145,17),(185,21)]:
    for i in range(n):
        a=math.pi-math.pi*i/(n-1);seats.append((a,218+r*math.cos(a),350-r*math.sin(a)))
for i,(a,x,y) in enumerate(sorted(seats,reverse=True)):
    p.circle(x,y,8.5,2 if i<33 else 3 if i<54 else 4)
p.center(345,'60',40,49,1,x=218)
p.center(376,'SEATS',20,24,6,x=218)
for y,name,n,c in [(190,'CIVIC','33',2),(268,'UNION','21',3),(346,'LEAGUE','06',4)]:
    p.rect(435,y-27,8,31,c)
    p.text(456,y,name,21,26,1)
    p.text(542,y+40,n,36,42,c)
p.rect(0,407,640,73,1)
p.text(22,437,'60/60 DECLARED',22,27,0)
p.text(22,470,'SWING +4.2% TO CIVIC',23,28,0)
p.save()
