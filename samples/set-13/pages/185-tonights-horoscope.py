"""Tonight's Horoscope: a zodiac wheel in the full palette and a reading for the reader's sign."""
from math import cos, radians, sin
from _drawing import Plate, save

META = dict(
    title="Tonight's Horoscope",
    purpose="A daily horoscope page: a zodiac wheel, the reader's sign blinking and a short reading",
    style='Twelve-segment wheel in the full palette on deep violet, with a reading panel',
    techniques=['16-entry colour map', 'filled ring segments', 'discs for planet marks', 'proportional text',
                'BLINK on the reader\'s sign', 'WAIT between wheel and reading'],
    animated=True,
)

PALETTE = (
    '10072e ff595e ff924c ffca3a c5ca30 8ac926 36c9a4 1982c4 '
    '4267ac 6a4c93 b5179e f15bb5 fee440 fffdf5 2b2a4c c8b6ff'
)
BACKGROUND, DEEP_RED = 0, 1
SIGNS = (
    # code, full name, dates
    ('ARI', 'ARIES', '21 MAR - 19 APR'),
    ('TAU', 'TAURUS', '20 APR - 20 MAY'),
    ('GEM', 'GEMINI', '21 MAY - 20 JUN'),
    ('CAN', 'CANCER', '21 JUN - 22 JUL'),
    ('LEO', 'LEO', '23 JUL - 22 AUG'),
    ('VIR', 'VIRGO', '23 AUG - 22 SEP'),
    ('LIB', 'LIBRA', '23 SEP - 22 OCT'),
    ('SCO', 'SCORPIO', '23 OCT - 21 NOV'),
    ('SAG', 'SAGITTARIUS', '22 NOV - 21 DEC'),
    ('CAP', 'CAPRICORN', '22 DEC - 19 JAN'),
    ('AQU', 'AQUARIUS', '20 JAN - 18 FEB'),
    ('PIS', 'PISCES', '19 FEB - 20 MAR'),
)
READERS_SIGN = 4          # LEO, the reader's sign
READERS_INK = 5           # the palette entry the reader's segment is drawn in; it blinks to white
BLINK_TO = 13
INSTRUMENT_RING = 14          # the dark indigo rings round the hub
HUB_INK = 13              # the hub at the wheel's centre takes the page's bright white
WHEEL_CENTRE = (200, 240)
WHEEL_OUTER = 175
WHEEL_INNER = 46
SEGMENT_SPAN = 30
READING = (
    'TODAY IS A GOOD',
    'DAY TO SETTLE AN',
    'OLD BUSINESS. A',
    'LETTER FROM AN',
    'OLD FRIEND ARRIVES',
    'BY NOON. LUCKY 7',
)
LUCKY_COLOURS = (7, 10, 12, 6)
PANEL_LEFT = 404
PLANET_RADIUS = 190
PLANET_MARK = 3


def segment(p, centre, outer, inner, first, last, ink):
    """A ring segment between two angles in degrees, as a closed polygon."""
    cx, cy = centre
    steps = 8
    span = last - first
    arc_out = [(cx + outer * cos(radians(first + span * i / steps)),
                cy + outer * sin(radians(first + span * i / steps))) for i in range(steps + 1)]
    arc_in = [(cx + inner * cos(radians(last - span * i / steps)),
               cy + inner * sin(radians(last - span * i / steps))) for i in range(steps + 1)]
    p.poly(arc_out + arc_in, ink)


def wheel(p):
    """Twelve segments, each in its own palette entry, with the sign's code set at its middle."""
    cx, cy = WHEEL_CENTRE
    for index, (code, _, _) in enumerate(SIGNS):
        first = -90 + SEGMENT_SPAN * index + 1
        last = first + SEGMENT_SPAN - 2
        ink = 1 + index
        segment(p, WHEEL_CENTRE, WHEEL_OUTER, WHEEL_INNER, first, last, ink)
        middle = radians(first + SEGMENT_SPAN / 2 - 1)
        label_x = cx + 118 * cos(middle) - 16
        label_y = cy + 118 * sin(middle) + 6
        p.text(label_x, label_y, code, 12, 18, BACKGROUND)
    p.disc(cx, cy, WHEEL_INNER, HUB_INK)
    # Two thin navy rings round the hub make the wheel read as an instrument.
    p.disc(cx, cy, WHEEL_INNER + 4, INSTRUMENT_RING, fill=False)
    p.disc(cx, cy, WHEEL_INNER + 10, INSTRUMENT_RING, fill=False)
    p.text(cx - 32, cy + 6, 'TODAY', 10, 14, BACKGROUND)
    p.blink(READERS_INK, BLINK_TO, on=6, off=6)
    p.wait(8, 'wheel')


def reading(p):
    """The reader's sign, its dates, a pointer from the wheel's LEO segment, the reading and the lucky colours."""
    code, name, dates = SIGNS[READERS_SIGN]
    p.poly([(PANEL_LEFT - 14, 118), (PANEL_LEFT - 2, 108), (PANEL_LEFT - 2, 128)], 3)
    p.text(PANEL_LEFT, 110, name, 18, 28, 3)
    p.text(PANEL_LEFT, 140, dates, 12, 18, 13)
    p.rect(PANEL_LEFT, 156, 220, 2, 4)
    for index, line in enumerate(READING):
        p.text(PANEL_LEFT, 186 + 26 * index, line, 12, 18, 13)
    p.text(PANEL_LEFT, 362, 'LUCKY COLOURS', 11, 15, 13)
    for index, colour in enumerate(LUCKY_COLOURS):
        p.rect(PANEL_LEFT + index * 56, 372, 46, 26, colour)
    p.text(PANEL_LEFT, 424, 'TOMORROW: A QUIET DAY', 10, 14, 13)
    p.wait(6, 'reading')


def planets(p):
    """Twelve planet marks on a ring outside the wheel, and a crescent moon above it."""
    cx, cy = WHEEL_CENTRE
    for index in range(12):
        angle = radians(-90 + 30 * index + 15)
        p.disc(cx + PLANET_RADIUS * cos(angle), cy + PLANET_RADIUS * sin(angle), PLANET_MARK, 12)
    p.disc(574, 84, 30, 12, fill=False)
    p.disc(574, 84, 22, 12)
    p.disc(584, 78, 19, BACKGROUND)


def build():
    p = Plate(PALETTE)
    p.rect(0, 0, 640, 480, BACKGROUND)
    # Stars are four-pointed sparkles of the moonlit colour.
    for x, y in ((14, 60), (340, 28), (372, 30), (560, 52), (12, 330), (40, 420), (300, 424)):
        p.line([(x - 5, y), (x + 5, y)], 15, 2)
        p.line([(x, y - 5), (x, y + 5)], 15, 2)
    p.title(24, 36, 'ORRERY DAILY', 12, 22, 30)
    planets(p)
    wheel(p)
    reading(p)
    p.rect(0, 440, 640, 40, DEEP_RED)
    p.text(24, 466, 'PRESS 4 FOR ANOTHER SIGN     0 FOR INDEX', 12, 18, 13)
    return p


if __name__ == '__main__':
    save(__file__, build)
