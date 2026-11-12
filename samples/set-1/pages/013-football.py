from _support import *
META=dict(number=13,title='Floodlight League',purpose='Football league table and last night\'s scores',style='Condensed scoreboard lettering on dark green',techniques=['fixed-pitch text','mosaics','condensed type'],animated=False)
def build():
    p=Page('013-football',['082b22','f0f4cf','d9e356','174838','729b7a','091e19'])
    p.rect(0,0,640,82,5)
    p.t(22,10,'FLOODLIGHT',29,49,c=2)
    p.t(620,27,'DIV 1',23,32,align='right')
    p.t(23,92,'CLUB',19,28,c=4)
    for x,s in [(353,'P'),(414,'W'),(473,'GD'),(566,'PTS')]:p.t(x,92,s,19,28,c=4)
    clubs=[('1 ROVERS','12','9','+18','29'),('2 ATHLETIC','12','8','+12','27'),('3 UNITED','12','7','+08','24'),('4 BOROUGH','12','6','+03','21'),('5 ALBION','12','4','-06','15'),('6 TOWN','12','3','-11','12')]
    for i,(club,played,won,gd,pts) in enumerate(clubs):
        y=129+i*40
        if i%2==0:p.rect(14,y+2,611,38,3)
        p.t(23,y,club,22,34,c=2 if i==0 else 1,prop=False)
        for x,s in [(351,played),(413,won),(473,gd),(571,pts)]:p.t(x,y,s,20,34,c=2 if i==0 else 1,prop=False)
    p.rect(0,383,640,97,5)
    p.t(20,390,'LAST NIGHT',19,27,c=4)
    p.t(20,429,'ROV 2-0 TOWN   ATH 1-1 UTD',21,31,prop=False)
    for x in [490,526,562,598]:p.mosaic(x,408,[0x23],24,24,2)
    return p
if __name__=='__main__':run(build)
