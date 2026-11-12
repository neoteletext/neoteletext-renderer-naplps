import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('052-household-budget',palette('f2e9d8','3a4850','d29483','e7c66d','8fbaa7','95aabf','fff6e3'))
p.txt(27,57,'WHERE IT GOES',34,42,1)
p.txt(29,100,'A HOUSEHOLD OF TWO',23,28,1)
# Native filled arcs provide the curved edges; triangles join each chord to centre.
cx=191;cy=281;rx=134;ry=rx*614.4/640
start=-90
for share,c in [(40,2),(25,3),(20,4),(15,5)]:
    end=start+share*3.6
    pt=lambda a:(cx+rx*math.cos(math.radians(a)),cy+ry*math.sin(math.radians(a)))
    a,m,b=pt(start),pt((start+end)/2),pt(end)
    p.arc(a,m,b,c,True);p.poly([(cx,cy),a,b],c)
    # A fine paper seam makes each allocation distinct.
    p.line([(cx,cy),a],6,2)
    start=end
for i,(name,amount,c) in enumerate([('HOUSING','40% / $960',2),('FOOD','25% / $600',3),('BILLS','20% / $480',4),('SAVING','15% / $360',5)]):
    y=167+i*77
    p.circle(378,y-12,9,c)
    p.txt(401,y,name,25,30,1)
    p.txt(372,y+33,amount,22,27,1)
p.txt(30,469,'$2,400 / MONTH',28,35,1)
p.save()
