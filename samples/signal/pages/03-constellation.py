import sys,math,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page,label,polar
p=Page('03-constellation',['0d192e','ede7ce','33465f','66788b','c0a775','90bdc7','21344e','f2b874','f6f1dd','526b80','869da6','b8b6a1','1b2a43','667b8c','d6c793','283e57'])
p.text(32,105,'AFTER',29,38,1)
p.text(32,148,'DARK',29,38,1)
p.text(33,179,'AN IMAGINED SKY',8,12,4,False)
p.line([(33,204),(144,204)],4)
p.text(33,232,'Follow the light.',9,14,5)
p.text(33,254,'Find your own',9,14,5)
p.text(33,276,'way home.',9,14,5)
p.text(33,364,'NIGHT ATLAS',8,12,4,False)
p.text(33,385,'PLATE 003 / N',8,12,4,False)
cx,cy=391,239
p.ellipse(cx,cy,161,161,2,False,96)
p.ellipse(cx,cy,139,139,6,False,96)
p.ellipse(cx,cy,90,90,6,False,72)
p.line([(222,239),(560,239)],6)
p.line([(391,70),(391,408)],6)
for a in range(0,360,10):
    p.line([polar(cx,cy,157,a),polar(cx,cy,162 if a%30 else 168,a)],4 if a%30==0 else 2)
for a,s in [(-90,'N'),(0,'E'),(90,'S'),(180,'W')]:
    x,y=polar(cx,cy,182,a);p.text(x-4,y+5,s,9,13,4)
r=random.Random(83)
for _ in range(83):
    a=r.random()*360;rad=math.sqrt(r.random())*148
    x,y=polar(cx,cy,rad,a)
    p.rect(x,y,1,1,3 if r.random()<.7 else 5)
stars=[(351,127),(415,148),(336,197),(386,212),(433,239),(339,284),(384,310),(455,325),(476,189)]
for i,(x,y) in enumerate(stars):
    p.ellipse(x,y,3 if i in(0,4,7) else 2,3 if i in(0,4,7) else 2,8 if i in(0,4,7) else 1,n=12)
    if i in(0,4,7):
        p.line([(x-7,y),(x+7,y)],5)
        p.line([(x,y-7),(x,y+7)],5)
p.text(292,112,'THE VOYAGER',8,12,4)
p.text(446,354,'LANTERN',8,12,4)
p.text(462,171,'ECHO',8,12,4)
label(p,3,'STAR BY STAR   /   A CELESTIAL FICTION',1)
p.blink(8,5,4,12)
p.wait(8,'stars')
for i,(a,b) in enumerate([(0,1),(0,2),(2,3),(3,4),(4,1),(2,5),(5,6),(6,7),(4,8)]):
    p.line([stars[a],stars[b]],4)
    p.wait(3, 'first-routes' if i==3 else ('complete' if i==8 else None))
# Bring the stars over the fine constellation links again.
for i,(x,y) in enumerate(stars):p.ellipse(x,y,3 if i in(0,4,7) else 2.5,3 if i in(0,4,7) else 2.5,8 if i in(0,4,7) else 1,n=12)
p.save()
