from _page import Plate, save, arc_points, star_points

META = dict(title='The Electronic Front Page',
            purpose='The morning newspaper arrives on the television: an invented city daily\'s videotext front page, '
                    'three stories with drawn icons and the page number to key for each.',
            style='Broadsheet masthead in red and cream over ruled story rows, poster-flat icons',
            techniques=['WAIT between stories', 'BLINK late-news tag', 'WAIT, then the planned bridge in dashed arc and line', 'offset shadow nameplate', 'native circles', 'filled polygons',
                        'proportional and fixed-pitch stroke text', 'keycap index of other departments', 'a picture repainted after a WAIT so the rocket lifts off'],
            animated=True)

PALETTE = ('0b1530 f4ecd6 15244a c8283a f2b83a 6fa8dc d9d2bd ffffff '
           '3f9a4a c99b62 e8eef4 ff7a1e 8a97b0 7a1020 2f6fae 2f5f9e').split()
NIGHT, PAPER, INK, RED, GOLD, SKY, STONE, WHITE, GRASS, TAN, METAL, FLAME, RULE, DEEP, WATER, BLUE = range(16)


def lead_picture(p, x, y):
    """City hall on the hill, the harbour, and the bridge the council approved, drawn in outline."""
    w, h = 300, 160
    p.rect(x, y, w, h, SKY)
    p.disc(x + 250, y + 34, 18, GOLD)
    # Clouds and the paper's own gulls over the water.
    for cx, cy, r in [(x + 150, y + 30, 12), (x + 166, y + 24, 15), (x + 184, y + 30, 11)]:
        p.disc(cx, cy, r, WHITE)
    p.rect(x + 140, y + 30, 54, 10, WHITE)
    for gx, gy in [(x + 200, y + 60), (x + 222, y + 50)]:
        p.line([(gx - 9, gy - 4), (gx - 4, gy - 6), (gx, gy), (gx + 4, gy - 6), (gx + 9, gy - 4)], INK, 2)
    p.rect(x, y + 108, w, 52, WATER)
    for wx in range(x + 10, x + w - 20, 34):
        p.line([(wx, y + 124), (wx + 16, y + 124)], METAL, 2)
        p.line([(wx + 14, y + 142), (wx + 30, y + 142)], METAL, 2)
    p.poly([(x + 190, y + 108), (x + 214, y + 92), (x + w, y + 88), (x + w, y + 108)], GRASS)
    # A ferry crossing where the bridge will go.
    p.poly([(x + 150, y + 130), (x + 214, y + 130), (x + 204, y + 142), (x + 158, y + 142)], WHITE)
    p.rect(x + 166, y + 120, 30, 10, WHITE)
    p.rect(x + 172, y + 122, 6, 4, INK)
    p.rect(x + 184, y + 122, 6, 4, INK)
    p.rect(x + 182, y + 110, 6, 10, RED)
    # City hall on its hill.
    p.poly([(x, y + 110), (x, y + 84), (x + 40, y + 74), (x + 96, y + 80), (x + 120, y + 110)], GRASS)
    hx, hy = x + 14, y + 24
    p.rect(hx + 8, hy + 56, 80, 6, WHITE)
    p.rect(hx + 12, hy + 32, 72, 24, STONE)
    for cx in range(hx + 16, hx + 82, 10):
        p.rect(cx, hy + 34, 4, 22, WHITE)
    p.poly([(hx + 8, hy + 33), (hx + 48, hy + 22), (hx + 88, hy + 33)], WHITE)
    p.rect(hx + 34, hy + 14, 28, 8, STONE)
    p.poly(arc_points(hx + 48, hy + 15, 16, 14, 0, 180, 14), WHITE)
    p.rect(hx + 47, hy - 4, 3, 6, INK)
    p.poly([(hx + 50, hy - 4), (hx + 60, hy - 1), (hx + 50, hy + 2)], RED)


def draw_bridge(p, x, y):
    """The planned bridge, drawn after a pause as the artist's plan, dashed because it is not yet built."""
    p.pel(3).cmd(0x23, b'\x42')
    p.color(RED)
    p.arc((x + 96, y + 108), (x + 170, y + 64), (x + 244, y + 108))
    p.line([(x + 80, y + 100), (x + 260, y + 100)], RED, 3)
    p.cmd(0x23, b'\x40')
    for bx in range(x + 116, x + 236, 20):
        p.line([(bx, y + 100), (bx, y + 108)], RED, 2)
    p.rect(x + 6, y + 128, 112, 26, PAPER)
    p.text(x + 12, y + 148, 'THE PLAN', 12, 19, RED, prop=False)


