"""207: a prairie farm service's closing grain prices, under its elevator at sunset."""
from _kit import BODY, LARGE, SMALL, TITLE, Fragment, Screen, furrow_mark, measure, save

META = dict(title='Grain Prices at the Elevator',
            purpose='A farm information service shows the closing prices paid at the local elevator.',
            style='Banded prairie sunset over a dark price board',
            techniques=['banded fills', 'filled polygons', 'native circles', 'DRCS grain and logo characters',
                        'defined stubble pattern', 'macro hopper cars', 'trend polylines', 'colour-map sunset',
                        'proportional text', 'keypad key tops', 'WAIT reveal', 'BLINK'],
            animated=True)

NIGHT, WHITE, VIOLET, PLUM, EMBER, ORANGE, GOLD, SUN = range(8)
SHADE, BARN, STUBBLE, UP, DOWN, CYAN, AMBER, BAND = range(8, 16)
HORIZON = 212

SUN_X = 572

# grain, close, change, and the last eight closes as heights for the small trend line
PRICES = [('WHEAT', '4.18', '+.03', (3, 4, 2, 5, 6, 5, 8, 10)),
          ('BARLEY', '2.71', '-.02', (8, 9, 7, 8, 6, 6, 5, 4)),
          ('CANOLA', '7.94', '+.11', (2, 2, 4, 3, 5, 7, 8, 11)),
          ('FLAX', '8.02', '+.00', (6, 5, 6, 6, 5, 6, 6, 6))]


def sky(p):
    for top, ink in [(44, VIOLET), (84, PLUM), (120, EMBER), (152, ORANGE), (182, GOLD)]:
        p.box(0, top, 640, HORIZON - top, ink)
    # Long thin clouds, each a flat lens lit from below.
    for x, y, w, ink in [(330, 96, 190, EMBER), (40, 128, 150, ORANGE), (470, 138, 150, GOLD),
                         (250, 164, 120, GOLD)]:
        p.poly([(x, y), (x + w * .3, y - 5), (x + w * .8, y - 3), (x + w, y + 1),
                (x + w * .6, y + 4), (x + w * .15, y + 3)], ink)
    p.disc(SUN_X, 204, 46, SUN)
    p.disc(SUN_X, 204, 35, WHITE)
    # Geese going south in a ragged V.
    for x, y in [(420, 78), (402, 86), (438, 88), (386, 96), (456, 99), (370, 107)]:
        p.stroke([(x - 7, y - 3), (x, y), (x + 7, y - 4)], SHADE, 2)


