"""School Bus Is Late: a district bulletin with a stopped bus, a snowbank and programmable snowflakes."""
from math import cos, pi, sin
from _drawing import Plate, save

META = dict(
    title='School Bus Is Late',
    purpose='A district bulletin that tells parents a route is twenty minutes late in the snow',
    style='Winter bulletin: a yellow bus in rectangles and discs behind a white snowbank, snowflakes as programmable characters',
    techniques=['16-entry colour map', 'filled polygons and discs', 'programmable characters for snowflakes',
                'proportional text in large type', 'BLINK on the alert line'],
    animated=False,
)

PALETTE = (
    '0f2741 f7fbff ffc300 1b1b1b e63946 9ec5e6 6b7c93 2d4f7c '
    'c8d6e5 264653 8d99ae ff9f1c 0b3954 fefae0 90be6d 4a4e69'
)
NIGHT, SNOW, BUS_YELLOW, TYRE, ALERT, SKY, ROAD, HILL = range(8)
SHADE, TEAL, GREY, ORANGE, NAVY, CREAM, LEAF, SLATE = range(8, 16)

SNOWFLAKE_BIG = 'S'
SNOWFLAKE_SMALL = 'T'
STAR_RADIUS = (46, 14)
SMALL_STAR_RADIUS = (34, 10)
SPOKES = 6


def star(outer, inner, centre=50):
    """A six-armed star on the 100 grid, alternating outer and inner points."""
    points = []
    for index in range(SPOKES * 2):
        radius = outer if index % 2 == 0 else inner
        angle = pi * index / SPOKES - pi / 2
        points.append((centre + radius * cos(angle), centre + radius * sin(angle)))
    return points


def bus(p):
    """The bus, side on: a yellow body, a row of windows and a stripe, with wheels under it."""
    p.rect(186, 206, 262, 118, BUS_YELLOW)
    p.rect(186, 206, 262, 8, NAVY)
    for x in range(200, 380, 50):
        p.rect(x, 224, 40, 40, SKY)
    # Two windows are lit from inside, as if passengers are aboard.
    p.disc(270, 244, 9, CREAM)
    p.disc(370, 244, 9, CREAM)
    # The front faces right: a windscreen, a door and a headlight.
    p.rect(412, 214, 30, 44, SKY)
    p.rect(412, 262, 26, 56, NAVY)
    p.disc(438, 300, 4, CREAM)
    # The stop arm folds out from the side of the bus as an octagon with a white bar.
    p.poly([(186 + 20 * cos(pi / 8 + index * pi / 4), 250 + 20 * sin(pi / 8 + index * pi / 4))
            for index in range(8)], ALERT)
    p.line([(170, 250), (202, 250)], SNOW, 4)
    # Three children wait at the stop by the octagon, in coats of red, teal and orange.
    for x, coat in ((586, ALERT), (608, TEAL), (628, ORANGE)):
        p.disc(x, 346, 9, CREAM)
        p.rect(x - 10, 356, 20, 30, coat)
        p.rect(x - 9, 386, 6, 14, TYRE)
        p.rect(x + 3, 386, 6, 14, TYRE)
    p.rect(186, 294, 262, 8, TYRE)
    p.line([(186, 300), (448, 300)], TYRE, 3)
    for wheel_x in (248, 390):
        p.disc(wheel_x, 318, 22, TYRE)
        p.disc(wheel_x, 318, 9, SHADE)
    p.text(246, 288, 'CROSSRIDGE', 9, 13, NAVY)
    p.wait(6, 'bus')


def snowbank(p):
    """A snowbank of white polygons, built in front of the bus's lower part."""
    # The bank sits below the wheels, so the stopped bus stands on the road.
    drop = 40
    p.poly([(x, y + drop) for x, y in ((150, 350), (150, 330), (176, 314), (210, 300), (246, 296), (290, 290),
                                        (330, 300), (366, 292), (410, 298), (446, 310), (474, 326), (490, 350))], SNOW)
    p.poly([(x, y + drop) for x, y in ((170, 340), (194, 326), (232, 322), (268, 330), (300, 318), (340, 326),
                                        (380, 318), (420, 330), (448, 340))], SHADE)
    p.wait(6, 'snowbank')


