"""215: a scene.  A spare-bedroom office: the terminal, the sales chart, and a toddler with blocks."""
from _kit import BODY, Screen, save

META = dict(title='Working from Home',
            purpose='A scene of the work the futurists moved into the home: a terminal on a bedroom desk, a child on the rug.',
            style='Striped-wallpaper interior with a suburban window and a green chart',
            techniques=['filled polygons', 'native circles', 'arcs', 'repeated rectangles', 'WAIT-drawn chart',
                        'proportional text', 'BLINK'],
            animated=True)

DARK, WHITE, WALL, STRIPE, RUG, DESK, GRAIN, LAMP = range(8)
TUBE, PHOSPHOR, SKIN, HAIR, SHIRT, RED, YELLOW, SKY = range(8, 16)
FLOOR = 340


def room(p):
    p.box(0, 0, 640, FLOOR, WALL)
    for x in range(8, 640, 32):
        p.box(x, 0, 8, FLOOR, STRIPE)
    p.box(0, FLOOR - 12, 640, 12, WHITE)
    p.box(0, FLOOR, 640, 480 - FLOOR, RUG)
    p.oval(176, 408, 176, 32, STRIPE, 32)
    p.oval(176, 408, 156, 24, WALL, 32)
    # The wall clock says a quarter past nine, beside a framed certificate.
    p.disc(316, 84, 26, DARK)
    p.disc(316, 84, 23, WHITE)
    p.stroke([(316, 84), (332, 84)], DARK, 2)
    p.stroke([(316, 84), (306, 78)], DARK, 3)
    p.box(290, 136, 56, 44, GRAIN)
    p.box(296, 142, 44, 32, WHITE)
    for y in (150, 157, 164):
        p.box(304, y, 28, 2, STRIPE)
    p.disc(330, 166, 4, RED)
    # Lower down, taped up at a child's height: a crayon drawing of the house.
    p.poly([(262, 232), (316, 236), (313, 290), (258, 286)], WHITE)
    p.box(270, 256, 24, 20, RED)
    p.poly([(266, 258), (282, 242), (298, 258)], SHIRT)
    p.disc(304, 248, 6, YELLOW)
    p.stroke([(262, 280), (274, 276), (288, 281), (300, 277), (312, 281)], PHOSPHOR, 3)
    p.box(282, 228, 12, 7, STRIPE)


def window(p):
    p.box(40, 44, 210, 184, WHITE)
    p.box(52, 56, 186, 160, SKY)
    # Across the street: a lawn, a house, a tree, a car at the kerb.
    p.box(52, 170, 186, 30, PHOSPHOR)
    p.box(52, 198, 186, 18, DARK)
    p.box(52, 205, 186, 2, YELLOW)
    p.box(76, 128, 78, 46, WHITE)
    p.poly([(68, 130), (115, 98), (162, 130)], RED)
    p.box(108, 146, 16, 28, GRAIN)
    p.box(84, 140, 16, 14, SKY)
    p.box(132, 140, 16, 14, SKY)
    p.box(196, 132, 6, 42, GRAIN)
    p.disc(199, 120, 22, PHOSPHOR)
    p.poly([(160, 204), (166, 190), (180, 182), (206, 182), (218, 190), (228, 194), (228, 204)], YELLOW)
    p.disc(176, 205, 6, DARK)
    p.disc(212, 205, 6, DARK)

    p.box(142, 56, 6, 160, WHITE)
    p.box(52, 132, 186, 5, WHITE)
    for edge, side in ((52, 1), (238, -1)):
        p.poly([(edge, 56), (edge + side * 30, 56), (edge + side * 22, 216), (edge, 216)], SHIRT)
        p.stroke([(edge + side * 10, 60), (edge + side * 8, 212)], SKY, 1)
        p.stroke([(edge + side * 20, 60), (edge + side * 15, 212)], SKY, 1)
    # The cat keeps watch on the street from the sill.
    p.oval(98, 204, 16, 13, DARK, 14)
    p.disc(108, 184, 9, DARK)
    p.poly([(101, 180), (103, 168), (109, 177)], DARK)
    p.poly([(109, 177), (115, 168), (116, 181)], DARK)
    p.bow((84, 212), (70, 204), (76, 190), DARK, width=4)


