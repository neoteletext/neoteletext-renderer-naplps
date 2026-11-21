import math
import random
from _page import Plate, save, arc_points

META = dict(title='The Night Sky Tonight',
            purpose='An almanac page for a hobby club: tonight\'s sky as a dome over the rooftops, with the '
                    'planets named, the Moon\'s phase and the times to go out and look.',
            style='Deep blue dome in concentric bands over a black roofline, twinkling stars, gold labels',
            techniques=['dusk turned to night by four colour-map changes after a WAIT', 'DRCS stars', 'Milky Way in two defined speckle textures', 'silhouetted stargazer at a telescope', 'three BLINKs with staggered delays for twinkling', 'concentric arcs',
                        'Moon phase from two arcs and a halo ring', 'Jupiter with its four moons', 'WAIT before the labels', 'entry 0 freed and recoloured for a meteor that BLINK flashes'],
            animated=True)

PALETTE = ('000008 ffffff 2c4a8c 5a6aa8 a07aa0 f0a070 05070f fff8e0 '
           'cfe4ff ffe0b0 46568e fff2b0 26305e e2683a ffd040 101830').split()
BLACK, WHITE, OUTER, MID, INNER, GLOW, ROOF, STAR_A, STAR_B, STAR_C, DIM, MOON, SHADOW, MARS, GOLD, BAND = range(16)
SPARKLE, DOT = 0x21, 0x22
METEOR = BLACK
CX, CY, R = 320, 352, 300
NIGHT_SKY = [(OUTER, '0a1440'), (MID, '13205a'), (INNER, '1d2f74'), (GLOW, '34408a')]


def roofline(p):
    """The houses, trees and the neighbour at the telescope, in silhouette."""
    roof = [(20, 352), (20, 330), (60, 312), (100, 330), (100, 352)]
    p.rect(0, 340, 640, 140, ROOF)
    p.poly(roof, ROOF)
    p.rect(120, 318, 60, 30, ROOF)
    p.poly([(112, 320), (150, 296), (188, 320)], ROOF)
    p.rect(164, 296, 8, 16, ROOF)
    for x, r in [(250, 26), (284, 32), (316, 24)]:
        p.disc(x, 344 - r, r, ROOF)
    p.rect(420, 312, 90, 36, ROOF)
    p.poly([(410, 314), (465, 286), (520, 314)], ROOF)
    p.line([(560, 340), (560, 282)], ROOF, 3)
    p.line([(546, 292), (574, 292)], ROOF, 2)
    p.disc(600, 326, 22, ROOF)
    p.rect(440, 324, 12, 10, GOLD)
    # A neighbour at a telescope in the garden, trained on the Moon.
    p.disc(352, 300, 7, ROOF)
    p.poly([(344, 308), (360, 308), (364, 340), (340, 340)], ROOF)
    p.line([(358, 314), (372, 304)], ROOF, 3)
    p.poly([(366, 306), (402, 282), (408, 290), (372, 314)], ROOF)
    p.line([(384, 300), (372, 340)], ROOF, 2)
    p.line([(384, 300), (396, 340)], ROOF, 2)
    p.line([(384, 300), (386, 340)], ROOF, 2)


