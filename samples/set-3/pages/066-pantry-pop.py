import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('066-pantry-pop','f3c833 22202b fdf0cf f3c833 df3c66 7f244c 44b8af 2f548d 17314f e39bbb d55230 8d2328 7b69b5 87bc45 28504a ffffff')
for i,(x,y) in enumerate([(0,0),(320,0),(0,240),(320,240)]):
    bg,body,shade=3+3*i,4+3*i,5+3*i
    p.rect(x,y,320,240,bg)
    p.ellipse(x+160,y+210,85,10,shade,n=16)
    p.rect(x+81,y+40,158,158,body)
    p.ellipse(x+160,y+42,79,15,2,n=20)
    p.ellipse(x+160,y+198,79,13,shade,n=20)
    p.rect(x+81,y+83,158,86,2)
    type(p,x+160,y+112,'LARK',27,30,1,'center')
    type(p,x+160,y+143,'SOUP',27,30,1,'center')
    p.line([(x+92,y+65),(x+228,y+65)],shade,2)
    type(p,x+160,y+187,'TOMATO',18,22,2,'center')
# Static palette revision: same indexed portrait structure, four final inkways.
p.set_palette(3,'f3c833');p.set_palette(6,'44b8af');p.set_palette(9,'e39bbb');p.set_palette(12,'7b69b5')
finish(p,66,'Pantry Pop','Fictional soup product portrait','Four-up pop-art screenprint',['palette redefinition','indexed colour variations','ellipses'], 'Four identical Lark soup cans are printed in separate three-entry colour families. Acid yellow, turquoise, pink and violet grounds clash with flat can inks. Palette entries are explicitly redefined at the end, demonstrating indexed recolouring without an animated reveal.')
