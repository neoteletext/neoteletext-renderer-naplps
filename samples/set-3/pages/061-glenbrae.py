import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('061-glenbrae','e7ddbd 173e38 922f36 21344a bda35f 42715a f4ebd1 101f29')
p.rect(0,0,640,348,1)
# Overlapping threads: wide woven bands, fine opposing hatch, gold pinstripes.
for x in [28,206,384,562]:
    p.rect(x,0,51,348,3)
    p.texture(1);p.rect(x+6,0,38,348,5);p.texture()
    p.rect(x+64,0,22,348,2)
for y in [23,162,301]:
    p.texture(2);p.rect(0,y,640,49,3);p.texture()
    p.texture(3);p.rect(0,y+54,640,21,2);p.texture()
for x in [15,98,193,276,371,454,549,632]:p.rect(x,0,3,348,4)
for y in [10,91,149,230,288,340]:p.rect(0,y,640,3,4)
p.rect(0,349,640,8,7)
type(p,32,414,'GLENBRAE',39,47,1)
type(p,34,456,'CLAN WEAVE / HIGHLAND WOOL',20,25,1)
finish(p,61,'Glenbrae','Clan tartan swatch and wool identification','Woven Scottish textile',['hatching','overlapping textures','palette'], 'A full-width green sett is crossed by navy and wine bands, opposing native hatch directions and narrow brass threads. An unframed wool label anchors the lower edge; the fictional clan and large lettering read at terminal size.')
