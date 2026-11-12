from lib import *
p=Page('102-football-tactics',['245C3D','F2EDCC','408455','D4B64A','AC433B','173C32'])
p.rect(0,0,640,72,5)
p.text(20,51,'ALDER UNITED',29,36,1)
p.text(426,52,'4-4-2',28,35,3)
# Horizontal pitch, with long strips distinct from calendar and chart grids.
for i in range(8):p.rect(28+i*73,95,73,347,2 if i%2 else 0)
p.rect(28,95,584,347,1,False)
p.line([(320,95),(320,442)],1,2)
p.circle(320,268,53,1,False)
p.circle(320,268,3,1)
p.rect(28,169,87,198,1,False);p.rect(525,169,87,198,1,False)
p.rect(28,219,36,98,1,False);p.rect(576,219,36,98,1,False)
# Passing lanes go behind the numbered discs.
for a,b in [((340,145),(475,191)),((340,392),(475,344)),((340,227),(485,250)),((170,221),(318,218)),((170,323),(318,322))]:arrow(p,a,b,3,4,14)
positions=[(64,268),(170,143),(170,221),(170,323),(170,398),(340,145),(340,227),(340,319),(340,392),(489,213),(489,337)]
for i,(x,y) in enumerate(positions):
    p.circle(x,y,20,1)
    p.center(y+11,str(i+1),22,26,5,x=x)
p.text(29,475,'PRESS HIGH / ATTACK TO THE RIGHT',20,24,1)
p.save()
