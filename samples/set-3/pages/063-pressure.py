import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('063-pressure','f5f4eb 101111')
# Warp an orthogonal mesh outward around an off-center lens.
def warp(x,y):
    dx=x-350;dy=y-216;r=math.hypot(dx,dy);k=1+.53*math.exp(-(r/145)**2)
    return 350+dx*k,216+dy*k
for x in range(25,626,25):p.line([warp(x,y) for y in range(18,393,16)],1,2)
for y in range(18,394,25):p.line([warp(x,y) for x in range(25,626,16)],1,2)
p.rect(0,406,640,74,1)
type(p,24,455,'PRESSURE',36,42,0)
type(p,614,452,'OPUS 03',21,27,0,'right')
finish(p,63,'Pressure','Optical perception exhibition poster','Black-and-white bulging op-art mesh',['polylines','nonlinear grid'], 'A mathematically expanded mesh creates a convex lens without shading or colour. Its displaced centre makes the tension asymmetric, while a reversed black title strip gives the eye a stable baseline. Every grid line uses a two-pixel logical pel.')
