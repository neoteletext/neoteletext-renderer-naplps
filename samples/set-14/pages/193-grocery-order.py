from _kit import *

META = dict(title='Grocery Order, Week of June 3',
            purpose='A corner grocer takes a weekly order: each item drops into a wire cart and the running total follows.',
            style='Fresh mint, cream and grocer green with flat-colour packages in a wire cart',
            techniques=['macros', 'DRCS', 'native circles', 'hatch fill', 'filled polygons', 'WAIT', 'BLINK', 'proportional text'],
            animated=True)

CREAM, INK, WHITE, GREEN, DKGREEN, RED, ORANGE, YELLOW, CHROME, STEEL, BLUE, TAN, BROWN, MINT, FLESH, LEAF = range(16)

ITEMS = [('MILK 2 LITRES', 219), ('BREAD, SLICED', 145), ('ORANGES, 1 KG', 299),
         ('CEREAL BOX', 349), ('EGGS, DOZEN', 235), ('BEANS, 4 CANS', 320)]

MESH_MACRO = 0x21
FRONT_TOP = 292


def mesh_fragment():
    """The cart's front wall: a macro, redrawn over each new item."""
    frag = Encoder()
    frag.pel(1)
    pts = [(48, FRONT_TOP), (336, FRONT_TOP), (308, 350), (80, 350)]
    frag.color(STEEL)
    frag.poly(pts, STEEL, True)
    frag.cmd(0x23, bytes([0x40 | 3 << 3]))
    frag.pel(4)
    frag.color(CHROME)
    frag.poly(pts, CHROME, True)
    frag.cmd(0x23, b'\x40')
    frag.pel(5)
    frag.line([(48, FRONT_TOP), (336, FRONT_TOP)], CHROME, 5)
    frag.line([(80, 350), (308, 350)], STEEL, 4)
    return frag


def cart_back(p):
    p.rect(8, 56, 336, 340, MINT)
    p.poly([(60, 222), (326, 222), (336, FRONT_TOP), (48, FRONT_TOP)], STEEL)
    p.fillpoly([(60, 222), (326, 222), (336, FRONT_TOP), (48, FRONT_TOP)], CHROME, 3, 5)
    p.line([(48, 270), (26, 170), (6, 170)], STEEL, 6)
    p.line([(80, 350), (96, 372)], STEEL, 5)
    p.line([(308, 350), (292, 372)], STEEL, 5)
    for x in (98, 290):
        p.disc(x, 380, 13, INK)
        p.disc(x, 380, 8, CHROME)
        p.disc(x, 380, 3, STEEL)
    p.rect(8, 392, 336, 4, STEEL)


def milk(p, x, base):
    p.rect(x - 22, base - 120, 44, 70, WHITE)
    p.poly([(x - 22, base - 120), (x - 12, base - 142), (x + 12, base - 142), (x + 22, base - 120)], WHITE)
    p.poly([(x - 22, base - 120), (x - 12, base - 142), (x - 12, base - 120)], BLUE)
    p.rect(x - 22, base - 106, 44, 26, BLUE)
    p.disc(x, base - 93, 8, WHITE)
    p.rect(x - 8, base - 152, 16, 10, RED)
    p.rect(x + 14, base - 120, 8, 70, CHROME)


def bread(p, x, base):
    p.poly([(x - 40, base - 56), (x - 38, base - 100), (x - 22, base - 116), (x + 22, base - 116), (x + 38, base - 100), (x + 40, base - 56)], TAN)
    p.poly([(x - 34, base - 60), (x - 33, base - 96), (x - 20, base - 109), (x + 20, base - 109), (x + 33, base - 96), (x + 34, base - 60)], BROWN)
    for dx in (-18, 0, 18):
        p.line([(x + dx - 8, base - 100), (x + dx + 6, base - 84)], TAN, 4)
    p.rect(x - 40, base - 60, 80, 8, WHITE)
    p.rect(x - 8, base - 122, 16, 8, RED)


def oranges(p, x, base):
    for dx, dy, r in [(-26, 0, 24), (22, -2, 26), (-2, -40, 25)]:
        p.disc(x + dx, base - 70 + dy, r, ORANGE)
        p.disc(x + dx - 7, base - 78 + dy, r * .45, FLESH)
        p.disc(x + dx + 2, base - 70 + dy - r, 3, LEAF)
    p.poly([(x - 6, base - 112), (x + 12, base - 124), (x + 18, base - 112), (x + 2, base - 108)], LEAF)


def eggs(p, x, base):
    p.poly([(x - 42, base - 54), (x - 38, base - 82), (x + 38, base - 82), (x + 42, base - 54)], FLESH)
    p.rect(x - 42, base - 56, 84, 8, TAN)
    for dx in (-26, -9, 8, 25):
        p.ellipse(x + dx, base - 92, 8, 11, WHITE)
        p.ellipse(x + dx - 2, base - 95, 3, 4, CREAM)
    p.rect(x - 42, base - 74, 84, 10, TAN)


