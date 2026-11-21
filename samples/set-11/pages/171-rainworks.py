from _drawing import Encoder, Plate, save, xy, Y_SCALE

META = dict(title='Rainworks', purpose='A weather foundry releases its first artificial rain.',
            style='Sea-green industrial frieze with copper pressure vessels',
            techniques=['relative macros', 'native circles', 'wide pels', 'WAIT', 'stroke text'],
            animated=True)


def build():
    p = Plate('103c43 eaffdd 23606a 2a7c77 5ab497 9cdab7 773957 b36569 f7ac88 fbd1a0 092b36 154b57 367979 bce9cb')
    p.rect(0, 104, 640, 238, 2)
    p.rect(0, 352, 640, 128, 10)
    for y in [101, 114, 331, 344]:
        p.rect(0, y, 640, 5, 3)
    p.line([(0,137),(602,137),(623,157),(623,275),(640,291)], 10, 15)
    p.line([(0,134),(602,134),(626,157),(626,275),(640,291)], 12, 4)
    p.line([(0,278),(640,278)], 10, 10)
    p.line([(38,157),(55,173),(55,240),(72,255),(578,255),(601,230),(601,179)], 10, 13)
    p.line([(38,157),(55,173),(55,240),(72,255),(578,255),(601,230),(601,179)], 4, 4)
    for x in (72,183,294,405,516):
        p.line([(x,248),(x,218),(x+27,200)], 10, 9)
        p.line([(x,246),(x,219),(x+27,200)], 4, 3)
        p.rect(x-6,243,12,10,5)
    for x, radius, pressure in [(100,35,-6),(211,39,2),(322,51,8),
                                (433,39,0),(544,34,-3)]:
        if x == 322:
            p.rect(x-57,143,114,186,12)
        p.line([(x,137),(x,172)], 10, 12)
        p.rect(x-12,147,24,7,4)
        p.rect(x-12,158,24,5,12)
        p.line([(x-39, 308), (x-39, 194), (x, 151), (x+39, 194), (x+39, 308)], 10, 8)
        p.disc(x, 211, radius, 6)
        p.disc(x-5, 205, radius*.84, 7)
        p.disc(x-10, 198, radius*.58, 8)
        p.disc(x-15, 191, radius*.27, 9)
        # Wrap the equator in a flange with visible fasteners.
        p.line([(x-radius*.92,207),(x-radius*.55,219),(x+radius*.50,223),
                (x+radius*.93,215)], 6, 7)
        p.line([(x-radius*.92,206),(x-radius*.55,217),(x+radius*.50,221),
                (x+radius*.93,214)], 9, 2)
        for dx, dy in [(-.61,216),(-.24,220),(.20,221),(.60,219)]:
            p.disc(x+dx*radius,dy,2,13)
        p.disc(x+21,228,10,10)
        p.disc(x+21,228,7,9)
        p.line([(x+21,228),(x+25+pressure*.3,225-pressure*.4)], 6, 2)
        p.line([(x, 249), (x, 270), (x+17, 287), (x+17, 316)], 5, 8)
        lip = 29 if x == 322 else 18
        p.poly([(x+17-lip,315),(x+17+lip,315),(x+12+lip,330),(x+22-lip,330)], 4)
        p.line([(x+22-lip,329),(x+12+lip,329)], 5, 2)
    p.poly([(0,451),(103,409),(554,409),(640,447),(640,480),(0,480)], 11)
    p.poly([(0,465),(110,416),(550,416),(640,459),(640,480),(0,480)], 0)
    p.line([(0,451),(103,409),(554,409),(640,447)], 12, 3)
    p.line([(17,470),(127,425),(538,425),(617,457)], 11, 2)
    # The catchment ends in a grated channel in the foreground.
    p.poly([(249,480),(281,458),(374,455),(418,480)], 10)
    p.line([(250,478),(283,459),(374,456),(417,478)], 12, 4)
    p.line([(272,480),(294,464),(362,462),(393,480)], 4, 2)
    for x in range(294,371,11):
        p.line([(x,479),(x-2,465)], 2, 3)
    for x in (137,246,356,468,579):
        p.disc(x,335,3,10)
        p.disc(x,334,1.5,13)
    p.title(38, 76, 'RAINWORKS', 1, 29, 42)

    # Change G3 from mosaics to local macros for the repeating drops.
    p.data.extend(b'\x1b/z')
    drop = Encoder()
    drop.cmd(0x35, xy(3/640, -6/Y_SCALE) + xy(-3/640, -4/Y_SCALE)
             + xy(-3/640, 4/Y_SCALE) + xy(3/640, 6/Y_SCALE))
    p.macro(0x21, drop)
    p.wait(10)
    for x, drift, depth in [(117,-9,-5),(228,8,4),(339,0,8),(450,-8,1),(561,10,-6)]:
        if x == 339:
            p.poly([(323,349),(349,349),(347,369),(352,389),(369,409),
                    (359,419),(338,420),(326,412),(307,421),(318,392),(324,367)], 4)
            p.poly([(329,350),(342,350),(340,373),(344,390),(356,409),
                    (341,415),(337,405),(322,411),(329,383)], 5)
            p.line([(332,350),(331,381),(326,397)], 13, 3)
            p.line([(343,374),(346,391),(354,403)], 13, 2)
            for x0,y0,w in [(309,416,21),(353,417,27),(335,426,42),(335,435,63)]:
                p.poly([(x0-w,y0+2),(x0-w*.40,y0-3),(x0+w*.42,y0-2),
                        (x0+w,y0+1),(x0+w*.62,y0+4),(x0-w*.46,y0+5)], 5)
                p.line([(x0-w*.52,y0+2),(x0,y0+4),(x0+w*.64,y0+1)], 0, 2)
            p.poly([(280,439),(321,435),(380,440),(368,455),(298,459)], 12)
            p.line([(286,442),(321,439),(369,444)], 5, 2)
            p.line([(292,449),(327,446),(367,448)], 4, 2)
            p.line([(307,456),(332,451),(364,453)], 5, 2)
            continue
        for dx, y, ink in [(0,348,5),(-8,365,4),(7,370,13),(-15,388,5),
                           (0,393,4),(15,402,5),(-23,413,4),(-7,420,13),(25,424,4)]:
            p.pos(x+dx+drift*(y-348)/76, y+depth*(y-348)/76)
            p.color(ink)
            p.data.extend(b'\x1d\x21')
        for dx,y,width in [(-16,438,21),(12,431,16),(0,450,35)]:
            cx, cy = x+dx+drift, y+depth
            p.line([(cx-width,cy),(cx-width*.62,cy+4),(cx+width*.45,cy+5),
                    (cx+width,cy+1)], 4, 2)
            p.line([(cx-width*.48,cy-2),(cx,cy-4),(cx+width*.55,cy-2)], 12, 2)
        p.line([(x+drift-7,434+depth),(x+drift,438+depth),
                (x+drift+8,431+depth)], 13, 2)
    return p


if __name__ == '__main__':
    save(__file__, build)
