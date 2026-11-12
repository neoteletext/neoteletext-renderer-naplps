import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder import Page,label,xy,Y_SCALE
p=Page('07-weather',['eee8d4','243f47','f2cd84','df9a5c','c86c4b','9bb8aa','6a918d','c1cdbb','faf0d2','8da29a','e1b36f','b65943','476d74','bfccba','7e8b79','c8b38d'])
p.text(32,88,'SOUTHERN',32,43,1)
p.text(32,132,'SEASON',32,43,1)
p.text(440,77,'THE WEATHER',9,13,1,False)
p.text(440,99,'ILLUSTRATIVE / 07',8,12,6,False)
p.line([(422,155),(422,399)],7)
coast=[(50,251),(58,227),(63,206),(82,203),(94,187),(115,184),(128,164),(144,171),(155,159),(171,167),(187,158),(208,166),(225,154),(243,160),(249,177),(266,186),(278,177),(289,153),(297,133),(305,158),(311,180),(328,201),(342,213),(351,233),(371,251),(378,278),(366,295),(359,321),(339,336),(326,353),(308,354),(298,345),(278,348),(267,333),(254,332),(247,317),(237,324),(219,321),(198,332),(174,336),(148,330),(134,314),(116,309),(103,292),(82,288),(69,273),(55,271)]
def clip(poly,y,above):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ia=a[1]>=y if above else a[1]<=y
        ib=b[1]>=y if above else b[1]<=y
        if ia:out.append(a)
        if ia!=ib:
            t=(y-a[1])/(b[1]-a[1]);out.append((a[0]+t*(b[0]-a[0]),y))
    return out
for low,high,c in [(120,213,4),(213,262,3),(262,310,10),(310,370,2)]:
    pts=clip(clip(coast,low,True),high,False)
    p.poly(pts,c)
p.poly(coast,1,False)
p.poly([(324,370),(337,375),(334,395),(323,399),(315,385)],5)
# Windward rain band, filled with the protocol's horizontal hatch.
p.texture(2)
p.poly([(342,229),(351,235),(371,254),(378,279),(365,294),(359,312),(346,308),(352,281),(344,254)],9)
p.texture()
# A reusable cloud and rain symbol, all coordinates relative to the caller.
f=Page()
f.relpoly([(0,0),(0,-7),(6,-11),(11,-9),(16,-16),(24,-16),(30,-10),(29,-6),(35,-5),(37,0)],8)
p.macro(0x21,f)
f=Page()
f.move(7,7).cmd(0x29,xy(-4/640,-7/Y_SCALE))
f.move(13,-7).cmd(0x29,xy(-4/640,-7/Y_SCALE))
f.move(13,-7).cmd(0x29,xy(-4/640,-7/Y_SCALE))
p.macro(0x22,f)
for x,y in [(89,247),(210,211),(329,280),(290,330)]:
    p.call(0x21,x,y);p.call(0x22,x,y,1)
for x,y in[(131,202),(279,246)]:
    p.ellipse(x,y,9,9,8,n=16)
    for dx,dy in[(-15,0),(15,0),(0,-15),(0,15)]:p.line([(x+dx*.78,y+dy*.78),(x+dx,y+dy)],8)
p.text(64,374,'AUSTRALIA',10,14,1,False)
p.text(64,394,'A SEASONAL IMPRESSION',8,12,6,False)
for y,city,temp,sub in[(164,'DARWIN','32','Warm rain'),(232,'SYDNEY','24','Coastal showers'),(300,'MELBOURNE','19','Cool change')]:
    p.text(442,y,city,9,13,1,False)
    p.text(550,y+4,temp,19,25,1,False)
    p.text(442,y+23,sub,9,13,6)
    p.line([(442,y+38),(600,y+38)],7)
for x,c,s in[(443,2,'18'),(493,3,'26'),(543,4,'34 C')]:
    p.rect(x,373,43,8,c);p.text(x,400,s,8,12,1)
label(p,7,'CLOUD, COUNTRY, COLOUR   /   NOT A LIVE FORECAST',1)
p.save()
