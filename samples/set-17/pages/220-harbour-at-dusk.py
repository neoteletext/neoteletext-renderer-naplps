"""Gallery Page: Harbour at Dusk, a picture built shape by shape whose sky turns from gold to violet."""
import random

from _screen import Plate, oval, save

META = dict(
    title='Gallery Page: Harbour at Dusk',
    purpose="The service's gallery shows a videotex artist's harbour, built layer by layer as the viewer watches",
    style='Layered flat-colour landscape in a garish sunset palette, after the period videotex painters',
    techniques=['elliptical sky bands round the sun', 'hundreds of overlapping polygons',
                'colour-map dusk in three WAIT steps', 'windows, stars, quay lamps and portholes lit by one SET COLOR', 'smoke curls in arcs',
                'two lighthouse beams sweeping by staggered BLINK', 'rigging and pennants in single lines', 'swell in incremental lines'],
    animated=True,
)

# The palette as first sent: a gold late afternoon. The dusk steps below redefine the sky, sun, sea and windows.
PALETTE = ('f8d35e f4ac4c ef8540 e8643a d94a3a fff1b0 2a3a6e f4b45a '
           '6a4a7a 1a1430 3a2c4a 3a2a2a f2ead8 ffe27a c8302c fff4c0')
(SKY_TOP, SKY_HIGH, SKY_MID, SKY_LOW, SKY_HORIZON, SUN, SEA, GLINT,
 HILLS, LAND, TOWN, WINDOW, TOWER, LAMP, HULL, BEAM) = range(16)
CAPTION = TOWER

DUSK = (
    {SKY_TOP: 'c88a5a', SKY_HIGH: 'e07a4a', SKY_MID: 'e8643a', SKY_LOW: 'e84a4a', SUN: 'ffd07a', SEA: '27305e'},
    {SKY_TOP: '6a3a6a', SKY_HIGH: 'a8466a', SKY_MID: 'd4505a', SKY_LOW: 'e8603a', SUN: 'ffa45a',
     GLINT: 'e87a5a', HILLS: '4a2e5a'},
    {SKY_TOP: '24184a', SKY_HIGH: '4a2466', SKY_MID: '7e2e6e', SKY_LOW: 'c0446a', SKY_HORIZON: 'f07048',
     SUN: 'ff8a4a', SEA: '161838', GLINT: 'c4507a', HILLS: '2e1e44', WINDOW: 'ffd76a'},
)
HORIZON = 276
SUN_X = 396


def sailboat(p, x, y, scale):
    p.poly([(x - 30 * scale, y), (x + 34 * scale, y), (x + 24 * scale, y + 12 * scale), (x - 22 * scale, y + 12 * scale)], HULL)
    p.line([(x, y), (x, y - 70 * scale)], LAND, 2)
    p.poly([(x + 3 * scale, y - 68 * scale), (x + 3 * scale, y - 6 * scale), (x + 32 * scale, y - 6 * scale)], TOWER)
    p.poly([(x - 3 * scale, y - 60 * scale), (x - 3 * scale, y - 6 * scale), (x - 24 * scale, y - 6 * scale)], CAPTION)
    # Forestay, backstay and a pennant at the masthead.
    p.line([(x, y - 70 * scale), (x + 34 * scale, y)], LAND, 1)
    p.line([(x, y - 70 * scale), (x - 30 * scale, y)], LAND, 1)
    p.poly([(x, y - 70 * scale), (x - 16 * scale, y - 65 * scale), (x, y - 61 * scale)], HULL)
    for k in range(3):
        p.rect(x - 26 * scale + k * 6, y + 16 * scale + k * 6, 50 * scale - k * 10, 2, GLINT)


# INCREMENTAL LINE moves (guide section 12): 01 a step across, 11 across and down, 00 then 10 reverses dy.
ACROSS, BOTH, ESCAPE, FLIP_DY = 1, 3, 0, 2


