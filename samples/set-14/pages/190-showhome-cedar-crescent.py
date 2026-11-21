from _kit import *

META = dict(title='The Showhome on Cedar Crescent',
            purpose='A realty listing that lets a buyer see a house, its floor plan and its mortgage without leaving home.',
            style='Brick and cream listing sheet with a house elevation and a labelled plan',
            techniques=['filled polygons', 'rectangles', 'native circles', 'hatch fill', 'dotted line texture', 'colour-map change', 'WAIT', 'BLINK', 'proportional text'],
            animated=True)

CREAM, INK, WHITE, BRICK, DKBRICK, ROOF, SIDING, SKY, GRASS, DKGRASS, TEAL, WOOD, GLASS, TAN, PALEBLUE, TAG = range(16)

PX, PY = 328, 58


def elevation(p):
    p.rect(16, 56, 292, 272, SKY)
    p.disc(262, 92, 20, TAG)
    p.rect(16, 262, 292, 66, GRASS)
    p.fillrect(16, 262, 292, 66, DKGRASS, 2, 4)
    p.rect(16, 258, 292, 6, DKGRASS)
    # tree
    p.rect(40, 206, 10, 62, WOOD)
    p.disc(45, 192, 32, DKGRASS)
    p.disc(34, 204, 20, GRASS)
    p.disc(58, 200, 18, GRASS)
    # house body with siding bands and brick base
    p.rect(84, 178, 198, 90, SIDING)
    p.fillrect(84, 178, 198, 90, TAN, 2, 5)
    p.rect(84, 238, 198, 30, BRICK)
    p.fillrect(84, 238, 198, 30, DKBRICK, 3, 7)
    p.poly([(70, 182), (183, 114), (296, 182)], ROOF)
    p.poly([(84, 182), (183, 124), (282, 182)], DKBRICK)
    p.line([(70, 182), (183, 114), (296, 182)], INK, 2)
    for dx, dy, r in ((248, 96, 7), (256, 82, 9), (268, 66, 11)):
        p.disc(dx, dy, r, WHITE)
    p.rect(238, 118, 18, 48, BRICK)
    p.rect(234, 114, 26, 8, DKBRICK)
    p.poly([(183, 132), (212, 150), (154, 150)], WHITE)
    p.rect(176, 140, 14, 12, GLASS)
    # door and windows
    p.rect(166, 204, 34, 64, WOOD)
    p.rect(171, 210, 24, 22, GLASS)
    p.disc(193, 246, 2, TAG)
    p.rect(160, 198, 46, 8, WHITE)
    for wx in (98, 224):
        p.rect(wx, 200, 44, 34, WHITE)
        p.rect(wx + 4, 204, 36, 26, GLASS)
        p.rect(wx + 20, 204, 4, 26, WHITE)
        p.rect(wx - 8, 200, 8, 34, TEAL)
        p.rect(wx + 44, 200, 8, 34, TEAL)
    # path and garage door
    p.poly([(168, 268), (198, 268), (212, 326), (150, 326)], TAN)
    p.rect(268, 250, 2, 18, INK)
    # sign
    p.rect(26, 286, 4, 40, WOOD)
    p.rect(14, 272, 54, 22, WHITE)
    p.frame(14, 272, 54, 22, TEAL, 2)
    p.say(41, 289, 'OPEN', SMALL, TEAL, 'c')
    p.poly([(16, 62), (96, 62), (16, 128)], TAG)
    p.say(28, 92, 'NEW', SMALL, INK)


ROOMS = [
    ('BED 1', 0, 0, 100, 106, TAN), ('BATH', 100, 0, 60, 106, PALEBLUE),
    ('BED 2', 160, 0, 70, 106, TAN), ('BED 3', 230, 0, 66, 106, TAN),
    ('LIVING', 0, 138, 120, 124, SIDING), ('DINING', 120, 138, 66, 124, WHITE),
    ('KITCHEN', 186, 138, 110, 68, PALEBLUE), ('BATH', 186, 206, 110, 56, PALEBLUE),
]


def plan_rooms(p):
    p.rect(PX - 4, PY - 4, 304, 272, INK)
    p.rect(PX, PY + 106, 296, 32, CREAM)
    for name, x, y, w, h, c in ROOMS:
        p.rect(PX + x + 2, PY + y + 2, w - 4, h - 4, c)
    p.rect(PX + 2, PY + 108, 292, 28, WHITE)


def bed(p, x, y, w=40, h=54):
    p.rect(x, y, w, h, WHITE)
    p.frame(x, y, w, h, INK, 2)
    p.rect(x + 3, y + 3, w - 6, 14, PALEBLUE)
    p.rect(x + 3, y + 24, w - 6, h - 28, TEAL)


def tub(p, x, y, w=46, h=20):
    p.rect(x, y, w, h, WHITE)
    p.frame(x, y, w, h, INK, 2)
    p.rect(x + 4, y + 4, w - 12, h - 8, SKY)
    p.disc(x + w - 5, y + h / 2, 2, INK)


