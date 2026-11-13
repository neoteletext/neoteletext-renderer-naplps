from _support import *

META=dict(number=112,title='The Little Journey',purpose='A pocket phrase card for travellers',style='Midnight blue, warm paper and coral; three editorial language bands',techniques=['non-spacing accents in French, German and Spanish','supplementary arrows and quotation marks','precise POINT SET text placement'],covers=[2,9,10],animated=False)

def build():
    p=Page('112-pocket-phrases',['142D42','F5EDD8','EF8564','527D89','21465A','D7CAB0','E8B65B','F5EDD8'])
    p.t(32,23,'THE LITTLE',28,36,1)
    p.t(32,61,'JOURNEY',48,62,1)
    p.t(605,31,'POCKET',11,16,2,align='right')
    p.t(605,52,'PHRASES / 3',11,16,2,align='right')
    p.t(605,80,'SMALL CHANGE',10,14,2,align='right')
    p.at(535,122,b'\x19\x23 \x19\x25 \x19\x22',w=14,h=22,c=1)
    rule(p,136,3)
    rows=[('01','FRANÇAIS','Où est le café?','Where is the cafe?',155),
          ('02','DEUTSCH','Grüße von der Küste.','Greetings from the coast.',247),
          ('03','ESPAÑOL','Mañana, a las diez.','Tomorrow, at ten.',339)]
    for num,lang,phrase,translation,y in rows:
        p.t(32,y,num,22,30,2)
        p.t(94,y,lang,11,15,2,prop=False)
        p.at(94,y+51,b'\x19\x2b'+ascii_accents(phrase)+b'\x19\x3b',w=20,h=28,c=1)
        p.t(94,y+60,translation,12,18,1)
        if num!='03': rule(p,y+84,3,x=94,w=514)
    p.at(32,463,b'\x19\x2c  Listen   /   Speak  \x19\x2e',w=12,h=18,c=2)
    p.t(608,447,'112',11,15,2,align='right')
    return p

if __name__=='__main__': finish(build,META)
