import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('076-salt-afternoon','d5e1d4 234a64 67a6b4 a5c8c2 e4d3a0 d0ad78 49846d 90a877 f8edbf 3f6e94')
p.rect(0,162,640,144,3);p.rect(0,288,640,192,4)
r=random.Random(76)
# Independent groups of actual POINT operands; coarse logical pels are the brush.
for c,count,area,size in [(2,110,(0,165,640,285),5),(9,90,(0,184,640,301),4),(8,55,(0,270,640,323),5),(5,85,(0,316,640,480),5),(8,55,(0,317,640,480),4)]:
    x0,y0,x1,y1=area;points(p,[(r.uniform(x0,x1),r.uniform(y0,y1)) for _ in range(count)],c,size)
# A point-built tree, trunks, and a blue distant headland.
p.poly([(468,174),(531,142),(640,154),(640,181)],2)
for i in range(3):p.line([(55+i*11,340),(62+i*15,147)],5,6)
for c,count in [(6,75),(7,50),(1,25)]:
    pts=[]
    for i in range(count):
        a=r.random()*2*math.pi;rad=math.sqrt(r.random());pts.append((69+rad*100*math.cos(a),128+rad*67*math.sin(a)))
    points(p,pts,c,7)
p.poly([(359,256),(413,256),(402,265),(369,265)],1)
p.poly([(386,199),(386,250),(353,250)],8)
p.line([(387,193),(387,258)],1,2)
# Beach parasol and its loose dotted shadow.
p.line([(470,333),(470,412)],1,3)
p.poly([(421,340),(470,298),(518,340)],8)
p.poly([(449,340),(470,298),(489,340)],5)
points(p,[(r.uniform(438,510),r.uniform(411,423)) for _ in range(18)],5,5)
p.rect(284,28,327,91,8)
type(p,301,65,'SALT AFTERNOON',25,31,1)
type(p,302,100,'LOW TIDE / 16:40',20,25,1)
finish(p,76,'Salt Afternoon','Seaside art postcard','Pointillist coastal afternoon',['POINT','large logical pel','deterministic stippling'], 'More than five hundred native POINT marks scatter cool and warm pigment across sea, sand and a tree canopy. A tiny cream sail and striped parasol give the loose dots a readable scene. A pale upper-right card carries the title clear of the stippling.')
