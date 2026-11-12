from lib import *
p=Page('109-radio-dial',['161F21','E9E3C2','EF9F44','D14D3C','6D9C88','344345','B0BEA4','23302D'])
p.rect(12,15,616,451,5,False)
p.text(31,62,'NORTHLINE FM',31,38,1)
p.text(447,60,'STEREO',20,25,4)
p.rect(30,89,580,153,7)
p.rect(30,89,580,153,4,False)
for i in range(41):
    x=49+i*13.5;major=i%4==0
    p.line([(x,159 if major else 176),(x,199)],6,2 if major else 1)
    if major:p.center(139,str(88+i//2),18,23,1,x=x)
p.line([(49,211),(588,211)],4,2)
p.line([(419,99),(419,231)],3,4)
p.poly([(411,99),(427,99),(419,110)],2)
p.text(33,274,'MHz',20,24,4)
# Native separated mosaic speaker grille. No raster image is embedded.
p.data.extend(b'\x1bY')
for y in [328,352,376,400]:p.mosaic(34,y,[0x7f]*8,17,24,5)
p.data.extend(b'\x1bZ');p._text=None
p.text(198,304,'101.7',57,63,2)
p.text(500,298,'FM',28,34,4)
p.text(198,352,'21:00 - 23:00',23,28,1)
p.text(198,391,'THE NIGHT TRAIN',25,31,1)
p.text(198,429,'with Ivo Marsh',21,26,4)
p.text(33,455,'TUNED',20,24,2)
p.save()
