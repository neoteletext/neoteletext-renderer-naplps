from lib import *
p=Page('092-tide-table',['102E40','E6E7CE','64C1BD','315568','A8B8BA','E4B66B'])
p.text(24,54,'GREYHOOK',35,43,1)
p.text(26,90,'HARBOUR / 21 MAY',20,24,2)
# Moon phases: four native circles with eclipsing discs.
for i,(x,k) in enumerate([(446,0),(493,1),(540,2),(587,3)]):
    p.circle(x,51,16,1)
    if k==0:p.circle(x+8,47,15,0)
    if k==1:p.rect(x,34,18,35,0)
    if k==3:p.circle(x,51,12,0)
p.text(13,124,'m',17,22,4)
x0,y0,w,h=45,143,550,167
for n in range(4):
    yy=y0+n*h/3;p.line([(x0,yy),(x0+w,yy)],3,1)
    p.text(13,yy+8,str(3-n),17,22,4)
for i in range(5):
    x=x0+w*i/4;p.line([(x,y0),(x,y0+h)],3,1)
    p.center(340,f'{i*6:02d}',20,24,1,x=x)
curve=[]
for i in range(65):
    t=24*i/64;v=1.75+1.25*math.cos((t-4.17)*2*math.pi/12.4)
    curve.append((x0+w*t/24,y0+h*(1-v/3)))
p.line(curve,2,4)
p.text(29,396,'HIGH',22,28,5);p.text(312,396,'LOW',22,28,2)
p.text(29,433,'04:10  3.0m',21,26,1)
p.text(312,433,'10:22  0.5m',21,26,1)
p.text(29,469,'16:34  3.0m',21,26,1)
p.text(312,469,'22:46  0.5m',21,26,1)
p.save()
