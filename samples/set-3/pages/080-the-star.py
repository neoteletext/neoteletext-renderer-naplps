import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('080-the-star','182b43 eddfb6 c9a45d 4c9c9c 8bb5aa b9775d 314760')
p.rect(135,13,370,454,2);p.rect(141,19,358,442,1);p.rect(154,32,332,416,0)
p.rect(166,71,308,328,2,False)
# Ornate corner scrolls and seven smaller stars.
for x in [160,480]:
    for y in [38,441]:
        p.poly(star(x,y,12,5,4),2)
for x,y,r in [(218,128,12),(427,119,11),(206,199,9),(435,210,10),(224,275,9),(417,278,9),(320,105,29),(392,172,8)]:p.poly(star(x,y,r,r*.39,8),1)
p.rect(169,333,302,63,3)
for y in [350,371,387]:p.line([(177,y),(257,y),(272,y-3),(344,y-3),(363,y),(464,y)],4,2)
# Symbolic kneeling figure, two vessels and flowing water.
circle(p,321,206,19,5)
p.poly([(301,209),(297,186),(317,176),(337,185),(341,212),(329,192),(312,191)],2)
p.poly([(310,225),(332,225),(344,282),(321,303),(293,279)],5)
p.poly([(298,238),(270,270),(238,273),(236,283),(282,282),(316,253)],5)
p.poly([(333,238),(355,259),(397,254),(400,264),(352,277),(326,257)],5)
p.poly([(306,282),(281,307),(289,333),(330,337),(339,327),(307,320),(319,304),(340,301),(360,321),(385,322),(377,335),(352,334),(324,312)],5)
p.poly([(223,263),(246,266),(251,283),(237,293),(225,284)],2)
p.poly([(389,245),(413,249),(414,268),(400,278),(389,267)],2)
p.line([(236,292),(231,317),(219,342)],4,4)
p.line([(403,277),(417,303),(420,332)],4,4)
type(p,320,63,'XVII',24,30,1,'center')
p.rect(174,402,293,32,1)
type(p,320,438,'THE STAR',27,30,0,'center')
finish(p,80,'The Star','Tarot card illustration','Ornate ivory card with symbolic celestial figure',['star polygons','figurative silhouette','border ornaments'], 'An ivory card floats on midnight blue. Eight celestial emblems surround a kneeling figure pouring two gold vessels toward water and earth. Corner diamonds, an inset rule and Roman numeral complete the card without making its symbolic scene depend on small ornament.')
