import sys,calendar
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('037-september',palette('f7f3e9','242c31','c83836','c9c5ba','eedad1'))
p.rect(0,0,640,99,2)
p.txt(28,66,'SEPTEMBER',36,45,0);p.txt(443,64,'1988',36,43,0)
# Binder rings.
for x in (92,548):p.rect(x,0,13,21,1);p.circle(x+6,23,9,0)
left=31;top=147;cw=82;ch=49
for i,s in enumerate(('MON','TUE','WED','THU','FRI','SAT','SUN')):p.center(left+i*cw+cw/2,133,s,20,24,2 if i>4 else 1)
for i in range(8):p.line([(left+i*cw,top),(left+i*cw,392)],3)
for j in range(6):p.line([(left,top+j*ch),(left+7*cw,top+j*ch)],3)
for row,week in enumerate(calendar.monthcalendar(1988,9)):
    for col,d in enumerate(week):
        if not d:continue
        x=left+col*cw+cw/2;y=top+row*ch+35
        if d in (8,17,25):p.rect(x-33,y-34,66,42,2)
        p.center(x,y,str(d),23,29,0 if d in (8,17,25) else (2 if col>4 else 1))
p.txt(31,434,'8 RENT    17 FAIR',22,27,2)
p.txt(31,469,'25 RIVERSIDE WALK',22,27)
p.save()
