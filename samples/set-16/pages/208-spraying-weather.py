"""208: a farm forecast that answers one question: when can I spray?"""
import math

from _kit import BODY, LARGE, SMALL, TITLE, Screen, furrow_mark, save

META = dict(title='Spraying Weather',
            purpose='A farm forecast gives wind and rain by the hour and names the hours fit for spraying.',
            style='Striped field under an hourly wind and rain board',
            techniques=['two defined fill patterns', 'DRCS logo character', 'filled polygons', 'native circles',
                        'rotated arrows', 'proportional text', 'keypad key tops', 'WAIT reveal',
                        'picture redrawn in stages', 'BLINK'],
            animated=True)

NAVY, WHITE, SKY, HAZE, CROP, ROW, SOIL, RED = range(8)
DARK, RAIN, YELLOW, GOOD, CAUTION, POOR, PANEL, BAND = range(8, 16)
HORIZON = 112
SOCK_X = 470

# hour, wind from (degrees), wind speed in miles an hour, chance of rain, verdict
HOURS = [('6 AM', 270, 4, 5, GOOD), ('9 AM', 225, 6, 10, GOOD), ('NOON', 180, 11, 20, CAUTION),
         ('3 PM', 135, 17, 45, POOR), ('6 PM', 90, 14, 70, POOR)]
DRIFT = {GOOD: 'LOW', CAUTION: 'SOME', POOR: 'HIGH'}
COMPASS = {270: 'W', 225: 'SW', 180: 'S', 135: 'SE', 90: 'E'}


def field(p):
    p.box(0, 44, 640, 40, SKY)
    p.box(0, 84, 640, HORIZON - 84, HAZE)
    p.disc(350, 68, 20, YELLOW)
    for x, y, r in [(92, 70, 15), (116, 64, 19), (142, 72, 14), (244, 86, 11), (262, 82, 14), (282, 88, 10)]:
        p.disc(x, y, r, WHITE)
    p.box(72, 72, 88, 12, WHITE)
    p.box(234, 88, 58, 8, WHITE)
    p.box(0, HORIZON, 640, 192 - HORIZON, CROP)
    # The crop rows are a defined pattern: slanted light stripes over the green.
    # Two scales of it, fine in the distance and coarse close to, give the field its depth.
    stripe = lambda cell: cell.poly([(0, 0), (22, 0), (60, 59), (38, 59)])
    p.weave('A', (10, 6), stripe)
    p.pattern(4, mask=(10, 6))
    p.box(0, HORIZON + 4, 640, 26, ROW)
    p.weave('B', (24, 14), stripe)
    p.pattern(5, mask=(24, 14))
    p.box(0, HORIZON + 30, 640, 192 - HORIZON - 30, ROW)
    p.pattern(0)
    # The tramline the tractor follows.
    p.poly([(300, 192), (314, HORIZON + 30), (326, HORIZON + 30), (340, 192)], SOIL)
    p.box(0, HORIZON - 2, 640, 4, DARK)
    # On the horizon: a shelterbelt, the neighbour's barn and silo, and three grain bins.
    for x, r in [(18, 7), (30, 9), (44, 8), (57, 10), (71, 7), (84, 8), (520, 8), (534, 10), (549, 8), (563, 9)]:
        p.disc(x, HORIZON - r + 2, r, DARK)
    p.poly([(196, HORIZON), (196, 100), (204, 92), (220, 88), (236, 92), (244, 100), (244, HORIZON)], DARK)
    p.box(250, 88, 14, 24, DARK)
    p.disc(257, 88, 7, DARK)
    for x in (400, 418, 436):
        p.box(x, 100, 14, 12, DARK)
        p.poly([(x - 1, 100), (x + 7, 93), (x + 15, 100)], DARK)


def sprayer(p):
    # A tractor seen from behind, its boom across twelve rows, each nozzle a fan of mist
    # that leans a little downwind.
    for x in range(132, 512, 30):
        if 290 < x < 350:
            continue
        p.poly([(x, 152), (x - 5, 178), (x + 15, 178)], HAZE)
        p.poly([(x, 152), (x + 2, 178), (x + 8, 178)], WHITE)
    p.box(118, 148, 404, 4, DARK)
    for x in range(132, 512, 30):
        p.box(x - 2, 150, 5, 5, DARK)
    for x in (196, 444):
        p.stroke([(x, 150), (320, 122)], DARK, 2)
    # Spray tank, rear wheels with their treads, the body and the cab.
    p.box(288, 140, 64, 22, YELLOW)
    p.box(288, 158, 64, 4, CAUTION)
    for x in (274, 342):
        p.box(x, 132, 24, 48, DARK)
        for y in range(138, 178, 9):
            p.stroke([(x + 2, y + 5), (x + 11, y), (x + 20, y + 5)], SOIL, 2)
    p.box(300, 116, 40, 26, RED)
    p.box(304, 92, 32, 26, DARK)
    p.box(308, 96, 24, 16, HAZE)
    p.disc(320, 108, 7, DARK)
    p.box(312, 86, 16, 6, RED)
    p.box(342, 84, 4, 34, DARK)
    # Windsock on a tall pole.  At dawn it hangs: the wind is light.
    p.box(SOCK_X, 58, 4, 118, DARK)
    p.poly([(SOCK_X + 4, 62), (SOCK_X + 12, 64), (SOCK_X + 11, 96), (SOCK_X + 4, 94)], RED)
    p.box(SOCK_X + 4, 74, 8, 7, WHITE)


