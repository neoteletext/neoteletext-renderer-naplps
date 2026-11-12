import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('055-solar-order',palette('0b1424','f0e5c5','f1bf58','a99c8c','d2ae73','6baac5','bb6a4d','b99b7b','ddd0a2','8cbcb6','4b6b9f','293b53'))
p.txt(25,54,'THE SOLAR SYSTEM',31,38,1)
p.txt(26,92,'FROM THE SUN, OUTWARD',22,27,1)
# Orbit arcs sweep up from an off-screen solar centre.
for r in (160,225,290,355,420,485,550,615):
    p.circle(-25,279,r,11,False)
p.circle(-38,279,111,2)
p.txt(7,288,'SUN',22,28,0)
planets=[(107,5,3),(171,9,4),(235,11,5),(299,8,6),(373,31,7),(463,25,8),(539,17,9),(606,16,10)]
for x,r,c in planets:p.circle(x,279,r,c)
# Jupiter's belts and Saturn's ring stay recognisable without tiny texture.
for y in (264,276,290):p.line([(349,y),(395,y)],4,4)
p.arc((422,281),(457,302),(505,274),8)
p.arc((505,274),(467,259),(422,281),8)
for x,y,s,c in [(107,151,'MERCURY',3),(235,198,'EARTH',5),(373,151,'JUPITER',7),(539,198,'URANUS',9)]:
    p.center(x,y,s,20,25,1);p.line([(x,y+9),(x,242 if x==373 else 258)],c)
for x,y,s,c in [(171,353,'VENUS',4),(299,397,'MARS',6),(463,353,'SATURN',8),(557,427,'NEPTUNE',10)]:
    p.center(x,y,s,20,25,1)
    anchor=606 if s=='NEPTUNE' else x
    p.line([(anchor,306),(anchor,y-33),(x,y-33)],c)
p.txt(25,470,'ORDER ONLY / SIZES & GAPS VARY',20,24,1)
p.save()
