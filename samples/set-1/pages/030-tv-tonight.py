from _support import *
META=dict(number=30,title='Tonight on three',purpose='Television schedule for one evening',style='Pastel electronic programme grid with colour-coded channel bands',techniques=['grid','colour panels','fixed-pitch time axis'],animated=False)
def build():
    p=Page('030-tv-tonight',['e6e9e5','26364a','b65d52','488d88','75699a','f9f4df','d9bf9f','b9d0c5','c9c5db'])
    p.t(21,9,'TONIGHT ON THREE',35,49)
    p.t(620,68,'FRIDAY 13 NOV',20,28,align='right')
    for x,s in [(143,'18:00'),(304,'19:00'),(465,'20:00')]:p.t(x,114,s,20,28,prop=False)
    for y,col,ch in [(160,2,'1'),(258,3,'2'),(356,4,'3')]:
        p.rect(15,y,112,91,col);p.t(71,y+12,ch,48,64,c=5,align='center')
    blocks=[(143,160,151,6,['NEWS','AT SIX']),(304,160,310,6,['THE GLASS HARBOUR','Film / 19:00-21:00']),
            (143,258,151,7,['COAST','PATHS']),(304,258,151,7,['NATURE','WATCH']),(465,258,149,7,['NIGHT','MUSIC']),
            (143,356,310,8,['THE LONG INNINGS','Cricket highlights']),(465,356,149,8,['LATE','REPORT'])]
    for x,y,w,col,lines in blocks:
        p.rect(x,y,w,91,col)
        for i,s in enumerate(lines):p.t(x+10,y+12+i*36,s,21 if len(s)<12 else 19,29)
    for x in [143,304,465,615]:p.line([(x,149),(x,160)],1,1)
    return p
if __name__=='__main__':run(build)
