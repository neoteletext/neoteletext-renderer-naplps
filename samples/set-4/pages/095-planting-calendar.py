from lib import *
p=Page('095-planting-calendar',['F4EBCF','31513B','82A36B','D79B4A','D7DABD','A14C38'])
p.rect(12,12,616,456,1,False)
p.text(25,52,'THE SEED CUPBOARD',27,34,1)
p.text(27,86,'A COOL-CLIMATE SOWING PLAN',20,24,1)
# Small seed packet ornament.
p.rect(553,29,47,56,4);p.line([(575,75),(575,43)],1,2)
p.poly([(575,58),(562,46),(560,56),(575,64)],2)
p.poly([(576,50),(587,39),(590,50),(576,58)],1)
months=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
# Two six-month tables keep every month name above the 32-column threshold.
for half,top in [(0,115),(1,282)]:
    for i in range(6):p.center(top+21,months[half*6+i],20,24,1,x=163+i*79)
    for r,name in enumerate(['PEAS','KALE','RADISH']):
        yy=top+34+r*38
        p.text(27,yy+27,name,20,24,1)
        for col in range(6):p.rect(125+col*79,yy,75,31,4)
# Southern temperate sowing windows, broad guide rather than a farm prescription.
sow=[{1,2,3,6,7,8},{1,2,3,4,7,8},{1,2,3,4,7,8,9,10}]
for r,ms in enumerate(sow):
    for m in ms:
        half=m//6;col=m%6;top=115 if half==0 else 282
        p.rect(126+col*79,top+35+r*38,73,29,2)
        p.circle(162+col*79,top+49+r*38,4,1)
p.rect(29,435,19,18,2);p.text(61,454,'SOW SEED',20,24,1)
p.text(307,454,'SOUTHERN GARDENS',20,24,1)
p.save()
