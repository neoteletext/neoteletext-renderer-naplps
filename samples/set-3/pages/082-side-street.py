import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('082-side-street','174b72 e8dec2 0b273e 4894af')
p.rect(0,0,248,480,1)
# Duotone saxophonist crop and sweeping bell shape.
p.poly([(320,480),(308,319),(330,262),(381,243),(427,277),(449,480)],2)
circle(p,374,204,43,2)
p.poly([(326,195),(335,157),(387,145),(416,162),(421,178)],1)
p.poly([(388,225),(431,236),(426,250),(388,241)],1)
p.line([(424,243),(460,278),(451,349),(481,380),(517,352)],1,13)
p.poly([(485,351),(546,325),(538,372),(517,393)],1)
p.line([(350,291),(416,315),(446,302)],3,9)
p.line([(409,319),(418,365)],3,9)
for y in [281,304,327]:circle(p,455,y,3,0)
# Big editorial typography occupies the light column.
type(p,20,92,'SIDE',55,69,0)
type(p,20,157,'STREET',40,51,0)
type(p,20,224,'THE',27,35,0)
type(p,20,263,'ORIN',35,43,0)
type(p,20,303,'QUARTET',28,36,0)
p.rect(20,330,203,6,0)
type(p,20,378,'LIVE AT',24,31,0)
p.data.extend(b'\x1b*|')
p.text(20,414,'CAFE SABLE',23,29,0)
p.data=p.data.replace(b'CAFE SABLE',b'CAF\x19\x42E SABLE')
type(p,20,459,'MONO / 014',21,27,0)
finish(p,82,'Side Street','Jazz quartet record sleeve','1950s duotone jazz editorial design',['supplementary accented letter','duotone silhouette','display typography'], 'An ink-blue saxophonist is tightly cropped against a darker blue ground, while a cream left column holds the sleeve typography. The bell and bent arm give the music a diagonal movement. A native supplementary acute accent prints the fictional venue name Café Sable.')
