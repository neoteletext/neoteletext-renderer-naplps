import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('078-amber-road','e59d70 382a40 7a4051 a85851 c77859 efbc7d f6d894')
circle(p,446,172,88,6)
p.poly([(0,271),(96,226),(196,243),(330,213),(480,245),(640,190),(640,480),(0,480)],4)
p.poly([(0,305),(143,266),(308,305),(489,268),(640,295),(640,480),(0,480)],3)
p.poly([(0,386),(117,329),(241,344),(397,312),(559,347),(640,324),(640,480),(0,480)],2)
# Four paper-cut camel silhouettes cresting a continuous dune.
def camel(x,y,s):
    coords=[(-42,0),(-39,-22),(-26,-27),(-19,-46),(-5,-51),(8,-33),(24,-29),(29,-62),(38,-74),(52,-72),(55,-60),(44,-56),(41,-15),(29,-2),(27,32),(20,32),(18,1),(-16,1),(-26,33),(-33,33),(-28,-3)]
    p.poly([(x+a*s,y+b*s) for a,b in coords],1)
    p.line([(x-40*s,y-19*s),(x-50*s,y-3*s)],1,2)
    p.poly([(x-10*s,y-26*s),(x-5*s,y-44*s),(x+6*s,y-44*s),(x+13*s,y-24*s)],1)
    circle(p,x+2*s,y-52*s,6*s,1)
for x,y,s in [(139,340,.75),(279,348,.86),(434,343,1.0),(584,354,.7)]:camel(x,y,s)
p.line([(177,298),(237,321),(327,300),(386,314),(487,294),(553,325)],1)
p.poly([(0,414),(120,386),(277,398),(428,382),(640,407),(640,480),(0,480)],1)
type(p,30,67,'THE AMBER ROAD',37,45,1)
type(p,32,109,'DESERT CROSSINGS / AUTUMN',20,27,1)
type(p,610,456,'SEVEN NIGHTS UNDER STARS',20,26,5,'right')
finish(p,78,'The Amber Road','Desert caravan tour poster','Layered sunset paper-cut silhouettes',['layered polygons','silhouette','native circles'], 'Four camel riders cross rose and terracotta dunes beneath an oversized pale sun. Each silhouette is a single cut shape, with connecting reins and varied scale forming the caravan. The dark foreground absorbs the travel caption, leaving the warm sky open.')
