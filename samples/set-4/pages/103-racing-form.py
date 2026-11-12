from lib import *
p=Page('103-racing-form',['EDE7DC','212B30','B3B9B1','AD2F40','DDBB42','386C91','FFFFFF'])
p.rect(0,0,640,74,1)
p.text(20,53,'BRACKEN PARK',31,39,6)
p.text(23,112,'RACE 4 / 14:40 / 1600 m',23,28,1)
p.line([(20,130),(620,130)],1,3)
p.text(108,163,'RUNNER / LAST 3',20,24,1)
p.text(504,163,'ODDS',20,24,1)
for i,(name,form,odds,c) in enumerate([('Copper Finch','2-1-3','3/1',3),('Pale Lantern','1-4-2','4/1',5),('Mossy Glen','3-2-1','5/2',4),('Evening Kite','6-3-2','8/1',1)]):
    y=185+i*65
    p.rect(20,y,600,60,6 if i%2==0 else 0)
    p.text(25,y+37,str(i+1),24,30,1)
    pts=[(67,y+8),(80,y+3),(92,y+8),(104,y+21),(95,y+29),(89,y+23),(89,y+50),(69,y+50),(69,y+23),(61,y+29),(52,y+21)]
    p.poly(pts,c)
    if i==0:p.line([(69,y+10),(89,y+43)],6,5)
    if i==1:p.rect(71,y+25,16,8,4)
    if i==2:p.poly([(79,y+17),(89,y+27),(79,y+37),(69,y+27)],3)
    if i==3:p.rect(70,y+10,19,9,4)
    p.text(118,y+25,name,22,26,1)
    p.text(119,y+53,form,20,23,1)
    p.text(510,y+38,odds,28,34,1)
p.text(24,479,'GOING: GOOD   /   PURSE $8,000',20,24,1)
p.save()
