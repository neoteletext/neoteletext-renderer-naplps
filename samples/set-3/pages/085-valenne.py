import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('085-valenne','91c1cd 153e5b f6e8c7 477b94 c65137 a5c5ca 2f647d')
circle(p,495,93,48,2)
p.poly([(0,297),(178,56),(321,289),(437,150),(640,310),(640,480),(0,480)],3)
p.poly([(100,161),(178,56),(250,173),(207,152),(185,178),(164,137),(133,168)],2)
p.poly([(363,219),(437,150),(515,211),(465,200),(445,216),(424,187),(396,220)],2)
p.poly([(0,325),(123,272),(259,317),(405,264),(640,320),(640,480),(0,480)],5)
p.poly([(0,381),(178,319),(377,358),(640,286),(640,480),(0,480)],2)
# Red skier drops diagonally down the white foreground.
circle(p,390,286,10,1)
p.poly([(375,298),(389,297),(410,324),(399,333),(381,320),(360,330),(349,321)],4)
p.line([(399,330),(420,348),(393,365),(422,372)],1,6)
p.line([(386,328),(390,347),(366,355)],1,6)
p.line([(348,328),(409,383)],1,2)
p.line([(386,365),(452,383)],4,3)
p.line([(352,355),(418,373)],4,3)
p.rect(0,396,640,84,1)
type(p,28,454,'VALENNE',60,60,2)
type(p,611,474,'ALPINE RAIL / WINTER 1936',20,25,2,'right')
type(p,24,42,'HIGH SNOW. CLEAR AIR.',22,28,1)
finish(p,85,'Valenne','Alpine ski resort rail travel poster','Vintage flat mountain travel print',['flat mountain polygons','skier silhouette','display typography'], 'A red skier descends a broad cream snowfield beneath two sharply faceted peaks and a pale sun. Glacial blue layers describe distance, while the large resort name sits in a deep-blue station-style base. The fictional rail destination and winter date give the poster a period travel purpose.')
