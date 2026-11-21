"""Title screen for a game about repairing torn weather."""
import _local
from encoder.screen import Screen, save

META = dict(title='Hem of the Sky', purpose='Title screen for a weather-stitching adventure',
            style='Ultramarine woodblock sky with vermilion pennants and wheat lettering',
            techniques=['native discs', 'faceted polygons', 'connected stitch lines', 'palette BLINK'],
            animated=True)


def build():
    p = Screen('152b68 fff0c2 294e97 f36a46 9d3344 ffc56b 5373ac 324782 fffaf0 ff9970 0d1b43 83a4db')
    p.disk(482, 237, 119, 5)
    for y in range(193, 327, 15):
        half = (119**2 - (y-237)**2)**.5
        p.rect(482-half, y, 2*half, 2 + (y-193)//30, 0)
    p.poly([(0, 366), (103, 321), (178, 353), (250, 333), (358, 371),
            (495, 326), (639, 348), (639, 480), (0, 480)], 2)
    p.poly([(0, 406), (113, 385), (209, 401), (313, 369), (439, 405),
            (540, 375), (639, 397), (639, 480), (0, 480)], 7)
    # Short warp marks follow the folds of the foreground cloth.
    folds = [(0, 406), (113, 385), (209, 401), (313, 369),
             (439, 405), (540, 375), (639, 397)]
    for (ax, ay), (bx, by) in zip(folds, folds[1:]):
        for step in range(9, bx-ax-8, 11):
            x = ax + step
            y = ay + (by-ay)*step/(bx-ax)
            p.line([(x, y+4), (x+6, y+14)], 6, 2)
        p.line([(ax, ay+19), (bx, by+19)], 2, 2)
    # The needle follows a torn seam, leaving cross stitches behind it.
    tear = [(315, 241), (263, 267), (231, 253), (174, 283),
            (142, 271), (92, 302), (27, 290)]
    p.poly(tear + [(24, 302), (94, 314), (148, 284), (177, 297),
                   (233, 266), (267, 277)], 10)
    p.poly([(313, 236), (345, 262), (365, 263), (391, 292), (423, 297),
            (403, 317), (385, 307), (359, 278), (342, 279)], 10)
    p.line([(315, 241), (342, 279), (359, 278), (385, 307), (403, 317)], 6, 2)
    for x, y in [(344, 279), (357, 279), (371, 291), (387, 309), (402, 317)]:
        p.line([(x, y), (x-2, y+5), (x+1, y+8)], 11, 2)
    p.line(tear, 6, 2)
    p.line([(29, 302), (94, 314), (148, 284), (177, 297),
            (233, 266), (267, 277), (315, 241)], 2, 2)
    eyes = [(46, 294, 54, 306), (71, 298, 80, 312), (98, 299, 110, 306),
            (122, 285, 134, 291), (151, 275, 162, 288), (177, 281, 186, 292),
            (204, 268, 217, 275), (230, 254, 240, 267), (260, 265, 269, 276)]
    # Cross the lips with paired stitches, then lead the free end into the needle.
    for (ax, ay, bx, by), (cx, cy, dx, dy) in zip(eyes, eyes[1:]):
        p.line([(ax, ay), (dx, dy)], 4, 2)
        p.line([(bx, by), (cx, cy)], 1, 2)
    for ax, ay, bx, by in eyes:
        p.disk(ax, ay, 2, 5).disk(bx, by, 2, 5)
    p.line([eyes[-1][2:], (287, 270), (301, 254), (322, 235)], 5, 3)
    for x, y in [(26, 251), (94, 242), (153, 250), (269, 224), (602, 94),
                 (547, 73), (396, 91), (326, 39)]:
        p.disk(x, y, 2, 11)
    p.poly([(320, 238), (491, 132), (558, 274), (461, 335)], 3)
    p.poly([(320, 238), (466, 223), (558, 274), (461, 335)], 4)
    p.poly([(491, 132), (466, 223), (558, 274)], 9)
    p.poly([(346, 233), (482, 148), (462, 214)], 3)
    p.line([(342, 236), (463, 214), (483, 146)], 4, 2)
    # A wound spool feeds the needle through the frame of the sail.
    p.line([(322, 235), (375, 229), (424, 244), (474, 272)], 5, 2)
    p.poly([(466, 263), (494, 252), (508, 273), (478, 285)], 10)
    p.poly([(473, 266), (493, 258), (502, 271), (481, 279)], 5)
    for x, y in [(478, 264), (483, 262), (488, 260), (493, 258)]:
        p.line([(x, y), (x+8, y+14)], 3, 2)
    p.line([(466, 263), (478, 285)], 1, 3)
    p.line([(494, 252), (508, 273)], 9, 3)
    # A steel sail needle protrudes past the kite's leading corner.
    p.poly([(289, 244), (318, 231), (360, 226), (332, 240)], 11)
    p.line([(290, 244), (320, 234), (352, 228)], 8, 2)
    p.disk(322, 235, 3, 10)
    p.disk(466, 223, 6, 5).disk(466, 223, 3, 4)
    p.line([(491, 132), (466, 223), (461, 335)], 1, 2)
    p.line([(320, 238), (466, 223), (558, 274)], 5, 2)
    p.line([(461, 335), (406, 354), (347, 339), (283, 360), (216, 351),
            (154, 375), (106, 363)], 1, 2)
    for x, y in [(403, 354), (347, 340), (282, 359), (219, 351), (155, 374)]:
        p.poly([(x-9, y-9), (x+10, y-2), (x+11, y+9), (x-10, y+2)], 3)
    p.text(29, 103, 'HEM OF', 60, 81, 1)
    p.text(28, 180, 'THE SKY', 55, 81, 1)
    p.text(33, 221, 'MEND THE WEATHER', 25, 34, 1)
    p.rect(33, 420, 230, 42, 1)
    p.text(50, 454, 'PRESS START', 24, 32, 0)
    p.poly([(279, 428), (294, 441), (279, 454)], 8)
    p.blink(8, 3, 5, 5)
    return p


if __name__ == '__main__':
    save(__file__, build())
