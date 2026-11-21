"""209: a scene.  A farmhouse kitchen before sunrise, the market page already on the television."""
from _kit import BODY, SMALL, Screen, save

META = dict(title='The Farm Kitchen',
            purpose='A scene of the promise made to the countryside: the markets on the kitchen television at dawn.',
            style='Lamp-lit interior in ochre and enamel with a glowing green screen',
            techniques=['filled polygons', 'native circles', 'arcs', 'perspective tiling', 'page 207 in miniature',
                        'colour-map dawn', 'WAIT', 'BLINK', 'proportional text'],
            animated=True)

DARK, CREAM, WALL, SHADOW, TILE, TILE2, ROSE, GLOW = range(8)
NIGHT, ENAMEL, SCREEN, DEEP, WOOD, RED, DENIM, SKIN = range(8, 16)
FLOOR = 336


def room(p):
    p.box(0, 0, 640, FLOOR, WALL)
    # Board wainscot to chair-rail height.
    p.box(0, 254, 640, FLOOR - 254, SHADOW)
    p.box(0, 250, 640, 5, WOOD)
    for x in range(14, 640, 28):
        p.box(x, 256, 2, FLOOR - 262, WOOD)
    p.box(0, FLOOR - 6, 640, 6, WOOD)
    p.box(0, FLOOR, 640, 480 - FLOOR, TILE)
    # Checkered floor: tiles between lines that fan out from a point behind the wall.
    edges = [FLOOR, 352, 374, 404, 446, 500]
    for row, (near, far) in enumerate(zip(edges[1:], edges)):
        for column in range(-8, 9):
            if (row + column) % 2:
                continue
            def at(col, y):
                return (320 + col * 46 * (y - 180) / (FLOOR - 180), y)
            p.poly([at(column, far), at(column + 1, far), at(column + 1, near), at(column, near)], TILE2)


def window(p):
    p.box(200, 48, 196, 176, CREAM)
    p.box(210, 58, 176, 60, NIGHT)
    p.box(210, 118, 176, 34, ROSE)
    p.box(210, 152, 176, 28, GLOW)
    p.disc(292, 182, 24, CREAM)
    p.box(210, 180, 176, 34, DARK)
    # The elevator a mile off, the yard fence and the pole with the yard light.
    p.poly([(340, 182), (340, 150), (347, 142), (347, 134), (357, 134), (357, 142), (364, 150), (364, 182)], DARK)
    for x in range(214, 336, 22):
        p.box(x, 172, 3, 12, DARK)
    p.box(210, 174, 128, 2, DARK)
    p.box(236, 110, 3, 72, DARK)
    p.box(228, 110, 12, 3, DARK)
    p.disc(229, 116, 4, CREAM)
    # A rooster on the fence, about to say so.
    p.oval(266, 162, 11, 8, DARK, 12)
    p.poly([(256, 160), (244, 146), (250, 164)], DARK)
    p.poly([(274, 158), (279, 144), (284, 148), (280, 162)], DARK)
    p.poly([(279, 144), (282, 139), (285, 144)], RED)
    p.poly([(284, 148), (290, 150), (284, 152)], GLOW)
    p.box(264, 168, 2, 6, DARK)
    p.box(295, 58, 6, 156, CREAM)
    p.box(210, 126, 176, 6, CREAM)
    # Gathered curtains with a checked hem.
    for side, edge in ((1, 210), (-1, 386)):
        p.poly([(edge, 58), (edge + side * 40, 58), (edge + side * 30, 110), (edge + side * 14, 150),
                (edge + side * 20, 214), (edge, 214)], RED)
        p.stroke([(edge + side * 12, 62), (edge + side * 8, 196)], CREAM, 1)
        p.stroke([(edge + side * 26, 62), (edge + side * 12, 140)], CREAM, 1)
        p.poly([(edge, 200), (edge + side * 19, 200), (edge + side * 20, 214), (edge, 214)], CREAM)
    p.box(192, 44, 212, 8, WOOD)
    p.box(192, 222, 212, 8, WOOD)
    # A geranium on the sill.
    p.poly([(262, 222), (266, 204), (286, 204), (290, 222)], WOOD)
    for x, y in [(268, 194), (280, 188), (288, 198)]:
        p.disc(x, y, 7, RED)
    p.stroke([(276, 204), (276, 194)], DEEP, 2)


