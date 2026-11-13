from _support import *

META=dict(number=118,title='Isle Air Boarding Card',purpose='A boarding card for the fictional Merehaven to Oriel service',style='Cream ticket with cobalt route panel and vermilion validation marks',techniques=['APH home','APS row and column','NSR with position','HT/APF','LF/APD','VT/APU','CR/APR','POINT SET exact placement'],covers=[10],animated=False)

def build():
    p=Page('118-isle-air',['F2EBD6','183B53','BC4938','275A7A','CCBE9A','E7D9B8','648A97','183B53'])
    # Home is deliberately used for the edge-to-edge airline heading.
    p.style().color(1).raw(SI+b'\x1e  ISLE AIR'+SO)
    p.t(608,5,'BOARDING CARD',12,18,2,align='right')
    rule(p,38,1)
    p.raw(b'\x1f\x42\x42') # NSR at top-origin row 2, col 2; default 16 x 24.
    p.write('FLIGHT IA 208  /  23 AUG 1986')
    # NSR also restores three-byte DOMAIN; restore the encoder's precision.
    p.pel(1).color(1)
    p.raw(SI+b'\x1c\x2e\x22LENA MOSS'+SO) # renderer APS row 14 upward
    p.t(32,90,'PASSENGER',10,14,2)
    p.rect(24,157,592,113,3)
    p.t(42,171,'MEREHAVEN',31,42,0)
    p.t(594,171,'ORIEL',31,42,0,align='right')
    p.arrow([(302,220),(365,220)],0,3,10)
    p.t(42,232,'MHV',15,22,0)
    p.t(594,232,'ORL',15,22,0,align='right')
    p.style(16,24).field(40,295,560,115).pos(40,320).color(1)
    # LF preserves x; VT returns to the first row to set its right-hand value.
    p.write(b'GATE\x09A4\x0a16:20\x0b\x09\x09SEAT 07A\r\nBOARD\r\nDEPART 16:50')
    p.field()
    p.rect(422,302,176,92,2,False)
    p.t(510,317,'CLEARED',20,28,2,align='center')
    p.t(510,352,'CABIN / 1 BAG',11,17,2,align='center')
    p.style(8,10).field(32,425,576,12).pos(32,435).color(4).write('=').eol().field()
    footer(p,118,'KEEP THIS CARD UNTIL ARRIVAL',1)
    return p

if __name__=='__main__': finish(build,META)
