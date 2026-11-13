from _support import *

META=dict(number=119,title='The Glass Horizon',purpose='A cinema programme for a fictional evening screening',style='Black, apricot and lilac; large marquee typography and mosaic lamps',techniques=['DRCS star in ordinary text','mosaics mixed with text','separated mosaics','REPEAT mosaic border','BLINK START on optional ornament','palette BLINK on text'],covers=[11,13,14,15],animated=True)

def build():
    p=Page('119-glass-horizon',['171B2A','F3E7CF','EDAA7C','AEA3D0','39415B','776A91','D48B86','F3E7CF','171B2A','171B2A','171B2A','171B2A','171B2A','E2C267','F3E7CF','AEA3D0'])
    p.at(24,27,UNDER+b'\x1d\x7f',w=16,h=12,c=2).repeat(36).raw(NOUNDER)
    p.t(32,47,'ASTER PICTURE HOUSE',18,26,3)
    p.t(32,103,'THE GLASS',54,69,1)
    p.t(32,175,'HORIZON',65,82,1)
    p.t(32,280,'ONE NIGHT  /  FRIDAY 18 JUNE',15,23,2)
    p.t(32,319,'19:30',39,52,2)
    p.t(314,326,'A journey beyond',18,25,3)
    p.t(314,354,'the last shoreline.',18,25,3)
    # Define a square custom star. Use a nonzero entry while recording the mask.
    p.style(24,24).color(1).raw(ESC+b'C!'+SO)
    points=[(.50,.94),(.61,.62),(.95,.62),(.68,.41),(.79,.08),(.50,.29),(.21,.08),(.32,.41),(.05,.62),(.39,.62)]
    data=xy(*points[0])+b''.join(xy(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:]))
    p.cmd(0x37,data).raw(ESC+b'E'+ESC+b'*{'+SO)
    p.at(32,419,b'A \x19! SABLE FILM  /  COLOUR',w=16,h=24,c=1)
    p.at(32,459,b'\x1d\x23  ADULT 6.00  /  STALLS  \x1d\x23',w=14,h=20,c=3)
    # Dedicated entries mean only these optional ornaments blink.
    p.at(552,410,'*',w=20,h=24,c=14).raw(ESC+b'N')
    p.at(584,410,'+',w=20,h=24,c=15).blink(15,13,on=7,off=9)
    return p

if __name__=='__main__': finish(build,META)
