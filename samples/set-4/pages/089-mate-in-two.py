from lib import *
p=Page('089-mate-in-two',['EEE5CA','282E35','B0A78A','F8F4E4','9B493C'])
p.rect(0,0,640,68,1);p.text(24,48,"THE KING'S TURN",29,35,3)
bx,by,s=43,100,39
for r in range(8):
    for f in range(8):p.rect(bx+f*s,by+r*s,s,s,3 if (r+f)%2==0 else 2)
p.rect(bx,by,8*s,8*s,1,False)
for i in range(8):
    p.text(16,by+i*s+29,str(8-i),19,23,1)
    p.center(442,chr(97+i),19,23,1,x=bx+i*s+s/2)
def piece(f,r,kind,white):
    x=bx+f*s+s/2;y=by+(8-r)*s+s/2
    pts=[(x-14,y+13),(x+14,y+13),(x+10,y+8),(x+7,y+6),(x+5,y-7),(x-5,y-7),(x-7,y+6),(x-10,y+8)]
    p.poly(pts,1)
    if white:p.poly([(x+(a-x)*.72,y+(b-y)*.8) for a,b in pts],3)
    if kind=='K':
        p.line([(x,y-17),(x,y-6)],1,3);p.line([(x-5,y-13),(x+5,y-13)],1,3)
    else:
        p.poly([(x-9,y-13),(x-5,y-7),(x+5,y-7),(x+9,y-13),(x+2,y-10),(x,y-17),(x-2,y-10)],1)
piece(0,8,'K',False);piece(0,5,'K',True);piece(0,1,'Q',True)
p.text(386,143,'MATE',35,43,1);p.text(386,188,'IN TWO',30,37,1)
p.text(385,245,'White moves',20,24,1)
p.text(385,287,'No. 042',20,24,4)
p.text(385,347,'3 pieces.',20,24,1)
p.text(385,378,'One key.',20,24,1)
p.save()
