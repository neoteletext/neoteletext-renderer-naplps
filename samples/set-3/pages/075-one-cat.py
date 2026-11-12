import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('075-one-cat','f1ede3 383b38 b27958')
# A single unbroken native incremental line, including eyes and whiskers.
path=bez((401,390),(556,422),(564,309),(474,342),23)
path+=bez(path[-1],(423,362),(459,415),(329,399),18)[1:]
path+=bez(path[-1],(212,398),(184,334),(226,270),18)[1:]
path+=bez(path[-1],(239,248),(241,220),(238,200),10)[1:]
path += [(223,122),(284,158),(340,151),(390,112),(396,201)]
path+=bez(path[-1],(431,242),(378,270),(361,278),15)[1:]
path+=bez(path[-1],(375,321),(382,367),(369,390),15)[1:]
path += [(343,390),(338,315),(312,355),(303,390),(277,390)]
path+=bez(path[-1],(290,343),(262,297),(273,275),15)[1:]
path += [(282,236),(301,229),(319,239),(338,226),(360,228),(375,220),(356,224),(338,226),(326,245),(319,251),(307,244),(319,239),(319,251),(320,263),(330,266),(341,260),(330,266),(320,263),(310,269),(299,266),(310,269),(320,263),(279,253),(254,251),(279,253),(320,263),(364,250),(392,245)]
# Quantized Bresenham walk packed three 2-bit instructions per byte.
coords=[(round(x/2),round(y/2)) for x,y in path]
codes=[];sx=sy=1;x,y=coords[0]
for tx,ty in coords[1:]:
    dx=tx-x;dy=ty-y
    ax=1 if dx>=0 else -1;ay=1 if dy>=0 else -1
    if dx and ax!=sx:codes += [0,1];sx=ax
    if dy and ay!=sy:codes += [0,2];sy=ay
    nx,ny=abs(dx),abs(dy);steps=max(nx,ny)
    for k in range(1,steps+1):
        hx=round(k*nx/steps)>round((k-1)*nx/steps)
        hy=round(k*ny/steps)>round((k-1)*ny/steps)
        codes.append((1 if hx else 0)|(2 if hy else 0))
    x,y=tx,ty
p.pel(2).scribble(coords[0][0]*2,coords[0][1]*2,2,2,codes,1)
type(p,40,63,'one cat.',31,39,1)
type(p,600,447,'ONE LINE / NO. 01',20,26,2,'right')
finish(p,75,'One Cat','Continuous-line cat portrait','Minimal warm-paper line art',['incremental lines','single continuous path','proportional text'], 'One uninterrupted incremental-line instruction traces a seated cat from the tail through the ears, paws, eyes and whiskers. A two-pixel step keeps the drawing compact and the mark visible at terminal resolution. Large paper margins and an understated copper caption preserve its restraint.')
