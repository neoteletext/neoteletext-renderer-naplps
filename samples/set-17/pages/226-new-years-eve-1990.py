"""New Year's Eve 1990: the service's makers imagine their own future, a skyline under fireworks at midnight."""
import random

from _screen import Plate, polar, save

META = dict(
    title="New Year's Eve 1990",
    purpose='The city service greets a new decade: a countdown, then fireworks over the skyline',
    style='Midnight skyline and river under multicoloured bursts, a greeting set along an arc',
    techniques=['bursts of lines, one colour-map entry each', 'BLINK colour cycling with staggered delays',
                'WAIT countdown then reveal', 'a greeting on a ribbon', 'firework reflections in the river',
                'lit windows and river reflections', 'a bridge of filled-arc arches', 'a crowd in silhouette', 'a drop-shadowed year', 'a tower clock at midnight', 'twinkling stars by BLINK'],
    animated=True,
)

PALETTE = ('070a24 121a4a 23286a 0b0b18 1c1c3a ffd36b 0a1a3a ff3b5c '
           'ffd23f 4de8ff 6bff7a ff6bff ffffff 2a1060 fff2b0 ffb0d8')
(SKY_TOP, SKY_MID, SKY_LOW, TOWER_DARK, TOWER, WINDOW, RIVER, RED,
 GOLD, CYAN, GREEN, MAGENTA, WHITE, BAND, SPARK, PINK) = range(16)

BURSTS = ((84, 84, 60, RED), (556, 84, 60, CYAN), (320, 62, 42, GOLD), (84, 272, 48, GREEN),
          (564, 268, 48, MAGENTA))
GREETING = 'HAPPY NEW DECADE'


def burst(p, cx, cy, radius, ink, rng):
    p.line([(cx + rng.randint(-20, 20), min(330, cy + 150)), (cx, cy + 10)], SPARK, 1)
    for k in range(18):
        a = k * 20 + rng.randint(-4, 4)
        inner, outer = polar(cx, cy, radius * 0.25, a), polar(cx, cy, radius * rng.uniform(0.8, 1.0), a)
        p.line([inner, outer], ink, 2)
        p.disc(*polar(cx, cy, radius * 1.08, a), 3, ink)
    p.disc(cx, cy, 5, SPARK)


