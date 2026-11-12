import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('054-first-eighteen',palette('e5ecec','263c48','abc9b9','f2d591','97b8d0','748c98'))
p.txt(24,52,'THE FIRST 18',36,43,1)
p.txt(25,94,'PERIODIC TABLE / MAIN GROUPS',21,26,1)
for i,g in enumerate((1,2,13,14,15,16,17,18)):p.center(59+i*74,135,str(g),20,24,1)
rows=[[(0,1,'H',3),(7,2,'He',4)],[(0,3,'Li',2),(1,4,'Be',2),(2,5,'B',3),(3,6,'C',3),(4,7,'N',3),(5,8,'O',3),(6,9,'F',3),(7,10,'Ne',4)],[(0,11,'Na',2),(1,12,'Mg',2),(2,13,'Al',2),(3,14,'Si',3),(4,15,'P',3),(5,16,'S',3),(6,17,'Cl',3),(7,18,'Ar',4)]]
for r,row in enumerate(rows):
    for col,num,s,c in row:
        x=24+col*74;y=150+r*83
        p.rect(x,y,68,76,c)
        p.txt(x+6,y+25,str(num),20,23,1)
        p.center(x+34,y+66,s,29,35,1)
# Broad educational classes; B and Si are explicitly included with other elements.
for x,c,s in [(25,2,'METALS'),(222,3,'OTHERS'),(419,4,'NOBLE GAS')]:
    p.rect(x,421,16,29,c);p.txt(x+25,447,s,20,25,1)
p.save()