def desk(p):
    p.box(330, 262, 310, 14, DESK)
    p.box(330, 276, 310, 5, GRAIN)
    p.box(346, 281, 12, 150, GRAIN)
    p.box(520, 281, 120, 130, DESK)
    for y in (290, 330, 370):
        p.box(528, y, 104, 34, GRAIN)
        p.box(566, y + 14, 28, 5, DESK)
    # Shelf of books above.
    p.box(430, 70, 200, 8, GRAIN)
    x = 440
    for wide, tall, ink in [(14, 40, RED), (10, 34, SHIRT), (16, 44, YELLOW), (12, 38, PHOSPHOR),
                            (14, 42, DARK), (10, 30, RED), (18, 40, WHITE)]:
        p.box(x, 70 - tall, wide, tall, ink)
        x += wide + 2
    # The terminal, its screen, the keyboard, and the telephone it dials through.
    p.box(430, 128, 150, 122, WHITE)
    p.frame(430, 128, 150, 122, STRIPE, 3)
    p.box(430, 244, 150, 6, GRAIN)
    p.box(442, 138, 126, 96, TUBE)
    p.box(450, 222, 110, 2, WHITE)
    p.box(450, 144, 2, 80, WHITE)
    p.box(458, 146, 40, 5, PHOSPHOR)
    p.disc(570, 240, 3, LAMP)
    p.box(470, 250, 70, 12, GRAIN)
    p.poly([(420, 262), (432, 252), (560, 252), (572, 262)], WHITE)
    for x in range(438, 560, 12):
        p.box(x, 254, 8, 4, GRAIN)
    # The telephone sits in the modem's cradle; the modem's two lamps flicker as it talks.
    p.box(584, 250, 56, 12, DARK)
    p.disc(596, 256, 3, LAMP)
    p.disc(608, 256, 3, PHOSPHOR)
    p.box(592, 230, 40, 20, RED)
    p.box(588, 222, 48, 9, RED)
    p.disc(612, 240, 6, WHITE)
    # The telephone's cord runs into the back of the terminal: that is the whole network.
    p.stroke([(600, 224), (600, 206), (580, 200)], DARK, 2)
    # Papers at her elbow.
    p.poly([(340, 262), (348, 250), (398, 250), (392, 262)], WHITE)
    p.stroke([(354, 255), (386, 255)], STRIPE, 1)


def sales_chart(p):
    """The month's sales come down the line: five bars rise in turn, then the trend is drawn
    across them, and the cursor waits after the last figure."""
    p.pause(10)
    points = [(452, 200), (476, 186), (498, 190), (520, 168), (556, 150)]
    for index, tall in enumerate((18, 30, 26, 44, 58)):
        p.box(454 + index * 22, 222 - tall, 14, tall, PHOSPHOR)
        p.pause(4)
    for start, end in zip(points, points[1:]):
        p.stroke([start, end], YELLOW, 2)
        p.pause(3)
    p.box(548, 138, 8, 10, LAMP)


def hanging_plant(p):
    # A spider plant in a macrame hanger, as every such room had.
    p.stroke([(392, 0), (380, 60)], WHITE, 1)
    p.stroke([(392, 0), (404, 60)], WHITE, 1)
    p.stroke([(392, 0), (392, 62)], WHITE, 1)
    p.poly([(376, 60), (408, 60), (402, 82), (382, 82)], DESK)
    p.box(374, 58, 36, 5, GRAIN)
    for dx, dy in [(-30, 10), (-22, 34), (-8, 44), (10, 46), (24, 32), (32, 8), (-16, -16), (16, -18), (0, -24)]:
        p.poly([(392, 62), (392 + dx * .5 - 4, 62 + dy * .5 - 6), (392 + dx, 62 + dy)], PHOSPHOR)


