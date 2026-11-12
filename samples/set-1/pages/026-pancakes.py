from _support import *
META=dict(number=26,title='Sunday pancakes',purpose='Pancake recipe with ingredients and method',style='Warm kitchen recipe card inside a red gingham border',techniques=['defined fill patterns','polygons','proportional text'],animated=False)
def build():
    p=Page('026-pancakes',['fff0ce','70402a','c56756','e0af69','c98a46','f2d697','eee0be','a05a31','edbb73','f8e7b9'])
    # A real repeating two-square NAPLPS fill mask, not manually drawn checks.
    p.cmd(0x23,b'\x40'+xy(24/640,24/Y_SCALE))
    p.color(1)  # MaskSurface treats entry zero as erasure, even on a light map.
    p.data.extend(b'\x1bDA\x0e')
    p.cmd(0x33,xy(0,0)+xy(.5,.5))
    p.cmd(0x33,xy(.5,.5)+xy(.499,.499))
    p.data.extend(b'\x1bE\x0e')
    p.texture(fill=4).rect(0,0,639,479,2).texture()
    p.rect(21,22,598,435,0)
    p.t(320,31,'SUNDAY PANCAKES',35,49,align='center')
    p.line([(43,92),(596,92)],2,2)
    p.t(45,112,'INGREDIENTS',22,31)
    for i,s in enumerate(['150g flour','1 egg','250ml milk','1 tsp sugar']):p.t(47,160+i*37,s,22,31)
    p.t(468,112,'MAKES 6',20,29,align='center')
    p.ellipse(464,280,121,70,6,n=24)
    for y,rx,ry in [(280,99,42),(263,94,41),(247,88,38)]:
        p.ellipse(464,y+8,rx,ry,4,n=24);p.ellipse(464,y,rx,ry,5,n=24)
    p.poly([(432,224),(465,218),(497,232),(506,255),(485,261),(477,290),(462,288),(456,257),(431,250)],7)
    p.poly([(454,221),(475,215),(490,224),(468,231)],0)
    p.t(45,343,'Mix. Rest for 10 minutes.',22,31)
    p.t(45,382,'Fry small rounds until golden.',22,31)
    p.t(595,423,'TURN ONCE  /  SERVE WARM',18,25,c=7,align='right')
    return p
if __name__=='__main__':run(build)
