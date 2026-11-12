from _support import *
META=dict(number=31,title='The Aster cinema',purpose='Cinema listings with show times',style='Wine-red cinema marquee with gold bulbs and a few blinking accents',techniques=['macro','blink','native arcs'],animated=True)
def build():
    p=Page('031-aster-cinema',['321c2b','ffe8b7','e4ac56','8b5345','522b38','edca8b','b17e57','f6dda8','fff2ce'])
    p.rect(16,17,608,446,2,False);p.rect(31,34,578,414,3,False)
    m=Page();m.move(-4,0).cmd(0x2d,xy(8/640,0));p.macro(0x21,m)
    for x in range(35,612,38):p.call(0x21,x,18,2);p.call(0x21,x,463,2)
    for y in range(57,444,38):p.call(0x21,16,y,2);p.call(0x21,624,y,2)
    for x,y in [(35,18),(605,18),(35,463),(605,463)]:p.call(0x21,x,y,8)
    p.t(320,45,'THE ASTER',45,59,c=1,align='center')
    p.t(320,105,'CINEMA  /  FRIDAY',20,28,c=2,align='center')
    for y,title,time in [(151,'THE LAST LIGHT','6:10  8:40  /  PG'),(243,'SUMMER ARCADE','5:45  8:15  /  PG'),(335,'THE SILVER ROAD','7:00  9:20  /  M')]:
        p.t(320,y,title,28,38,c=1,align='center')
        p.t(320,y+39,time,23,31,c=5,align='center')
        if y<335:p.line([(104,y+82),(536,y+82)],3,1)
    p.t(320,413,'BOX OFFICE 555 0162',20,28,c=2,align='center')
    p.blink(8,2,on=5,off=10)
    return p
if __name__=='__main__':run(build)