def storm(p):
    """The afternoon's weather comes into the picture from the south-east as the forecast reaches it."""
    for x, y, r in [(506, 66, 20), (536, 68, 20), (572, 66, 21), (608, 68, 20), (636, 66, 20)]:
        p.disc(x, y, r, PANEL)
    p.box(506, 68, 134, 18, PANEL)
    for x in range(514, 640, 22):
        p.stroke([(x, 90), (x - 7, 108)], RAIN, 2)
    # The wind gets up ahead of it: the hanging sock is painted out and drawn streaming.
    p.box(SOCK_X + 4, 60, 10, 24, SKY)
    p.box(SOCK_X + 4, 84, 10, 14, HAZE)
    p.poly([(SOCK_X, 62), (SOCK_X - 44, 68), (SOCK_X - 46, 80), (SOCK_X, 84)], RED)
    p.poly([(SOCK_X - 14, 64), (SOCK_X - 26, 66), (SOCK_X - 27, 82), (SOCK_X - 14, 83)], WHITE)
    # And the spray no longer falls where it is aimed: each fan now trails off downwind.
    for x in range(132, 512, 30):
        if 290 < x < 350:
            continue
        p.poly([(x, 153), (x - 30, 166), (x - 34, 174), (x - 6, 170)], HAZE)


def wind_arrow(p, x, y, bearing, speed, ink):
    """An arrow pointing where the wind blows to, longer for a stronger wind."""
    p.disc(x, y, 22, DARK)
    p.disc(x, y, 22, ink, fill=False, width=2)
    angle = math.radians(bearing + 180)
    ux, uy = math.sin(angle), -math.cos(angle)
    px, py = -uy, ux
    length = 9 + speed * .6
    tail = (x - ux * length, y - uy * length)
    neck = (x + ux * (length - 10), y + uy * (length - 10))
    tip = (x + ux * length, y + uy * length)
    p.poly([(tail[0] + px * 3, tail[1] + py * 3), (neck[0] + px * 3, neck[1] + py * 3),
            (neck[0] + px * 9, neck[1] + py * 9), tip, (neck[0] - px * 9, neck[1] - py * 9),
            (neck[0] - px * 3, neck[1] - py * 3), (tail[0] - px * 3, tail[1] - py * 3)], ink)


def build():
    p = Screen('08142c ffffff 6cc4f0 c4e8f8 2f9a3c 86d444 6a4420 d83a2a '
               '1c1c24 3a8cff ffd23a 30d868 ff9a1e ff5050 12305a 0c5a3a')
    p.glyph(0x22, (34, 34), furrow_mark)
    field(p)
    sprayer(p)
    p.box(0, 0, 640, 44, BAND)
    p.stamp(10, 39, 0x22, (34, 34), YELLOW)
    p.say(54, 38, 'FURROWLINE', TITLE, YELLOW, bold=1)
    p.say(626, 34, 'SPRAYING 322', SMALL, WHITE, 'r')
    p.box(0, 192, 640, 208, NAVY)
    p.box(0, 192, 640, 3, YELLOW)
    p.say(8, 220, 'TUES', SMALL, WHITE, bold=1)
    p.say(8, 262, 'WIND', SMALL, YELLOW)
    p.say(8, 304, 'MPH', SMALL, YELLOW)
    p.say(8, 330, 'DRIFT', SMALL, YELLOW)
    p.say(8, 376, 'RAIN', SMALL, RAIN)
    for column, (hour, bearing, speed, rain, verdict) in enumerate(HOURS):
        x = 142 + column * 110
        # One card an hour, headed in the colour of its verdict.
        p.box(x - 50, 198, 100, 198, PANEL)
        p.box(x - 50, 198, 100, 28, verdict)
        p.say(x, 222, hour, SMALL, NAVY, 'c')
        wind_arrow(p, x, 254, bearing, speed, verdict)
        p.say(x, 306, f'{COMPASS[bearing]} {speed}', BODY, WHITE, 'c')
        # What that wind does to a fine spray.
        p.say(x, 330, DRIFT[verdict], SMALL, verdict, 'c')
        # The rain gauge: a scale to 100 per cent with a mark at half.
        p.box(x - 44, 338, 36, 52, NAVY)
        p.box(x - 44, 363, 36, 2, PANEL)
    # The verdict's two hours are bracketed before it is spelled out below.
    p.frame(88, 194, 218, 206, WHITE, 3)
    p.pause(8)
    for column, (hour, bearing, speed, rain, verdict) in enumerate(HOURS):
        x = 142 + column * 110
        tall = rain * .5
        p.box(x - 44, 390 - tall, 36, tall, RAIN)
        p.say(x + 22, 388, f'{rain}%', SMALL, WHITE, 'c')
        p.pause(3)
        if hour == 'NOON':
            storm(p)
    p.box(0, 400, 640, 46, GOOD)
    p.say(320, 436, 'GOOD SPRAYING: TUES AM', LARGE, NAVY, 'c', bold=1)
    p.box(0, 446, 640, 34, BAND)
    p.menu(472, [('1', 'WEDNESDAY'), ('2', 'FROST'), ('0', 'INDEX')], YELLOW, WHITE)
    p.flash(POOR, CAUTION, 5, 5)
    return p


if __name__ == '__main__':
    save(__file__, build)