def emblem(p, x, y):
    """The paper's device: a gull over two waves, in cream on the red band."""
    p.disc(x + 30, y + 30, 28, PAPER)
    p.disc(x + 30, y + 30, 24, RED)
    p.line([(x + 14, y + 26), (x + 22, y + 20), (x + 30, y + 26), (x + 38, y + 20), (x + 46, y + 26)], PAPER, 3)
    for wy in (y + 38, y + 46):
        p.line([(x + 12, wy), (x + 20, wy - 4), (x + 30, wy), (x + 40, wy - 4), (x + 48, wy)], PAPER, 2)


def ballpark(p, x, y):
    p.rect(x, y, 120, 84, DEEP)
    p.poly([(x, y + 38), (x + 60, y + 14), (x + 120, y + 38), (x + 120, y + 84), (x, y + 84)], GRASS)
    p.poly([(x + 60, y + 34), (x + 96, y + 56), (x + 60, y + 80), (x + 24, y + 56)], TAN)
    p.poly([(x + 60, y + 44), (x + 82, y + 57), (x + 60, y + 70), (x + 38, y + 57)], GRASS)
    for bx, by in [(x + 60, y + 34), (x + 96, y + 56), (x + 24, y + 56)]:
        p.rect(bx - 3, by - 3, 6, 6, WHITE)
    p.poly([(x + 55, y + 80), (x + 65, y + 80), (x + 60, y + 75)], WHITE)
    p.disc(x + 60, y + 57, 4, TAN)
    # Light towers and a night sky.
    for lx in (x + 10, x + 110):
        p.line([(lx, y + 40), (lx, y + 8)], RULE, 2)
        p.rect(lx - 6, y + 4, 12, 6, GOLD)
    p.disc(x + 32, y + 14, 2, WHITE)
    p.disc(x + 88, y + 12, 2, WHITE)


def rocket(p, x, y):
    p.rect(x, y, 120, 84, INK)
    for sx, sy in [(x + 14, y + 12), (x + 100, y + 22), (x + 24, y + 48), (x + 104, y + 60), (x + 90, y + 8)]:
        p.disc(sx, sy, 1.5, WHITE)
    p.poly([(x, y + 84), (x, y + 74), (x + 30, y + 68), (x + 54, y + 76), (x + 66, y + 76),
            (x + 92, y + 68), (x + 120, y + 74), (x + 120, y + 84)], STONE)
    p.disc(x + 44, y + 74, 9, METAL)
    p.disc(x + 78, y + 74, 9, METAL)
    p.poly([(x + 52, y + 64), (x + 60, y + 84), (x + 68, y + 64)], FLAME)
    p.poly([(x + 56, y + 64), (x + 60, y + 76), (x + 64, y + 64)], GOLD)
    p.poly([(x + 52, y + 22), (x + 68, y + 22), (x + 68, y + 64), (x + 52, y + 64)], METAL)
    p.poly([(x + 52, y + 22), (x + 60, y + 4), (x + 68, y + 22)], RED)
    p.poly([(x + 52, y + 48), (x + 42, y + 66), (x + 52, y + 62)], RED)
    p.poly([(x + 68, y + 48), (x + 78, y + 66), (x + 68, y + 62)], RED)
    p.disc(x + 60, y + 32, 4, WATER)


def rocket_climbing(p, x, y):
    """The same panel repainted a moment later: the rocket has cleared the pad on a column of smoke."""
    p.rect(x, y, 120, 84, INK)
    for sx, sy in [(x + 14, y + 12), (x + 100, y + 22), (x + 24, y + 48), (x + 104, y + 60), (x + 90, y + 8)]:
        p.disc(sx, sy, 1.5, WHITE)
    p.poly([(x, y + 84), (x, y + 74), (x + 30, y + 68), (x + 54, y + 76), (x + 66, y + 76),
            (x + 92, y + 68), (x + 120, y + 74), (x + 120, y + 84)], STONE)
    for cy, r in [(y + 76, 10), (y + 64, 8), (y + 54, 7), (y + 46, 6)]:
        p.disc(x + 60, cy, r, METAL)
    p.poly([(x + 54, y + 36), (x + 60, y + 52), (x + 66, y + 36)], FLAME)
    p.poly([(x + 57, y + 36), (x + 60, y + 44), (x + 63, y + 36)], GOLD)
    p.poly([(x + 54, y + 6), (x + 66, y + 6), (x + 66, y + 36), (x + 54, y + 36)], METAL)
    p.poly([(x + 54, y + 6), (x + 60, y - 6), (x + 66, y + 6)], RED)
    p.poly([(x + 54, y + 24), (x + 46, y + 38), (x + 54, y + 35)], RED)
    p.poly([(x + 66, y + 24), (x + 74, y + 38), (x + 66, y + 35)], RED)


