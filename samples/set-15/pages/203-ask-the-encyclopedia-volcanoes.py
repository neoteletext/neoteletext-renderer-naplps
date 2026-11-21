from _page import Plate, save, arc_points

META = dict(title='Ask the Encyclopedia: Volcanoes',
            purpose='A home encyclopedia on the television: a volcano cut open, layer by layer, then the '
                    'eruption, with every part named on a leader line.',
            style='Textbook cross-section in earth browns and lava reds under a dusk sky',
            techniques=['nested polygons for strata', 'defined fill texture for rock', 'WAIT before the eruption', 'magma rising up the vent in WAIT steps',
                        'BLINK lava glow', 'dotted arcs for the bombs\' paths', 'scale bar', 'labels on leader lines'],
            animated=True)

PALETTE = ('1a1838 ffffff 3a2f5c e83a1c ff9a1e ffe04a 8a8a94 55525e '
           '6a4a34 a87a52 3a2a22 5a4030 f6ecd0 0e2f3a c9c2b0 4a7a3a').split()
SKY, WHITE, DUSK, LAVA, ORANGE, GLOW, ASH, ASHDARK, ROCK, TAN, CRUST, CRUSTMID, CREAM, BAND, LEADER, GREEN = range(16)


def label(p, text, tx, ty, point, right=False):
    """A cream label with a leader line to the point it names."""
    w = 13
    p.line([(tx if not right else tx, ty - 7), point], LEADER, 2)
    p.disc(point[0], point[1], 3, CREAM)
    if right:
        p.rtext(tx - 4, ty, text, w, 21, CREAM)
    else:
        p.text(tx + 4, ty, text, w, 21, CREAM)


