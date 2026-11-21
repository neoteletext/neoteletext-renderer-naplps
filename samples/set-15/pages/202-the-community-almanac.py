from _page import Plate, save, arc_points

META = dict(title='The Community Almanac',
            purpose='A provincial statistics bureau puts its census on the television: towns by population as '
                    'rising bars, and the region\'s farms by type as a hatched pie.',
            style='Government report on cream paper: teal band, blue bars, period hatching in the pie',
            techniques=['WAIT as each row is counted', 'isotype rows of a DRCS figure drawn with REPEAT', 'exploded pie wedge',
                        'native vertical, horizontal and cross hatching over solid fills', 'polygon pie wedges'],
            animated=True)

PALETTE = ('f3ecd8 1c2430 1f6f78 ffffff 2f62b8 d8452e e7b23a 8a5a2c '
           '4f9a3c b8cf3a 8cc4e8 b8b0a0 d8cfb8 0f3f46 e9dfc4 5a3418').split()
PAPER, INK, TEAL, WHITE, BAR, TOP, GOLD, BROWN, GREEN, LIME, SKY, GRID, SHADOW, DEEP, CREAM, DARKBROWN = range(16)
PERSON = 0x21
FIG_W, FIG_H = 17, 34

TOWNS = [('Orrin', 4180), ('Tasker', 9650), ('Ninefield', 2340), ('Pellham', 6020),
         ('Brackwater', 12410), ('Sedgely', 3770)]
FARMS = [('Grain', 42, GOLD, None, GOLD), ('Cattle', 23, CREAM, 1, BROWN), ('Mixed', 17, CREAM, 3, GREEN),
         ('Oilseed', 11, LIME, None, LIME), ('Dairy', 7, SKY, None, SKY)]


