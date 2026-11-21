from _page import Plate, save, arc_points

META = dict(title='Your Own Newspaper',
            purpose='The newspaper the futurists promised: only the topics one reader chose, gathered each '
                    'morning into coloured folders with her name on the masthead.',
            style='Plum desk with four pastel file folders, each with a coloured tab and a flat drawing',
            techniques=['WAIT as each folder is filed', 'DRCS frost crystal at two sizes', 'BLINK new-item marker', 'native circles and arcs',
                        'filled polygons', 'proportional text'],
            animated=True)

PALETTE = ('3e3060 ffffff fbf2dc 2a2430 2e8a3a d8f0c8 2f6fc0 d0e4f8 '
           'c8601a fde3c4 c0306a f8d4e2 7a7a84 e8402a ffd23a e8402a').split()
DESK, WHITE, PAPER, INK, GREEN, GREENPALE, BLUE, BLUEPALE, ORANGE, ORANGEPALE, PINK, PINKPALE, GRANITE, TOMATO, GOLD, NEW = range(16)
SHADOW = INK
LEAF = GREEN


FLAKE = 0x21


def snowflake(p):
    """A six-armed frost crystal as a programmable character."""
    import math
    arms = []
    for i in range(6):
        a = math.radians(90 + 60 * i)
        c, s = math.cos(a), math.sin(a)
        arms.append([(0.5 - 0.05 * s, 0.5 + 0.05 * c), (0.5 + 0.46 * c - 0.05 * s, 0.5 + 0.46 * s + 0.05 * c),
                     (0.5 + 0.46 * c + 0.05 * s, 0.5 + 0.46 * s - 0.05 * c), (0.5 + 0.05 * s, 0.5 - 0.05 * c)])
        bx, by = 0.5 + 0.30 * c, 0.5 + 0.30 * s
        for turn in (50, -50):
            b = a + math.radians(turn)
            arms.append([(bx, by), (bx + 0.16 * math.cos(b) - 0.03 * math.sin(b), by + 0.16 * math.sin(b) + 0.03 * math.cos(b)),
                         (bx + 0.16 * math.cos(b) + 0.03 * math.sin(b), by + 0.16 * math.sin(b) - 0.03 * math.cos(b))])
    p.define_drcs(FLAKE, 24, 24 * 0.96, arms)


def tomatoes(p, x, y):
    p.line([(x + 10, y + 70), (x + 10, y + 4)], LEAF, 3)
    p.line([(x + 10, y + 30), (x + 40, y + 16), (x + 58, y + 22)], LEAF, 3)
    p.line([(x + 10, y + 50), (x + 34, y + 44)], LEAF, 3)
    p.poly([(x + 10, y + 14), (x + 26, y + 6), (x + 22, y + 20)], LEAF)
    for tx, ty, r in [(x + 40, y + 30, 11), (x + 58, y + 34, 9), (x + 34, y + 56, 10)]:
        p.disc(tx, ty, r, TOMATO)
        p.disc(tx - 3, ty - 4, 2.5, WHITE)
    p.rect(x, y + 70, 70, 6, GRANITE)
    # Frost coming: crystals drawn from one programmable character.
    p.chars(x + 50, y + 4, [FLAKE], 24, 24 * 0.96, BLUE)
    p.chars(x + 62, y + 58, [FLAKE], 16, 16 * 0.96, BLUE)


def curling(p, x, y):
    """A stone at rest on the button of the house, seen from the side."""
    for r, c in [(38, BLUE), (27, WHITE), (16, TOMATO), (6, WHITE)]:
        p.poly(arc_points(x + 38, y + 76, r, r * 0.28, 0, 360, 24), c)
    p.poly(arc_points(x + 38, y + 70, 26, 8, 180, 360, 12), INK)
    p.rect(x + 12, y + 52, 52, 18, GRANITE)
    p.rect(x + 12, y + 58, 52, 5, INK)
    p.poly(arc_points(x + 38, y + 52, 26, 8, 0, 360, 20), GRANITE)
    p.poly(arc_points(x + 38, y + 52, 18, 5, 0, 360, 16), WHITE)
    p.rect(x + 32, y + 36, 10, 16, TOMATO)
    p.poly([(x + 32, y + 30), (x + 70, y + 30), (x + 70, y + 40), (x + 42, y + 40), (x + 42, y + 44), (x + 32, y + 44)], TOMATO)


def chart(p, x, y):
    p.rect(x, y + 4, 70, 70, WHITE)
    for i, h in enumerate([16, 26, 22, 40, 52]):
        p.rect(x + 6 + i * 12, y + 70 - h, 9, h, ORANGE)
    p.line([(x + 8, y + 50), (x + 30, y + 38), (x + 42, y + 42), (x + 64, y + 14)], GREEN, 3)
    p.poly([(x + 56, y + 12), (x + 68, y + 8), (x + 66, y + 20)], GREEN)


