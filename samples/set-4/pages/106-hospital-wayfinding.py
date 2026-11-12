from lib import *
p=Page('106-hospital-wayfinding',['F4F5EB','184F69','C24B3F','337F8C','807298','DDE7E1','FFFFFF'])
p.rect(25,21,67,67,1)
p.rect(51,33,15,43,6);p.rect(37,47,43,15,6)
p.text(115,47,'MEREVALE',29,36,1)
p.text(115,82,'HOSPITAL',23,28,1)
# Oversized directional arrows and pictograms: no tiny auxiliary instructions.
for y,c,title,direction in [(116,2,'EMERGENCY','left'),(216,3,'WARD 3','up'),(316,4,'X-RAY','right')]:
    p.rect(0,y,640,88,c)
    p.text(118,y+58,title,31,38,6)
    if direction=='left':
        p.rect(44,y+20,12,49,6);p.rect(26,y+38,49,12,6)
        arrow(p,(587,y+44),(529,y+44),6,8,25)
    elif direction=='up':
        p.circle(41,y+35,7,6)
        p.line([(27,y+66),(27,y+47),(78,y+47),(78,y+66)],6,5)
        p.rect(53,y+36,23,10,6)
        arrow(p,(558,y+67),(558,y+20),6,8,23)
    else:
        p.rect(27,y+18,49,52,6,False)
        p.line([(44,y+27),(44,y+60)],6,4)
        p.line([(60,y+27),(60,y+60)],6,4)
        p.line([(35,y+37),(69,y+49)],6,3)
        arrow(p,(528,y+44),(589,y+44),6,8,25)
p.text(26,451,'YOU ARE AT: NORTH ENTRANCE',22,28,1)
p.save()
