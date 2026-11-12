import sys, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page,label
p=Page('02-botanical',['efe9d6','233e35','64765a','a5ad8a','d9dbc1','b2a478','8c7957','476353','f6f0df','d0c8ae','7c8b6b','364c3f','9b9e76','cecba8','eee5c8','867f67'])
p.rect(23,57,594,369,1,False)
p.rect(29,63,582,357,3,False)
p.text(44,93,'HERBARIUM',14,21,1,False)
p.text(500,92,'II',22,29,1)
p.line([(44,108),(596,108)],3)
# Curved rachis. The entire silhouette is original, algorithmically drawn.
def stem(t):return (224+55*t-34*t*t,389-254*t)
p.line([stem(i/40) for i in range(41)],1,2)
for side in (-1,1):
    for i in range(15):
        t=.10+i*.059+(0.012 if side>0 else 0)
        x,y=stem(t)
        length=(math.sin(t*math.pi)**.75)*122*(1.05 if side<0 else .87)*(1+.065*math.sin(i*2.7))
        ex=x+side*length; ey=y-21-length*(.28+.035*math.sin(i*1.8))
        vx,vy=ex-x,ey-y
        norm=math.hypot(vx,vy); nx,ny=-vy/norm,vx/norm
        # Saw-edged pinnae: small, changing teeth give the frond its engraved edge.
        pts=[(x,y)]
        for k in range(1,10):
            u=k/10; a=9*math.sin(math.pi*u)*(1 if k%2 else .48)
            pts.append((x+vx*u+nx*a,y+vy*u+ny*a))
        pts.append((ex,ey))
        for k in range(9,0,-1):
            u=k/10;a=8*math.sin(math.pi*u)*(1 if k%2 else .4)
            pts.append((x+vx*u-nx*a,y+vy*u-ny*a))
        if i%4==0:p.texture(1)
        p.poly(pts,1 if i%3 else 7)
        p.texture()
        # Native incremental diagonal, nearly one byte per three steps.
        p.scribble(x,y,vx/12,vy/12,[3]*12,2)
p.poly([(244,145),(238,122),(245,114),(251,128)],1)
# The small analytical detail is hatched with native TEXTURE.
p.ellipse(479,213,72,72,3,False)
p.texture(1)
p.poly([(443,235),(466,164),(492,174),(518,212),(473,252)],2)
p.texture()
p.line([(453,244),(486,177)],1,2)
for j in range(5):
    y=189+j*10
    p.line([(479-j*4,y),(495-j*2,y+6)],1)
p.text(433,306,'PINNA / x4',9,13,1,False)
p.line([(343,229),(398,229),(420,251)],2)
p.text(400,344,'Dryopteris',15,22,1)
p.text(400,371,'filix-mas',15,22,1)
p.text(400,390,'Woodland specimen',8,12,2)
p.text(45,405,'FIG. 02',8,12,2,False)
label(p,2,'A STUDY IN GREEN   /   NATURAL HISTORIES',1)
p.save()
