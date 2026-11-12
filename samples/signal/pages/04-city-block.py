import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page,label
p=Page('04-city-block',['e9dfc6','26394b','d6c498','b9ad86','648f88','3d6f71','97b7a1','bc765e','814c50','e5ad7c','e1ca88','8ba4a0','f7e9bd','d8c9a6','b19e7a','26394b'])
p.text(32,89,'COMMON',33,43,1)
p.text(32,134,'GROUND',33,43,1)
p.text(405,82,'A SMALL CITY',9,13,1,False)
p.text(405,103,'BETWEEN TWO LIGHTS',8,12,1,False)
p.text(443,428,'DAY / NIGHT',8,12,1,False)
# Two window macros, one for each face. Their geometry is relative to the caller.
for num,points in [(0x21,[(0,0),(8,4),(8,13),(0,9)]),(0x22,[(0,0),(-8,4),(-8,13),(0,9)])]:
    frag=Page();frag.relpoly(points)
    p.macro(num,frag)
def iso(u,v,z=0):return 327+u-v,284+(u+v)*.48-z
p.poly([iso(-147,-111),iso(137,-111),iso(137,128),iso(-147,128)],2)
for v in(-80,-20,40,100):p.line([iso(-147,v),iso(137,v)],3)
for u in(-110,-50,10,70,130):p.line([iso(u,-111),iso(u,128)],3)
p.poly([iso(-145,145),iso(137,145),iso(137,163),iso(-145,163)],15)
p.poly([iso(153,-111),iso(171,-111),iso(171,163),iso(153,163)],15)
for u in range(-125,130,35):p.line([iso(u,154),iso(u+15,154)],12,2)
def building(u,v,w,d,h,cs):
    a,b,c,d0=[iso(*q) for q in[(u,v),(u+w,v),(u+w,v+d),(u,v+d)]]
    at,bt,ct,dt=[(x,y-h) for x,y in(a,b,c,d0)]
    # Back to front painter order.
    p.poly([d0,c,ct,dt],cs[1]);p.poly([b,c,ct,bt],cs[2]);p.poly([at,bt,ct,dt],cs[0])
    p.line([at,bt,ct,dt,at],1)
    for level in range(15,h-8,21):
        for off in range(9,w-6,17):
            x,y=iso(u+off,v+d,h-level);p.call(0x21,x,y,10)
        for off in range(9,d-6,17):
            x,y=iso(u+w,v+off,h-level);p.call(0x22,x,y,12)
    return at,ct
building(-102,-78,74,55,92,(6,4,5))
building(4,-76,66,56,145,(9,7,8))
building(-95,17,61,70,65,(9,7,8))
building(3,18,76,68,96,(6,4,5))
# Little roof garden and a solitary street tree.
x,y=iso(22,45,96)
p.rect(x-3,y-10,5,12,1);p.ellipse(x,y-17,11,10,4,n=16)
x,y=iso(-120,82)
p.line([(x,y),(x,y-25)],1,2);p.ellipse(x,y-31,12,13,5,n=16)
p.text(32,406,'04 / BLOCK SECTION',8,12,1,False)
label(p,4,'AN EXERCISE IN SHARED SPACE',1)
p.wait(20,'day')
for i,c in [(0,'182539'),(1,'e9dfc6'),(2,'354456'),(3,'495666'),(4,'36636b'),(5,'243f52'),(6,'6c938e'),(7,'754e5b'),(8,'4f384e'),(9,'b98271'),(10,'edbf6c'),(12,'ffe4a1'),(15,'101d2e')]:p.set_palette(i,c)
p.wait(20,'night')
p.save()
