from lib import *
p=Page('090-crossword',['F1EEDF','20211F','C4BEAD','AB352D'])
p.text(20,49,'THE MORNING FOLD',29,36,1)
p.line([(20,64),(620,64)],1,3)
p.text(20,103,'MINI CROSSWORD',22,27,1)
p.text(423,102,'No. 218',20,24,1)
x,y,s=24,138,54
p.rect(x,y,s*5,s*5,1)
for r in range(5):
    for c in range(5):p.rect(x+c*s+1,y+r*s+1,s-2,s-2,0)
for k in range(6):
    p.line([(x+k*s,y),(x+k*s,y+5*s)],1,2.5)
    p.line([(x,y+k*s),(x+5*s,y+k*s)],1,2.5)
for c in range(5):p.text(x+c*s+4,y+23,str(c+1),17,20,1)
for r in range(1,5):p.text(x+4,y+r*s+23,str(5+r),17,20,1)
p.text(322,153,'ACROSS / DOWN',20,24,3)
for yy,num,desc in [(198,'1 / 1','Love, at its core'),(247,'6 / 2','A glowing coal'),(296,'7 / 3','Treat cruelly'),(345,'8 / 4','Sticky tree sap'),(394,'9 / 5','A fashion wave')]:
    p.text(322,yy,num,20,24,1)
    p.text(322,yy+26,desc,20,24,1)
p.text(24,459,'A WORD SQUARE / 5 x 5',20,24,1)
p.save()
