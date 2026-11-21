from math import cos, pi, sin
from random import Random
from _canvas import Canvas, write_page

META = dict(title='Final Spin', purpose='A single machine still running in a closed laundromat',
            style='Midnight shopfront in fuchsia and mint',
            techniques=['native circles and arcs', 'sampled reflection streaks', 'palette BLINK'],
            animated=True)


def build():
    p = Canvas('111224 231d36 424054 ef72ae ffb7d7 36545f 538d87 a1f0be'
               ' 191a2c 68376d 3a283f b8ffd6 504557 705068 212338 2b2f40')
    p.rect(43, 65, 554, 307, 10)
    p.rect(58, 123, 524, 229, 2)
    p.rect(71, 135, 498, 197, 8)
    p.poly([(71, 135), (569, 135), (569, 170), (71, 275)], 1)
    for shelf in (156, 165):
        p.line([(73, shelf+5), (565, shelf-5)], 12, 2)
    for left in (85, 105, 215, 438, 455, 522):
        p.poly([(left, 155), (left+3, 144), (left+13, 143),
                (left+16, 155)], 10)
    p.poly([(235, 330), (255, 145), (380, 137), (409, 330)], 15)
    p.poly([(244, 330), (267, 167), (374, 158), (398, 330)], 5)
    for x in (148, 319, 489):
        active = x == 319
        p.rect(x - 65, 176, 130, 146, 6 if active else 5)
        p.rect(x - 58, 182, 116, 24, 8)
        p.rect(x + 33, 188, 15, 9, 7 if active else 2)
        p.line([(x-64, 321), (x-64, 177), (x+64, 177)], 7 if active else 12, 2)
        p.line([(x-55, 311), (x+49, 311)], 2, 2)
        for i in range(4):
            p.line([(x-50, 189+3*i), (x-37, 189+3*i)], 12, 1)
        p.circle(x, 259, 46, 5 if active else 0)
        p.circle(x, 259, 43, 7 if active else 2)
        p.circle(x, 259, 36, 0)
        p.pel(3).arc((x-30, 268), (x-12, 290), (x+23, 284), 5 if active else 15)
        p.pel(2).arc((x-32, 249), (x-17, 226), (x+11, 223), 7 if active else 12)
        p.rect(x+30, 248, 9, 22, 6 if active else 12)
        if not active:
            p.ellipse(x, 265, 31, 24, 15, n=48)
            if x < 319:
                p.poly([(x-25, 268), (x-17, 262), (x-5, 273),
                        (x+12, 268), (x+22, 278), (x+9, 286),
                        (x-14, 283)], 12)
            else:
                for offset in (-16, -8, 0, 8, 16):
                    p.circle(x+offset, 273+abs(offset)/5, 1.6, 5)
            p.pel(2).arc((x-24, 258), (x-13, 242), (x+9, 239), 5)
        if active:
            p.circle(x, 259, 32, 5)
            p.circle(x, 259, 28, 0)
            for hole in range(26):
                a = hole*pi/13
                p.circle(x+30*cos(a), 259+30*sin(a), 1.2, 7)
            for phase, reach in [(0, 1), (2*pi/3, .83), (4*pi/3, .94)]:
                def at(radius, angle):
                    return (x + reach*radius*cos(phase + angle),
                            259 + reach*radius*sin(phase + angle))

                p.poly([at(8, .72), at(19, -.30), at(26, -.62),
                        at(27, .12), at(22, .78), at(13, 1.18)], 6)
                p.poly([at(8, .72), at(13, .23), at(23, -.42),
                        at(19, .39), at(13, 1.18)], 5)
                p.line([at(15, .56), at(21, .24), at(24, -.15)], 7, 2)
                p.pel(3).arc(at(30, -.56), at(30, -.16), at(30, .24), 11)
    for left, right in [(72, 226), (238, 409), (420, 570)]:
        p.line([(left+1, 217), (right-1, 191)], 12, 1)
    for x in (58, 227, 410, 574):
        p.rect(x, 120, 8, 230, 2)
    p.rect(42, 346, 556, 15, 9)
    p.rect(43, 362, 554, 14, 1)
    # Paving joints recede toward the window sill. Reflections cross them in fragments.
    for y, shift in [(381, 15), (394, -11), (413, 24), (443, 0), (474, -20)]:
        p.line([(0, y), (204, y-2), (432, y), (639, y-1)], 14, 2)
        for x in range(45, 640, 99):
            edge = min(639, x + shift)
            p.line([(x, y-10), (edge, y)], 14, 2)
    for top, bottom, left, right in [(377, 394, 282, 358), (398, 418, 273, 371),
                                      (422, 443, 253, 394), (449, 478, 224, 415)]:
        p.poly([(left+11, top), (right-8, top), (right, bottom),
                (left, bottom)], 14)
        p.line([(left, bottom), (right, bottom)], 15, 2)
    rng = Random(148)
    for y in range(380, 474, 3):
        spread = 1 + (y-380)/42
        for centre, width, inks in [(126, 21, (10, 9, 13)), (319, 30, (5, 6, 7)),
                                    (482, 31, (10, 9, 13))]:
            left = centre + rng.uniform(-width, width)*spread
            right = min(639, left+rng.uniform(5, width)*spread)
            p.line([(max(0, left), y), (right, y+rng.choice((-1, 0, 1)))],
                   inks[rng.randrange(3) if y < 432 else rng.randrange(2)], 2)
    p.rect(65, 62, 505, 53, 1)
    p.line([(69, 115), (566, 115)], 9, 3)
    p.text(75, 109, 'FINAL SPIN', 33, 46, 4)
    for x, phase in [(430, 0), (475, 1), (520, 2)]:
        p.circle(x, 88, 16, 9)
        p.circle(x, 88, 13, 3, fill=False, width=2)
        angle = phase*1.7
        p.line([(x-7*cos(angle), 88-7*sin(angle)),
                (x+7*cos(angle), 88+7*sin(angle))], 4, 2)
    p.line([(240, 343), (404, 343)], 5, 3)
    p.line([(277, 349), (362, 349)], 6, 2)
    p.blink(11, 6, on=5, off=5)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
