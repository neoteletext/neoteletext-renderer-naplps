import math
from _page import Plate, save, arc_points, measure

META = dict(title='Weather Map of the Westmark',
            purpose='The afternoon forecast map of an invented prairie region: town symbols, temperatures, '
                    'and a cold front that arrives last.',
            style='Flat green land on a deep blue sea, symbols as programmable characters, cream temperature tags',
            techniques=['DRCS weather symbols overlaid in two colours', 'WAIT before the fronts', 'the same DRCS symbols reused small in the outlook',
                        'dashed and dotted line textures', 'wind arrow', 'BLINK storm bolt and rain', 'rain area in a defined texture of drops, shimmering with the rain entry', 'native hatching', 'filled polygons'],
            animated=True)

PALETTE = ('163a78 ffffff 5aa04a 3d7f3a 3a7fd0 ffd23a dfe6ee 8f9cb0 '
           '58c8ff 1f4fd8 e0302a 0a1a3a fff4d0 10203a ffe86a f08020').split()
SEA, WHITE, LAND, FIELD, LAKE, SUN, CLOUD, SHADE, RAIN, COLD, WARM, BAND, TAG, INK, BOLT, HOT = range(16)
RIVER = LAKE

SUN_C, CLOUD_C, RAIN_C, BOLT_C, SMALL_CLOUD_C = 0x21, 0x22, 0x23, 0x24, 0x25
SIDE = 64  # the symbols' square field, in 640-pixel units


def symbols(p):
    rays = []
    for i in range(8):
        a = math.radians(i * 45)
        c, s = math.cos(a), math.sin(a)
        rays.append([(0.5 + 0.30 * c - 0.06 * s, 0.5 + 0.30 * s + 0.06 * c),
                     (0.5 + 0.46 * c, 0.5 + 0.46 * s),
                     (0.5 + 0.30 * c + 0.06 * s, 0.5 + 0.30 * s - 0.06 * c)])
    p.define_drcs(SUN_C, SIDE, SIDE * 0.96, [('disc', 0.5, 0.5, 0.22)] + rays)
    p.define_drcs(CLOUD_C, SIDE, SIDE * 0.96,
                  [('disc', 0.30, 0.40, 0.17), ('disc', 0.52, 0.52, 0.22), ('disc', 0.74, 0.40, 0.15),
                   ('rect', 0.14, 0.25, 0.74, 0.16)])
    p.define_drcs(RAIN_C, SIDE, SIDE * 0.96,
                  [[(x, 0.20), (x + 0.05, 0.20), (x - 0.04, 0.02), (x - 0.09, 0.02)] for x in (0.30, 0.50, 0.70)])
    p.define_drcs(BOLT_C, SIDE, SIDE * 0.96,
                  [[(0.52, 0.30), (0.66, 0.30), (0.56, 0.16), (0.66, 0.16), (0.40, -0.0), (0.48, 0.12), (0.40, 0.12)]])
    p.define_drcs(SMALL_CLOUD_C, SIDE, SIDE * 0.96,
                  [('disc', 0.52, 0.34, 0.15), ('disc', 0.70, 0.40, 0.17), ('disc', 0.86, 0.32, 0.11),
                   ('rect', 0.40, 0.20, 0.54, 0.13)])


LAND_SHAPE = [(18, 140), (60, 98), (140, 90), (200, 112), (262, 98), (330, 106), (382, 86), (432, 98),
              (470, 128), (520, 118), (598, 138), (624, 188), (610, 258), (624, 330), (598, 398),
              (520, 410), (420, 402), (330, 412), (240, 402), (150, 410), (60, 402), (24, 360),
              (36, 290), (14, 220)]

TOWNS = [  # name, dot, symbol, temperature
    ('ORRIN', (156, 200), 'storm', 14),
    ('TASKER', (292, 196), 'part', 22),
    ('NINEFIELD', (514, 206), 'sun', 27),
    ('PELLHAM', (168, 330), 'rain', 16),
    ('BRACKWATER', (372, 330), 'part', 25),
    ('SEDGELY', (552, 346), 'sun', 28),
]


def symbol(p, kind, x, y):
    """Draw a town's symbol with its lower left at (x, y)."""
    if kind == 'sun':
        p.chars(x, y, [SUN_C], SIDE, SIDE * 0.96, SUN)
    elif kind == 'part':
        p.chars(x - 8, y - 6, [SUN_C], SIDE, SIDE * 0.96, SUN)
        p.chars(x, y, [SMALL_CLOUD_C], SIDE, SIDE * 0.96, CLOUD)
    elif kind == 'rain':
        p.chars(x, y, [RAIN_C], SIDE, SIDE * 0.96, RAIN)
        p.chars(x, y, [CLOUD_C], SIDE, SIDE * 0.96, CLOUD)
    else:
        p.chars(x, y, [BOLT_C], SIDE, SIDE * 0.96, BOLT)
        p.chars(x, y, [CLOUD_C], SIDE, SIDE * 0.96, SHADE)


