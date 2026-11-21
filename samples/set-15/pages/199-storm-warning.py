from _page import Plate, save, arc_points

META = dict(title='Storm Warning',
            purpose='A severe-weather bulletin pushed to every set in two counties: the sky over the farms, '
                    'a flashing bolt and the watch in red.',
            style='Bruised green storm sky over black farm silhouettes, alarm-red bulletin panel',
            techniques=['BLINK lightning hidden in the sky colour', 'BLINK sky flash on the same beat', 'BLINK warning text', 'WAIT reveal',
                        'banded sky with scud and shelf cloud', 'debris cloud of native circles', 'BLINK bands that turn the funnel', 'defined texture of slanting rain', 'inset county map in cross-hatching', 'filled polygons and arcs', 'large stroke text'],
            animated=True)

PALETTE = ('060a08 ffffff e8221c 5a0a0a 1c2a24 2c4034 3f5a44 7d8a5a '
           '3f5a44 4a5450 222826 141c14 222826 ffb020 6a7a78 e8e2c8').split()
BLACK, WHITE, ALERT, DARKRED, DECK, SKY2, SKY, GLOW, BOLT, CLOUD, FUNNEL, GROUND, TWIST, AMBER, STREAK, CREAM = range(16)
# The bulletin panel is drawn in black; entry 12 is the funnel's turning band.
PANEL = BLACK


