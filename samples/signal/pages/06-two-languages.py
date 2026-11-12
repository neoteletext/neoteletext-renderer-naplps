import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page,label
p=Page('06-two-languages',['efe7cf','153f50','288b9a','2f677e','d86c49','e7b24e','f8edca','7eb6ad','bb503c','9abca7','d3c59f','41606b','d99a68','b5d3ba','7b8e85','f4d9a4'])
p.text(32,92,'ONE BIRD.',31,42,1)
p.text(32,139,'TWO LANGUAGES.',25,34,1)
p.text(34,169,'THE MOSAIC AND THE VECTOR',9,13,3,False)
p.line([(320,202),(320,394)],10)
def oval(cx,cy,rx,ry,n=32):return [(cx+rx*math.cos(i*2*math.pi/n),cy+ry*math.sin(i*2*math.pi/n)) for i in range(n)]
shapes=[(1,[(42,123),(13,207),(68,176),(87,140)]),
        (2,oval(80,124,42,58)),(4,oval(96,137,23,44)),
        (2,oval(103,58,32,30)),(5,[(128,53),(187,69),(129,74)]),
        (6,[(115,77),(131,76),(112,110),(94,104)]),
        (3,[(67,89),(103,112),(83,170),(56,141)]),
        (1,oval(118,54,4,4,12)),(6,oval(119,53,1,1,8)),
        (1,[(81,173),(84,173),(84,193),(81,193)]),
        (1,[(99,174),(102,174),(102,193),(99,193)]),
        (1,[(0,193),(190,193),(190,198),(0,198)])]
def inside(x,y,pts):
    hit=False
    for a,b in zip(pts,pts[1:]+pts[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    return hit
# Native 2x3 G3 mosaics, layered in foreground-only colour mode.
for c in range(1,7):
    for row in range(9):
        codes=[]
        for col in range(12):
            code=0x20
            for j,bit in enumerate((1,2,4,8,16,64)):
                x=col*16+(j%2)*8+4;y=row*24+(j//2)*8+4
                ink=0
                for colour,pts in shapes:
                    if inside(x,y,pts):ink=colour
                if ink==c:code|=bit
            codes.append(code)
        p.mosaic(48.125,202.8+(row+1)*22.2,codes,18.125,22.2,c)
p.text(48,423,'01 / SIX BLOCKS',9,13,1,False)
p.text(360,423,'02 / ONE OUTLINE',9,13,1,False)
label(p,6,'TWO WAYS OF SEEING   /   KINGFISHER',1)
p.wait(18,'mosaic')
for c,pts in shapes:p.poly([(x*1.125+360,y*.925+202.8) for x,y in pts],c)
p.wait(18,'vector')
p.save()
