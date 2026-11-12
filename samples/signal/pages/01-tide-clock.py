import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page, label

p=Page('01-tide-clock',['18293b','f6e7c5','ed9471','c96667','704c68','304762','436078','2f777e','6eaaa2','f3c98b','101f30','aec4b1','dfad84','466d7a','34566a','b9d1b7'])
# Broad screen-print bands with a dark, quiet margin.
p.rect(24,62,592,348,4)
p.rect(24,62,592,77,3)
p.rect(24,62,592,40,2)
p.ellipse(408,152,45,45,9)
p.rect(24,208,592,202,6)
p.poly([(24,215),(95,189),(130,205),(171,173),(212,196),(266,183),(307,208),(380,194),(465,222)],5)
p.rect(24,245,592,165,7)
p.poly([(24,259),(90,242),(142,255),(197,235),(226,248),(270,238),(330,264),(380,260),(430,275),(24,296)],10)
# Colour-indexed lighthouse beams and water reflections.
p.poly([(498,187),(616,132),(616,221)],11)
p.poly([(498,187),(381,160),(381,207)],13)
p.poly([(471,270),(478,198),(496,198),(504,270)],1)
p.rect(477,185,20,15,10)
p.poly([(472,185),(487,174),(503,185)],10)
p.rect(484,190,7,8,9)
p.rect(482,219,7,13,10)
p.poly([(440,277),(465,259),(509,260),(533,278)],10)
# Quayside houses.
for x,y,w,h in [(57,239,32,26),(102,241,40,31),(153,246,24,24),(190,247,35,32)]:
    p.rect(x,y,w,h,3 if x%2 else 2)
    p.poly([(x-3,y),(x+w/2,y-14),(x+w+3,y)],10)
    p.rect(x+8,y+9,5,8,9)
p.line([(39,287),(257,287)],1,2)
p.line([(62,287),(62,325)],10,3)
p.line([(222,287),(222,322)],10,3)
# A cutter, with restrained sail and a fine mast.
p.poly([(285,322),(356,322),(344,337),(301,337)],10)
p.line([(321,321),(321,253)],1)
p.poly([(317,261),(291,313),(317,313)],1)
p.poly([(326,272),(348,314),(326,314)],12)
for j,(y,x,w) in enumerate([(293,443,45),(303,424,83),(316,450,57),(330,433,90),(346,457,39),(361,438,67),(379,459,44)]):
    p.rect(x,y,w,2,8 if j%2 else 14)
for x,y,w in [(40,345,107),(92,364,94),(248,373,108),(332,351,60),(361,390,57),(42,393,152)]:p.rect(x,y,w,2,8)
p.text(40,116,'TIDE',41,52,0)
p.text(40,164,'CLOCK',41,52,0)
p.text(41,194,'HARBOUR / 18:40',9,13,1,False)
label(p,1,'THE BLUE HOUR   /   PORT STUDY',1)
p.wait(12,'dusk')
for n in range(3):
    for i,c in [(7,'28646f'),(8,'a5c9b6'),(11,'f3c98b'),(13,'34566a'),(14,'6eaaa2')]:p.set_palette(i,c)
    p.wait(12,'beam-east' if n==0 else None)
    for i,c in [(7,'2f777e'),(8,'6eaaa2'),(11,'466d7a'),(13,'b9d1b7'),(14,'aec4b1')]:p.set_palette(i,c)
    p.wait(12,'beam-west' if n==0 else None)
p.save()
