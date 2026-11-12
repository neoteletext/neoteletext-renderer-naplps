import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page
p=Page('05-form',['efece2','202726','d8332f','c2c3b9','9d9e96','dedbd1','4f5650','b05a49','e5c4ad','d9cbb7','acb8af','7f9086','f7f1de','bbb3a5','6a706a','dbad8b'])
p.text(32,33,'SIGNAL / 05',8,12,1,False)
p.text(406,33,'STUDIES IN TRANSMISSION',8,12,1,False)
p.text(27,221,'FORM',185,172,1)
p.text(34,261,'FOLLOWS FREQUENCY.',17,24,1,False)
p.rect(34,284,569,12,2)
p.text(27,425,'05',103,128,3,False)
p.text(272,334,'A language of points.',13,20,1)
p.text(272,365,'A picture is a sequence of decisions:',9,14,1)
p.text(272,386,'where to begin, when to turn,',9,14,1)
p.text(272,407,'how much to leave unsaid.',9,14,1)
p.text(34,458,'NORTH AMERICAN PRESENTATION LEVEL PROTOCOL SYNTAX',8,12,1)
p.text(552,458,'1983',10,14,2,False)
p.save()
