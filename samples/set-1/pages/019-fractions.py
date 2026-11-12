from _support import *
META=dict(number=19,title='A piece of the whole',purpose='Fractions lesson with pie diagrams',style='Pastel chalk diagrams on a hand-ruled slate-green board',techniques=['hatching','polygons','native arcs'],animated=False)
def wedge(p,cx,cy,r,start,stop,c):
    pts=[(cx,cy)]+[(cx+r*math.cos(math.radians(a)),cy+r*.96*math.sin(math.radians(a))) for a in range(start,stop+1,5)]
    p.poly(pts,c)
def build():
    p=Page('019-fractions',['244d43','f1efcf','e9bf7b','e5afa9','a4d0d1','467466','73988a'])
    p.line([(10,8),(629,11),(630,470),(11,467),(10,8)],6,4)
    p.t(320,21,'A PIECE OF THE WHOLE',27,40,align='center')
    p.t(320,72,'Equal parts make a fraction.',20,29,align='center')
    for cx,n,d,col in [(118,1,2,2),(320,1,3,3),(522,3,4,4)]:
        p.circle(cx,221,73,5)
        wedge(p,cx,221,73,-90,int(-90+360*n/d),col)
        p.circle(cx,221,73,1,False,3)
        for j in range(d):
            a=math.radians(-90+360*j/d)
            p.line([(cx,221),(cx+73*math.cos(a),221+70*math.sin(a))],1,2)
        p.t(cx,308,f'{n}/{d}',35,47,c=col,align='center',prop=False)
    p.t(29,393,'1/2 = 2/4',29,40)
    p.rect(337,391,268,44,5)
    p.texture(fill=3);p.rect(337,391,134,44,2);p.texture()
    for x in [337,404,471,538,605]:p.line([(x,391),(x,435)],1,2)
    p.line([(337,391),(605,391),(605,435),(337,435),(337,391)],1,2)
    return p
if __name__=='__main__':run(build)
