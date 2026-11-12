from lib import *
p=Page('108-festival-poster',['F6CB63','542B6D','F1E8AE','DF6441','6DAB8D','B24077','2A665D'])
# Flowing, nested full-height ribbons: no conventional margins or frame.
for i,c in enumerate([1,5,3,4,1]):
    edge=174-i*28
    pts=[(0,0),(edge+27,0)]
    pts += [(edge+31*math.sin(y/58+i*.55),y) for y in range(0,481,16)]
    pts += [(0,480)]
    p.poly(pts,c)
# Two exuberant flower rosettes in the ribbon.
for cx,cy,r in [(66,79,24),(72,390,25)]:
    for a in range(0,360,60):p.circle(cx+r*math.cos(math.radians(a)),cy+r*math.sin(math.radians(a)),18,0)
    p.circle(cx,cy,14,3)
# Each letter has its own baseline: a playful waveform in native stroke type.
for word,x,y,w in [('SUN',270,86,59),('SPIRAL',212,153,55)]:
    for i,ch in enumerate(word):p.text(x+i*w*.91,y+7*math.sin(i*1.15),ch,w,65,1)
p.center(202,'MUSIC FAIR / 26-28 JUN',21,26,6,x=401)
p.poly([(182,221),(611,213),(623,243),(191,251)],3)
p.center(248,'THE MOTH PARADE',26,32,2,x=403)
p.center(294,'GLASS CANOE',28,34,1,x=405)
p.center(335,'HONEY STATIC',27,33,5,x=405)
p.center(376,'ECHO MOUNTAIN',26,32,1,x=405)
p.center(419,'WILLOW FIELDS',26,32,6,x=405)
p.rect(173,443,467,37,1)
p.center(472,'3 DAYS / MEADOW PARK / $24',20,24,2,x=406)
p.save()
