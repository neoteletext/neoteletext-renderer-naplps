from lib import *
p=Page('093-ski-report',['DCECF5','153C68','FFFFFF','7EB5D2','356E9B','E98D62'])
p.rect(0,0,640,233,1)
p.text(24,57,'RIME RIDGE',34,43,2)
p.text(26,94,'07 JUL / 06:00',20,24,3)
p.poly([(276,233),(390,113),(429,160),(479,92),(640,233)],3)
p.poly([(363,145),(390,113),(417,146),(395,137),(386,149),(378,137)],2)
p.poly([(452,125),(479,92),(516,130),(490,120),(479,135),(470,119)],2)
# Snowflake DRCS, defined in a square normalised character field.
b=bytes([0x21,0x4c])+xy(.045,.045)
for a in range(0,180,60):
    t=math.radians(a);dx=.43*math.cos(t);dy=.43*math.sin(t)
    b+=bytes([0x2a])+xy(.5-dx,.5-dy)+xy(.5+dx,.5+dy)
    for sign in [-1,1]:
        ex=.5+sign*dx*.65;ey=.5+sign*dy*.65
        for turn in [-.6,.6]:
            vx=.17*math.cos(t+turn);vy=.17*math.sin(t+turn)
            b+=bytes([0x2a])+xy(ex,ey)+xy(ex-sign*vx,ey-sign*vy)
p.drcs(0x21,b)
for x,y in [(42,157),(108,191),(191,153),(526,67),(584,120)]:p.glyph(x,y,0x21,34,34,2)
p.text(26,291,'124',58,62,1);p.text(184,285,'cm',24,29,1)
p.text(28,323,'BASE DEPTH',20,24,4)
p.text(313,279,'18 cm fresh',26,32,1)
p.text(313,318,'7 / 9 lifts',26,32,1)
p.line([(26,342),(614,342)],3,2)
for y,title,frac,copy in [(384,'TRAILS',.8,'24/30'),(435,'GROOMED',.6,'18/30')]:
    p.text(26,y,title,20,24,1)
    p.rect(205,y-21,263,18,3);p.rect(205,y-21,263*frac,18,4)
    p.text(499,y,copy,22,26,1)
p.save()