def build():
    p = Plate('203', PALETTE)
    p.rect(0, 0, 640, 40, BAND)
    p.text(16, 30, 'QUARTO HOME ENCYCLOPEDIA', 15, 24, CREAM)
    p.rtext(624, 30, 'p 711', 14, 22, GLOW, prop=False)
    p.rect(0, 40, 640, 120, SKY)
    p.rect(0, 160, 640, 140, DUSK)
    # Distant ranges behind the volcano.
    p.poly([(0, 300), (0, 220), (60, 190), (120, 214), (170, 186), (230, 230), (400, 228), (450, 196),
            (520, 214), (580, 180), (640, 206), (640, 300)], BAND)
    p.rtext(624, 80, 'VOLCANOES', 22, 32, WHITE, prop=False)
    # Crust: a speckled texture over two bands.
    p.rect(0, 300, 640, 130, CRUST)
    p.rect(0, 300, 640, 40, CRUSTMID)
    p.define_texture('A', 16, [[(0.1, 0.1), (0.3, 0.1), (0.3, 0.25), (0.1, 0.25)],
                              [(0.6, 0.55), (0.8, 0.55), (0.8, 0.7), (0.6, 0.7)]])
    p.cmd(0x23, b'\x60')
    p.rect(0, 300, 640, 130, ROCK)
    p.solid()
    # Magma chamber.
    # An irregular chamber fed from below, glowing at its heart.
    p.poly([(180, 392), (200, 372), (240, 362), (282, 368), (320, 358), (372, 364), (414, 380), (424, 398),
            (396, 414), (340, 418), (300, 410), (252, 418), (206, 412)], LAVA)
    p.poly([(226, 392), (260, 378), (300, 380), (346, 374), (384, 388), (352, 402), (300, 398), (250, 404)], ORANGE)
    p.line([(250, 416), (236, 430)], LAVA, 5)
    p.line([(360, 416), (380, 430)], LAVA, 5)
    # Stratified cone: nested cones share the base, alternating ash and lava rock.
    # Strata of uneven thickness, each eruption's deposit bending a little differently.
    layers = [(0, 0, 0, ROCK), (22, 30, 18, TAN), (40, 50, 34, ASHDARK), (62, 66, 52, TAN),
              (90, 84, 70, ROCK), (108, 112, 88, ASH), (134, 128, 104, TAN), (150, 152, 122, ROCK)]
    for left_in, right_in, drop, colour in layers:
        top = 126 + drop
        lx0, rx0 = 40 + left_in, 560 - right_in
        lx1, rx1 = 268 - drop * 0.1, 332 + drop * 0.1
        bend = 6 if colour in (ASH, ASHDARK) else -4
        p.poly([(lx0, 300), ((lx0 + lx1) / 2 + bend, (300 + top) / 2), (lx1, top), (rx1, top),
                ((rx0 + rx1) / 2 - bend, (300 + top) / 2), (rx0, 300)], colour)
    p.poly([(262, 126), (280, 142), (320, 142), (338, 126)], SKY)
    p.rect(0, 296, 640, 6, GREEN)
    for tx, th in [(612, 30), (628, 22), (596, 18)]:
        p.poly([(tx - 8, 297), (tx, 297 - th), (tx + 8, 297)], GREEN)
    p.poly([(0, 296), (40, 296), (90, 280), (0, 284)], GREEN)
    p.poly([(640, 296), (560, 296), (514, 282), (640, 286)], GREEN)
    # Labels for the still volcano.
    label(p, 'Layers of ash', 150, 270, (190, 262), right=True)
    p.rtext(146, 292, 'and lava', 13, 21, CREAM)
    label(p, 'Magma chamber', 450, 408, (408, 396))
    label(p, 'Solid crust', 450, 330, (430, 322))
    p.wait(15)
    # The eruption: the conduit fills, then the column of ash and the flow.
    # Magma climbs the main vent in steps, from the chamber to the crater.
    for top in range(330, 139, -38):
        p.rect(292, top, 16, 376 - top, LAVA)
        p.wait(2)
    # The side vent reaches the flank and builds a small cone of its own there.
    p.line([(300, 260), (360, 222), (400, 214), (440, 210)], LAVA, 6)
    p.poly([(432, 214), (448, 196), (462, 222)], TAN)
    p.poly([(440, 206), (448, 196), (452, 210)], ORANGE)
    p.poly([(282, 142), (300, 100), (318, 142)], ORANGE)
    # The flow runs down the surface of the right flank, from the crater rim to the plain.
    flank = [(332 + 228 * f, 126 + 174 * f) for f in (0.0, 0.2, 0.4, 0.6, 0.8, 0.95)]
    outer = [(x + 9, y - 12) for x, y in flank]
    p.poly(flank + [(578, 300), (600, 300)][:1] + outer[::-1], LAVA)
    p.line([(x + 4, y - 6) for x, y in flank[:-1]], ORANGE, 4)
    p.poly([(548, 292), (600, 294), (604, 300), (540, 300)], LAVA)
    # Ash falls from the column as hatching, then the column billows above the crater.
    p.hatch(1)
    p.poly([(190, 72), (410, 72), (440, 150), (380, 150), (300, 110), (220, 150), (170, 150)], ASHDARK)
    p.solid()
    for x, y, r, c in [(300, 96, 24, ASHDARK), (300, 70, 30, ASHDARK), (256, 64, 28, ASH), (346, 58, 30, ASH),
                       (300, 50, 28, ASH), (214, 62, 22, ASHDARK), (388, 60, 24, ASHDARK), (230, 50, 18, ASH),
                       (372, 46, 18, ASH), (300, 84, 18, ASH)]:
        p.disc(x, y, r, c)
    # Lightning inside the ash column, which real eruptions make.
    p.line([(328, 48), (318, 62), (330, 66), (316, 84)], WHITE, 2)
    p.line([(262, 56), (270, 68), (260, 74)], WHITE, 2)
    # Volcanic bombs thrown from the crater on dotted paths.
    p.pel(2).cmd(0x23, b'\x41')
    p.color(GLOW)
    p.arc((292, 122), (252, 98), (214, 130))
    p.arc((308, 122), (348, 98), (386, 130))
    p.cmd(0x23, b'\x40')
    for x, y in [(252, 112), (348, 106), (236, 128), (366, 124)]:
        p.disc(x, y, 4, GLOW)
    p.blink(ORANGE, GLOW, 4, 6)
    label(p, 'Ash cloud', 150, 104, (234, 72), right=True)
    label(p, 'Crater', 150, 150, (276, 138), right=True)
    label(p, 'Main vent', 150, 236, (292, 236), right=True)
    label(p, 'Lava flow', 520, 176, (452, 206))
    label(p, 'Side vent', 490, 236, (452, 214))
    # A scale bar on the crust.
    p.line([(24, 356), (124, 356)], CREAM, 3)
    for sx in (24, 74, 124):
        p.line([(sx, 350), (sx, 362)], CREAM, 2)
    p.text(48, 386, '5 km', 13, 20, CREAM)
    p.rect(0, 430, 640, 50, BAND)
    p.text(16, 464, 'NEXT: Famous eruptions', 15, 24, CREAM)
    # Which page of the article this is: two of six.
    for i in range(6):
        p.disc(360 + i * 18, 456, 5, GLOW if i == 1 else LEADER)
    p.rtext(624, 464, 'KEY 712', 15, 24, GLOW, prop=False)
    return p


if __name__ == '__main__':
    save(__file__, build)