def stove(p):
    p.box(40, 250, 150, 170, ENAMEL)
    p.box(40, 250, 150, 12, DARK)
    p.box(52, 284, 126, 86, DARK)
    p.box(60, 292, 110, 70, SHADOW)
    p.box(70, 274, 90, 5, WOOD)
    for x in (62, 92, 122, 152):
        p.disc(x, 384, 6, DARK)
    p.box(40, 404, 150, 16, SHADOW)
    p.box(46, 420, 10, 12, DARK)
    p.box(174, 420, 10, 12, DARK)
    # A checked tea towel over the oven rail.
    p.box(128, 274, 30, 44, CREAM)
    for y in (282, 296, 310):
        p.box(128, y, 30, 4, RED)
    for x in (134, 148):
        p.box(x, 274, 4, 44, RED)
    p.box(30, 214, 170, 38, ENAMEL)
    p.box(30, 246, 170, 6, SHADOW)
    # Speckled enamel coffee pot on the back ring: body, lid, spout and handle.
    p.poly([(118, 250), (124, 200), (160, 200), (166, 250)], DENIM)
    p.poly([(122, 200), (142, 186), (162, 200)], NIGHT)
    p.disc(142, 186, 4, CREAM)
    p.poly([(120, 232), (98, 208), (104, 204), (124, 218)], DENIM)
    p.bow((164, 212), (184, 224), (165, 240), NIGHT, width=4)
    for x, y in [(132, 212), (150, 220), (138, 234), (154, 240), (128, 242)]:
        p.box(x, y, 3, 3, CREAM)
    # Steam, and a frying pan beside it.
    p.bow((150, 180), (142, 166), (152, 152), CREAM, width=2)
    p.bow((152, 152), (162, 138), (154, 124), CREAM, width=2)
    p.bow((166, 176), (174, 164), (166, 150), CREAM, width=2)
    p.box(40, 238, 60, 12, DARK)
    p.box(18, 242, 24, 4, DARK)
    # Two eggs in the pan.
    for x in (58, 82):
        p.oval(x, 238, 11, 4, CREAM, 12)
        p.oval(x, 237, 4, 2, GLOW, 8)


def calendar(p):
    p.box(38, 50, 84, 120, CREAM)
    p.box(38, 50, 84, 46, GLOW)
    # A sheaf of wheat for the co-operative's picture.
    for lean in (-12, -4, 4, 12):
        p.stroke([(80, 92), (80 + lean, 58)], WOOD, 2)
    p.box(71, 80, 18, 4, RED)
    p.say(80, 118, 'CO-OP', SMALL, RED, 'c', fit=84)
    for row in range(4):
        for column in range(6):
            p.box(45 + column * 12, 124 + row * 11, 9, 8, RED if (row, column) == (1, 2) else SHADOW)
    p.disc(80, 48, 3, DARK)


def television(p):
    # The counter, the set in its wooden cabinet, the terminal box on top.
    p.box(404, 300, 236, 16, WOOD)
    p.box(412, 316, 228, 110, SHADOW)
    p.box(412, 316, 228, 4, DARK)
    for x in (420, 494, 568):
        p.box(x, 330, 64, 84, WALL)
        p.disc(x + 32, 346, 4, WOOD)
    p.box(420, 150, 200, 150, WOOD)
    p.box(420, 150, 200, 6, DARK)
    p.box(432, 164, 134, 122, DARK)
    # On the screen, small: the grain page of 207.  A title band, the elevator against the
    # sky, and four rows of prices with their arrows.
    p.box(438, 170, 122, 110, DEEP)
    p.box(438, 170, 122, 14, DENIM)
    p.box(442, 174, 40, 6, GLOW)
    p.box(438, 184, 122, 16, ROSE)
    p.box(438, 200, 122, 14, GLOW)
    p.poly([(452, 214), (452, 196), (458, 188), (466, 188), (472, 196), (472, 214)], DARK)
    p.box(472, 204, 14, 10, DARK)
    p.disc(536, 212, 9, CREAM)
    p.box(438, 213, 122, 4, DARK)
    for row, rising in enumerate((True, False, True, True)):
        y = 222 + row * 14
        p.box(444, y, 34, 6, CREAM)
        p.box(500, y, 22, 6, CREAM)
        if rising:
            p.poly([(534, y + 7), (540, y - 1), (546, y + 7)], SCREEN)
        else:
            p.poly([(534, y - 1), (540, y + 7), (546, y - 1)], RED)
    for y in (176, 196, 216):
        p.disc(592, y + 6, 8, DARK)
    p.box(578, 240, 30, 42, DARK)
    for y in range(246, 280, 7):
        p.box(582, y, 22, 2, WOOD)
    p.box(460, 128, 110, 22, ENAMEL)
    p.box(460, 144, 110, 6, SHADOW)
    p.box(470, 135, 30, 6, DARK)
    p.disc(556, 138, 4, RED)
    p.stroke([(570, 140), (608, 140), (608, 150)], DARK, 2)
    # The kitchen clock says twenty to six.
    p.disc(520, 84, 26, DARK)
    p.disc(520, 84, 23, CREAM)
    p.stroke([(520, 84), (516, 71)], DARK, 2)
    p.stroke([(520, 84), (506, 92)], DARK, 2)


def shelf(p):
    # A pendant lamp, and a shelf of enamel canisters in three sizes.
    p.box(398, 0, 2, 22, DARK)
    p.poly([(380, 44), (390, 22), (408, 22), (418, 44)], ENAMEL)
    p.box(380, 42, 38, 4, SHADOW)
    p.disc(399, 48, 7, CREAM)
    p.box(566, 96, 74, 6, WOOD)
    for x, wide, tall in [(572, 22, 34), (598, 18, 27), (620, 15, 21)]:
        p.box(x, 96 - tall, wide, tall, ENAMEL)
        p.box(x - 1, 96 - tall - 5, wide + 2, 6, RED)
        p.box(x + 3, 96 - tall + 8, wide - 6, 5, DENIM)


