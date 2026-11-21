from _kit import *

META = dict(title='Today\'s Special at the Hardware Store',
            purpose='A late-videotex page whose advertising band at the foot opens into a full-screen advertisement with a SALE starburst that cycles colour.',
            style='Hazard yellow and charcoal, a large cordless drill, a three-layer starburst chasing through the colour map',
            techniques=['native circles', 'filled polygons', 'clipped sunburst', 'DRCS', 'dotted line texture', 'WAIT', 'BLINK chase', 'bevelled keys', 'proportional text'],
            animated=True)

CHAR, WHITE, HAZARD, BLACK, STEEL, DKSTEEL, RED, ORANGE, TEAL, PAPER, WOOD, DKWOOD, BURST_A, BURST_B, BURST_C, INK = range(16)


DRILL_ICON = 0x21
ICON_W, ICON_H = 44, 24
DRILL_SHAPES = [
    ('poly', [(0, 4), (24, 4), (24, 14), (14, 14), (11, 22), (5, 22), (6, 14), (0, 14)]),
    ('poly', [(24, 6), (32, 6), (32, 12), (24, 12)]),
    ('line', [(32, 9), (43, 9)], 1.6),
    ('hole', 8, 8, 2),
]


def article(p):
    p.rect(0, 44, 640, 402, PAPER)
    p.rect(0, 44, 640, 40, TEAL)
    p.say(14, 74, 'WEEKEND PROJECTS', LARGE, WHITE)
    p.say(14, 116, 'A BIRDHOUSE IN ONE AFTERNOON', BODY, TEAL)
    for i, line in enumerate(['1  CUT SIX BOARDS FROM A 1 BY 6',
                              '2  DRILL THE ENTRY HOLE, 1 1/4 IN',
                              '3  NAIL THE WALLS TOGETHER',
                              '4  HANG IT FACING EAST']):
        p.disc(22, 151 + i * 30, 11, HAZARD)
        p.say(22, 158 + i * 30, line[0], BODY, BLACK, 'c')
        p.say(44, 158 + i * 30, line[3:], BODY, INK)
        p.wait(5)
    # the birdhouse
    p.poly([(448, 250), (448, 160), (500, 120), (552, 160), (552, 250)], WOOD)
    p.poly([(432, 164), (500, 108), (568, 164), (556, 170), (500, 126), (444, 170)], DKWOOD)
    p.disc(500, 190, 14, BLACK)
    p.rect(494, 232, 12, 6, DKWOOD)
    p.rect(494, 250, 12, 56, DKWOOD)
    p.color(INK)
    p.cmd(0x23, bytes([0x40 | 2]))
    p.pel(3)
    p.line([(596, 112), (596, 250)], INK, 3)
    p.line([(432, 296), (568, 296)], INK, 3)
    p.cmd(0x23, b'\x40')
    p.say(596, 104, '10 IN', SMALL, INK, 'c')
    p.say(500, 322, '7 IN', SMALL, INK, 'c')


def ad_band(p, top, label=True):
    p.rect(0, top, 640, 446 - top, HAZARD)
    p.fillpoly([(0, top), (640, top), (640, top + 10), (0, top + 10)], BLACK, 1, 6)
    if label:
        p.say(14, top + 32, 'BIRCH & BOLT HARDWARE', BODY, BLACK)
        p.say(14, top + 56, 'TODAY:', BODY, BLACK)
        character(p, DRILL_ICON, 84, top + 62, ICON_W, ICON_H, BLACK)
        p.say(134, top + 56, 'CORDLESS DRILL $39.99', BODY, BLACK)
        p.bevel(530, top + 18, 96, 40, ORANGE, WHITE, DKSTEEL, 3)
        p.say(578, top + 46, 'LOOK', LARGE, BLACK, 'c')


