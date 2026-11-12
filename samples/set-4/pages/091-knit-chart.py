from lib import *
p=Page('091-knit-chart',['F2DDCB','543E4C','9D5267','6C8574','FFF1DD','C8AB94'])
p.rect(0,0,640,77,2)
p.text(22,55,'FERN COWL',36,42,4)
p.text(433,53,'CHART 02',20,25,4)
x,y,s=42,106,28
p.rect(x,y,280,280,1)
for r in range(10):
    for c in range(10):p.rect(x+c*s+2,y+r*s+2,s-4,s-4,4)
# An actual relative stitch macro, reused at each motif location.
f=BasePage();f.relpoly([(-7,0),(0,-8),(7,0),(0,8),(-7,0)])
p.macro(0x21,f)
for r in range(10):
    for c in range(10):
        if (r+c)%5 in [0,1]:p.call(0x21,x+(c+.5)*s,y+(r+.5)*s,c=3 if r%4<2 else 2)
for r in [0,4,9]:p.text(13,y+(r+1)*s-7,str(10-r),17,21,1)
p.text(352,132,'FAIR ISLE',23,29,1)
p.text(352,179,'10-st repeat',20,24,1)
p.text(352,213,'Read from',20,24,1)
p.text(352,243,'lower right.',20,24,1)
p.text(352,294,'Knit every',20,24,1)
p.text(352,324,'round.',20,24,1)
p.circle(370,367,15,3);p.text(396,377,'Moss / B',20,24,1)
p.circle(370,412,15,2);p.text(396,422,'Rose / C',20,24,1)
p.rect(43,421,24,24,4);p.rect(43,421,24,24,1,False)
p.text(79,444,'Cream / A',20,24,1)
p.save()