def school(p, x, y):
    p.poly([(x + 4, y + 34), (x + 35, y + 10), (x + 66, y + 34)], TOMATO)
    p.rect(x + 10, y + 34, 50, 40, GOLD)
    p.rect(x + 28, y + 50, 14, 24, INK)
    p.rect(x + 14, y + 42, 10, 10, WHITE)
    p.rect(x + 46, y + 42, 10, 10, WHITE)
    p.rect(x + 30, y, 10, 14, TOMATO)
    p.disc(x + 35, y + 22, 4, WHITE)
    for kx, colour in [(x + 2, BLUE), (x + 66, GREEN)]:
        p.disc(kx + 4, y + 58, 5, INK)
        p.poly([(kx - 2, y + 76), (kx + 10, y + 76), (kx + 8, y + 63), (kx, y + 63)], colour)
    for nx, ny in [(x + 58, y + 6), (x + 66, y + 14)]:
        p.disc(nx, ny + 8, 3, INK)
        p.line([(nx + 2, ny + 8), (nx + 2, ny - 2)], INK, 2)


FOLDERS = [
    ('GARDENING', GREEN, GREENPALE, tomatoes, ['Frost tonight.', 'Cover tomatoes', 'before 8 pm.'], 'p 451'),
    ('CURLING', BLUE, BLUEPALE, curling, ['Ladies league', 'Your rink plays', 'Sunday at 2.'], 'p 462'),
    ('STOCK CLUB', ORANGE, ORANGEPALE, chart, ['Club fund up', '3.2% this month.', 'Meeting Tues.'], 'p 473'),
    ('LAKESIDE SCHOOL', PINK, PINKPALE, school, ['Grade 2 concert', 'Friday 7 pm,', 'gym doors 6:30.'], 'p 484'),
]


def build():
    p = Plate('205', PALETTE)
    snowflake(p)
    p.rect(0, 0, 640, 92, PAPER)
    p.rect(0, 88, 640, 4, PINK)
    # A rose on the left of the masthead and the reader's monogram on the right.
    p.line([(58, 84), (58, 50)], LEAF, 3)
    p.poly([(58, 70), (34, 60), (46, 76)], LEAF)
    p.poly([(58, 64), (82, 56), (72, 72)], LEAF)
    for dx, dy, r in [(-10, -4, 12), (10, -4, 12), (0, -16, 12), (0, 6, 11)]:
        p.disc(58 + dx, 36 + dy, r, PINK)
    p.disc(58, 32, 8, TOMATO)
    p.disc(58, 32, 3, PINK)
    p.disc(584, 46, 34, PINK)
    p.disc(584, 46, 29, PAPER)
    p.ctext(584, 62, 'EP', 21, 32, PINK, prop=False)
    p.ctext(320, 50, 'The Pellow Post', 30, 46, INK)
    p.ctext(320, 78, 'Edited for Edna Pellow  -  Thursday', 14, 22, INK)
    for i, (tab, dark, pale, icon, lines, page) in enumerate(FOLDERS):
        x, y = 16 + (i % 2) * 312, 128 + (i // 2) * 166
        p.wait(8)
        tab_width = len(tab) * 13 + 22
        # A shadow on the desk gives each folder its thickness.
        p.rect(x + 6, y - 22, tab_width, 30, SHADOW)
        p.rect(x + 6, y + 6, 296, 142, SHADOW)
        p.rect(x, y - 28, tab_width, 30, dark)
        p.text(x + 10, y - 6, tab, 13, 20, WHITE, prop=False)
        p.rect(x, y, 296, 142, pale)
        p.rect(x, y, 296, 4, dark)
        # Each picture sits on a white plate, like a clipping pasted into the folder.
        p.disc(x + 48, y + 64, 44, WHITE)
        icon(p, x + 12, y + 20)
        p.rtext(x + 288, y + 134, page, 13, 20, dark, prop=False)
        p.text(x + 98, y + 42, lines[0], 15, 24, dark)
        for j, line in enumerate(lines[1:]):
            p.text(x + 98, y + 74 + j * 28, line, 14, 22, INK)
    # A new item in the stock club folder.
    # A paper clip holds a cutting to the curling folder.
    p.rect(578, 98, 40, 52, WHITE)
    for ly in (110, 120, 130, 140):
        p.line([(584, ly), (612, ly)], GRANITE, 1)
    p.frame(592, 90, 12, 30, GRANITE, 2)
    p.rect(160, 404, 62, 28, NEW)
    p.ctext(191, 426, 'NEW', 15, 24, WHITE, prop=False)
    p.blink(NEW, ORANGE, 5, 5)
    p.rect(0, 446, 640, 34, INK)
    p.text(16, 470, 'KEY 9 TO CHOOSE YOUR TOPICS', 14, 22, GOLD, prop=False)
    return p


if __name__ == '__main__':
    save(__file__, build)
