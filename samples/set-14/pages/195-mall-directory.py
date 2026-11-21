from _kit import *

META = dict(title='The Mall Directory',
            purpose='A shopping-centre kiosk page: two floor plans in pastel, numbered stores, a blinking YOU ARE HERE and a column of touch targets.',
            style='Navy kiosk with pastel store blocks and bevelled touch keys',
            techniques=['rectangles', 'bevelled keys', 'DRCS', 'hatch fill', 'dotted line texture', 'native circles', 'WAIT', 'BLINK', 'proportional text'],
            animated=True)

NAVY, WHITE, CREAM, INK, PINK, MINT, LAVENDER, PEACH, SKY, BUTTER, RED, SLATE, GOLD, TEAL, GREY, FLASH = range(16)
PASTELS = [PINK, MINT, LAVENDER, PEACH, SKY, BUTTER]

TOUCHED = 5
STORES = {1: 'OAKLEAF', 2: 'HEELS', 3: 'CABOOSE', 4: 'SPINDLE', 5: 'CRUMB',
          6: 'RIVER CREDIT', 7: 'SNAPSHOT', 8: 'KITE', 9: 'PETAL', 10: 'LANTERN'}

ICON_SCALE = 1.2
ICON_W, ICON_H = round(28 * ICON_SCALE), round(22 * ICON_SCALE)


def scaled(shapes):
    out = []
    for shape in shapes:
        kind = shape[0]
        if kind == 'poly':
            out.append((kind, [(x * ICON_SCALE, y * ICON_SCALE) for x, y in shape[1]]))
        elif kind in ('line', 'cut'):
            out.append((kind, [(x * ICON_SCALE, y * ICON_SCALE) for x, y in shape[1]], shape[2] * ICON_SCALE))
        else:
            out.append((kind, *(v * ICON_SCALE for v in shape[1:])))
    return out


def ring_shape(x, y, outer, inner):
    return [('disc', x, y, outer), ('hole', x, y, inner)]


ICONS = {
    1: [('poly', [(2, 3), (26, 3), (26, 20), (2, 20)]), ('cut', [(6, 3), (6, 20)], 1.4), ('cut', [(10, 8), (22, 8)], 1.2), ('cut', [(10, 12), (22, 12)], 1.2), ('cut', [(10, 16), (18, 16)], 1.2)],
    2: [('poly', [(2, 6), (10, 6), (12, 12), (26, 14), (26, 20), (2, 20)])],
    3: [('poly', [(2, 6), (20, 6), (20, 15), (2, 15)]), ('poly', [(20, 10), (26, 10), (26, 15), (20, 15)]), ('disc', 7, 18, 3), ('disc', 17, 18, 3)],
    4: ring_shape(14, 11, 10, 3) + [('line', [(14, 11), (20, 5)], 1)],
    5: [('poly', [(2, 18), (14, 4), (26, 18)]), ('poly', [(2, 18), (26, 18), (26, 21), (2, 21)]), ('hole', 14, 14, 2)],
    6: ring_shape(14, 11, 10, 7) + [('poly', [(12, 6), (16, 6), (16, 16), (12, 16)])],
    7: [('poly', [(2, 7), (26, 7), (26, 20), (2, 20)]), ('poly', [(9, 3), (19, 3), (19, 7), (9, 7)]), ('hole', 14, 13, 5), ('disc', 14, 13, 2)],
    8: [('poly', [(2, 4), (26, 4), (26, 19), (2, 19)]), ('cut', [(2, 4), (14, 12), (26, 4)], 1.5)],
    9: [('disc', 14, 5, 4), ('disc', 14, 17, 4), ('disc', 6, 11, 4), ('disc', 22, 11, 4), ('disc', 14, 11, 4), ('hole', 14, 11, 1.5)],
    10: [('poly', [(4, 6), (20, 6), (18, 20), (6, 20)]), ('line', [(20, 8), (25, 8), (25, 14), (19, 14)], 2), ('line', [(8, 2), (10, 4), (8, 5)], 1)],
}


FLOOR_X, FLOOR_W, FLOOR_H = 12, 392, 168
UPPER_Y, LOWER_Y = 58, 266
CORRIDOR = 44
STORE_H = (FLOOR_H - CORRIDOR - 8) // 2


def floor(p, y, top, bottom, label, you_are_here=False):
    p.rect(FLOOR_X, y, FLOOR_W, FLOOR_H, SLATE)
    p.rect(FLOOR_X + 4, y + 4 + STORE_H, FLOOR_W - 8, CORRIDOR, CREAM)
    p.fillrect(FLOOR_X + 4, y + 4 + STORE_H, FLOOR_W - 8, CORRIDOR, GREY, 3, 10)
    corridor_y = y + 4 + STORE_H
    p.say(FLOOR_X + 12, corridor_y + 28, label, BODY, INK)
    xs_top = [FLOOR_X + 4 + i * 128 for i in range(3)]
    for n, x in zip(top, xs_top):
        store(p, n, x, y + 4, 124 if x != xs_top[-1] else FLOOR_X + FLOOR_W - 4 - x, STORE_H)
    widths_bottom = [(FLOOR_X + 4, 150), (FLOOR_X + 158, 150)] if len(bottom) == 2 else []
    for n, (x, w) in zip(bottom, widths_bottom):
        store(p, n, x, corridor_y + CORRIDOR + 0, w, STORE_H, 'top')
    # escalator well at the end of the corridor, at the same place on both floors
    p.rect(FLOOR_X + FLOOR_W - 4 - 70, corridor_y + CORRIDOR, 66, STORE_H, TEAL)
    p.fillrect(FLOOR_X + FLOOR_W - 4 - 70, corridor_y + CORRIDOR, 66, STORE_H, WHITE, 2, 5)
    p.say(FLOOR_X + FLOOR_W - 4 - 37, corridor_y + CORRIDOR + STORE_H / 2 + 7, 'UP' if y == LOWER_Y else 'DOWN', SMALL, INK, 'c')


