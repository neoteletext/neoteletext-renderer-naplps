from _support import *
META=dict(number=34,title='Alder Metro',purpose='Metro network diagram',style='Three coloured routes at 45 degrees with rings at interchanges',techniques=['thick polylines','native arcs','transit symbols'],animated=False)
def station(p,x,y,c,interchange=False):
    p.circle(x,y,10 if interchange else 7,1)
    p.circle(x,y,7 if interchange else 4,0)
def build():
    p=Page('034-alder-metro',['f4f1e4','273639','c34e47','3a78a0','51926b','c7c7b7'])
    p.t(16,4,'ALDER METRO',35,46)
    p.t(618,21,'NETWORK',20,28,align='right')
    p.line([(42,186),(194,186),(298,290),(589,290)],2,10)
    p.line([(81,422),(194,309),(194,186),(282,98),(553,98)],3,10)
    p.line([(42,357),(292,357),(432,217),(594,217)],4,10)
    for x,y,c in [(42,186,2),(589,290,2),(81,422,3),(282,98,3),(410,98,3),(553,98,3),(42,357,4),(292,357,4),(432,217,4),(594,217,4)]:station(p,x,y,c)
    for x,y in [(194,186),(146,357),(359,290)]:station(p,x,y,1,True)
    for x,y,s in [(17,138,'RIVER'),(67,215,'CENTRAL'),(524,307,'DOCK'),(21,439,'SOUTH'),(248,62,'WOOD'),(364,115,'NORTH'),(472,62,'AIRPORT'),(17,382,'PARK'),(66,316,'MERE'),(243,383,'GARDEN'),(418,242,'EAST'),(526,174,'HILL'),(371,311,'MUSEUM')]:p.t(x,y,s,19,27)
    for x,col,s in [(365,2,'1'),(447,3,'2'),(529,4,'3')]:
        p.line([(x,451),(x+27,451)],col,8);p.t(x+38,435,s,21,30)
    return p
if __name__=='__main__':run(build)
