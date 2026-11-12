from lib import *
p=Page('104-lottery-results',['3C1A66','FFF4CF','E89421','BA397F','40A7AF','6C398D','F0D05A','DF8C45'])
p.center(58,'LUCKY COMET',37,46,1)
p.center(101,'DRAW 318 / SAT 12 JUN',21,26,6)
# Confetti is deliberate and sparse so the six results remain dominant.
for i in range(22):
    x=(37+i*83)%640;y=138+(i*47)%286
    if i%3==0:p.poly([(x,y),(x+8,y+4),(x+2,y+13)],3 if i%2 else 4)
    elif i%3==1:p.line([(x,y),(x+8,y+10)],7,4)
    else:p.circle(x,y,4,6)
for i,(x,y,n) in enumerate([(113,208,'07'),(320,197,'12'),(527,208,'19'),(113,357,'28'),(320,345,'34'),(527,357,'41')]):
    p.wait(3)
    p.circle(x+5,y+8,62,5)
    p.circle(x,y,62,2 if i%2==0 else 4)
    p.circle(x,y,47,1)
    p.center(y+21,n,44,49,0,x=x)
    p.arc((x-41,y-29),(x-26,y-44),(x-9,y-47),1)
p.center(464,'BONUS 03 / KEEP YOUR TICKET',21,26,1)
# Recolour already drawn confetti after a brief reveal, final settled gold.
p.wait(3);p.set_palette(7,'F0D05A')
p.save()