def swell(p, x, y, crests, ink):
    """A line of swell: each crest is six steps across with one rise and one fall, two bits a step."""
    half = [ACROSS, ACROSS, BOTH, ACROSS, ACROSS, BOTH, ACROSS, ACROSS, ESCAPE, FLIP_DY]
    p.pel(2)
    p.scribble(x, y, 6, 2, half * (2 * crests), ink)


def build():
    rng = random.Random(220)
    p = Plate(PALETTE, SKY_TOP)

    # Sky: concentric bands round the setting sun, then thin cloud strata lit from below.
    for ry, ink in ((300, SKY_HIGH), (220, SKY_MID), (150, SKY_LOW), (90, SKY_HORIZON)):
        p.poly(oval(SUN_X, HORIZON, ry * 1.8, ry, 64), ink)
    # Early stars, drawn in the windows' entry: dark specks now, lit with the town at dusk.
    for sx, sy in ((30, 30), (110, 64), (200, 22), (604, 40), (520, 18), (36, 120), (624, 96), (280, 52)):
        p.disc(sx, sy, 2, WINDOW)
    for cx, cy, rx, ink in ((140, 96, 120, SKY_MID), (500, 70, 150, SKY_LOW), (270, 160, 100, SKY_HIGH),
                            (560, 190, 90, SKY_MID), (90, 210, 80, SKY_LOW), (430, 130, 70, SKY_HORIZON)):
        p.poly(oval(cx, cy, rx, 7, 20), ink)
        p.poly(oval(cx + rx * 0.3, cy + 6, rx * 0.6, 4, 16), SKY_HORIZON if ink != SKY_HORIZON else SKY_LOW)
    p.disc(SUN_X, HORIZON, 44, SUN)
    p.wait(6, 'sky')

    # Far hills across the horizon, the sea, and the glitter road beneath the sun.
    p.poly([(0, HORIZON), (0, 236), (60, 226), (120, 240), (190, 228), (250, 252), (300, HORIZON)], HILLS)
    p.poly([(470, HORIZON), (520, 254), (600, 246), (640, 252), (640, HORIZON)], HILLS)
    p.rect(0, HORIZON, 640, 480 - HORIZON, SEA)
    for row in range(26):
        y = HORIZON + 4 + row * 6.5
        spread = 30 + row * 7
        for _ in range(3):
            width = rng.randint(10, 40)
            x = SUN_X + rng.randint(-spread, spread) - width / 2
            # The road is brightest where it begins: its first rows in the sun's own entry.
            p.rect(x, y, width, 2, SUN if row < 5 else GLINT)

    # A steamer on the horizon, against the sun, its portholes in the windows' entry.
    p.poly([(318, HORIZON), (324, HORIZON - 10), (432, HORIZON - 10), (424, HORIZON)], LAND)
    p.rect(344, HORIZON - 20, 60, 10, LAND)
    p.rect(368, HORIZON - 34, 12, 14, LAND)
    p.rect(368, HORIZON - 36, 12, 3, HULL)
    for px in range(332, 424, 10):
        p.rect(px, HORIZON - 7, 3, 3, WINDOW)
    p.wait(6, 'sea')

    # Long swell across the near water, in the town's shadow colour.
    for sx, sy, crests in ((20, 372, 5), (300, 392, 6), (40, 428, 7), (380, 436, 4), (180, 410, 3)):
        swell(p, sx, sy, crests, TOWN)

    # The town on the quay: gabled warehouses, their dark windows, the pier and its posts.
    p.poly([(0, 300), (0, 196), (34, 176), (68, 196), (68, 210), (110, 186), (152, 210), (152, 200),
            (196, 180), (240, 200), (240, 300)], TOWN)
    p.poly([(176, 300), (176, 150), (190, 136), (204, 150), (204, 300)], TOWN)
    p.rect(186, 120, 8, 18, TOWN)
    for x, y in ((14, 210), (40, 210), (14, 238), (40, 238), (82, 222), (120, 222), (82, 252), (120, 252),
                 (164, 216), (206, 216), (164, 246), (206, 246), (184, 166), (184, 196), (226, 252)):
        p.rect(x, y, 12, 16, WINDOW)
    # Chimneys with curls of smoke.
    for cx, top in ((24, 170), (120, 180), (226, 176)):
        p.rect(cx, top, 10, 18, TOWN)
        for k in range(3):
            p.arc((cx + 5 + k * 10, top - 4 - k * 16), (cx + 12 + k * 10, top - 12 - k * 16),
                  (cx + 5 + k * 10, top - 20 - k * 16), HILLS)
    p.rect(0, 296, 300, 12, LAND)
    # Quay lamps in the windows' entry, so they light with the town.
    for lx in (60, 150, 250):
        p.line([(lx, 296), (lx, 268)], LAND, 2)
        p.disc(lx, 266, 5, WINDOW)
    for x in range(10, 300, 28):
        p.rect(x, 308, 5, 26, LAND)
        p.rect(x - 2, 336, 9, 2, GLINT)
    # The lit windows' reflections under the pier.
    for x in (20, 46, 88, 126, 170, 212):
        for k in range(3):
            p.rect(x + (k % 2) * 3, 342 + k * 10, 8 - k * 2, 3, WINDOW)
    p.wait(6, 'town')

    # The lighthouse on its rocks, its beam hatched across the sky.
    p.poly([(500, 300), (530, 262), (566, 252), (612, 258), (640, 248), (640, 310), (520, 316)], LAND)
    # The rock in facets of two tones.
    for facet in ([(520, 300), (536, 270), (566, 262), (560, 296)], [(600, 262), (640, 254), (640, 286), (612, 292)],
                  [(560, 300), (580, 276), (610, 296), (590, 312)]):
        p.poly(facet, HILLS)
    p.poly([(560, 256), (566, 150), (590, 150), (596, 256)], TOWER)
    for y in (172, 214):
        p.poly([(565, y), (591, y), (592, y + 16), (564, y + 16)], HULL)
    # The gallery and its rail.
    p.rect(554, 146, 48, 6, LAND)
    for rx in range(556, 602, 8):
        p.line([(rx, 146), (rx, 138)], LAND, 1)
    p.line([(554, 138), (602, 138)], LAND, 1)
    p.rect(562, 128, 32, 22, LAND)
    p.rect(566, 132, 24, 16, LAMP)
    p.poly([(560, 128), (578, 112), (596, 128)], HULL)
    # Two beams, each in its own entry; they blink into the sky's colour in turn, so the light sweeps.
    p.poly([(566, 134), (384, 92), (392, 130), (566, 144)], LAMP)
    p.poly([(590, 134), (640, 112), (640, 140), (590, 144)], BEAM)

    # Boats with their reflections, and gulls.
    sailboat(p, 330, 352, 1.0)
    sailboat(p, 470, 318, 0.6)
    sailboat(p, 120, 410, 1.3)
    # A rower pulls home past the pier.
    p.poly([(214, 376), (286, 376), (276, 388), (222, 388)], HULL)
    p.rect(244, 356, 12, 20, TOWER)
    p.disc(250, 350, 6, TOWER)
    p.line([(236, 368), (204, 392)], LAND, 2)
    p.line([(262, 368), (296, 392)], LAND, 2)
    for k in range(2):
        p.rect(222 + k * 4, 394 + k * 6, 56 - k * 8, 2, GLINT)
    for gx, gy in ((300, 90), (322, 104), (260, 120), (480, 150)):
        p.line([(gx - 8, gy - 4), (gx, gy), (gx + 8, gy - 4)], LAND, 2)
    p.wait(6, 'harbour')

    # Dusk falls in three steps; the windows light on the last.
    for step in DUSK:
        for entry, colour in step.items():
            p.recolour(entry, colour)
        p.wait(10, 'dusk')
    p.blink(LAMP, SKY_MID, on=6, off=6)
    p.blink(BEAM, SKY_MID, on=6, off=6, delay=6)

    p.rect(0, 448, 640, 32, LAND)
    p.text(16, 472, 'GALLERY 220  HARBOUR AT DUSK  M. OSTRANDER', 12, 18, CAPTION, prop=False)
    return p


if __name__ == '__main__':
    save(__file__, build)
