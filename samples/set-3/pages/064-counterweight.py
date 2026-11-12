import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('064-counterweight','eeeada 111413 d83222 f2c72e 20559a')
p.rect(0,0,640,480,1)
for x,y,w,h,c in [(0,0,153,96,0),(165,0,475,96,2),(0,108,153,246,0),(165,108,304,246,0),(481,108,159,246,0),(0,366,153,114,4),(165,366,304,114,0),(481,366,159,114,3)]:p.rect(x,y,w,h,c)
type(p,185,177,'BALANCE',31,39,1)
type(p,185,220,'STUDIES IN',20,26,1)
type(p,185,254,'COLOUR',26,34,1)
type(p,185,451,'FORM BUREAU / 04',19,25,1)
finish(p,64,'Balance','Modern design seminar announcement','De Stijl asymmetric primary planes',['rectangles','negative space','stroke typography'], 'A heavy black structural grid holds unequal planes of vermilion, cobalt and yellow. The seminar copy occupies the open central white field; the offset blue and yellow weights prevent a symmetric poster. No decorative footer or shared collection furniture is used.')
