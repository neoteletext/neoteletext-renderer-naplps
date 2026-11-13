from _support import *

META=dict(number=120,title='The Ribbon Check',purpose='A typewriter service slip and complete keyboard impression',style='Ivory service sheet on a grey desk, black type and red workshop annotations',techniques=['every printable ASCII character 20-7E','BS overstrike','HT/APF','CR/LF','fixed-pitch text','small-print fields'],covers=[2,10,16],animated=False)

def build():
    p=Page('120-ribbon-check',['78817E','242D2E','A34435','CDBFA3','EDE6D5','FAF4E3','98A19C','242D2E'])
    p.rect(29,17,590,455,6)
    p.rect(21,9,590,455,4)
    p.t(49,29,'TESSERA LETTER SERVICE',23,30,1)
    p.t(49,65,'WORKSHOP SLIP  /  MACHINE 04  /  12 SEP',12,18,2)
    rule(p,96,3,x=49,w=534)
    p.style(13,21,rows=1).field(49,112,534,122).pos(49,134).color(1)
    p.write(b'Dear keeper,\r\nThe keys are clean. Fit a red\x08\x08\x08///\x09black\r\nribbon and return this impression.\r\n\x09With care,  The workshop')
    p.field()
    p.t(49,244,'KEYBOARD IMPRESSION / ALL PRINTING KEYS',12,18,2)
    p.rect(46,275,538,117,5)
    start=len(p.data)
    for y,a,b in [(303,0x20,0x40),(336,0x40,0x60),(369,0x60,0x7f)]:
        p.at(60,y,bytes(range(a,b)),w=16,h=25,c=1)
    p.evidence_note('primary-set',start,characters='20-7E',count=95)
    p.t(49,410,'RIBBON: BLACK   /   FEED: EVEN   /   PLATEN: SOUND',10,15,1)
    p.t(49,436,'Keep this sheet with the machine.',10,15,2)
    p.t(581,436,'120',10,15,2,align='right')
    return p

if __name__=='__main__': finish(build,META)