def telephone(p):
    # The wall telephone, and the wire from its jack to the box on the set: the whole
    # connection between this kitchen and the exchange.
    p.box(398, 92, 20, 44, DARK)
    p.box(394, 96, 28, 8, DARK)
    p.disc(408, 120, 6, ENAMEL)
    p.disc(408, 120, 2, DARK)
    p.stroke([(408, 136), (404, 144), (412, 150), (404, 156), (410, 162)], DARK, 1)
    p.stroke([(418, 132), (438, 132), (440, 138), (460, 138)], RED, 2)


def dog(p):
    # The dog has not got up yet.
    p.oval(540, 430, 56, 14, DARK, 20)
    p.oval(536, 420, 50, 16, WOOD, 20)
    p.disc(586, 418, 15, WOOD)
    p.poly([(578, 408), (590, 404), (584, 426)], DARK)
    p.poly([(596, 420), (614, 424), (598, 430)], WOOD)
    p.disc(612, 424, 3, DARK)
    p.bow((488, 424), (478, 410), (490, 404), WOOD, width=5)


def farmer(p):
    # A braided rag rug under the chair, and his boots left by the stove.
    p.oval(302, 426, 150, 18, RED, 28)
    p.oval(302, 426, 124, 13, CREAM, 28)
    p.oval(302, 426, 96, 8, DENIM, 28)
    for x in (196, 214):
        p.poly([(x, 432), (x, 398), (x + 12, 398), (x + 12, 422), (x + 24, 426), (x + 24, 432)], DARK)
    # The chair's legs, the farmer from behind, then the chair back in front of him.
    for x in (236, 364):
        p.box(x, 380, 12, 66, WOOD)
    p.poly([(232, 446), (240, 344), (262, 318), (340, 318), (362, 344), (370, 446)], DENIM)
    for x in range(256, 360, 26):
        p.stroke([(x, 326), (x - 2, 444)], NIGHT, 2)
    for y in (346, 376, 406, 436):
        p.stroke([(238, y), (364, y)], NIGHT, 2)
    # Braces, crossed at the back.
    p.stroke([(268, 320), (318, 400), (322, 444)], RED, 6)
    p.stroke([(332, 320), (286, 400), (282, 444)], RED, 6)
    # The left hand holds the keypad that turns the pages.
    p.poly([(250, 334), (212, 362), (220, 380), (254, 366)], DENIM)
    p.disc(212, 372, 10, SKIN)
    p.poly([(176, 352), (206, 346), (212, 384), (182, 390)], ENAMEL)
    for row in range(3):
        for column in range(3):
            p.box(183 + column * 8 + row, 355 + row * 10 - column, 5, 6, DARK)
    p.box(190, 348, 6, 3, RED)
    # The right arm brings the mug up.
    p.poly([(352, 332), (398, 366), (390, 384), (346, 366)], DENIM)
    p.poly([(398, 366), (392, 310), (376, 312), (376, 372)], DENIM)
    p.disc(384, 306, 10, SKIN)
    p.box(362, 284, 24, 26, ENAMEL)
    p.box(362, 284, 24, 5, RED)
    p.box(282, 296, 38, 26, SKIN)
    p.disc(301, 276, 31, SKIN)
    p.disc(270, 280, 7, SKIN)
    p.disc(332, 280, 7, SKIN)
    p.poly([(270, 268), (276, 268), (282, 296), (274, 292)], ENAMEL)
    p.poly([(332, 268), (326, 268), (320, 296), (328, 292)], ENAMEL)
    # Feed cap, worn straight.
    p.bow((270, 270), (301, 236), (332, 270), RED, fill=True)
    p.box(270, 266, 62, 8, RED)
    p.box(293, 244, 16, 8, CREAM)
    p.box(232, 388, 144, 12, WOOD)
    p.box(232, 424, 144, 12, WOOD)


def build():
    # The window's sky starts as night; a WAIT later the map turns it to dawn.
    p = Screen('1a1210 fff4d6 d9a45c a8743a d8c8a0 8a6a48 2c2850 3a2c58 '
               '18203c e8e8e0 3cf07c 0a4a2c 8a4a20 c8302a 3a5a9a e8b088')
    room(p)
    window(p)
    calendar(p)
    stove(p)
    television(p)
    shelf(p)
    telephone(p)
    dog(p)
    farmer(p)
    p.box(0, 446, 640, 34, DARK)
    p.say(320, 473, '5:40 AM.  THE MARKETS ARE IN.', BODY, CREAM, 'c')
    p.pause(15)
    p.recolour(NIGHT, '2a3a78')
    p.recolour(ROSE, 'c8587a')
    p.pause(10)
    p.recolour(NIGHT, '4a5aa8')
    p.recolour(ROSE, 'f78a6a')
    p.recolour(GLOW, 'ffd070')
    # The arrows of the rising prices wink.
    p.flash(SCREEN, DEEP, 3, 9)
    return p


if __name__ == '__main__':
    save(__file__, build)
