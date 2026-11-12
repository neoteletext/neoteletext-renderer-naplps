import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('079-fox-ridge','e9e4c9 704e33 b49a6e 3f7462 b64b31 93bbb5 f9f1d6')
# Contours: offset, irregular nested forms around two hills.
for j in range(11):
    rx=35+j*24;ry=25+j*17
    pts=[]
    for k in range(31):
        a=k*2*math.pi/30
        pts.append((290+rx*math.cos(a)+13*math.sin(3*a+j*.12),245+ry*math.sin(a)+10*math.sin(2*a)))
    p.line(pts,2 if j%3 else 1,1.5)
# Creek through the contour valleys.
p.line(bez((512,100),(342,219),(561,299),(432,429),28),5,5)
trail=[(82,389),(156,347),(188,306),(252,295),(291,241),(355,211),(381,159),(443,125),(485,202),(462,282),(373,338),(257,363),(156,397),(82,389)]
p.texture(line=2);p.line(trail,4,4);p.texture()
for x,y in [(82,389),(291,241),(443,125),(485,202),(462,282),(373,338),(257,363),(156,397),(82,389)]:circle(p,x,y,7,4)
p.rect(15,14,383,84,6)
type(p,30,49,'FOX RIDGE',32,39,1)
type(p,31,82,'LOOP / 8.4 km / 3 hr',21,27,1)
p.rect(19,425,602,42,6)
type(p,31,457,'START',21,27,4)
type(p,192,457,'CONTOUR 20 m',20,26,1)
type(p,610,457,'N',25,31,1,'right')
p.line([(596,421),(596,386),(587,401),(596,386),(605,401)],1,2)
p.rect(422,74,197,37,6);type(p,447,103,'1260 m',26,31,1)
p.rect(25,332,116,32,6);type(p,34,359,'PARK',24,29,1)
finish(p,79,'Fox Ridge Loop','Hiking trail map','Topographic contours and dashed red route',['contour polylines','dashed line texture','native points'], 'Warm brown contours surround a crooked red hiking loop beside a blue-green creek. Large trail endpoints, summit elevation and a simple north arrow carry the practical information. Paper label patches keep names legible above the contour field; the native dashed path uses an explicit logical pel.')
