import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page,label,polar
p=Page('08-kaleidoscope',['132f39','f0e2bd','e7a650','d66c4e','b44d60','477f87','81aaa0','d4c593','2d555d','d78f64','ddc37f','9cb7a0','e2baa0','6e7473','ab806b','f4dcb1'])
p.text(32,87,'CHROMATIC',26,35,1)
p.text(33,112,'TWELVE TURNS OF THE SAME IDEA',8,12,7,False)
# Twelve oriented definitions of one wedge. Each is invoked twice; the
# second ring translates the same geometry radially, rather than resending it.
for k in range(12):
    a=k*30-90
    pts=[(0,0),polar(0,0,74,a-12),polar(0,0,127,a),polar(0,0,74,a+12)]
    f=Page();f.relpoly(pts)
    p.macro(0x21+k,f)
for k in range(12):
    a=k*30-90;x,y=polar(320,271,23,a)
    p.call(0x21+k,x,y,2+k%5)
for k in range(12):p.call(0x21+k,320,271,5 if k%2 else 7)
# An inner wheel, crisp spokes and small floating lozenges.
for k in range(12):
    a=k*30-90
    p.poly([polar(320,271,10,a),polar(320,271,57,a-11),polar(320,271,86,a),polar(320,271,57,a+11)],2+k%4)
    x,y=polar(320,271,167,a)
    p.poly([(x,y-3),(x+3,y),(x,y+3),(x-3,y)],7)
# Tiny inlaid diamonds add a second scale to the radial pattern.
for k in range(12):
    a=k*30-90
    p.poly([polar(320,271,39,a),polar(320,271,49,a-4),polar(320,271,61,a),polar(320,271,49,a+4)],1)
p.ellipse(320,271,14,14,0,n=24)
p.ellipse(320,271,5,5,1,n=12)
# Delicate corner brackets set the geometry into a quiet field.
for x,sgn in[(54,1),(586,-1)]:
    p.line([(x+sgn*33,169),(x,169),(x,202)],5)
    p.line([(x,342),(x,375),(x+sgn*33,375)],5)
p.text(46,276,'08',13,18,6,False)
p.text(555,276,'12',13,18,6,False)
label(p,8,'COLOUR IN MOTION   /   A PALETTE BLOOM',1)
p.wait(8,'ochre')
for n in range(4):
    for i,c in[(2,'81aaa0'),(3,'e7a650'),(4,'d66c4e'),(5,'b44d60'),(6,'477f87')]:p.set_palette(i,c)
    p.wait(8,'jade' if n==0 else None)
    for i,c in[(2,'b44d60'),(3,'81aaa0'),(4,'e7a650'),(5,'477f87'),(6,'d66c4e')]:p.set_palette(i,c)
    p.wait(8,'rose' if n==0 else None)
    for i,c in[(2,'e7a650'),(3,'d66c4e'),(4,'b44d60'),(5,'477f87'),(6,'81aaa0')]:p.set_palette(i,c)
    p.wait(8)
p.save()
