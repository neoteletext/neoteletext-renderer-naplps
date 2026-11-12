import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('069-vespera','253d3b c5ad73 e5dcc0 71856b 9ca38a 112f31')
# Organic frame and long whiplash stems.
p.rect(20,18,600,444,1,False);p.rect(27,25,586,430,3,False)
for mirror in [False,True]:
    def flip(pts):return [(640-x if mirror else x,y) for x,y in pts]
    pts=bez((83,430),(214,323),(21,188),(164,70),28)
    p.line(flip(pts),1,3)
    p.line(flip(bez((86,430),(42,271),(178,240),(108,141))),3,3)
    p.poly(flip([(102,333),(45,286),(42,243),(76,260),(108,303)]),3)
    p.poly(flip([(117,219),(170,179),(173,139),(141,153),(118,190)]),4)
# Single lily flaring from the long curved stem.
p.line(bez((331,354),(391,266),(273,235),(324,133)),1,3)
for pts in [[(324,151),(254,115),(235,67),(277,80),(323,126)],[(324,151),(328,82),(368,50),(355,107)],[(324,151),(377,110),(416,109),(380,145)]]:p.poly(pts,2)
p.line([(324,149),(306,94)],1,3)
# Scent bottle.
p.poly([(267,300),(287,279),(354,279),(376,300),(372,396),(270,396)],1)
p.poly([(276,304),(293,289),(350,289),(366,304),(363,386),(280,386)],0)
p.rect(298,257,47,23,1);p.rect(305,245,32,12,2)
type(p,321,348,'V',37,47,2,'center')
type(p,320,224,'VESPERA',39,49,2,'center')
type(p,320,435,'LILY / EAU DE PARFUM',20,26,1,'center')
finish(p,69,'Vespera','Lily perfume advertisement','Art nouveau whiplash curves in muted gold',['curved polylines','botanical polygons','proportional text'], 'A single ivory lily grows above an angular perfume bottle. Mirrored whiplash stems form an organic frame, with sage leaves and dull gold outlines on a deep green ground. Open space around the large name keeps the advertisement poised at small size.')
