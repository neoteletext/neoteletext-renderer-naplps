import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('083-orbits-of-glass','272740 edd8b3 e4ac61 d87851 b95658 8e4c72 5a527b 3f697f 6e9b9a')
# Horizontally stepped sunset inks, interrupted by a ringed planet.
for i,c in enumerate([8,7,6,5,4,3,2]):p.rect(0,132+i*30,640,30,c)
# Elliptical orbit is intentionally polygonal; front half cuts across planet.
p.line([(382+192*math.cos(a),258+58*math.sin(a)-.37*192*math.cos(a)) for a in [math.pi+i*math.pi/30 for i in range(31)]],1,4)
circle(p,382,258,106,0)
circle(p,374,247,96,1)
circle(p,352,226,82,2)
p.line([(382+192*math.cos(a),258+58*math.sin(a)-.37*192*math.cos(a)) for a in [i*math.pi/30 for i in range(31)]],0,12)
p.line([(382+192*math.cos(a),258+58*math.sin(a)-.37*192*math.cos(a)) for a in [i*math.pi/30 for i in range(31)]],1,4)
# Small space traveller against the stripe field.
p.poly([(67,360),(78,300),(86,275),(92,302),(105,360)],0)
circle(p,86,265,8,0)
points(p,[(51,100),(580,66),(544,112),(144,166),(604,365),(238,365)],1,3)
type(p,24,54,'ORBITS OF',42,50,1)
type(p,24,111,'GLASS',57,65,1)
p.rect(0,392,640,88,0)
type(p,25,432,'MIRA SORN',31,39,1)
type(p,26,464,'A NOVEL / FAR HORIZON BOOKS',20,26,2)
finish(p,83,'Orbits of Glass','Fictional science-fiction paperback cover','1970s ringed planet and stripe gradient',['palette stripe gradient','native circles','elliptical polylines'], 'A huge ringed planet cuts through seven horizontal bands of muted sunset ink. The tiny traveller supplies scale beneath an oversized two-line title. A dark author strip closes the paperback cover; the stepped colours are palette bands, not a raster gradient.')
