from _support import *
META=dict(number=28,title='Small ads',purpose='Classified ads column with one highlighted advertisement',style='Dense plum ink in ruled white boxes with one yellow display ad',techniques=['rules','proportional text','colour panels'],animated=False)
def build():
    p=Page('028-classifieds',['faf7f0','4e3850','e9c84d','ded7db','887686'])
    p.t(11,1,'SMALL ADS',38,52)
    p.t(626,20,'WED 18 NOV',19,27,align='right')
    ads=[(11,79,'CYCLE / $45','Blue 10-speed.','Call 555 0127.'),
         (11,207,'ROOM TO LET','Quiet riverside.','$60/wk. 555 0184.'),
         (11,335,'PIANO LESSONS','Beginners welcome.','555 0192, after 6.'),
         (324,79,'LOST / CAT','Ginger, white paws.','Reward. 555 0176.'),
         (324,207,'MARKET DAY','Sat 9-2 / Town Hall','Stalls: 555 0133.'),
         (324,335,'REPAIRS','Radios & small TVs.','555 0168. Free quote.')]
    for x,y,title,a,b in ads:
        if title=='MARKET DAY':p.rect(x,y,302,127,2)
        p.rect(x,y,302,127,1,False)
        p.t(x+10,y+7,title,22,30)
        p.line([(x+10,y+42),(x+292,y+42)],4,1)
        p.t(x+10,y+50,a,19,27)
        p.t(x+10,y+86,b,19,27)
    return p
if __name__=='__main__':run(build)
