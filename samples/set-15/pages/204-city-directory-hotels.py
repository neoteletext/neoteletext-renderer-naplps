import math
from _page import Plate, save

META = dict(title='City Directory: Hotels',
            purpose='The electronic city directory a visitor consults before booking: downtown hotels with '
                    'addresses, telephone numbers, stars and tonight\'s free rooms.',
            style='Dusk skyline whose windows light up, over a cream directory card with coloured availability dots',
            techniques=['colour-map change after WAIT lights every window and its reflection at once', 'DRCS star and bed characters',
                        'BLINK beacon, sign and last-room dot', 'text on a downward path', 'rows of rectangles', 'WAIT between directory rows', 'proportional text'],
            animated=True)

PALETTE = ('0c1030 ffffff 7a2f6a e07a3a 2a2450 161634 2a2a40 f2ead6 '
           'e4d8bc 1a1a30 2aa84a d83030 e8a820 3a1a5a 4c4c68 ff3a3a').split()
NIGHT, WHITE, DUSK, GLOW, FAR, NEAR, WINDOW, CARD, ALT, INK, FREE, FULL, GOLD, BAND, GREY, BEACON = range(16)
STAR, BED = 0x21, 0x22

HOTELS = [('The Harbourview', '14 Quay St   555-0142', 3, '12', FREE, '$46'),
          ('Lantern Inn', '3 Mill Rd   555-0177', 2, 'FULL', FULL, '$29'),
          ('Grand Calder', '200 King Ave   555-0100', 4, '4', FREE, '$68'),
          ('Westmark Motor Hotel', '88 Prairie Way   555-0129', 2, '31', FREE, '$24'),
          ('Station House', '1 Depot Sq   555-0163', 3, '1', BEACON, '$38')]


def build():
    p = Plate('204', PALETTE)
    star = [(0.5 + 0.5 * (1 if i % 2 == 0 else 0.42) * math.cos(math.radians(90 + 36 * i)),
             0.47 + 0.5 * (1 if i % 2 == 0 else 0.42) * math.sin(math.radians(90 + 36 * i))) for i in range(10)]
    p.define_drcs(STAR, 20, 20 * 0.96, [star])
    # A bed for the availability column: headboard, mattress, pillow and foot.
    p.define_drcs(BED, 30, 30 * 0.96, [('rect', 0.04, 0.14, 0.12, 0.62), ('rect', 0.04, 0.30, 0.92, 0.20),
                                       ('rect', 0.20, 0.50, 0.26, 0.12), ('rect', 0.84, 0.14, 0.10, 0.18)])
    p.rect(0, 0, 640, 40, BAND)
    # The visitor-information emblem: a lower-case i in a gold disc.
    p.disc(26, 20, 14, GOLD)
    p.rect(23, 17, 6, 13, BAND)
    p.disc(26, 11, 3, BAND)
    p.text(50, 31, 'CALDER BAY CITY GUIDE', 17, 26, WHITE)
    p.rtext(624, 30, 'p 230', 14, 22, GOLD, prop=False)
    # Dusk sky in bands and the skyline.
    p.rect(0, 40, 640, 130, NIGHT)
    p.rect(0, 112, 640, 30, DUSK)
    p.rect(0, 142, 640, 28, GLOW)
    p.disc(560, 74, 16, CARD)
    p.disc(568, 70, 14, NIGHT)
    far = [(0, 110), (40, 96), (90, 120), (150, 84), (200, 104), (260, 92), (330, 116), (380, 78),
           (440, 100), (500, 90), (560, 112), (610, 96)]
    for i, (x, top) in enumerate(far):
        p.rect(x, top, 46, 170 - top, FAR)
    near = [(10, 124, 52), (70, 100, 40), (118, 134, 60), (190, 70, 44), (246, 120, 56), (312, 104, 48),
            (372, 128, 60), (440, 88, 50), (500, 130, 44), (552, 112, 70)]
    for x, top, w in near:
        p.rect(x, top, w, 170 - top, NEAR)
    p.line([(212, 70), (212, 44)], GREY, 2)
    p.disc(212, 44, 4, BEACON)
    for x, top, w in near:
        for wy in range(top + 8, 140, 12):
            p.rect(x + 6, wy, w - 12, 5, WINDOW)
    p.hatch(1)
    for x, top, w in near:
        p.rect(x + 6, top + 8, w - 12, 136 - top, NEAR)
    p.solid()
    # The bay in front of the city: its reflections are drawn in the window entry, so they light with it.
    p.rect(0, 148, 640, 22, NEAR)
    for x, top, w in near:
        for i, ry in enumerate((153, 159, 165)):
            # Broken, narrowing streaks: a reflection on moving water.
            seg = (w - 12) / 4
            for s in range(0, 4, 2):
                p.rect(x + 6 + s * seg + (i % 2) * seg / 2, ry, seg * (1 - i * 0.25), 1, WINDOW)
    # The moon's path on the water.
    for i, ry in enumerate((151, 156, 161, 166)):
        p.rect(552 - 8 + i * 2, ry, 16 - i * 3, 2, CARD)
    for gx in range(20, 640, 70):
        p.rect(gx, 158, 26, 2, GLOW)
    # A vertical HOTEL sign on the Grand Calder, lit in the beacon's flashing entry.
    p.rect(346, 88, 30, 84, INK)
    p.text(351, 106, 'HOTEL', 20, 16, BEACON, prop=False, path=3)
    p.rect(0, 170, 640, 4, GOLD)
    # Directory card.
    p.rect(0, 174, 640, 262, CARD)
    p.text(16, 200, 'HOTELS DOWNTOWN', 14, 22, INK, prop=False)
    p.rtext(624, 200, 'ROOMS TONIGHT', 14, 22, INK, prop=False)
    for i, (name, line2, stars, rooms, colour, price) in enumerate(HOTELS):
        top = 208 + i * 45
        p.wait(3)
        if i % 2 == 0:
            p.rect(0, top, 640, 45, ALT)
        p.text(16, top + 22, f'{i + 1}', 15, 23, BAND, prop=False)
        p.text(44, top + 22, name, 15, 23, INK)
        p.chars(318, top + 22, [STAR] * stars, 20, 20 * 0.96, GOLD)
        p.text(44, top + 42, line2, 13, 20, GREY)
        p.rtext(482, top + 42, f'{price} a night', 13, 20, INK)
        p.chars(496, top + 38, [BED], 38, 38 * 0.96, colour)
        p.rtext(624, top + 30, rooms, 15, 23, INK, prop=False)
    # The visitor's choice so far: the Grand Calder, boxed with a pointer.
    p.frame(2, 208 + 2 * 45 + 1, 634, 42, BAND, 3)
    p.rect(0, 436, 640, 44, BAND)
    p.text(16, 465, 'KEY 1-5 TO BOOK A ROOM', 15, 24, WHITE)
    p.rtext(624, 465, 'MAP p 231', 14, 22, GOLD, prop=False)
    # The tower's light and the last free room share an entry and flash together.
    p.blink(BEACON, CARD, 5, 5)
    p.wait(15)
    p.recolour(WINDOW, 'ffd85a')
    return p


if __name__ == '__main__':
    save(__file__, build)
