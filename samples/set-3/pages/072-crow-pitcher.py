import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('072-crow-pitcher','f0ead7 1b1b18')
p.rect(17,17,606,446,1,False)
# Rough black ground and woodcut diagonal cuts.
p.poly([(34,376),(121,359),(186,370),(269,358),(354,374),(427,358),(601,374),(601,407),(34,407)],1)
# Pitcher body and handle.
p.ellipse(446,277,73,77,1,True,n=22)
p.ellipse(447,277,48,54,0,True,n=20)
p.poly([(331,183),(431,183),(419,225),(440,333),(420,366),(347,366),(325,332),(345,225)],1)
p.poly([(349,212),(416,212),(404,244),(420,328),(405,346),(358,346),(345,327),(360,243)],0)
p.texture(3);p.poly([(363,252),(401,252),(415,329),(401,342),(362,342),(351,326)],1);p.texture()
p.ellipse(382,186,53,15,1,n=18)
p.ellipse(382,184,38,7,0,n=16)
# Crow silhouette, lifted tail and strongly engraved wing.
p.poly([(105,221),(81,169),(146,195),(183,168),(237,169),(270,187),(290,184),(318,197),(285,208),(266,207),(250,254),(196,282),(159,267)],1)
p.poly([(146,220),(192,191),(238,199),(216,241),(170,256)],0)
for i in range(5):p.line([(157+i*12,246),(190+i*9,204)],1,3)
circle(p,266,192,3,0)
p.line([(191,277),(186,347),(165,354),(197,352)],1,3)
p.line([(220,269),(230,344),(215,352),(247,350)],1,3)
p.poly([(305,203),(316,208),(310,217),(300,213)],1)
for x,y,r in [(289,363,8),(310,348,7),(282,342,5),(327,375,6)]:p.ellipse(x,y,r,r*.7,1,n=8)
type(p,320,68,'THE CROW',36,44,1,'center')
type(p,320,112,'AND THE PITCHER',27,34,1,'center')
type(p,320,446,'WISDOM OUTWEIGHS STRENGTH.',21,27,1,'center')
finish(p,72,'The Crow and the Pitcher','Illustrated fable page','Two-ink woodcut with carved hatch shading',['hatching','silhouette polygons','engraved lines'], 'A black crow drops a stone into a heavy jug. White cuts through its wing and cross-hatching in the pitcher evoke carved wood; scattered stones and a rough ground link the two silhouettes. The moral forms a single legible line below the illustration.')
