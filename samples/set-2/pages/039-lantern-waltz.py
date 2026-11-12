import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
from encoder import xy
p=Art('039-lantern-waltz',palette('f4ecd8','292625','947b58','d6c5a3'))
p.center(320,72,'LANTERN WALTZ',30,40)
p.center(320,114,'FOR SOLO FLUTE',20,25,2)
p.txt(38,171,'GENTLY',20,24,2);p.txt(450,171,'3 / 4',23,28)
# Five engraved staff lines and two barlines.
for y in (226,242,258,274,290):p.line([(32,y),(608,y)],1,2)
for x in (306,589,598):p.line([(x,226),(x,290)],1,2)
# Treble clef drawn from an angular ribbon and a native arc curl.
p.poly([(79,204),(95,183),(105,194),(101,217),(75,246),(64,265),(69,284),(89,291),(106,278),(104,263),(94,254),(80,260),(78,271),(88,278),(94,270),(87,267),(90,263),(97,269),(95,279),(82,282),(72,274),(72,262),(88,241),(107,219),(113,198),(106,182),(95,176),(85,183),(79,200)],1)
p.line([(91,195),(101,304)],1,3);p.circle(94,308,7,1)
p.txt(128,249,'3',21,28);p.txt(128,285,'4',21,28)
# Quarter notes with polished slanted heads; the last pair is beamed.
for x,y in [(183,274),(230,258),(277,242),(356,250),(410,266),(517,242),(559,234)]:
    p.poly([(x-10,y+2),(x-7,y-5),(x+5,y-7),(x+11,y-2),(x+7,y+5),(x-5,y+7)],1)
    p.line([(x+10,y),(x+10,y-57)],1,3)
p.poly([(527,185),(569,177),(569,185),(527,193)],1)
p.txt(188,337,'p',26,31,2)
p.arc((351,326),(432,348),(558,320),2)
p.center(320,418,'A SMALL EVENING AIR',21,28,2)
p.line([(206,443),(434,443)],3,2)
p.save()
