import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('070-void-patrol','090c26 70e3db f0cb43 e969a7 524c96 dce9e0')
# Each sprite is made of actual six-cell mosaic characters.
def sprite(x,y,rows,c,cell=10):
    rows=rows+['0'*len(rows[0])]*((-len(rows))%3)
    width=len(rows[0]);width+=width%2
    for j in range(0,len(rows),3):
        codes=[]
        for i in range(0,width,2):
            code=32
            for dy in range(3):
                for dx in range(2):
                    if i+dx<len(rows[j+dy]) and rows[j+dy][i+dx]=='1':code|=[1,2,4,8,16,64][dy*2+dx]
            codes.append(code)
        p.mosaic(x,y+(j+3)*cell,codes,2*cell,3*cell,c)
inv=['001000100','000101000','001111100','011010110','111111111','101111101','101000101','000101000','001000100']
for x,c in [(58,3),(274,1),(490,3)]:sprite(x,158,inv,c)
ship=['000010000','000111000','000111000','001111100','101111101','111111111','111010111','100010001','000000000']
sprite(270,310,ship,2,11)
points(p,[(30,137),(598,119),(206,244),(451,275),(153,318),(538,358),(63,423),(580,451),(380,294)],5,3)
p.rect(315,273,5,20,1)
type(p,320,84,'VOID',74,70,1,'center')
type(p,320,148,'PATROL',57,61,3,'center')
type(p,320,298,'1 PLAYER / 2 PLAYERS',21,27,5,'center')
type(p,320,452,'HIGH SCORE  028450',23,29,2,'center',False)
finish(p,70,'Void Patrol','Space shooter title screen','Arcade mosaic pixel art',['mosaics','large text fields','points'], 'Three chunky six-cell-mosaic invaders face a gold player ship beneath a cyan and magenta title. Sparse stars and one laser leave generous dark space. The title screen is complete as a still; no essential instruction blinks.')
