"""Inventory screen for a game about trading physical properties."""
import _local
from encoder.screen import Screen, save

META = dict(title='Tessera Vault', purpose='Inventory with a gravity-changing relic selected',
            style='Black enamel display case with mint, pale lilac and electric amber',
            techniques=['faceted polygons', 'outlined rectangles', 'native discs', 'fixed-pitch numerals'],
            animated=False)


def build():
    p = Screen('171623 f0dbff 342b4c 625276 c290fa ffca62 89f1cb 886026 eee7cc 514467 96734b 29786a')
    p.text(28, 57, 'TESSERA VAULT', 36, 46, 1)
    p.rect(24, 78, 366, 323, 2)
    p.rect(34, 88, 346, 303, 3, False)
    p.ellipse(207, 308, 141, 37, 9)
    p.ellipse(207, 308, 122, 29, 0)
    p.line([(103, 316), (158, 330), (212, 334), (264, 329), (309, 316)], 6, 2)
    # Stone chips climb out of the well along converging trajectories.
    for x, y, size, tilt in [(83, 231, 11, -3), (103, 166, 8, 4),
                              (117, 283, 6, -2), (331, 208, 12, 4),
                              (306, 146, 8, -4), (302, 264, 8, 3)]:
        p.line([(x+tilt*4, y+64), (x+tilt, y+size), (x, y)], 11, 3)
        p.poly([(x-size, y), (x+tilt, y-size), (x+size, y-3),
                (x+size//2, y+size), (x-4, y+size)], 6)
        p.poly([(x-size, y), (x+size, y-3), (x+size//2, y+size),
                (x-4, y+size)], 11)
        p.line([(x, y-size-9), (x-tilt, y-size-18)], 6, 2)
    p.poly([(125, 179), (214, 110), (293, 174), (275, 246), (211, 294), (151, 263)], 5)
    p.poly([(125, 179), (212, 203), (211, 294), (151, 263)], 7)
    p.poly([(212, 203), (293, 174), (275, 246), (211, 294)], 8)
    p.poly([(152, 182), (213, 137), (267, 177), (211, 191)], 0)
    p.poly([(165, 177), (213, 143), (253, 175), (213, 165)], 6)
    p.poly([(165, 177), (213, 165), (253, 175), (211, 189)], 11)
    p.line([(211, 164), (211, 151)], 11, 2)
    p.poly([(184, 121), (212, 97), (240, 121), (213, 135)], 6)
    p.poly([(184, 121), (213, 122), (240, 121), (212, 146)], 11)
    p.poly([(202, 119), (212, 108), (224, 119), (212, 124)], 8)
    for x, y, size in [(168, 143, 5), (255, 142, 7), (248, 109, 4),
                       (148, 150, 4), (273, 124, 4)]:
        p.poly([(x, y-size), (x+size, y), (x+1, y+size+2), (x-size, y)], 6)
        p.line([(x, y+size+5), (x, y+size+10)], 11, 2)
    p.poly([(133, 191), (203, 211), (203, 275), (156, 254)], 10)
    p.line([(125, 179), (212, 203), (293, 174)], 8, 2)
    p.line([(212, 206), (211, 287)], 5, 3)
    p.rect(35, 348, 344, 42, 0)
    p.line([(35, 348), (378, 348)], 9, 2)
    p.text(55, 384, 'REVERSE GRAVITY', 26, 36, 5)
    p.poly([(409, 114), (389, 128), (409, 142)], 5)
    for index, y in enumerate((78, 188, 298)):
        p.rect(409, y, 207, 103, 5 if index == 0 else 3)
        p.rect(413, y+4, 199, 95, 0 if index == 0 else 2)
        p.text(497, y+40, ('WEIGHT', 'ECHO', 'HEAT')[index], 23, 31, 1)
        p.text(497, y+76, ('01', '02', '03')[index], 29, 36, 5 if index == 0 else 6, False)
    p.poly([(432, 116), (451, 99), (474, 116), (466, 145), (450, 157), (437, 144)], 5)
    p.poly([(432, 116), (451, 122), (450, 157), (437, 144)], 7)
    p.poly([(441, 115), (451, 106), (465, 116), (451, 119)], 6)
    for radius, ink in [(30, 4), (25, 2), (20, 4), (15, 2), (7, 6)]:
        p.disk(452, 239, radius, ink)
    p.poly([(431, 372), (440, 349), (453, 319), (460, 344), (470, 334),
            (476, 372), (452, 385)], 6)
    p.rect(27, 420, 33, 37, 5)
    p.text(35, 451, 'A', 25, 33, 0)
    p.text(72, 451, 'EQUIP', 25, 33, 5)
    p.poly([(443, 368), (457, 346), (461, 359), (467, 354), (467, 369),
            (452, 377)], 8)
    p.rect(416, 420, 33, 37, 3)
    p.text(424, 451, 'B', 25, 33, 1)
    p.text(461, 451, 'RETURN', 25, 33, 1)
    return p


if __name__ == '__main__':
    save(__file__, build())