def furniture(p):
    ox, oy = PX, PY
    bed(p, ox + 30, oy + 10)
    bed(p, ox + 172, oy + 10, 40, 54)
    bed(p, ox + 244, oy + 10, 36, 54)
    tub(p, ox + 106, oy + 12, 48, 20)
    p.disc(ox + 120, oy + 56, 7, WHITE)
    p.frame(ox + 113, oy + 49, 14, 14, INK, 2)
    # living: sofa, table and rug
    p.rect(ox + 12, oy + 148, 14, 66, BRICK)
    p.rect(ox + 42, oy + 168, 40, 26, WOOD)
    p.rect(ox + 60, oy + 214, 52, 8, INK)
    # dining: round table and four chairs
    p.disc(ox + 153, oy + 184, 20, WOOD)
    for dx, dy in ((-30, 0), (30, 0), (0, -30), (0, 30)):
        p.disc(ox + 153 + dx, oy + 184 + dy, 6, DKBRICK)
    # kitchen: counter along two walls with a stove
    p.rect(ox + 190, oy + 142, 102, 14, ROOF)
    p.rect(ox + 278, oy + 142, 14, 60, ROOF)
    for dx in (210, 234):
        p.disc(ox + dx, oy + 149, 4, INK)
    tub(p, ox + 196, oy + 220, 46, 18)
    p.disc(ox + 270, oy + 230, 8, WHITE)


def plan_labels(p):
    for name, x, y, w, h, c in ROOMS:
        p.say(PX + x + w / 2, PY + y + h - 8, name, SMALL, INK, 'c')
    for x in (30, 112, 170, 240):
        p.rect(PX + x, PY + 104, 24, 6, WHITE)
        p.arc((PX + x, PY + 108), (PX + x + 8, PY + 112), (PX + x + 24, PY + 96), INK)
    p.rect(PX + 118, PY + 258, 28, 6, TAG)


def tour(p):
    """A dotted walk-through from the front door to the bedrooms."""
    p.color(BRICK)
    p.cmd(0x23, bytes([0x40 | 2]))
    p.pel(3)
    p.line([(PX + 132, PY + 256), (PX + 132, PY + 124), (PX + 58, PY + 124), (PX + 58, PY + 118)], BRICK, 3)
    p.line([(PX + 132, PY + 124), (PX + 264, PY + 124), (PX + 264, PY + 118)], BRICK, 3)
    p.cmd(0x23, b'\x40')
    p.poly([(PX + 50, PY + 118), (PX + 66, PY + 118), (PX + 58, PY + 106)], BRICK)
    p.poly([(PX + 256, PY + 118), (PX + 272, PY + 118), (PX + 264, PY + 106)], BRICK)


def stats(p):
    p.say(18, 360, 'THE SHOWHOME, CEDAR CRESCENT', BODY, TEAL)
    bed(p, 18, 372, 26, 24)
    p.say(52, 392, '3 BED', BODY, INK)
    tub(p, 140, 376, 30, 16)
    p.say(178, 392, '2 BATH', BODY, INK)
    p.poly([(262, 396), (262, 380), (276, 372), (290, 380), (290, 396)], WOOD)
    p.say(298, 392, '1,320 SQ FT', BODY, INK)
    p.say(18, 424, '13.25% FIXED: ABOUT $876 A MONTH', BODY, DKBRICK)


def build():
    p = Screen('f4ecd4 20242c ffffff b5452f 7d2c1f 4a5560 e8c15a 9fd6f2 4caf50 2e7d32 0f6b73 8a5a2b 5aa0c8 e3d0a0 b9d9e8 ff9a1f')
    p.rect(0, 0, 640, 480, CREAM)
    p.rect(0, 0, 640, 44, TEAL)
    p.say(14, 32, 'NORTHGATE REALTY', LARGE, WHITE)
    p.say(626, 32, '190', LARGE, TAG, 'r')
    p.rect(0, 44, 640, 5, TAG)
    p.wait(5)
    elevation(p)
    p.wait(10)
    plan_rooms(p)
    p.wait(8)
    furniture(p)
    p.wait(6)
    plan_labels(p)
    p.wait(8)
    tour(p)
    p.wait(6)
    stats(p)
    p.burst(520, 392, 70, 56, 16, TAG, 5)
    p.say(520, 388, '$84,900', LARGE, INK, 'c')
    p.say(520, 410, 'DOWN $8,490', SMALL, INK, 'c')
    p.rect(0, 446, 640, 34, TEAL)
    p.say(14, 470, '1 BOOK A VIEWING   2 SEE THE MORTGAGE', BODY, WHITE)
    p.blink(TAG, SIDING, 6, 6)
    p.wait(15)
    p.set_palette(GLASS, 'ffe27a')   # the showhome's windows light up
    return p


if __name__ == '__main__':
    save(__file__, build)