def build():
    p = Plate('199', PALETTE)
    p.rect(0, 0, 640, 46, ALERT)
    p.text(18, 36, 'WEATHER ALERT', 22, 32, WHITE, prop=False)
    p.rtext(622, 35, '6:40 PM  p 9', 16, 26, WHITE, prop=False)
    # Sky: glow at the horizon, the green middle, a low cloud deck with a ragged base.
    p.rect(0, 46, 640, 222, SKY)
    p.rect(0, 220, 640, 48, GLOW)
    p.rect(0, 196, 640, 24, SKY)
    p.hatch(2)
    p.rect(0, 206, 640, 24, GLOW)
    p.solid()
    p.rect(0, 46, 640, 50, DECK)
    base = [(0, 96)]
    for i, x in enumerate(range(0, 661, 40)):
        base.append((x, 112 + (i % 3) * 8))
    p.poly([(0, 46), (640, 46)] + base[::-1][:-1] + [(0, 112)], DECK)
    for x, y, r in [(60, 104, 34), (150, 116, 30), (250, 110, 36), (520, 108, 40), (610, 118, 30)]:
        p.disc(x, y, r, DECK)
    # A shelf cloud runs in from the left, its lit underside a lighter band.
    p.poly([(0, 118), (120, 128), (250, 140), (330, 150), (250, 156), (120, 152), (0, 150)], SKY2)
    p.poly([(0, 150), (120, 152), (250, 156), (330, 150), (240, 164), (110, 166), (0, 166)], CLOUD)
    # Mammatus pouches under the deck on the right.
    for i, x in enumerate(range(470, 640, 26)):
        p.disc(x, 140 + (i % 2) * 6, 13, DECK)
    # Low scud drifting across the middle of the sky, dark against the flash.
    p.poly([(240, 186), (330, 176), (470, 180), (600, 172), (640, 178), (640, 192), (520, 196), (380, 194), (260, 198)], SKY2)
    p.poly([(0, 190), (60, 184), (150, 190), (110, 198), (0, 200)], SKY2)
    # Rain shafts on the left.
    # Rain shafts: a defined texture of slanting streaks fills two leaning curtains.
    p.define_texture('A', 12, [[(0.62, 0.98), (0.74, 0.98), (0.36, 0.02), (0.24, 0.02)]])
    p.cmd(0x23, b'\x60')
    p.poly([(10, 140), (120, 150), (96, 262), (-20, 262)], STREAK)
    p.poly([(150, 156), (214, 160), (190, 262), (126, 262)], STREAK)
    p.solid()
    p.wait(10)
    # The funnel: a wall cloud, then a twisting cone to the ground.
    p.poly(arc_points(410, 128, 110, 30, 180, 360, 18), CLOUD)
    p.poly([(352, 130), (468, 130), (450, 160), (432, 200), (424, 236), (416, 262), (404, 262),
            (402, 232), (392, 196), (372, 160)], FUNNEL)
    for y, w in [(150, 44), (178, 30), (210, 18), (240, 10)]:
        p.line([(410 - w, y), (410 + w, y + 6)], CLOUD, 2)
    # A second set of bands in their own entry, which BLINK shows and hides: the funnel turns.
    for y, w in [(164, 36), (194, 24), (226, 14)]:
        p.line([(410 - w, y + 6), (410 + w, y)], TWIST, 3)
    # The debris cloud where the funnel touches the ground, with flung fragments.
    for dx, dy, r in [(-26, 258, 12), (-8, 252, 15), (14, 254, 14), (32, 260, 11)]:
        p.disc(410 + dx, dy, r, CLOUD)
    for fx, fy in [(372, 236), (452, 232), (440, 214), (380, 216), (462, 248)]:
        p.rect(fx, fy, 4, 3, BLACK)
    # The bolt has its own entry so BLINK can strike it against the green sky.
    p.poly([(566, 122), (582, 122), (568, 160), (590, 160), (548, 196), (556, 170), (538, 170)], BOLT)
    # Ground and farm silhouettes.
    p.rect(0, 262, 640, 40, GROUND)
    p.poly([(70, 262), (70, 226), (98, 206), (126, 226), (126, 262)], BLACK)
    # Someone is home: one lit window in the farmhouse.
    p.rect(90, 236, 14, 12, AMBER)
    p.rect(132, 214, 22, 48, BLACK)
    p.poly(arc_points(143, 215, 11, 10, 0, 180, 8), BLACK)
    for x, r in [(220, 18), (246, 22), (274, 16), (296, 20), (318, 15)]:
        p.disc(x, 252 - r, r, BLACK)
    p.rect(214, 240, 112, 22, BLACK)
    # A road and a car with its headlights on, for scale.
    p.rect(0, 280, 640, 6, CLOUD)
    p.poly([(500, 280), (506, 270), (520, 264), (546, 264), (556, 272), (566, 274), (566, 280)], BLACK)
    p.disc(512, 282, 5, BLACK)
    p.disc(552, 282, 5, BLACK)
    p.poly([(566, 273), (620, 266), (620, 282), (566, 279)], STREAK)
    p.disc(565, 276, 3, CREAM)
    p.line([(480, 262), (480, 236)], BLACK, 2)
    p.line([(476, 238), (500, 238), (520, 240), (600, 242)], BLACK, 1)
    p.line([(600, 262), (600, 236)], BLACK, 2)
    # An inset map: the two counties under the watch, cross-hatched in red.
    p.rect(10, 54, 156, 92, PANEL)
    p.frame(10, 54, 156, 92, CREAM, 2)
    p.text(18, 76, 'WATCH AREA', 12, 19, CREAM, prop=False)
    west = [(22, 90), (84, 86), (88, 138), (24, 138)]
    east = [(84, 86), (152, 92), (156, 138), (88, 138)]
    for county in (west, east):
        p.poly(county, GROUND)
        p.hatch(3)
        p.poly(county, ALERT)
        p.solid()
        p.line(county + [county[0]], CREAM, 1)
    p.disc(50, 112, 4, WHITE)
    p.disc(124, 118, 4, WHITE)
    p.wait(10)
    # The bulletin.
    p.rect(0, 302, 640, 178, PANEL)
    p.rect(0, 302, 640, 6, ALERT)
    p.ctext(320, 366, 'TORNADO WATCH', 40, 58, DARKRED, prop=False)
    p.ctext(320, 404, 'UNTIL 9 PM TONIGHT', 22, 34, AMBER, prop=False)
    p.ctext(320, 436, 'Orrin and Calder counties', 17, 26, CREAM)
    p.ctext(320, 466, 'Go to a basement or inner room', 16, 25, WHITE)
    p.blink(DARKRED, ALERT, 5, 5)
    # The bolt's own colour is the sky's, so it is hidden until its blink lights it; the sky flashes
    # on the same beat (each delay counts from the blink defined before it).
    p.blink(BOLT, CREAM, 3, 9, 0)
    p.blink(SKY, GLOW, 3, 9, 0)
    p.blink(TWIST, CLOUD, 2, 2, 0)
    # The flash lights the fields too (each delay counts from the blink before, so all start together).
    p.blink(GROUND, CLOUD, 3, 9, 0)
    return p


if __name__ == '__main__':
    save(__file__, build)