def build():
    p = Plate('197', PALETTE)
    # Masthead with the paper's device and a weather ear.
    p.rect(0, 0, 640, 80, RED)
    p.rect(0, 80, 640, 4, GOLD)
    emblem(p, 12, 10)
    p.text(84, 30, 'THE', 13, 20, GOLD, prop=False)
    # The nameplate in a heavier face: a dark offset shadow, then the cream letters drawn twice.
    p.text(87, 71, 'CALDER BAY COURIER', 25, 38, DEEP)
    p.text(84, 68, 'CALDER BAY COURIER', 25, 38, PAPER)
    p.text(85, 68, 'CALDER BAY COURIER', 25, 38, PAPER)
    p.rect(528, 10, 100, 62, DEEP)
    p.disc(552, 41, 13, GOLD)
    for i in range(8):
        a = i * 45
        x0, y0 = arc_points(552, 41, 16, 16, a, a, 1)[0]
        x1, y1 = arc_points(552, 41, 21, 21, a, a, 1)[0]
        p.line([(x0, y0), (x1, y1)], GOLD, 2)
    p.text(578, 40, '24', 17, 26, PAPER, prop=False)
    p.text(578, 64, 'SUN', 12, 19, GOLD, prop=False)
    p.rect(0, 84, 640, 30, NIGHT)
    p.text(16, 107, 'TUESDAY 14 JUNE 1983', 13, 20, PAPER)
    p.text(270, 107, 'MORNING EDITION', 13, 20, RULE, prop=False)
    p.rtext(624, 107, 'PAGE 100', 13, 20, GOLD, prop=False)
    p.rect(0, 114, 640, 304, PAPER)
    # The lead story takes the top half.
    lead_picture(p, 16, 122)
    p.wait(10)
    draw_bridge(p, 16, 122)
    p.text(332, 150, 'Council votes', 20, 32, INK)
    p.text(332, 186, 'yes to harbour', 20, 32, INK)
    p.text(332, 222, 'bridge', 20, 32, INK)
    p.text(332, 262, '8 to 3 after', 14, 22, DEEP)
    p.text(332, 284, 'a night sitting', 14, 22, DEEP)
    p.rect(542, 242, 82, 40, RED)
    p.ctext(583, 272, '110', 19, 30, PAPER, prop=False)
    p.wait(12)
    p.rect(16, 292, 608, 2, RULE)
    for column, (icon, line1, line2, page) in enumerate([
            (ballpark, 'Gulls take', 'opener 5-3', '140'),
            (rocket, 'Weather', 'satellite up', '160')]):
        x = 16 + column * 312
        if column:
            p.wait(10)
            p.rect(320, 300, 2, 110, RULE)
        icon(p, x, 304)
        p.text(x + 130, 334, line1, 15, 24, INK)
        p.text(x + 130, 362, line2, 15, 24, INK)
        p.rect(x + 130, 372, 60, 32, RED)
        p.ctext(x + 160, 397, page, 15, 24, PAPER, prop=False)
    # Late news tag: entry BLUE blinks to RED.
    p.wait(8)
    p.rect(0, 418, 640, 62, NIGHT)
    p.rect(12, 424, 74, 28, BLUE)
    p.ctext(49, 446, 'LATE', 14, 22, PAPER, prop=False)
    p.text(98, 446, 'Mill strike ends', 15, 23, PAPER)
    p.text(300, 446, '6:40 am', 13, 20, RULE)
    p.rtext(628, 446, '105', 15, 23, GOLD, prop=False)
    # The index: the other departments as keycaps, each with its page number.
    for i, (dept, page) in enumerate([('WEATHER', '300'), ('MARKETS', '400'), ('CITY', '230'), ('ASK', '711')]):
        x = 12 + i * 156
        p.rect(x, 455, 148, 24, DEEP)
        p.text(x + 6, 474, dept, 14, 20, PAPER)
        p.rtext(x + 142, 474, page, 13, 20, GOLD, prop=False)
    p.blink(BLUE, RED, 6, 6)
    # The satellite story's picture draws itself a second time: the rocket lifts off.
    p.wait(15)
    rocket_climbing(p, 328, 304)
    return p


if __name__ == '__main__':
    save(__file__, build)
