from lib import *
p=Page('101-wine-label',['4F2031','F1E3BE','562D36','B3914D','D7C99F','8F7953'])
p.poly([(76,39),(564,39),(580,56),(580,424),(564,441),(76,441),(60,424),(60,56)],1)
p.poly([(87,53),(553,53),(566,66),(566,414),(553,427),(87,427),(74,414),(74,66)],3,False)
p.rect(82,62,476,356,2,False)
# Chateau engraving: hatching is confined to the vineyard slopes.
p.color(5).pel(3).texture(fill=2)
p.cmd(0x37,xy(158/640,(480-178)/Y_SCALE)+xy(165/640,51/Y_SCALE)+xy(160/640,-51/Y_SCALE))
p.texture()
p.rect(244,132,152,45,4)
p.poly([(230,133),(321,99),(409,133)],2)
for x in [252,375]:p.rect(x,100,14,77,2)
for x in range(273,368,23):p.rect(x,145,9,16,2)
p.rect(311,151,16,26,2)
p.line([(172,180),(471,180)],3,2)
# An heraldic shield and leaf scrolls.
p.poly([(302,80),(337,80),(334,97),(320,109),(306,97)],3)
p.poly([(311,84),(328,84),(326,94),(320,100),(314,94)],2)
p.data.extend(b'\x1b*|')
p.rawtext(320-measure('CHATEAU',25)/2,225,b'CH\x19\x43ATEAU',25,30,2)
p.center(279,'AUBREL',45,48,2)
# Serif terminals embellish the existing Microstar letter strokes.
xx=320-measure('AUBREL',45)/2
for ch in 'AUBREL':
    for gx,gy in {'A':[(1,2),(5,2)],'U':[(1,8),(5,8)],'B':[(1,2),(1,8)],'R':[(1,2),(1,8),(5,2)],'E':[(1,2),(1,8)],'L':[(1,8),(1,2)]}[ch]:
        # Proportional text aligns the leftmost glyph stroke to the cursor.
        px=xx+(gx-1)*45/8;py=279-gy*48/10
        p.line([(px-4,py),(px+4,py)],2,2)
    xx+=METRICS[ch]*45
p.line([(144,289),(496,289)],3,2)
p.center(333,'RESERVE / 1983',26,31,2)
p.center(376,'VAL DE LUNE',22,27,2)
p.center(407,'750 ml     12.5% vol',20,24,2)
p.save()
