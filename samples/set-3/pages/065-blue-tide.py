import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('065-blue-tide','e8dfbe 142e53 315779 75949e f6edcd a43b30')
p.rect(22,20,596,440,1,False)
circle(p,459,141,45,4)
p.poly([(280,296),(427,110),(558,297)],3)
p.poly([(384,166),(427,110),(465,165),(444,157),(428,168),(412,151)],4)
p.poly([(23,319),(116,278),(233,307),(316,291),(460,307),(617,274),(617,458),(23,458)],2)
# Great curling wave with foam claws and three nested indigo ribbons.
wave=[(24,359),(68,307),(108,225),(157,170),(207,152),(250,164),(281,191),(294,224),(273,218),(258,199),(232,196),(217,218),(224,251),(259,281),(322,314),(410,340),(494,360),(617,367),(617,458),(24,458)]
p.poly(wave,1)
foam=[(67,309),(109,220),(155,164),(203,144),(247,155),(281,183),(303,218),(285,222),(278,205),(260,202),(258,187),(240,184),(229,193),(218,185),(206,200),(195,194),(181,218),(168,215),(145,249),(134,243),(112,279),(100,276)]
p.poly(foam,4)
for off in [0,27,55]:
    pts=bez((31,400+off),(150,258+off),(162,280+off),(312,358+off),18)+bez((312,358+off),(400,400+off),(520,415+off),(617,401+off),14)[1:]
    p.line(pts,3 if off==27 else 4,3)
type(p,43,76,'BLUE TIDE',28,36,1)
type(p,45,109,'WOODBLOCK No. 7',20,24,1)
p.rect(545,62,46,71,5)
type(p,568,93,'AO',20,25,4,'center');type(p,568,121,'VII',17,23,4,'center')
finish(p,65,'Blue Tide','Coastal woodblock print catalogue','Ukiyo-e flat indigo print',['layered polygons','polylines','native arc'], 'A clawed cream wave curls toward a distant snow-capped mountain. Indigo ribbons sweep across the foreground, leaving warm paper in the sky; a small vermilion publisher seal supplies the only hot colour. The title sits on the paper instead of a common page band.')