def land(p):
    p.box(0, HORIZON, 640, 52, STUBBLE)
    # Stubble: a defined pattern of short cut stalks over the gold.
    p.weave('A', (16, 9), lambda cell: cell.poly([(8, 4), (20, 4), (34, 52), (26, 52)]).box(60, 30, 10, 24))
    p.pattern(4, mask=(16, 9))
    p.box(0, HORIZON + 6, 640, 46, BARN)
    p.pattern()
    # Furrows run to a vanishing point under the sun.
    for foot in range(-200, 900, 70):
        p.poly([(SUN_X, HORIZON), (foot, 264), (foot + 22, 264)], SHADE)
    p.box(0, HORIZON - 3, 640, 5, SHADE)
    # A wire fence comes forward down the left, its posts growing as they near.
    posts = [(250, 216, 8), (190, 222, 13), (124, 231, 20), (50, 244, 30)]
    for x, y, tall in posts:
        p.box(x, y - tall, 3 + tall // 8, tall + 4, SHADE)
    for rise in (.35, .75):
        p.stroke([(x + 1, y - tall * rise) for x, y, tall in posts] + [(-10, 262 - 44 * rise)], SHADE, 1)


def elevator(p):
    # Driveway shed, the tall house with its sloped shoulders, the cupola, the annex.
    p.poly([(70, HORIZON), (70, 176), (92, 162), (116, 176), (116, HORIZON)], SHADE)
    p.poly([(110, HORIZON), (110, 112), (132, 86), (188, 86), (210, 112), (210, HORIZON)], BARN)
    p.poly([(110, HORIZON), (110, 112), (132, 86), (150, 86), (150, HORIZON)], SHADE)
    p.poly([(138, 86), (138, 62), (160, 46), (182, 62), (182, 86)], BARN)
    p.poly([(138, 86), (138, 62), (160, 46), (160, 86)], SHADE)
    p.poly([(210, HORIZON), (210, 150), (250, 132), (290, 150), (290, HORIZON)], SHADE)
    p.poly([(250, 132), (290, 150), (290, HORIZON), (250, HORIZON)], BARN)
    # The lit faces are cribbed timber: thin shadow lines mark the courses.
    for y in range(96, HORIZON, 10):
        p.box(150 if y >= 112 else 150 + (112 - y) * .1, y, 60 - (0 if y >= 112 else (112 - y) * .85), 1, SHADE)
    for y in range(160, HORIZON, 10):
        p.box(250, y, 40, 1, SHADE)
    p.box(166, 66, 8, 10, GOLD)
    p.box(84, 186, 20, 26, NIGHT)
    p.box(262, 168, 14, 12, GOLD)
    p.say(160, 146, 'HALVEN', SMALL, WHITE, 'c')
    p.box(118, 150, 84, 3, WHITE)
    # The loading spout swung out over the first car, a ladder up the house, a lightning rod.
    p.stroke([(206, 128), (300, 178)], SHADE, 4)
    p.box(296, 176, 8, 10, SHADE)
    for y in range(160, 208, 8):
        p.box(196, y, 10, 2, SHADE)
    p.box(194, 156, 2, 54, SHADE)
    p.box(206, 156, 2, 54, SHADE)
    p.box(159, 30, 2, 18, SHADE)
    # A grain truck waits its turn at the driveway.
    p.poly([(8, 208), (8, 186), (40, 186), (40, 194), (54, 194), (60, 202), (60, 208)], SHADE)
    p.box(10, 180, 28, 7, STUBBLE)
    p.disc(20, 209, 5, NIGHT)
    p.disc(50, 209, 5, NIGHT)


CAR = 0x21


def railway(p):
    # A hopper car is a macro, drawn with relative commands and called three times:
    # body, two bays cut out underneath, the ladder at its end.
    car = Fragment()
    car.fan([(6, -12), (72, 0), (6, 12), (-12, 12), (-60, 0)])
    p.routine(CAR, car)
    for x in (304, 392, 480):
        p.run(CAR, x, 196, SHADE)
        p.poly([(x + 30, 208), (x + 42, 198), (x + 54, 208)], GOLD)
        p.box(x + 6, 188, 72, 2, BARN)
        p.disc(x + 16, 209, 4, NIGHT)
        p.disc(x + 68, 209, 4, NIGHT)
    for x, tall in [(308, 40), (414, 30), (500, 23), (570, 18), (624, 15)]:
        p.box(x, HORIZON - tall, 3, tall, SHADE)
        p.box(x - 7, HORIZON - tall + 3, 17, 2, SHADE)
    p.stroke([(301, 175), (407, 185), (493, 192), (563, 197), (617, 200)], SHADE, 1)
    # The engine at the head of the train, black against the sun.
    p.poly([(568, 208), (568, 186), (586, 186), (586, 178), (604, 178), (604, 186), (640, 188), (640, 208)], SHADE)
    p.box(590, 181, 9, 6, GOLD)
    p.box(576, 176, 5, 10, SHADE)
    for x in (578, 600, 624):
        p.disc(x, 209, 4, NIGHT)
    # Two birds on the wire.
    p.disc(352, 177, 3, SHADE)
    p.disc(362, 178, 3, SHADE)


def arrow(p, x, y, change):
    if change.startswith('+') and change != '+.00':
        p.poly([(x, y), (x + 12, y - 20), (x + 24, y)], UP)
    elif change.startswith('-'):
        p.poly([(x, y - 20), (x + 12, y), (x + 24, y - 20)], DOWN)
    else:
        p.box(x + 2, y - 12, 20, 5, AMBER)


def money(p, right, y, amount, ink):
    """A price with its decimal point drawn as a square, so that it cannot be missed."""
    whole, cents = amount.split('.')
    p.say(right, y, cents, LARGE, ink, 'r')
    left = right - measure(cents, LARGE[0])
    p.box(left - 9, y - 12, 5, 5, ink)
    p.say(left - 14, y, whole, LARGE, ink, 'r')


def trend(p, x, y, closes, ink):
    """Eight closes as a line over a faint floor, the last marked with a dot in the colour of
    the day's change."""
    p.box(x, y + 1, 104, 1, CYAN)
    points = [(x + index * 14, y - 1 - close * 2.2) for index, close in enumerate(closes)]
    p.stroke(points, CYAN, 2)
    p.disc(points[-1][0] + 1, points[-1][1] - 1, 4, ink)


def ear(cell):
    """A head of grain for the DRCS character: a stalk and four pairs of kernels."""
    cell.box(34, 4, 6, 60)
    for rise in (30, 46, 62, 78):
        cell.poly([(37, rise - 4), (10, rise + 8), (14, rise + 20), (37, rise + 10)])
        cell.poly([(37, rise - 4), (64, rise + 8), (60, rise + 20), (37, rise + 10)])
    cell.poly([(30, 88), (37, 99), (44, 88)])


LATE_AFTERNOON = {VIOLET: '5a6ab8', PLUM: '8a8ac8', EMBER: 'c8a0b0', ORANGE: 'f0c890', GOLD: 'ffe8a0'}
SUNSET = {VIOLET: '3a1a5c', PLUM: '8a2a6a', EMBER: 'd8482e', ORANGE: 'f58a1e', GOLD: 'ffc93a'}


def blend(first, second, share):
    return ''.join(f'{round(int(first[i:i + 2], 16) * (1 - share) + int(second[i:i + 2], 16) * share):02x}'
                   for i in (0, 2, 4))


def build():
    # The sky is drawn in late-afternoon colours; the map carries it down to sunset
    # while the prices arrive.
    sky_now = [LATE_AFTERNOON[entry] for entry in (VIOLET, PLUM, EMBER, ORANGE, GOLD)]
    p = Screen('0b1030 fff8e0 ' + ' '.join(sky_now) + ' fff0a0 '
               '2a1420 7a2c22 b07a1a 4be06a ff5a4a 3ad0e0 ffb020 143c8c')
    p.glyph(0x21, (22, 30), ear)
    p.glyph(0x22, (34, 34), furrow_mark)
    sky(p)
    land(p)
    railway(p)
    elevator(p)
    p.box(0, 0, 640, 44, BAND)
    p.stamp(10, 39, 0x22, (34, 34), AMBER)
    p.say(54, 38, 'FURROWLINE', TITLE, AMBER, bold=1)
    p.say(626, 34, 'GRAIN 310', SMALL, WHITE, 'r')
    p.box(0, 264, 640, 182, NIGHT)
    p.box(0, 264, 640, 3, AMBER)
    p.say(16, 294, 'TUES 5 PM', SMALL, CYAN)
    p.say(180, 294, '8 DAYS', SMALL, CYAN)
    p.say(624, 294, 'CLOSE  $ A BUSHEL', SMALL, CYAN, 'r')
    p.pause(10)
    for row, (grain, price, change, closes) in enumerate(PRICES):
        y = 330 + row * 36
        if row % 2 == 0:
            p.box(8, y - 29, 624, 36, BAND)
        ink = UP if change[0] == '+' and change != '+.00' else DOWN if change[0] == '-' else AMBER
        p.stamp(14, y + 2, 0x21, (22, 30), (GOLD, SUN, AMBER, CYAN)[row])
        p.say(44, y - 2, grain, BODY, WHITE)
        trend(p, 180, y - 3, closes, ink)
        money(p, 420, y + 1, price, WHITE)
        arrow(p, 452, y - 4, change)
        p.say(612, y - 2, change if change != '+.00' else 'UNCH', BODY, ink, 'r')
        p.pause(5)
        # One step of the sunset with each row.
        for entry in (VIOLET, PLUM, EMBER, ORANGE, GOLD):
            p.recolour(entry, blend(LATE_AFTERNOON[entry], SUNSET[entry], (row + 1) / len(PRICES)))
    p.box(0, 446, 640, 34, BAND)
    p.menu(472, [('1', 'FUTURES'), ('2', 'WEATHER'), ('0', 'INDEX')], AMBER, WHITE)
    # Dusk: the yard light comes on over the driveway, and the evening star is out.
    p.pause(6)
    p.box(62, 150, 3, 62, SHADE)
    p.box(62, 150, 16, 3, SHADE)
    p.disc(79, 156, 6, SUN)
    p.poly([(79, 160), (66, 210), (70, 210), (79, 172), (88, 210), (92, 210)], GOLD)
    p.poly([(8, 208), (8, 186), (40, 186), (40, 194), (54, 194), (60, 202), (60, 208)], SHADE)
    p.disc(20, 209, 5, NIGHT)
    p.disc(50, 209, 5, NIGHT)
    p.poly([(250, 62), (253, 68), (259, 70), (253, 72), (250, 78), (247, 72), (241, 70), (247, 68)], WHITE)
    p.box(520, 58, 3, 3, WHITE)
    p.box(86, 70, 3, 3, WHITE)
    # The lamp in the cupola window winks: the elevator is open late for harvest.
    p.flash(GOLD, ORANGE, 6, 12)
    return p


if __name__ == '__main__':
    save(__file__, build)
