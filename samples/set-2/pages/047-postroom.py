import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('047-postroom',palette('184e56','f1f1d7','83b8b4','153a44','c7d9c9','d5ac58'))
p.rect(0,0,640,62,3);p.txt(19,45,'POSTROOM',31,37,1)
p.rect(409,11,214,39,2);p.txt(429,42,'MAIL 04',25,29,3)
p.rect(13,79,151,343,3)
for y,s in [(123,'INBOX'),(187,'SENT'),(251,'DRAFT'),(315,'TRASH')]:
    if s=='INBOX':
        p.mode2(3,2);p.text(25,y,s,22,28,None,False)
    else:p.txt(25,y,s,22,28,2)
p.rect(180,79,447,343,1)
p.txt(196,111,'4 MESSAGES / 1 NEW',21,26,3)
rows=[('01 * LEO','08:42','FERRY TIMES'),('02   ADA','07:16','RE: SUNDAY LUNCH'),('03   MIRA','YEST.','THE NEW CATALOGUE'),('04   IVAN','YEST.','GARDEN ROSTER')]
for i,(name,when,subject) in enumerate(rows):
    top=125+i*72
    if i==0:p.rect(188,top,431,70,4)
    p.txt(198,top+27,name,21,25,3);p.txt(509,top+27,when,20,24,3)
    p.txt(219,top+57,subject,21,25,0)
    if i<3:p.line([(196,top+71),(610,top+71)],2)
p.rect(13,439,614,32,3)
p.mode2(1,3);p.text(24,465,'1 READ   2 REPLY   3 DELETE',22,26,None,False)
p.save()