def store(p, number, x, y, w, h, door='bottom'):
    p.rect(x, y, w - 4, h - 4 if y < LOWER_Y else h - 4, PASTELS[(number - 1) % 6])
    p.frame(x, y, w - 4, h - 4, INK, 2)
    p.say(x + (w - 4) / 2, y + (h - 4) / 2 + 9, str(number), LARGE, INK, 'c')
    gap_y = y + h - 8 if door == 'bottom' else y - 1
    p.rect(x + (w - 4) / 2 - 15, gap_y, 30, 5, CREAM)


def legend_row(p, number, y):
    colour = PASTELS[(number - 1) % 6]
    if number == TOUCHED:
        p.bevel(412, y, 220, 30, colour, SLATE, WHITE, 3)
        p.frame(410, y - 2, 224, 34, GOLD, 3)
    else:
        p.bevel(412, y, 220, 30, colour, WHITE, SLATE, 2)
    p.say(424, y + 22, str(number), BODY, INK)
    character(p, 0x20 + number, 448, y + 28, ICON_W, ICON_H, INK)
    p.say(488, y + 22, STORES[number], BODY, INK)


def fountain(p):
    cy = UPPER_Y + 4 + STORE_H + CORRIDOR // 2
    cx = FLOOR_X + 250
    p.ellipse(cx, cy, 36, 17, SLATE)
    p.ellipse(cx, cy, 31, 14, SKY)
    p.ellipse(cx, cy, 20, 8, WHITE)
    p.rect(cx - 2, cy - 14, 4, 14, WHITE)
    p.disc(cx, cy - 15, 4, WHITE)
    for dx in (-110, 110):
        p.disc(cx + dx, cy, 9, TEAL)
        p.disc(cx + dx, cy - 3, 6, MINT)


def route(p):
    mx = FLOOR_X + 250
    my = LOWER_Y + 4 + STORE_H + CORRIDOR // 2
    bottom = LOWER_Y + 4 + STORE_H + CORRIDOR
    p.color(RED)
    p.cmd(0x23, bytes([0x40 | 2]))
    p.pel(3)
    p.line([(mx - 80, my + 8), (FLOOR_X + 196, my + 8), (FLOOR_X + 196, bottom + 20)], RED, 3)
    p.cmd(0x23, b'\x40')
    p.poly([(FLOOR_X + 186, bottom + 18), (FLOOR_X + 206, bottom + 18), (FLOOR_X + 196, bottom + 34)], RED)


def build():
    p = Screen('14213d ffffff f4ecd6 1c2233 f7b6c8 b8ecd0 cdbdf2 ffd0a6 a9d8f5 fbeaa0 e5383b 5c6784 f2b632 2a9d8f cfd4de ffffff')
    p.rect(0, 0, 640, 480, NAVY)
    p.rect(0, 0, 640, 44, TEAL)
    p.say(14, 32, 'RIVERSIDE GALLERIA', LARGE, WHITE)
    p.say(626, 32, '195', LARGE, WHITE, 'r')
    p.rect(0, 44, 640, 5, GOLD)
    p.rect(0, 446, 640, 34, TEAL)
    p.say(14, 470, '5 CRUMB DELI: FOLLOW THE DOTTED LINE', BODY, WHITE)
    for number, shapes in ICONS.items():
        define_character(p, 0x20 + number, ICON_W, ICON_H, scaled(shapes))
    p.wait(4)
    floor(p, UPPER_Y, [6, 7, 8], [9, 10], 'UPPER LEVEL')
    p.wait(6)
    floor(p, LOWER_Y, [1, 2, 3], [4, 5], 'LOWER LEVEL', True)
    p.wait(6)
    fountain(p)
    route(p)
    p.say(420, 78, 'TOUCH A NUMBER', BODY, GOLD)
    for n in range(1, 11):
        legend_row(p, n, 86 + (n - 1) * 35 + (n - 1) // 5 * 4)
        p.wait(1)
    # marker
    mx, my = FLOOR_X + 250, LOWER_Y + 4 + STORE_H + CORRIDOR // 2
    p.rect(mx - 78, my - 16, 150, 26, RED)
    p.say(mx - 3, my + 4, 'YOU ARE HERE', SMALL, FLASH, 'c')
    p.poly([(mx + 72, my - 16), (mx + 92, my - 3), (mx + 72, my + 10)], RED)
    p.disc(mx + 100, my - 3, 6, RED)
    p.blink(FLASH, BUTTER, 5, 5)
    return p


if __name__ == '__main__':
    save(__file__, build)