def build():
    rng = random.Random(226)
    p = Plate(PALETTE, SKY_TOP)
    p.rect(0, 140, 640, 90, SKY_MID)
    p.rect(0, 230, 640, 180, SKY_LOW)
    for _ in range(40):
        p.disc(rng.randint(0, 639), rng.randint(4, 220), 1.5, WHITE)

    # The countdown, before the city is drawn round it.
    for number in ('3', '2', '1'):
        p.rect(264, 236, 112, 90, SKY_LOW)
        p.text(296, 318, number, 48, 76, WHITE, prop=False)
        p.wait(10)
    p.rect(264, 236, 112, 90, SKY_LOW)

    # The skyline: towers of two depths and their windows.
    x = 0
    while x < 640:
        width, height = rng.randint(36, 70), rng.randint(30, 90)
        p.rect(x, 410 - height - 30, width, height + 30, TOWER)
        # The back row is lit too, more sparsely.
        for wy in range(410 - height - 22, 410 - height + 10, 12):
            for wx in range(x + 5, x + width - 12, 14):
                if rng.random() < 0.3:
                    p.rect(wx, wy, 5, 6, WINDOW)
        x += width - 8
    x = 0
    while x < 640:
        width, height = rng.randint(40, 80), rng.randint(20, 80)
        p.rect(x, 410 - height, width, height, TOWER_DARK)
        for wy in range(int(410 - height + 8), 404, 14):
            for wx in range(x + 6, x + width - 8, 12):
                if rng.random() < 0.45:
                    p.rect(wx, wy, 6, 7, WINDOW)
        x += width + rng.randint(0, 10)
    p.rect(460, 250, 40, 160, TOWER_DARK)
    p.poly([(460, 250), (480, 214), (500, 250)], TOWER_DARK)
    p.line([(480, 214), (480, 206)], TOWER_DARK, 3)
    # The tower clock at midnight: both hands at twelve.
    p.disc(480, 276, 14, SPARK)
    p.line([(480, 276), (480, 264)], TOWER_DARK, 3)
    p.line([(480, 276), (480, 266)], TOWER_DARK, 2)
    for k in range(12):
        p.disc(*polar(480, 276, 11, k * 30), 1, TOWER_DARK)
    # The river and the city's reflection.
    p.rect(0, 410, 640, 40, RIVER)
    for _ in range(36):
        wx = rng.randint(0, 630)
        p.rect(wx, rng.randint(414, 444), rng.randint(6, 20), 2, WINDOW if rng.random() < 0.6 else CYAN)
    p.wait(6, 'city')

    for cx, cy, radius, ink in BURSTS:
        burst(p, cx, cy, radius, ink, rng)
        p.wait(4)

    # Each burst is mirrored in the river as broken streaks of its own colour.
    for cx, _, radius, ink in BURSTS:
        for k in range(6):
            x = cx - radius / 2 + rng.randint(0, int(radius))
            p.rect(x, 414 + k * 6, rng.randint(4, 14), 2, ink)

    # A bridge of arches over the river, its lamps lit.
    p.rect(0, 398, 300, 12, TOWER)
    for k in range(5):
        x = k * 60
        p.rect(x, 410, 60, 22, TOWER)
        p.arc((x + 8, 432), (x + 30, 414), (x + 52, 432), RIVER, fill=True)
        p.rect(x + 8, 432, 44, 2, RIVER)
    for x in range(10, 300, 30):
        p.line([(x, 398), (x, 386)], TOWER, 2)
        p.disc(x, 384, 3, WINDOW)

    # The water behind the crowd holds the glow of the bursts.
    p.rect(300, 418, 340, 4, GOLD)
    p.rect(300, 426, 340, 3, MAGENTA)
    p.rect(300, 432, 340, 2, CYAN)
    # The crowd on the near bank, arms raised.
    for k in range(26):
        x = 300 + k * 13 + rng.randint(-3, 3)
        top = 432 + rng.randint(-4, 4)
        p.disc(x, top, 6, TOWER_DARK)
        p.rect(x - 7, top + 4, 14, 20, TOWER_DARK)
        if k % 3 == 0:
            p.line([(x + 5, top + 6), (x + 12, top - 12)], TOWER_DARK, 3)

    # The greeting on a ribbon, and the year below it.
    p.poly([(112, 132), (140, 132), (140, 196), (112, 196), (124, 164)], PINK)
    p.poly([(528, 132), (500, 132), (500, 196), (528, 196), (516, 164)], PINK)
    p.rect(132, 124, 376, 64, BAND)
    p.rect(132, 124, 376, 64, SPARK, fill=False)
    p.text(144, 170, GREETING, 22, 32, SPARK, prop=False)
    p.text(206, 324, '1990', 60, 84, TOWER_DARK, prop=False)
    p.text(200, 318, '1990', 60, 84, PINK, prop=False)

    # The bursts cycle through each other's colours, each on its own beat.
    for step, (_, _, _, ink) in enumerate(BURSTS):
        p.blink(ink, (GOLD, MAGENTA, RED, CYAN, GREEN)[step], on=3, off=3 + step, delay=step)
    p.blink(WINDOW, SPARK, on=2, off=9)
    # The stars twinkle: their entry dips to the mid sky's colour now and then.
    p.blink(WHITE, SKY_MID, on=2, off=7, delay=4)

    p.rect(0, 450, 640, 30, BAND)
    p.text(16, 472, 'CITYLAMP 226  31 DEC 1989   12:00 MIDNIGHT', 12, 18, SPARK, prop=False)
    return p


if __name__ == '__main__':
    save(__file__, build)
