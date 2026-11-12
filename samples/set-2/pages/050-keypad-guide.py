import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
from encoder import xy
p=Art('050-keypad-guide',palette('ede9d7','303e45','899a95','b9c4b7','d27c49','fbf7e7'))
p.txt(24,51,'FIND YOUR WAY',32,40,1)
p.txt(25,93,'A GUIDE TO YOUR KEYPAD',22,27,1)
p.rect(24,116,282,344,2);p.rect(31,122,268,330,3)
# Download a small home glyph. The definition is drawn in unit coordinates.
body=bytes([0x37])+xy(.1,.48)+xy(.38,.38)+xy(.38,-.38)+xy(-.08,0)+xy(0,-.4)+xy(-.6,0)+xy(0,.4)
p.drcs(0x21,body,36,36)
for row,labels in enumerate(('123','456','789','*0#')):
    for col,s in enumerate(labels):
        x=45+col*82;y=137+row*76
        p.rect(x+3,y+4,66,58,1);p.rect(x,y,66,58,5)
        p.center(x+33,y+42,s,30,37,1)
        if s in ('4','6','0','#'):p.rect(x+5,y+48,54,5,4)
# Callouts align to useful key rows, without crossing the key labels.
p.txt(342,169,'4 BACK',27,33,1)
p.txt(342,217,'6 NEXT',27,33,1)
p.glyph(341,280,0x21,32,32,1);p.txt(388,279,'0 HOME',26,32,1)
p.txt(342,344,'# SELECT',26,32,1)
p.line([(311,362),(324,362),(324,327),(336,327)],4,3)
p.txt(342,410,'* HELP',26,32,1)
p.save()
