import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
from encoder import xy
p=Art('041-green-fingers',palette('e4c04b','20282b','fff6dc','60aaa5','d85946','b2b299'))
p.txt(20,57,'GREEN FINGERS',31,38,1)
# Genuine downloaded halftone pattern, tiled behind the actors.
mask=bytes([0x2f])+xy(.18,.18)+xy(.32,0)
p.texture_mask(mask,14)
for i in range(3):
    x=16+i*208
    p.rect(x,85,192,318,2);p.line([(x,85),(x+192,85),(x+192,403),(x,403),(x,85)],1,5)
    p.texture(4);p.rect(x+5,268,181,129,5);p.texture()
    p.line([(x+5,356),(x+185,356)],1,3)
    # Speech balloon, with a different speaker in the last frame.
    p.rect(x+15,103,163,90,1);p.rect(x+19,107,155,82,2)
    tail=x+42 if i<2 else x+148
    p.poly([(tail,188),(tail+18,188),(tail+8,214)],1)
    if i==0:p.center(x+96,159,'GROW.',22,29,1)
    elif i==1:p.center(x+96,159,'PLEASE?',21,29,1)
    else:
        p.center(x+96,140,'MORE',23,26,1);p.center(x+96,174,'SUN.',23,26,1)
    # Tin gardener.
    rx=x+53
    p.rect(rx-26,241,54,46,1);p.rect(rx-21,246,44,36,3)
    p.rect(rx-21,291,44,45,3);p.rect(rx-23,291,48,5,1)
    for ex in (-10,12):p.rect(rx+ex,256,6,8,1)
    p.line([(rx,240),(rx,227)],1,3);p.circle(rx,224,5,4)
    for dx in (-14,14):p.line([(rx+dx,335),(rx+dx,356),(rx+dx+9,356)],1,4)
    p.line([(rx+23,302),(rx+46,315)],1,4)
    # Patient plant, growing in the wrong conditions.
    px=x+145;p.poly([(px-18,336),(px+18,336),(px+12,357),(px-12,357)],4)
    p.line([(px,337),(px,301)],1,3)
    for dx,dy in [(-17,311),(16,303)]:p.poly([(px,324),(px+dx,dy),(px+dx,dy+15)],3)
    if i==2:
        p.circle(x+154,232,20,0)
        for dx,dy in [(0,-32),(30,0),(-27,0),(20,-24)]:p.line([(x+154+dx*.75,232+dy*.75),(x+154+dx,232+dy)],1,3)
        p.line([(rx+23,302),(x+152,264),(x+152,252)],1,3)
p.txt(21,453,'A LITTLE LIGHT HELPS.',27,32,1,True)
p.save()