def build():
    p = Plate('206', PALETTE)
    # Everything outside the dome is painted in the roof's near-black, so nothing is left in entry 0
    # and that entry can be given to the meteor.
    p.rect(0, 0, 640, 480, ROOF)
    p.define_drcs(SPARKLE, 18, 18 * 0.96, [[(0.5, 0.98), (0.6, 0.6), (0.98, 0.5), (0.6, 0.4), (0.5, 0.02),
                                             (0.4, 0.4), (0.02, 0.5), (0.4, 0.6)]])
    p.define_drcs(DOT, 18, 18 * 0.96, [('disc', 0.5, 0.5, 0.16)])
    p.rect(0, 0, 640, 40, BAND)
    p.text(16, 31, 'THE SKY TONIGHT', 18, 28, GOLD, prop=False)
    p.rtext(624, 30, 'p 880', 14, 22, WHITE, prop=False)
    # The page opens at dusk: the dome's four entries hold twilight colours, the houses stand against it,
    # and after a pause the same entries are turned to night before the stars come out.
    for radius, colour in [(R, OUTER), (R * 0.72, MID), (R * 0.45, INNER), (R * 0.2, GLOW)]:
        p.poly(arc_points(CX, CY, radius, radius * 0.98, 0, 180, 40), colour)
    roofline(p)
    p.wait(12)
    for entry, colour in NIGHT_SKY:
        p.recolour(entry, colour)
    p.wait(6)
    # The Milky Way: two defined speckle textures, a broad haze and a denser core, across the dome.
    speck = lambda x, y: [(x, y), (x + 0.17, y), (x + 0.17, y + 0.17), (x, y + 0.17)]
    p.define_texture('A', 14, [speck(0.1, 0.2), speck(0.55, 0.7), speck(0.75, 0.15)])
    p.define_texture('B', 14, [speck(0.1, 0.2), speck(0.55, 0.7), speck(0.75, 0.15), speck(0.35, 0.45),
                               speck(0.8, 0.85), speck(0.3, 0.9)])
    p.cmd(0x23, b'\x60')
    p.poly([(96, 338), (140, 250), (210, 160), (290, 96), (340, 80), (384, 92), (330, 126), (266, 184),
            (210, 262), (186, 338)], DIM)
    p.cmd(0x23, b'\x68')
    p.poly([(124, 338), (168, 252), (236, 166), (306, 108), (346, 96), (312, 126), (250, 186), (196, 266),
            (160, 338)], DIM)
    p.solid()
    rng = random.Random(206)
    stars = []
    while len(stars) < 46:
        x, y = rng.uniform(40, 600), rng.uniform(70, 330)
        if math.hypot((x - CX), (y - CY) / 0.98) > R - 14:
            continue
        if math.hypot(x - 470, y - 150) < 52 or math.hypot(x - 210, y - 200) < 30:
            continue
        stars.append((x, y, rng.choice([STAR_A, STAR_B, STAR_C]), rng.random() < 0.3))
    for x, y, colour, bright in stars:
        p.chars(x - 9, y + 9, [SPARKLE if bright else DOT], 18, 18 * 0.96, colour)
    # The Moon, waxing gibbous: the whole disc in shadow, then the lit part.
    p.ring(470, 150, 41, DIM, 1)
    p.disc(470, 150, 34, SHADOW)
    lit = arc_points(470, 150, 34, 34, -90, 90, 20) + arc_points(470, 150, 16, 34, 90, 270, 20)
    p.poly(lit, MOON)
    # Planets.
    p.disc(210, 200, 9, MOON)
    # Jupiter's four large moons in a line, as binoculars show them.
    for mx in (184, 194, 228, 240):
        p.disc(mx, 200, 2, MOON)
    p.disc(392, 262, 6, MARS)
    roofline(p)
    for x, letter in [(36, 'E'), (178, 'SE'), (320, 'S'), (462, 'SW'), (604, 'W')]:
        p.ctext(x, 374, letter, 15, 24, GOLD if len(letter) == 1 else DIM, prop=False)
    p.wait(10)
    p.line([(218, 196), (232, 206)], GOLD, 1)
    p.text(234, 216, 'Jupiter', 15, 24, GOLD)
    p.line([(398, 258), (412, 248)], GOLD, 1)
    p.text(414, 250, 'Mars', 15, 24, GOLD)
    p.text(522, 140, "Moon", 15, 24, GOLD)
    p.text(522, 164, "9 days old", 13, 20, WHITE)
    # A meteor in the east, drawn in entry 0 given the outer sky's colour: BLINK flashes it white for
    # two tenths of a second in every three seconds.
    p.recolour(METEOR, NIGHT_SKY[0][1])
    p.line([(168, 118), (214, 144)], METEOR, 2)
    p.disc(215, 145, 3, METEOR)
    p.wait(6)
    p.text(16, 410, 'Sunset 8:51 pm', 15, 24, WHITE)
    p.rtext(624, 410, 'Moon sets 1:12 am', 15, 24, WHITE)
    p.text(16, 440, 'Clear skies until 3 am. Jupiter is the', 14, 22, STAR_B)
    p.text(16, 466, 'brightest light in the south-east.', 14, 22, STAR_B)
    p.blink(METEOR, WHITE, 2, 28)
    for entry, delay in [(STAR_A, 0), (STAR_B, 3), (STAR_C, 6)]:
        p.blink(entry, DIM, 2, 7, delay)
    return p


if __name__ == '__main__':
    save(__file__, build)
