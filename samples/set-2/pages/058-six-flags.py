import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('058-six-flags',palette('d3ddd7','293f4a','fffdf4','d0363e','283e85','f4cf3f','1aaba8','151c20','286a9b'))
p.txt(24,55,'FLAGS OF SIX NATIONS',29,36,1)
p.line([(25,81),(613,81)],1,2)
w=170;h=w*2/3
# Japan, 3:2; disc diameter is three fifths of the height.
x=28;y=126;p.rect(x,y,w,h,2);p.circle(x+w/2,y+h/2,h*.3,3)
p.center(113,280,'JAPAN',22,27,1)
# France, 3:2, equal vertical bands.
x=235
for i,c in enumerate((4,2,3)):p.rect(x+i*w/3,y,w/3,h,c)
p.center(320,280,'FRANCE',22,27,1)
# Sweden, 16:10; cross divisions are 5:2:9 horizontally, 4:2:4 vertically.
x=442;sh=w*10/16;sy=y+(h-sh)/2
p.rect(x,sy,w,sh,8);p.rect(x+w*5/16,sy,w*2/16,sh,5);p.rect(x,sy+sh*.4,w,sh*.2,5)
p.center(527,280,'SWEDEN',22,27,1)
# Bahamas, 2:1, gold middle third and equilateral black hoist triangle.
x=28;by=330;bh=w/2
for i,c in enumerate((6,5,6)):p.rect(x,by+i*bh/3,w,bh/3,c)
p.poly([(x,by),(x+bh*math.sqrt(3)/2,by+bh/2),(x,by+bh)],7)
p.center(113,468,'BAHAMAS',22,27,1)
# Vietnam, 3:2, gold five-pointed star.
x=235;vy=316;p.rect(x,vy,w,h,3);p.star(x+w/2,vy+h/2,h*.3,5)
p.center(320,468,'VIETNAM',22,27,1)
# Czechia, 3:2, white over red, triangle reaches halfway across.
x=442;p.rect(x,vy,w,h/2,2);p.rect(x,vy+h/2,w,h/2,3)
p.poly([(x,vy),(x+w/2,vy+h/2),(x,vy+h)],4)
p.center(527,468,'CZECHIA',22,27,1)
p.save()
