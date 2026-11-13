from _support import *

META=dict(number=113,title='The Copper Spoon',purpose='A seasonal supper menu with prices and serving sizes',style='Forest green on cream with copper-red headings',techniques=['REPEAT dot leaders','REPEAT TO EOL rule and fill','underline','reverse video','colour mode 2','supplementary currency and fractions'],covers=[8,9,11,12],animated=False)

def build():
    p=Page('113-copper-spoon',['EEE5CC','234C40','AD4A30','CABC99','D9CFAF','F8F0DD','7A8160','234C40'])
    p.t(320,23,'THE COPPER SPOON',30,40,1,align='center')
    p.t(320,75,'SUPPER  /  LATE SUMMER  /  18:00-21:30',12,18,2,align='center')
    p.style(8,12).field(40,101,560,14).pos(40,113).color(2).write('_').eol().field()
    p.at(40,152,UNDER+b'TONIGHT\'S TABLE'+NOUNDER,w=14,h=22,c=1)
    items=[('Roast tomato soup','4.50',190),('Leek & barley pie','9.00',235),('Garden leaf salad','5.50',280),('Pear & ginger tart','4.00',325)]
    for name,price,y in items:
        p.at(40,y,name,w=16,h=24,c=1)
        p.at(360,y,'.',w=10,h=24,c=2).repeat(12)
        p.at(515,y,b'\x19\x23'+price.encode(),w=15,h=24,c=1)
    p.at(40,364,b'\x19\x3d portion for small appetites; \x19\x3c jug of cordial.',w=12,h=18,c=1)
    p.at(40,408,REVERSE+b' BREAD INCLUDED '+NOREVERSE,w=14,h=24,c=1,bg=0)
    p.t(335,388,'Ask about today\'s herbs.',12,18,1)
    # A repeated space in colour mode 2 is a text fill, not a rectangle.
    p.style(8,6).field(40,428,560,8).pos(40,435).cmd(0x3e,b'\x44\x4c').write(' ').eol().field()
    footer(p,113,'MILL LANE  /  ALL PRICES IN CROWNS',1)
    return p

if __name__=='__main__': finish(build,META)
