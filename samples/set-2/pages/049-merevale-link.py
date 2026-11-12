import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('049-merevale-link',palette('e4e9e7','214969','187c87','8faeae','c38253','f6f3df'))
# A single geometric M emblem with offset horizontal broadcast stripes.
p.poly([(39,167),(39,58),(81,58),(127,109),(172,58),(213,58),(213,167),(175,167),(175,112),(127,163),(78,112),(78,167)],1)
for i in range(4):p.rect(245,63+i*27,395-i*36,12,2 if i%2==0 else 3)
p.txt(38,249,'MEREVALE',48,58,1)
p.txt(40,303,'LINK',48,58,2)
p.txt(42,350,'YOUR REGIONAL INFORMATION NET',20,25,1)
p.rect(0,385,640,95,1)
p.txt(40,419,'GOOD EVENING, RIVER DISTRICT',20,25,5)
# Short finite reveal; final state always includes the complete welcome prompt.
p.wait(8,'welcome')
p.txt(40,463,'PRESS # TO BEGIN',25,31,5)
# The emblem and lettering share an entry: one deliberate brand-colour update.
p.set_palette(2,'227982')
p.save()
