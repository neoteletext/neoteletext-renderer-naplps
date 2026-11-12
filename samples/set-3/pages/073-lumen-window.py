import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('073-lumen-window','100f20 e9cd79 2e6fab a33459 258477 734a97 d86a3f f0e0a2')
cx,cy=320,221
circle(p,cx,cy,201,1);circle(p,cx,cy,194,0)
# Twelve lobed jewel petals with thick unpainted leading between them.
for i in range(12):
    a=i*math.pi/6
    def q(r,t):return cx+r*math.cos(a+t),cy+r*math.sin(a+t)
    p.poly([q(78,-.12),q(152,-.20),q(184,-.10),q(190,0),q(184,.10),q(152,.20),q(78,.12)],2+i%5)
    p.poly([q(92,0),q(151,-.10),q(171,0),q(151,.10)],7 if i%3==0 else 1)
    p.poly([q(75,.20),q(126,.26),q(75,.32),q(55,.26)],3+i%3)
circle(p,cx,cy,64,1);circle(p,cx,cy,56,0)
p.poly(star(cx,cy,51,24,8),2)
circle(p,cx,cy,22,1)
p.poly(star(cx,cy,18,9,4),7)
type(p,320,458,'LUMEN / ROSE OF THE EAST',23,29,1,'center')
finish(p,73,'Lumen','Cathedral stained-glass window study','Jewel-coloured rose window with black leading',['radial polygons','native circles','eight-point star'], 'Twelve lancet petals surround an eight-point central star. Dark gaps act as lead came between ruby, teal, amber, sapphire and violet glass. A gold perimeter and repeated pale lozenges produce a bright outer ring without relying on hairline detail.')
