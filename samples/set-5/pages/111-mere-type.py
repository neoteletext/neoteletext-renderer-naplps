from _support import *

META=dict(number=111,title='Mere Type Bureau',purpose='A printer\'s specimen and type-order proof',style='Ivory, ink and vermilion; asymmetric type specimen',techniques=['five C1 size presets','120-pixel TEXT field','small-print TEXT field','proportional display type'],covers=[1,2,3],animated=False)

def build():
    p=Page('111-mere-type',['F2EBD9','1B2B30','BF4632','CFC5AA','57766D','F7F2E7','9F6C46','1B2B30'])
    p.t(32,20,'MERE TYPE BUREAU',16,22,1)
    p.t(608,25,'SPECIMEN  /  08',11,15,1,align='right')
    rule(p,55)
    p.t(28,65,'Aa',104,120,2)
    p.t(295,83,'A voice for',24,32,1)
    p.t(295,120,'every size.',24,32,1)
    p.t(297,167,'CUT 06  /  STROKE ROMAN',11,15,4)
    rule(p,209)
    p.t(32,224,'01 / SMALL',10,14,4)
    p.preset(32,272,'Letters, finely set.',SMALL)
    p.t(32,284,'02 / MEDIUM',10,14,4)
    p.preset(32,333,'Mere Press',MEDIUM)
    p.t(32,347,'03 / NORMAL',10,14,4)
    p.preset(32,398,'A clear impression',NORMAL)
    p.line([(330,225),(330,413)],3)
    p.t(360,224,'04 / DOUBLE HEIGHT',10,14,4)
    p.preset(360,298,'TALL TYPE',TALL,2)
    p.t(360,321,'05 / DOUBLE SIZE',10,14,4)
    p.preset(360,398,'BOLD',DOUBLE,1)
    rule(p,426)
    p.t(32,445,'Order by letter. Proofs supplied on warm ivory stock.',8,12,1)
    p.t(608,445,'111',10,14,2,align='right')
    return p

if __name__=='__main__': finish(build,META)
