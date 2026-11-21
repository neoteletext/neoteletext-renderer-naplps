from _drawing import Plate, save

META = dict(title='Umbra Loom', purpose='A train of orbital shuttles draws ribbons of light off a dark star.',
            style='Sweeping rose filaments against a cropped aubergine star',
            techniques=['native circles', 'native arcs', 'linework', 'filled polygons', 'BLINK', 'stroke text'],
            animated=True)


def build():
    p = Plate('1c102c fff0f5 291738 432247 642c58 944273 cf6092 ff9aa7 ffd198 9f6699 713b68 ee79a3 503352 c390ae 7b345f 381d40')
    for radius, ink in [(227, 2), (210, 3), (195, 4), (180, 5), (166, 6), (151, 0)]:
        p.disc(56, 295, radius, ink)
    for radius, ink in [(142,2),(130,3)]:
        p.color(ink).pel(2)
        p.arc((4,295-radius),(63,295-radius),(155,295-radius*.55))
    # Offset shells and irregular prominences give the limb a turbulent edge.
    for points, ink, width in [
        ([(0,142),(32,130),(63,135),(87,143),(108,160)], 11, 3),
        ([(2,173),(22,167),(46,170),(69,181),(90,197),(113,225)], 14, 5),
        ([(0,111),(32,101),(72,104),(104,116),(145,153)], 15, 5),
        ([(137,210),(148,224),(154,247),(162,264),(162,292)], 14, 5),
        ([(185,249),(194,267),(199,294),(192,323),(190,345)], 7, 2),
        ([(209,299),(219,320),(219,347),(207,373),(182,398)], 14, 5),
        ([(172,364),(160,394),(139,415),(112,428),(86,435)], 7, 2),
        ([(151,421),(124,445),(81,457),(43,455),(0,448)], 14, 3),
    ]:
        p.line(points, ink, width)
    for x,y,w in [(27,149,27),(111,183,35),(164,239,24),(174,364,26),(119,417,34)]:
        p.color(14).pel(4)
        p.arc((x,y),(x+w*.52,y-16),(x+w,y+6))
        p.color(7).pel(2)
        p.arc((x+3,y),(x+w*.5,y-11),(x+w-4,y+2))
    for x,y,r in [(270,89,2),(390,56,1.5),(554,229,2),(505,290,1.5),
                  (323,374,2),(592,351,2),(264,416,1.5),(596,150,1.5)]:
        p.disc(x,y,r,13)
    # Each ribbon leaves the limb on its own tangent.
    for x, y, s, source, bend in [
        (292,335,.72,(207,347),(242,351)),
        (372,258,.88,(207,269),(267,284)),
        (456,180,1,(181,201),(254,214)),
        (553,96,1.19,(124,157),(242,137)),
    ]:
        sx, sy = source
        p.color(5).pel(5)
        p.arc((sx-17,sy+14),(sx-8,sy-20),(sx+19,sy-11))
        p.color(7).pel(2)
        p.arc((sx-8,sy+13),(sx+1,sy-14),(sx+18,sy-9))
        bx, by = bend
        intake = x-33*s
        # Cross-sections keep the ribbon broad as it twists toward the guide.
        sections = [(sx-3,sy-8,2),(sx+7,sy-11,10),((sx+bx)*.5,(sy+by)*.5,10),
                    (bx,by,6),(bx+(intake-bx)*.30,by+(y-by)*.15,7),
                    (bx+(intake-bx)*.68,by+(y-by)*.53,11),(intake,y,10)]
        for low, high, ink in [(-1,1,5),(-.68,.85,6),(-.45,.16,11),(-.23,.03,7)]:
            p.poly([(cx,cy+half*low) for cx,cy,half in sections]
                   + [(cx,cy+half*high) for cx,cy,half in reversed(sections)], ink)
        p.line([(cx,cy+half*.86) for cx,cy,half in sections], 13, 2)
        p.disc(sx-11, sy+7, 4*s, 7)
        p.poly([(x-19*s,y-20*s),(x+56*s,y-35*s),(x+30*s,y+13*s),(x-33*s,y+18*s)], 10)
        p.poly([(x-19*s,y-20*s),(x+56*s,y-35*s),(x+14*s,y-7*s),(x-33*s,y+18*s)], 9)
        p.line([(x-33*s,y+18*s),(x+14*s,y-7*s),(x+56*s,y-35*s)], 8, 2)
        p.poly([(x-20*s,y-19*s),(x-36*s,y-9*s),(x-40*s,y+12*s),
                (x-30*s,y+19*s),(x-6*s,y+5*s)], 12)
        p.line([(x-34*s,y-8*s),(x-28*s,y-9*s),(x-31*s,y+13*s),
                (x-38*s,y+13*s)], 13, 3)
        p.poly([(x+10*s,y-8*s),(x+29*s,y-26*s),(x+43*s,y-29*s),
                (x+30*s,y-11*s)], 12)
        for offset in (-8, 3, 14):
            p.line([(x-38*s,y+offset*s),(x-25*s,y+(offset-3)*s),
                    (x-15*s,y+(offset-10)*s)], 13, 2)
        # The intake guides divide the ribbon and feed the exposed storage cells.
        p.line([(x-24*s,y+5*s),(x-4*s,y+7*s),(x+24*s,y-1*s),(x+38*s,y-14*s)], 12, 5)
        p.line([(x-24*s,y+5*s),(x-4*s,y+7*s),(x+24*s,y-1*s)], 7, 2)
        for dx, dy in [(4,7),(14,4),(24,1),(34,-5)]:
            p.poly([(x+(dx-4)*s,y+dy*s),(x+dx*s,y+(dy-4)*s),
                    (x+(dx+6)*s,y+(dy-5)*s),(x+(dx+3)*s,y+(dy+2)*s)], 8)
        p.disc(x+14*s, y-7*s, 4*s, 8)
    # The overseer carries a pair of reels and a heat shield behind the guide.
    p.poly([(510,91),(530,65),(578,49),(614,60),(597,92),(545,113),(518,107)], 12)
    p.poly([(530,65),(578,49),(614,60),(578,63),(537,80)], 9)
    p.poly([(542,94),(579,75),(607,68),(597,92),(546,109)], 10)
    p.line([(518,94),(538,96),(582,74),(607,67)], 13, 3)
    for x,y,r in [(544,83,12),(576,70,10)]:
        p.disc(x,y,r,15)
        p.disc(x,y,r-3,8)
        p.disc(x,y,r-6,5)
        p.disc(x,y,2,7)
    p.poly([(508,87),(522,79),(527,88),(517,104),(507,106)], 13)
    p.line([(510,92),(516,88),(520,89)], 8, 3)
    # A split horn turns the raw ribbon around a luminous capstan.
    for points in [[(487,83),(509,85),(525,96),(543,95),(548,86)],
                   [(488,110),(509,107),(524,98),(543,95)]]:
        p.line(points, 12, 8)
        p.line(points, 13, 3)
    p.disc(529,97,9,15)
    p.disc(529,97,6,11)
    p.disc(529,97,2.5,8)
    p.blink(11, 7, on=4, off=7)
    p.title(368, 454, 'UMBRA LOOM', 1, 23, 37)
    return p


if __name__ == '__main__':
    save(__file__, build)
