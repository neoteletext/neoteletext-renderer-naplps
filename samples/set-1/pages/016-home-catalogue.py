from _support import *
META=dict(number=16,title='Homepost autumn offers',purpose='Mail-order catalogue for three products',style='Bright 1980s panels, product silhouettes and serrated price bursts',techniques=['polygons','native arcs','price bursts'],animated=False)
def build():
    p=Page('016-home-catalogue',['fff4d8','172b51','eb4b39','29a8c7','f7ca3f','fffaf0','b2dce1','344c70','9d312f'])
    p.rect(0,0,640,98,2)
    p.t(18,4,'HOMEPOST',48,65,c=5)
    p.t(620,60,'AUTUMN 87',19,27,c=5,align='right')
    for x,col in [(0,4),(214,3),(428,2)]:p.rect(x,98,212,382,col)
    p.t(105,111,'POCKET',23,32,align='center');p.t(105,144,'RADIO',23,32,align='center')
    p.t(320,111,'DESK',23,32,align='center');p.t(320,144,'LAMP',23,32,align='center')
    p.t(534,111,'QUICK',23,32,c=5,align='center');p.t(534,144,'KETTLE',23,32,c=5,align='center')
    # Radio: aerial, speaker perforations, tuning scale and dial.
    p.line([(144,214),(168,180)],1,3);p.rect(39,216,136,93,1)
    p.rect(49,229,116,17,5)
    for y in [260,273,286]:
        for x in [54,68,82,96]:p.circle(x,y,2.5,7)
    p.circle(144,276,14,5);p.circle(144,276,7,7)
    # Adjustable lamp.
    p.line([(285,307),(351,248),(326,208)],1,10)
    p.poly([(304,197),(343,198),(362,230),(290,230)],5)
    p.rect(272,307,95,11,1);p.circle(351,248,8,5)
    # Kettle with negative-space handle.
    p.circle(583,253,29,1,False,8)
    p.poly([(473,238),(550,238),(571,308),(461,308)],5)
    p.poly([(476,253),(453,241),(440,245),(465,278)],5)
    p.rect(486,225,51,12,1);p.circle(512,220,7,1)
    for x,price,code in [(106,'$19','R14'),(320,'$24','L08'),(534,'$32','K21')]:
        burst(p,x,378,87,49,5)
        p.t(x,350,price,35,50,c=1,align='center')
        p.t(x,439,code+'  POST $3',17,24,c=5 if x==534 else 1,align='center')
    return p
if __name__=='__main__':run(build)
