from _drawing import Plate, save

META = dict(title='The Second Floor', purpose='Two surveyors meet across a reversal in gravity.',
            style='Blue and peach perspective cutaway',
            techniques=['filled polygons', 'native circles', 'wide pels', 'stroke text'],
            animated=False)


def build():
    p = Plate('122640 fff1df 274962 3a6c83 69b8bf 693957 ac606d e9957d fcc58e def8d7 102033 24536c 9d5367 4b7683 8199a1 f0a297')
    vanishing = (341, 240)
    for a, b, ink in [((0, 0), (640, 0), 5), ((640, 0), (640, 480), 2),
                      ((640, 480), (0, 480), 3), ((0, 480), (0, 0), 10)]:
        p.poly([a, b, vanishing], ink)
    for t in (.24, .43, .66, .88):
        left, right = 341*(1-t), 341+299*t
        top, bottom = 240*(1-t), 240+240*t
        depth = 22*t
        p.poly([(left,top),(right,top),(right-depth,top+depth),
                (left+depth,top+depth)], 11 if t < .5 else 12)
        p.poly([(right,top),(right,bottom),(right-depth,bottom-depth),
                (right-depth,top+depth)], 13)
    for t in (.12, .24, .43, .66, .88):
        left, right = 341*(1-t), 341+299*t
        top, bottom = 240*(1-t), 240+240*t
        p.line([(left, bottom), (right, bottom), (right, top)], 4, 2)
        p.line([(right, top), (left, top), (left, bottom)], 7, 2)
    for x in [83, 200, 450, 554]:
        p.line([(x, 480), vanishing], 2, 2)
        p.line([(640-x, 0), vanishing], 6, 2)
    # A damping collar silhouettes the exchange against a quiet back plane.
    p.poly([(263,193),(292,168),(384,168),(416,193),(416,276),
            (385,303),(294,303),(263,277)], 10)
    p.line([(263,234),(263,193),(292,168),(384,168),(416,193)], 12, 8)
    p.line([(263,277),(294,303),(385,303),(416,276),(416,228)], 11, 8)
    p.line([(269,209),(269,197),(296,175),(380,175),(406,198)], 7, 2)
    p.line([(269,264),(269,275),(298,296),(382,296),(409,273)], 4, 2)
    for x in (300,314,328,342,356,370):
        p.line([(x,158),(x+3,168)], 7, 2)
        p.line([(x,303),(x-3,313)], 4, 2)
    for x,y,w,h in [(24,122,26,50),(99,150,17,36),(149,178,13,24)]:
        p.poly([(x,y),(x+w,y+12),(x+w,y+h),(x,y+h+7)], 11)
        p.line([(x+4,y+10),(x+w-4,y+16)], 14, 2)
        p.line([(x+4,y+19),(x+w-4,y+22)], 4, 2)
    # Recessed structural bays and opposing deck anchor shoes.
    for x,y,w,h in [(17,191,72,146),(103,207,45,96),(553,153,39,223),(611,143,28,274)]:
        p.poly([(x,y),(x+w,y+20),(x+w,y+h-12),(x,y+h)], 2)
        p.line([(x+3,y+h-3),(x+3,y+4),(x+w-2,y+22)], 11, 3)
        for t in (.28,.47,.66):
            yy = y+h*t
            p.line([(x+9,yy),(x+w-8,yy+4)], 13, 2)
    p.poly([(0,322),(54,325),(85,351),(55,393),(0,421)], 11)
    p.line([(0,326),(51,331),(75,353),(50,388)], 4, 4)
    p.poly([(640,58),(586,84),(555,128),(585,150),(640,140)], 12)
    p.line([(640,134),(587,144),(569,124),(592,89)], 7, 4)
    p.poly([(0,394),(163,346),(309,352),(309,367),(203,433),(0,477)], 11)
    p.poly([(640,89),(477,137),(331,127),(331,113),(441,52),(640,9)], 12)
    p.line([(20,457),(172,416),(207,398)], 9, 2)
    p.line([(620,20),(483,57),(443,77)], 8, 2)
    p.poly([(0, 391), (163, 343), (309, 353), (199, 418), (0, 463)], 4)
    p.poly([(640, 89), (477, 137), (331, 127), (441, 62), (640, 17)], 7)
    p.line([(0, 391), (163, 343), (309, 353)], 9, 3)
    p.line([(640, 89), (477, 137), (331, 127)], 8, 3)

    # The two survey decks have opposite working surfaces.
    for x,y,sign,surface,shade,edge in [(0,391,1,4,11,9),(640,89,-1,7,12,8)]:
        def deck(dx, dy):
            return x+sign*dx, y+sign*dy

        p.line([deck(0,18),deck(164,-30),deck(255,-22)], shade, 3)
        p.line([deck(0,39),deck(171,-7),deck(225,-3)], shade, 3)
        for offset in (34,71,108,145):
            p.line([deck(offset,9-offset*.28),deck(offset+17,32-offset*.28)], surface, 5)
            p.line([deck(offset,9-offset*.28),deck(offset+17,32-offset*.28)], edge, 2)
        p.poly([deck(162,-39),deck(192,-39),deck(199,-33),deck(165,-32)], shade)
        p.line([deck(168,-36),deck(190,-36)], edge, 3)

    for x, y, sign, suit, light in [(231, 349, 1, 1, 4), (438, 128, -1, 8, 6)]:
        def at(dx, dy):
            return x+sign*dx, y-sign*dy

        p.line([at(-14, 0), at(-7, 35), at(9, 37), at(22, 0)], 10, 12)
        p.poly([at(-19, 69), at(15, 72), at(18, 35), at(-11, 30)], suit)
        p.line([at(-19,56),at(13,55)], 10, 4)
        p.line([at(-12,70),at(-15,38)], light, 5)
        pack = 14 if sign == 1 else 15
        p.poly([at(-23,38),at(-31,45),at(-29,69),at(-16,76),at(-12,43)], pack)
        p.line([at(-27,53),at(-27,64)], 10, 3)
        p.line([at(10,64),at(44,57),at(65,76),at(83,99)], 10, 13)
        p.line([at(10,64),at(44,57),at(65,76),at(83,99)], suit, 8)
        p.disc(*at(44,57), 4, light)
        p.line([at(80,94),at(89,103),at(97,102)], light, 6)
        p.disc(*at(0, 87), 17, suit)
        p.line([at(-2,92),at(13,88),at(13,82)], 10, 7)
        p.line([at(2,92),at(11,89)], light, 3)
        p.line([at(-18,65),at(-25,49),at(-28,33)], suit, 8)
        p.disc(*at(-28,30), 5, light)
        p.line([at(-24,1),at(-11,1),at(-8,6)], light, 5)
        p.line([at(18,4),at(23,1),at(34,1)], light, 5)
        p.poly([at(-3,65),at(8,65),at(8,58),at(-3,58)], 10)
        p.disc(*at(1,62), 2, light)
        p.line([at(-7,84),at(-5,77),at(7,77)], light, 2)
    p.line([(309,241),(301,242),(299,234),(311,226),(318,228)], 4, 6)
    p.line([(347,222),(356,216),(363,219),(361,228),(352,234)], 7, 6)
    p.poly([(304,238),(321,214),(351,214),(361,228),(344,254),(317,259)], 10)
    p.poly([(308,238),(323,218),(349,218),(355,229),(342,249),(318,254)], 11)
    p.line([(309,238),(323,218),(349,218),(355,229)], 9, 3)
    p.line([(355,230),(342,249),(318,254)], 4, 3)
    p.disc(333,234,10,8)
    p.disc(333,234,5,10)
    p.disc(334,233,2.5,1)
    p.disc(302,242,4,9)
    p.disc(361,220,4,8)
    p.line([(325,212),(326,203)], 8, 2)
    p.line([(344,259),(343,268)], 4, 2)
    p.rect(15, 423, 357, 49, 10)
    p.title(28, 461, 'THE SECOND FLOOR', 1, 21, 32)
    return p


if __name__ == '__main__':
    save(__file__, build)