def parent(p):
    # Swivel chair, then the parent in profile, typing.
    p.box(366, 402, 8, 36, DARK)
    p.poly([(330, 446), (340, 436), (400, 436), (410, 446)], DARK)
    p.box(330, 386, 86, 16, DARK)
    p.box(322, 280, 16, 110, DARK)
    p.poly([(342, 392), (348, 300), (372, 280), (398, 284), (408, 312), (410, 392)], SHIRT)
    p.poly([(374, 282), (386, 296), (398, 284)], WHITE)
    p.poly([(388, 300), (440, 264), (448, 276), (400, 322)], SHIRT)
    p.poly([(436, 266), (444, 260), (452, 272), (446, 278)], WHITE)
    p.disc(452, 264, 8, SKIN)
    p.poly([(346, 388), (430, 380), (442, 396), (440, 436), (420, 436), (418, 404), (350, 404)], DARK)
    # Dressed for the office to the ankle, and then slippers.
    p.poly([(416, 434), (456, 434), (460, 446), (416, 446)], RED)
    p.disc(450, 434, 6, WHITE)
    # The briefcase has not left its place by the drawers since March.
    p.box(476, 408, 40, 32, GRAIN)
    p.box(476, 408, 40, 5, DARK)
    p.bow((488, 408), (496, 400), (504, 408), DARK, width=3)
    p.box(493, 416, 6, 5, YELLOW)
    # The wastebasket, and the drafts that missed it.
    p.poly([(586, 406), (626, 406), (620, 444), (592, 444)], STRIPE)
    for x in range(594, 622, 8):
        p.stroke([(x, 410), (x + 1, 440)], GRAIN, 1)
    p.box(584, 404, 44, 4, GRAIN)
    for x, y, r in [(600, 400, 7), (612, 398, 6), (560, 438, 6), (636, 440, 5)]:
        p.disc(x, y, r, WHITE)
        p.stroke([(x - 3, y - 1), (x + 2, y + 2)], STRIPE, 1)
    p.box(372, 262, 16, 22, SKIN)
    p.disc(384, 244, 26, SKIN)
    p.poly([(406, 238), (418, 250), (408, 254)], SKIN)
    p.poly([(396, 264), (408, 262), (404, 272), (392, 270)], SKIN)
    # Hair to the collar, an ear, glasses, and a small smile.
    p.bow((360, 250), (378, 214), (408, 232), HAIR, fill=True)
    p.poly([(392, 222), (410, 230), (408, 240), (394, 232)], HAIR)
    p.poly([(358, 236), (374, 224), (378, 268), (360, 276)], HAIR)
    p.disc(378, 248, 5, SKIN)
    p.disc(400, 242, 6, DARK, fill=False, width=2)
    p.stroke([(394, 242), (380, 244)], DARK, 2)
    p.stroke([(398, 258), (406, 258)], DARK, 2)


def toddler(p):
    # Blocks: a tower of three and two strays.
    for x, y, ink in [(70, 396, RED), (74, 368, YELLOW), (70, 340, SHIRT), (112, 404, PHOSPHOR), (30, 412, YELLOW)]:
        p.box(x, y, 28, 28, ink)
        p.frame(x, y, 28, 28, DARK, 2)
    # The child sits on the rug, reaching for the tower with a fourth block.
    p.poly([(176, 432), (170, 384), (190, 360), (222, 360), (240, 384), (246, 432)], YELLOW)
    p.poly([(176, 432), (140, 432), (136, 418), (176, 412)], YELLOW)
    p.disc(138, 424, 9, SKIN)
    p.poly([(184, 374), (128, 366), (126, 378), (186, 394)], YELLOW)
    p.box(100, 354, 24, 24, RED)
    p.frame(100, 354, 24, 24, DARK, 2)
    p.disc(124, 372, 8, SKIN)
    p.disc(200, 336, 30, SKIN)
    p.bow((176, 322), (204, 302), (228, 326), HAIR, fill=True)
    p.disc(184, 336, 3, DARK)
    p.bow((176, 346), (182, 352), (190, 348), DARK, width=2)
    # A toy telephone, off the hook like the real one, and a ball.
    p.box(18, 366, 34, 18, RED)
    p.disc(26, 386, 5, DARK)
    p.disc(44, 386, 5, DARK)
    p.disc(35, 374, 6, WHITE)
    p.bow((14, 366), (35, 350), (56, 366), YELLOW, width=6)
    p.stroke([(18, 384), (4, 396), (0, 410)], DARK, 2)
    p.disc(318, 424, 15, RED)
    p.bow((304, 420), (318, 416), (333, 422), WHITE, width=4)
    # A bear, left where it fell.
    p.disc(280, 424, 16, HAIR)
    p.disc(280, 400, 12, HAIR)
    p.disc(270, 390, 5, HAIR)
    p.disc(290, 390, 5, HAIR)
    p.disc(280, 403, 5, STRIPE)
    p.disc(264, 420, 6, HAIR)
    p.disc(296, 420, 6, HAIR)


def build():
    p = Screen('181420 f8f4ec ecc8a8 dca888 3a6a9a b06c2c 6a3c18 ffb030 '
               '06242c 40f080 f0c098 5a3418 4a6ad8 e83838 ffd030 8cd0f8')
    room(p)
    window(p)
    hanging_plant(p)
    desk(p)
    parent(p)
    toddler(p)
    p.box(0, 446, 640, 34, DARK)
    p.say(320, 473, '9:15 AM.  AT THE OFFICE.', BODY, WHITE, 'c')
    sales_chart(p)
    p.flash(LAMP, TUBE, 4, 4)
    return p


if __name__ == '__main__':
    save(__file__, build)