def build():
    p = Plate('198', PALETTE)
    symbols(p)
    p.rect(0, 0, 640, 52, BAND)
    p.text(18, 38, 'WESTMARK WEATHER', 20, 30, WHITE)
    p.rtext(622, 36, 'TUES 4 PM', 15, 24, SUN, prop=False)
    p.poly(LAND_SHAPE, LAND)
    # The eastern province in a deeper green, east of the provincial line.
    p.poly([(450, 96), (470, 128), (520, 118), (598, 138), (624, 188), (610, 258), (624, 330), (598, 398),
            (520, 410), (452, 404), (458, 250)], FIELD)
    p.text(470, 76, 'Kestrel Bay', 14, 22, RAIN)
    p.poly([(586, 82), (600, 70), (618, 74), (624, 88), (604, 94)], FIELD)
    p.poly([(400, 70), (414, 64), (424, 72), (410, 78)], LAND)
    # Cultivated land in the south: native horizontal hatching over the green.
    p.hatch(2)
    p.poly([(36, 290), (240, 280), (420, 296), (456, 296), (452, 404), (420, 402),
            (330, 412), (240, 402), (150, 410), (60, 402), (24, 360)], FIELD)
    p.solid()
    p.poly([(250, 220), (290, 208), (340, 214), (352, 236), (318, 252), (270, 248)], LAKE)
    p.line([(352, 236), (400, 250), (430, 280), (470, 300), (520, 360), (530, 408)], RIVER, 3)
    p.line([(270, 248), (230, 280), (200, 330), (210, 404)], RIVER, 3)
    # The provincial line, dashed.
    p.pel(3).cmd(0x23, b'\x42')
    p.line([(450, 106), (458, 250), (452, 404)], WHITE, 3)
    p.cmd(0x23, b'\x40')

    # Where it is raining now, as the radar sees it: hatching in the rain entry, which shimmers as it blinks.
    p.define_texture('A', 12, [[(0.1, 0.5), (0.35, 0.5), (0.25, 0.95)], [(0.6, 0.05), (0.85, 0.05), (0.75, 0.5)]])
    p.cmd(0x23, b'\x60')
    p.poly([(36, 168), (90, 128), (170, 136), (226, 178), (232, 256), (214, 330), (180, 378), (110, 392),
            (52, 360), (30, 280)], RAIN)
    p.solid()
    # The highway between the towns, dotted.
    p.pel(2).cmd(0x23, b'\x41')
    roads = [[(156, 200), (292, 196), (514, 206)], [(292, 196), (372, 330), (552, 346)], [(168, 330), (372, 330)]]
    for road in roads:
        p.line(road, TAG, 2)
    p.cmd(0x23, b'\x40')
    for name, (x, y), kind, temp in TOWNS:
        symbol(p, kind, x - SIDE / 2, y - 6)
        p.disc(x, y, 6, INK)
        p.disc(x, y, 3, WHITE)
        # A chip under each town: its name on cream, its temperature on a coloured end.
        name_width = measure(name, 13) + 8
        left = x - (name_width + 40) / 2
        p.rect(left, y + 10, name_width + 40, 28, TAG)
        p.text(left + 6, y + 32, name, 13, 20, INK)
        p.rect(left + name_width + 4, y + 10, 36, 28, HOT if temp >= 25 else COLD)
        p.ctext(left + name_width + 22, y + 33, str(temp), 14, 22, WHITE, prop=False)

    p.rect(0, 418, 640, 62, BAND)
    p.text(16, 442, 'Front reaches Orrin 6 pm', 14, 22, WHITE)
    # The outlook: the same programmable symbols, drawn small.
    small = 30
    for i, (day, kind, temp) in enumerate([('WED', 'part', 21), ('THU', 'sun', 24), ('FRI', 'rain', 15)]):
        x = 16 + i * 160
        p.text(x, 474, day, 13, 20, SUN, prop=False)
        if kind == 'sun':
            p.chars(x + 46, 476, [SUN_C], small, small * 0.96, SUN)
        elif kind == 'part':
            p.chars(x + 42, 473, [SUN_C], small, small * 0.96, SUN)
            p.chars(x + 46, 476, [SMALL_CLOUD_C], small, small * 0.96, CLOUD)
        else:
            p.chars(x + 46, 476, [RAIN_C], small, small * 0.96, RAIN)
            p.chars(x + 46, 476, [CLOUD_C], small, small * 0.96, CLOUD)
        p.text(x + 84, 474, str(temp), 13, 20, WHITE, prop=False)
    p.wait(15)
    # Low pressure, the cold front sweeping south-west and the warm front east.
    p.disc(200, 104, 22, WARM)
    p.ctext(200, 118, 'L', 22, 32, WHITE, prop=False)
    cold = [(182, 118), (122, 138), (72, 186), (42, 250), (30, 320)]
    p.line(cold, COLD, 6)
    for (x0, y0), (x1, y1) in zip(cold, cold[1:]):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        # Teeth on the side the front is moving toward, the south-east.
        p.poly([(mx - ux * 14, my - uy * 14), (mx + ux * 14, my + uy * 14),
                (mx + uy * 22, my - ux * 22)], COLD)
    # The wind behind the front.
    p.poly([(40, 150), (76, 176), (82, 168), (94, 196), (64, 190), (70, 182), (34, 158)], WHITE)
    p.text(22, 140, 'NW 40', 13, 20, WHITE, prop=False)
    warm = [(222, 104), (290, 110), (360, 106), (436, 116)]
    p.line(warm, WARM, 6)
    for (x0, y0), (x1, y1) in zip(warm, warm[1:]):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        p.poly(arc_points(mx, my, 13, 13, 180, 360, 10), WARM)
    p.rtext(624, 442, 'FRONTS p 302', 14, 22, SUN, prop=False)
    # The storm's bolt flickers and the rain falls by turns.
    p.blink(BOLT, SHADE, 2, 6)
    p.blink(RAIN, CLOUD, 4, 4, 2)
    return p


if __name__ == '__main__':
    save(__file__, build)