def drill(p, x, y):
    # chuck and bit
    p.rect(x + 214, y + 36, 84, 6, DKSTEEL)
    for i in range(11):
        p.poly([(x + 300 + i * 14, y + 33), (x + 310 + i * 14, y + 33), (x + 304 + i * 14, y + 48), (x + 296 + i * 14, y + 48)], STEEL)
        p.line([(x + 300 + i * 14, y + 33), (x + 296 + i * 14, y + 48)], DKSTEEL, 1)
    p.rect(x + 296, y + 40, 150, 3, STEEL)
    p.poly([(x + 436, y + 38), (x + 468, y + 41), (x + 436, y + 44)], STEEL)
    p.poly([(x + 200, y + 14), (x + 266, y + 14), (x + 296, y + 28), (x + 296, y + 52), (x + 266, y + 66), (x + 200, y + 66)], STEEL)
    p.poly([(x + 214, y + 18), (x + 266, y + 18), (x + 288, y + 30), (x + 214, y + 30)], WHITE)
    for i in range(5):
        p.line([(x + 226 + i * 14, y + 14), (x + 226 + i * 14, y + 66)], DKSTEEL, 2)
    # housing
    p.poly([(x, y + 28), (x + 40, y), (x + 206, y), (x + 206, y + 84), (x + 140, y + 98), (x + 40, y + 98), (x, y + 70)], HAZARD)
    p.poly([(x, y + 70), (x, y + 28), (x + 40, y), (x + 60, y), (x + 20, y + 28), (x + 20, y + 80)], ORANGE)
    p.rect(x + 66, y + 20, 100, 24, BLACK)
    p.say(x + 116, y + 38, 'CORDLESS', SMALL, HAZARD, 'c')
    p.poly([(x + 206, y), (x + 206, y + 84), (x + 220, y + 80), (x + 220, y + 4)], BLACK)
    # grip and trigger
    p.poly([(x + 54, y + 96), (x + 112, y + 96), (x + 134, y + 232), (x + 78, y + 242)], BLACK)
    p.fillpoly([(x + 54, y + 96), (x + 112, y + 96), (x + 134, y + 232), (x + 78, y + 242)], DKSTEEL, 2, 4)
    p.poly([(x + 112, y + 98), (x + 132, y + 98), (x + 150, y + 124), (x + 132, y + 128), (x + 118, y + 112)], DKSTEEL)
    p.poly([(x + 108, y + 108), (x + 124, y + 110), (x + 134, y + 134), (x + 120, y + 134)], RED)
    # battery pack
    p.poly([(x + 36, y + 236), (x + 160, y + 224), (x + 168, y + 266), (x + 40, y + 280)], BLACK)
    p.poly([(x + 40, y + 240), (x + 156, y + 228), (x + 160, y + 242), (x + 44, y + 254)], HAZARD)
    p.rect(x + 80, y + 256, 60, 8, ORANGE)


def starburst(p, cx, cy):
    # three nested layers: each takes its own colour-map entry so BLINK can chase them
    p.burst(cx, cy, 112, 86, 18, BURST_A, 3)
    p.burst(cx, cy, 90, 70, 18, BURST_B, 12)
    p.burst(cx, cy, 70, 56, 18, BURST_C, 3)
    p.say(cx, cy + 16, 'SALE', BIG, BLACK, 'c')


def build():
    p = Screen('1e2024 ffffff ffcc00 0b0b0b c5ccd2 7c858d e0301e ff7a00 1d7a8c f2ead3 c58b4e 7a4a22 e0301e ff7a00 ffd400 2b2b2b')
    define_character(p, DRILL_ICON, ICON_W, ICON_H, DRILL_SHAPES)
    p.rect(0, 0, 640, 480, CHAR)
    p.rect(0, 0, 640, 44, BLACK)
    p.say(14, 32, 'THE SATURDAY PAGE', LARGE, HAZARD)
    p.say(626, 32, '196', LARGE, HAZARD, 'r')
    p.rect(0, 446, 640, 34, BLACK)
    p.say(14, 470, '0 INDEX   8 BACK   9 NEXT', BODY, STEEL)
    article(p)
    ad_band(p, 380)
    p.blink(ORANGE, HAZARD, 4, 4)
    p.wait(24)
    # the band rises until the advertisement fills the page
    for top in (330, 260, 170, 90, 44):
        ad_band(p, top, label=False)
        p.wait(2)
    p.rect(0, 44, 640, 402, BLACK)
    rays(p, 520, 178, 24, CHAR, 0, 44, 640, 446, 0, .5)
    p.rect(0, 44, 640, 36, HAZARD)
    p.say(14, 72, 'BIRCH & BOLT HARDWARE', LARGE, BLACK)
    p.say(626, 72, 'TODAY ONLY', BODY, BLACK, 'r')
    drill(p, 36, 150)
    p.wait(6)
    starburst(p, 520, 178)
    p.say(520, 326, '$39.99', HEAD, HAZARD, 'c')
    p.say(520, 354, 'WAS $54.99', BODY, STEEL, 'c')
    p.line([(520, 310), (520, 301)], STEEL, 1)
    p.wait(8)
    p.line([(450, 352), (590, 332)], RED, 4)
    p.bevel(404, 384, 224, 52, ORANGE, WHITE, DKSTEEL, 3)
    p.say(516, 420, 'PRESS LOOK', LARGE, BLACK, 'c')
    p.blink(BURST_A, BURST_C, 3, 6, 0)
    p.blink(BURST_B, BURST_A, 3, 6, 3)
    p.blink(BURST_C, BURST_B, 3, 6, 6)
    return p


if __name__ == '__main__':
    save(__file__, build)