def build():
    p = Plate('202', PALETTE)
    p.rect(0, 0, 640, 46, TEAL)
    p.text(16, 34, 'WESTMARK BUREAU OF STATISTICS', 15, 24, WHITE)
    p.rtext(624, 33, 'p 510', 13, 20, CREAM, prop=False)
    p.text(16, 82, 'Community Almanac 1982', 18, 28, DEEP)
    # A prairie town on the skyline beside the title: elevator, water tower, houses.
    ground = 90
    p.rect(400, ground - 2, 240, 4, DEEP)
    p.rect(420, ground - 30, 22, 30, BROWN)
    p.poly([(416, ground - 30), (431, ground - 40), (446, ground - 30)], DARKBROWN)
    p.rect(442, ground - 24, 18, 24, BROWN)
    for hx, hw in [(474, 22), (504, 26), (580, 22), (610, 24)]:
        p.rect(hx, ground - 14, hw, 14, TEAL)
        p.poly([(hx - 2, ground - 14), (hx + hw / 2, ground - 24), (hx + hw + 2, ground - 14)], DEEP)
    p.line([(546, ground), (546, ground - 22)], DEEP, 2)
    p.line([(560, ground), (560, ground - 22)], DEEP, 2)
    p.rect(538, ground - 34, 30, 14, SKY)
    p.poly(arc_points(553, ground - 34, 15, 6, 0, 180, 8), DEEP)
    # Bar chart.
    p.text(16, 116, 'People by town', 14, 22, INK)
    # Isotype rows: one programmable figure for every thousand people, drawn with REPEAT.
    p.define_drcs(PERSON, FIG_W, FIG_H, [('disc', 0.25, 0.80, 0.11),
                                   [(0.06, 0.64), (0.44, 0.64), (0.40, 0.30), (0.34, 0.30), (0.34, 0.02),
                                    (0.26, 0.02), (0.25, 0.22), (0.24, 0.02), (0.16, 0.02), (0.16, 0.30),
                                    (0.10, 0.30)]])
    left = 116
    biggest = max(t[1] for t in TOWNS)
    # Light rules at five and ten thousand, so the rows can be read off.
    for thousands in (5, 10):
        gx = left + thousands * FIG_W
        p.line([(gx, 130), (gx, 396)], GRID, 1)
        p.ctext(gx, 414, str(thousands), 12, 19, INK, prop=False)
    for i, (name, people) in enumerate(TOWNS):
        y = 168 + i * 44
        whole, part = divmod(people, 1000)
        figures = whole + (1 if part else 0)
        p.wait(3)
        p.rtext(left - 10, y - 6, name, 13, 21, INK)
        p.chars(left, y, [PERSON], FIG_W, FIG_H, TOP if people == biggest else BAR)
        if figures > 1:
            p.data.extend(b'\x1bF' + bytes([0x40 | (figures - 1)]))
        if part:
            # The last figure is cut to the fraction of a thousand it stands for, as isotype charts did.
            cut = left + whole * FIG_W + FIG_W * (0.12 + 0.76 * part / 1000)
            p.rect(cut, y - FIG_H, left + figures * FIG_W - cut + 1, FIG_H + 1, PAPER)
        p.text(left + figures * FIG_W + 6, y - 6, f'{people / 1000:.1f}', 12, 19, INK, prop=False)
    p.line([(left - 4, 128), (left - 4, 408)], GRID, 2)
    p.chars(16, 438, [PERSON], FIG_W, FIG_H, BAR)
    p.text(40, 432, '= 1,000 people, 1981', 13, 20, INK)

    # Pie of farm types, wedges from twelve o'clock clockwise.
    cx, cy, r = 520, 240, 98
    p.wait(6)
    p.text(408, 116, 'Farms by type', 14, 22, INK)
    p.disc(cx + 6, cy + 6, r, SHADOW)
    angle = 90
    for name, share, base_colour, pattern, ink in FARMS:
        sweep = share * 3.6
        from math import cos, sin, radians
        mid = radians(angle - sweep / 2)
        shift = 12 if name == 'Grain' else 0
        ox, oy = cx + shift * cos(mid), cy - shift * sin(mid)
        pts = [(ox, oy)] + arc_points(ox, oy, r, r, angle, angle - sweep, max(4, int(sweep / 6)))
        p.poly(pts, base_colour)
        if pattern:
            p.hatch(pattern)
            p.poly(pts, ink)
            p.solid()
        p.line(pts + [pts[0]], INK, 2)
        angle -= sweep
        p.wait(3)
    # A sheaf of wheat on the grain wedge.
    sx, sy = cx + 70, cy - 4
    for dx in (-8, 0, 8):
        p.line([(sx, sy + 34), (sx + dx, sy - 6)], DARKBROWN, 2)
        p.poly(arc_points(sx + dx * 1.2, sy - 14, 4, 10, 0, 360, 10), DARKBROWN)
    p.rect(sx - 8, sy + 14, 16, 4, DARKBROWN)
    angle = 90
    for name, share, base_colour, pattern, ink in FARMS:
        mid = angle - share * 1.8
        from math import cos, sin, radians
        lx = cx + r * 0.62 * cos(radians(mid))
        ly = cy - r * 0.62 * sin(radians(mid))
        if share >= 11 and name != 'Grain':
            p.rect(lx - 24, ly - 14, 48, 26, WHITE)
            p.ctext(lx, ly + 8, f'{share}%', 13, 20, INK, prop=False)
        elif name == 'Grain':
            p.rect(cx + 20, cy - 74, 48, 26, WHITE)
            p.ctext(cx + 44, cy - 52, f'{share}%', 13, 20, INK, prop=False)
        angle -= share * 3.6
    # The smallest wedge is labelled outside, on a leader.
    p.line([(cx - 20, cy - r + 12), (cx - 62, cy - r + 4)], INK, 1)
    p.rtext(cx - 66, cy - r + 12, '7%', 13, 20, INK, prop=False)
    # Legend.
    for i, (name, share, base_colour, pattern, ink) in enumerate(FARMS):
        x, y = 392 + (i % 2) * 124, 372 + (i // 2) * 28
        p.rect(x, y - 18, 22, 20, base_colour)
        if pattern:
            p.hatch(pattern)
            p.rect(x, y - 18, 22, 20, ink)
            p.solid()
        p.frame(x, y - 18, 22, 20, INK, 1)
        p.text(x + 30, y, name, 13, 21, INK)
    p.text(516, 428, '2,840 farms', 13, 20, DEEP)
    p.rect(0, 452, 640, 28, TEAL)
    p.text(16, 474, 'MORE TABLES p 512', 13, 20, WHITE)
    p.rtext(624, 474, 'TOWN MAP p 515', 13, 20, WHITE)
    return p


if __name__ == '__main__':
    save(__file__, build)
