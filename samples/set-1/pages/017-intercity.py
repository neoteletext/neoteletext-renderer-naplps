from _support import *
META=dict(number=17,title='Coastlink intercity',purpose='Intercity train timetable',style='White railway wayfinding on deep blue with a schematic route strip',techniques=['macro','fixed-pitch timetable','route lines'],animated=False)
def build():
    p=Page('017-intercity',['103c74','f9fbef','6fc6dc','2a578a','efd25b'])
    p.rect(0,0,92,96,1)
    p.arrow([(18,48),(73,48)],0,8,21)
    p.t(112,10,'COASTLINK',36,49)
    p.t(113,62,'WEEKDAY INTERCITY',20,28,c=2)
    p.rect(0,111,640,44,3)
    for x,s in [(17,'DEPART'),(167,'TO'),(428,'ARRIVE'),(577,'PL')]:p.t(x,119,s,19,27)
    rows=[('07:10','EASTPORT','08:42','2'),('08:25','BELLTOWN','10:05','1'),('09:40','EASTPORT','11:12','2'),('11:15','NORTH BAY','13:00','3'),('13:20','EASTPORT','14:52','2')]
    for i,(dep,dest,arr,plat) in enumerate(rows):
        y=167+i*41
        p.t(17,y,dep,21,29,prop=False);p.t(167,y,dest,23,30)
        p.t(428,y,arr,21,29,prop=False);p.t(585,y,plat,21,29,prop=False)
    p.line([(17,385),(620,385)],2,1.5)
    p.line([(48,420),(589,420)],2,6)
    m=Page();m.move(-7,0).cmd(0x2d,xy(14/640,0));p.macro(0x21,m)
    for x,name in [(48,'CITY'),(217,'MERE'),(394,'BAY'),(589,'PORT')]:
        p.call(0x21,x,420,1);p.t(x,437,name,19,27,align='center')
    return p
if __name__=='__main__':run(build)