def stop_sign(p):
    """A red octagon of the kind a driver meets at a stop, its letters drawn in white."""
    centre_x, centre_y, radius = 560, 262, 34
    outline = [(centre_x + radius * cos(pi / 8 + index * pi / 4), centre_y + radius * sin(pi / 8 + index * pi / 4))
               for index in range(8)]
    p.poly(outline, ALERT)
    p.text(centre_x - 20, centre_y + 6, 'STOP', 9, 13, SNOW)
    p.line([(centre_x, centre_y + radius), (centre_x, 350)], TYRE, 4)


def hills(p):
    """Blue hills behind the road and the bus, lit on their ridges by shade."""
    p.poly([(0, 236), (80, 210), (170, 226), (250, 200), (340, 222), (430, 196), (520, 218), (640, 200),
            (640, 300), (0, 300)], HILL)
    p.poly([(0, 260), (120, 244), (240, 256), (360, 240), (480, 258), (600, 244), (640, 250), (640, 300), (0, 300)],
           GREY)


# Each run is (x, baseline y, character, width, height): snowflakes are programmable characters.
FALLING_SNOW = (
    (40, 150, SNOWFLAKE_BIG, 34, 44), (104, 190, SNOWFLAKE_SMALL, 22, 28),
    (470, 130, SNOWFLAKE_BIG, 30, 40), (560, 186, SNOWFLAKE_SMALL, 22, 28),
    (330, 172, SNOWFLAKE_SMALL, 24, 32), (10, 290, SNOWFLAKE_BIG, 28, 36),
    (196, 120, SNOWFLAKE_SMALL, 20, 26), (272, 108, SNOWFLAKE_BIG, 26, 34),
    (400, 210, SNOWFLAKE_SMALL, 18, 24), (606, 252, SNOWFLAKE_BIG, 30, 40),
    (60, 360, SNOWFLAKE_SMALL, 24, 30), (520, 386, SNOWFLAKE_BIG, 36, 46),
    (150, 420, SNOWFLAKE_SMALL, 22, 28), (470, 418, SNOWFLAKE_SMALL, 26, 34),
)


def snowflakes(p):
    """Snowflakes are programmable characters, so each one is a single character in the text stream."""
    for x, y, character, width, height in FALLING_SNOW:
        p.programmable(x, y, character, width, height, SNOW)


def build():
    p = Plate(PALETTE)
    # The sky and the ground.
    p.rect(0, 0, 640, 480, SKY)
    p.rect(0, 300, 640, 180, SNOW)
    # The road runs across the foot of the picture, with tyre tracks leading to the bus.
    p.poly([(0, 326), (640, 326), (640, 440), (0, 440)], ROAD)
    for x in range(20, 640, 96):
        p.rect(x, 380, 48, 4, CREAM)
    p.line([(120, 440), (236, 330)], SHADE, 4)
    p.line([(170, 440), (276, 330)], SHADE, 4)
    # The programmable characters are defined once, before the snow that uses them.
    p.glyph(SNOWFLAKE_BIG, (SNOW, star(*STAR_RADIUS)))
    p.glyph(SNOWFLAKE_SMALL, (SNOW, star(*SMALL_STAR_RADIUS)))
    hills(p)
    snowflakes(p)
    # The band at the top carries the district's name and the route.
    p.rect(0, 0, 640, 56, NAVY)
    p.title(24, 40, 'CROSSRIDGE SCHOOLS', CREAM, 18, 28)
    p.text(466, 40, 'BUS NOTICE', 12, 18, BUS_YELLOW)
    # The headline sits on a red band.
    p.rect(0, 76, 640, 64, ALERT)
    p.text(24, 122, 'ROUTE 14 IS LATE', 28, 40, SNOW)
    p.text(24, 186, '20 MIN LATE', 22, 32, NAVY)
    p.wait(6, 'headline')
    bus(p)
    snowbank(p)
    stop_sign(p)
    p.rect(0, 440, 640, 40, NAVY)
    p.text(24, 466, 'PARENTS: TEXT 5 FOR ALERTS', 12, 18, CREAM)
    p.text(380, 466, 'NEW ARRIVAL 8:40 AM', 12, 18, BUS_YELLOW)
    return p


if __name__ == '__main__':
    save(__file__, build)
