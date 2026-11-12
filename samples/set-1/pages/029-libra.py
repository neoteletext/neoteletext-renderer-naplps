from _support import *
META=dict(number=29,title='Libra: the balanced day',purpose='Daily horoscope for one sign',style='Deep purple, gold stars, a zodiac wheel and a custom scales glyph',techniques=['DRCS','macro','native arcs','palette redefinition'],animated=False)
def build():
    p=Page('029-libra',['26173f','e5c479','9b7fac','584066','f5e4af','37244d','bc985b'])
    p.t(25,0,'LIBRA',60,80)
    p.t(29,82,'23 SEP - 22 OCT',20,28,c=2)
    p.t(610,26,'THE DAILY',19,27,c=2,align='right')
    p.t(610,58,'ORACLE',24,33,c=4,align='right')
    cx,cy=188,294
    p.circle(cx,cy,151,1,False,2)
    p.circle(cx,cy,136,6,False,1)
    p.circle(cx,cy,90,6,False,1)
    for i in range(12):
        a=i*math.pi/6
        p.line([(cx+91*math.cos(a),cy+87*math.sin(a)),(cx+135*math.cos(a),cy+130*math.sin(a))],6,1)
    m=Page();m.relpoly([(0,-7),(2,-2),(7,0),(2,2),(0,7),(-2,2),(-7,0),(-2,-2)])
    p.macro(0x21,m)
    for i in range(12):
        a=(i+.5)*math.pi/6
        p.call(0x21,cx+114*math.cos(a),cy+109*math.sin(a),1)
    for x,y in [(379,145),(585,140),(605,384),(362,438)]:p.call(0x21,x,y,4)
    # Define an actual downloadable scales character in a square field.
    p.cmd(0x22,b'\x40\x40'+xy(.15,.15))
    p.data.extend(b'\x1b+{\x1bC!\x0e')
    p.cmd(0x21,b'\x4c'+xy(.025,.025))
    for pts in [[(.5,.86),(.5,.18)],[(.18,.65),(.82,.65)],[(.23,.65),(.23,.40)],[(.77,.65),(.77,.40)],[(.24,.17),(.76,.17)]]:
        p.cmd(0x2a,b''.join(xy(x,y) for x,y in pts))
    for x in [.23,.77]:p.cmd(0x37,xy(x-.17,.40)+xy(.34,0)+xy(-.17,-.15))
    p.data.extend(b'\x1bE\x0e')
    p.pel(1).color(4).cmd(0x22,b'\x40\x40'+xy(116/640,116/Y_SCALE)).pos(130,353)
    p.data.extend(b'\x1d!')
    p.t(385,174,'Make room',25,35,c=4)
    p.t(385,215,'for a new',25,35,c=4)
    p.t(385,256,'idea today.',25,35,c=4)
    p.line([(385,316),(608,316)],6,2)
    p.t(385,332,'LUCKY  6',21,29)
    p.t(385,375,'COLOUR',19,27,c=2)
    p.t(385,406,'OLD GOLD',23,32)
    return p
if __name__=='__main__':run(build)
