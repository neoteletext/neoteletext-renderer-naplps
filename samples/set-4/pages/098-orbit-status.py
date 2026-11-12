from lib import *
p=Page('098-orbit-status',['071D21','BFE7C9','4F8C72','233F43','E6B765','67BCA4','DAE5CD','102E2B','7FE4AE'])
p.text(20,42,'KESTREL / FLIGHT 03',25,31,1)
p.line([(20,59),(620,59)],2,2)
p.circle(34,90,5,8);p.text(52,100,'LINK OK',20,24,1)
p.text(441,101,'ORBIT 128',20,24,1)
cx,cy=207,265
p.circle(cx,cy,61,5);p.circle(cx,cy,61,1,False)
p.poly([(164,247),(190,226),(208,238),(218,259),(205,269),(209,290),(188,309),(173,281)],2)
p.poly([(230,224),(245,241),(241,260),(226,259),(223,242)],2)
for r in [98,147]:p.circle(cx,cy,r,3,False)
# Inclined ellipse is a deliberate orbit track, not a native arc spline.
pts=[]
for i in range(41):
    a=2*math.pi*i/40;u=172*math.cos(a);v=85*math.sin(a)
    pts.append((cx+u*.86-v*.51,cy+u*.51+v*.86))
p.line(pts,2,2)
x,y=pts[5]
p.poly([(x-10,y-7),(x+10,y-7),(x+10,y+7),(x-10,y+7)],4)
p.rect(x-31,y-13,18,26,5);p.rect(x+13,y-13,18,26,5)
p.line([(x,y-8),(x+6,y-20)],1,2)
for yy,name,value in [(171,'ALTITUDE','408 km'),(261,'VELOCITY','7.67 km/s'),(351,'BATTERY','94 %')]:
    p.text(416,yy,name,20,24,2)
    p.text(416,yy+37,value,23,29,1)
p.line([(20,429),(620,429)],2,2)
p.text(24,466,'PERIOD 92m   /   CREW 03',23,28,1)
p.blink(8,7,on=2,off=14)
p.save()