def cereal(p, x, base):
    p.rect(x - 32, base - 132, 64, 84, RED)
    p.rect(x - 32, base - 132, 64, 10, DKGREEN)
    p.disc(x, base - 90, 18, YELLOW)
    p.disc(x, base - 90, 11, ORANGE)
    p.disc(x, base - 90, 5, YELLOW)
    p.say(x, base - 58, 'OATS', SMALL, WHITE, 'c')
    p.rect(x + 32, base - 128, 7, 76, DKGREEN)


def beans(p, x, base):
    for dx in (-30, 6):
        cx = x + dx + 12
        p.rect(cx - 18, base - 100, 36, 54, BROWN)
        p.rect(cx - 18, base - 88, 36, 24, ORANGE)
        p.ellipse(cx, base - 100, 18, 5, STEEL)
        p.ellipse(cx, base - 100, 12, 3, CHROME)
        p.say(cx, base - 69, 'BN', SMALL, INK, 'c')


def list_panel(p):
    p.rect(354, 56, 278, 330, WHITE)
    p.rect(354, 56, 278, 34, GREEN)
    p.say(366, 80, 'YOUR ORDER', LARGE, WHITE)


TICK = 0x21
TICK_SHAPES = [('poly', [(2, 11), (6, 8), (9, 13), (18, 1), (22, 4), (9, 20)])]


VAN_SHAPES = [('poly', [(1, 4), (28, 4), (28, 18), (1, 18)]), ('poly', [(28, 8), (38, 8), (43, 13), (43, 18), (28, 18)]),
              ('disc', 9, 19, 4), ('disc', 34, 19, 4), ('hole', 9, 19, 1.5), ('hole', 34, 19, 1.5),
              ('hole', 32, 11, 0.1), ('poly', [(30, 9), (37, 9), (40, 13), (30, 13)])]


def list_item(p, index):
    y = 118 + index * 32
    name, cents = ITEMS[index]
    character(p, TICK, 364, y + 2, 24, 22, GREEN)
    p.say(394, y, name, BODY, INK)
    p.say(620, y, f'{cents / 100:.2f}', BODY, INK, 'r')
    p.rect(362, y + 6, 262, 2, MINT)


def total(p, count):
    cents = sum(c for _, c in ITEMS[:count])
    p.rect(354, 316, 278, 70, DKGREEN)
    p.say(366, 346, 'TOTAL', LARGE, WHITE)
    p.say(620, 352, f'${cents / 100:.2f}', HEAD, YELLOW, 'r')
    p.say(366, 376, 'ADD $4.33 FOR FREE DELIVERY' if cents < 2000 else '', SMALL, MINT)


def build():
    p = Screen('fbf6e6 22302b ffffff 1e8a4a 135c33 d9402e f58a1f f7d046 c3ced2 6d7a80 3b82d6 d6a25c 8c5a2b d9f0df ffd9a0 5bbd4a')
    p.rect(0, 0, 640, 480, CREAM)
    p.rect(0, 0, 640, 44, GREEN)
    p.say(14, 32, 'CORNER BASKET GROCERS', LARGE, WHITE)
    p.say(626, 32, '193', LARGE, YELLOW, 'r')
    p.rect(0, 44, 640, 5, DKGREEN)
    p.rect(0, 446, 640, 34, GREEN)
    p.say(14, 470, '1 SEND ORDER  2 CHANGE  3 SAME AS LAST WEEK', BODY, WHITE)
    p.say(344, 410, '', SMALL, INK)
    define_character(p, 0x22, 44, 24, VAN_SHAPES)
    character(p, 0x22, 14, 430, 44, 24, DKGREEN)
    p.say(66, 424, 'DELIVERY THURSDAY 4 TO 6', BODY, DKGREEN)
    cart_back(p)
    list_panel(p)
    total(p, 0)
    define_character(p, TICK, 24, 22, TICK_SHAPES)
    p.macro(MESH_MACRO, mesh_fragment())
    p.call(MESH_MACRO)
    p.wait(8)
    for i, painter, x, base in [(0, milk, 78, 338), (1, bread, 160, 336), (2, oranges, 268, 336),
                                (3, cereal, 214, 352), (4, eggs, 118, 352), (5, beans, 300, 354)]:
        painter(Scaled(p, x, base, 1.3), x, base)
        p.call(MESH_MACRO)
        list_item(p, i)
        total(p, i + 1)
        p.wait(8)
    p.bevel(480, 396, 140, 44, ORANGE, YELLOW, RED)
    p.say(550, 426, 'SEND', LARGE, INK, 'c')
    p.blink(ORANGE, YELLOW, 5, 5)
    p.wait(20)
    # the order is sent: the key goes down and the grocer confirms
    p.bevel(480, 396, 140, 44, ORANGE, RED, YELLOW)
    p.say(550, 428, 'SENT', LARGE, INK, 'c')
    p.rect(0, 404, 470, 40, CREAM)
    character(p, 0x22, 14, 432, 44, 24, DKGREEN)
    p.say(66, 424, 'ORDER SENT - THANK YOU, MRS REYES', SMALL, DKGREEN)
    p.say(66, 442, 'DELIVERY THURSDAY 4 TO 6', SMALL, DKGREEN)
    return p


if __name__ == '__main__':
    save(__file__, build)
