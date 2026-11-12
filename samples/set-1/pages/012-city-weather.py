from _support import *
META=dict(number=12,title='Belltown: five days',purpose='Five-day city weather forecast',style='Flat pictograms on five full-height pastel cards',techniques=['native arcs','polygons','palette redefinition'],animated=False)
def build():
    p=Page('012-city-weather',['f6f0e5','273b55','e5ad35','c6dfe5','e8cedb','d1dfbd','f0d8ae','ccd1e7','557c9e','fff9ed'])
    p.t(24,14,'BELLTOWN',32,44)
    p.t(24,62,'FIVE-DAY FORECAST',20,28)
    p.t(616,31,'13-17 NOV',20,28,align='right')
    days=[('FRI','24','14','SUN',6),('SAT','22','13','FAIR',5),('SUN','18','12','RAIN',3),('MON','19','11','CLOUD',7),('TUE','23','13','SUN',4)]
    for i,(day,hi,lo,desc,col) in enumerate(days):
        x=10+i*126;cx=x+58
        p.rect(x,115,116,346,col)
        p.t(cx,132,day,23,32,align='center')
        if i in [0,4]:sun(p,cx,226,22,2)
        elif i==1:
            sun(p,cx+15,210,20,2,False);cloud(p,cx-5,236,9,.70)
        elif i==2:
            cloud(p,cx,211,9,.80)
            for a in [-22,0,22]:p.line([(cx+a,246),(cx+a-8,263)],8,4)
        else:cloud(p,cx,227,9,.85)
        p.t(cx,293,hi,35,48,align='center')
        p.t(cx,352,lo,22,30,align='center')
        p.t(cx,412,desc,19,26,align='center')
    return p
if __name__=='__main__':run(build)
