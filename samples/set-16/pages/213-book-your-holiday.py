"""213: a travel agent's page: the beach, the flights, the price and the key that books it."""
import math

from _kit import BANNER, BODY, LARGE, SMALL, TITLE, Screen, save

META = dict(title='Book Your Holiday',
            purpose='A travel service sells a week on an island: the beach, the flights, the price, and one key to book.',
            style='Travel-poster beach in bands over a booking panel',
            techniques=['banded fills', 'defined wave pattern', 'DRCS logo character', 'filled polygons',
                        'native circles', 'proportional text', 'keypad key tops', 'WAIT', 'BLINK shimmer'],
            animated=True)

NAVY, WHITE, ZENITH, SKY, HAZE, DEEP, SURF, SAND = range(8)
DUNE, PALM, LEAF, TRUNK, SUN, PINK, ORANGE, PANEL = range(8, 16)
SHORE = 150


def sky_and_sea(p):
    for top, ink in [(44, ZENITH), (82, SKY), (120, HAZE)]:
        p.box(0, top, 640, SHORE - top, ink)
    p.disc(540, 92, 28, SUN)
    for step in range(12):
        angle = math.radians(step * 30)
        p.stroke([(540 + 36 * math.cos(angle), 92 + 36 * math.sin(angle)),
                  (540 + 48 * math.cos(angle), 92 + 48 * math.sin(angle))], SUN, 3)
    # A far island and a sail.
    p.poly([(250, SHORE), (290, 132), (330, 126), (372, 138), (400, SHORE)], PALM)
    p.box(0, SHORE, 640, 70, DEEP)
    p.weave('A', (32, 12), lambda cell: cell.poly([(0, 6), (25, 22), (50, 6), (75, 22), (99, 6),
                                                    (99, 14), (75, 30), (50, 14), (25, 30), (0, 14)]))
    p.pattern(4, mask=(32, 12))
    p.box(0, SHORE + 4, 640, 62, SURF)
    p.pattern(0)
    # The sun's path on the water, widening toward the beach.
    for row, wide in enumerate((16, 26, 20, 36, 28, 46, 34)):
        p.box(540 - wide / 2 + (row % 2) * 6, SHORE + 4 + row * 8, wide, 3, SUN)
    # Fair-weather cloud over the island.
    for x, y, r in [(286, 96, 9), (300, 90, 12), (316, 97, 9), (196, 62, 8), (208, 57, 10), (222, 63, 8)]:
        p.disc(x, y, r, WHITE)
    p.box(280, 98, 42, 8, WHITE)
    p.box(190, 64, 38, 7, WHITE)
    # A thatched hut on stilts at the end of a short pier.
    p.box(566, 176, 74, 4, TRUNK)
    for x in (572, 596, 620):
        p.box(x, 180, 3, 18, TRUNK)
    p.box(588, 152, 40, 24, DUNE)
    p.box(602, 160, 10, 16, NAVY)
    p.poly([(580, 154), (608, 132), (636, 154)], TRUNK)
    p.poly([(362, 172), (362, 140), (386, 172)], WHITE)
    p.poly([(358, 172), (358, 148), (342, 172)], PINK)
    p.poly([(338, 174), (392, 174), (384, 182), (346, 182)], NAVY)


def beach(p):
    p.poly([(0, 214), (120, 206), (300, 212), (460, 204), (640, 210), (640, 282), (0, 282)], WHITE)
    p.poly([(0, 220), (120, 212), (300, 218), (460, 210), (640, 216), (640, 282), (0, 282)], SAND)
    p.poly([(0, 256), (200, 246), (420, 262), (640, 250), (640, 282), (0, 282)], DUNE)
    # Parasol, towel and a pail.
    p.box(450, 196, 4, 62, TRUNK)
    p.bow((400, 204), (452, 168), (504, 204), PINK, fill=True)
    p.poly([(434, 204), (452, 172), (470, 204)], WHITE)
    p.poly([(382, 258), (442, 250), (450, 262), (390, 270)], ORANGE)
    # A deck chair in the parasol's shade, a starfish and two shells at the water's edge.
    p.stroke([(400, 262), (426, 226)], TRUNK, 3)
    p.stroke([(408, 228), (432, 262)], TRUNK, 3)
    p.poly([(404, 256), (426, 228), (432, 232), (412, 260)], WHITE)
    p.poly([(410, 248), (420, 235), (426, 239), (416, 252)], PINK)
    points = []
    for step in range(10):
        reach = 11 if step % 2 == 0 else 4.5
        points.append((300 + reach * math.sin(step * math.pi / 5), 232 - reach * math.cos(step * math.pi / 5)))
    p.poly(points, ORANGE)
    p.oval(280, 240, 7, 5, PINK, 10)
    p.oval(180, 236, 6, 4, WHITE, 10)
    p.poly([(600, 248), (620, 248), (617, 266), (603, 266)], ZENITH)
    p.bow((600, 248), (610, 238), (620, 248), NAVY, width=2)


def frond(p, crown, tip, lift, ink):
    """A palm leaf: a curved spine from crown to tip, its lower edge cut into leaflets."""
    control = ((crown[0] + tip[0]) / 2, (crown[1] + tip[1]) / 2 - lift)
    spine = []
    for step in range(7):
        s = step / 6
        spine.append(((1 - s) ** 2 * crown[0] + 2 * s * (1 - s) * control[0] + s * s * tip[0],
                      (1 - s) ** 2 * crown[1] + 2 * s * (1 - s) * control[1] + s * s * tip[1]))
    under = []
    for step in range(6, 0, -1):
        x, y = spine[step]
        droop = 20 * math.sin(math.pi * step / 6.5) + 3
        under.append((x, y + droop))
        under.append(((x + spine[step - 1][0]) / 2, (y + spine[step - 1][1]) / 2 + droop * .35))
    p.poly(spine + under, ink)


def palm(p, foot, crown, scale=1.0):
    fx, fy = foot
    cx, cy = crown
    bend = (fx + (cx - fx) * .25, fy + (cy - fy) * .6)
    thick = 12 * scale
    p.poly([(fx - thick, fy), (bend[0] - thick * .8, bend[1]), (cx - thick * .4, cy), (cx + thick * .4, cy + 4),
            (bend[0] + thick * .8, bend[1] + 4), (fx + thick, fy)], TRUNK)
    for step in range(1, 8):
        s = step / 8
        x = fx + (bend[0] - fx) * min(1, s * 2) + (cx - bend[0]) * max(0, s * 2 - 1)
        y = fy + (bend[1] - fy) * min(1, s * 2) + (cy - bend[1]) * max(0, s * 2 - 1)
        p.stroke([(x - thick * .7, y), (x + thick * .7, y - 4)], NAVY, 1)
    for dx, dy, lift, ink in [(-104, 34, 44, PALM), (104, 40, 46, PALM), (-92, -22, 30, LEAF),
                              (96, -16, 30, LEAF), (-44, -62, 14, PALM), (48, -60, 14, PALM),
                              (-70, 62, 30, LEAF), (66, 70, 30, LEAF)]:
        frond(p, (cx, cy), (cx + dx * scale, cy + dy * scale), lift * scale, ink)
    p.disc(cx - 6 * scale, cy + 8 * scale, 7 * scale, TRUNK)
    p.disc(cx + 8 * scale, cy + 9 * scale, 7 * scale, TRUNK)


def plane(p, x, y, heading, ink):
    """A small airliner seen from above, nose toward heading (1 right, -1 left)."""
    h = heading
    p.poly([(x - 12 * h, y), (x + 8 * h, y - 3), (x + 13 * h, y), (x + 8 * h, y + 3)], ink)
    p.poly([(x + 2 * h, y), (x - 6 * h, y - 11), (x - 10 * h, y - 11), (x - 4 * h, y)], ink)
    p.poly([(x + 2 * h, y), (x - 6 * h, y + 11), (x - 10 * h, y + 11), (x - 4 * h, y)], ink)
    p.poly([(x - 10 * h, y), (x - 14 * h, y - 5), (x - 16 * h, y - 5), (x - 13 * h, y)], ink)
    p.poly([(x - 10 * h, y), (x - 14 * h, y + 5), (x - 16 * h, y + 5), (x - 13 * h, y)], ink)


def burst(p, x, y, rx, ry, points, ink):
    """A price sticker: a star whose points alternate between two ellipses."""
    edge = []
    for step in range(points * 2):
        angle = math.pi * step / points
        k = 1 if step % 2 == 0 else .84
        edge.append((x + rx * k * math.cos(angle), y + ry * k * math.sin(angle)))
    p.poly(edge, ink)


def mark(cell):
    """The travel service's mark for a DRCS character: a half sun over two waves."""
    cell.disc(50, 50, 28)
    cell.cut()
    cell.box(0, 0, 99, 48)
    cell.ink()
    for base in (30, 8):
        cell.poly([(2, base), (26, base + 12), (50, base), (74, base + 12), (98, base), (98, base + 9),
                   (74, base + 21), (50, base + 9), (26, base + 21), (2, base + 9)])


def build():
    p = Screen('0a1a3c ffffff 2484e0 6cc0f4 c4ecfc 0a6ab0 3cc8dc f6de9c '
               'dcb468 1c8a3c 5ccc4c 8a5a2a ffe040 ff4a8a ff8a1e 0c3c5c')
    p.glyph(0x21, (34, 34), mark)
    sky_and_sea(p)
    beach(p)
    # Somebody has built a castle.
    p.poly([(206, 254), (206, 238), (212, 238), (212, 244), (220, 244), (220, 232), (232, 232), (232, 244),
            (240, 244), (240, 238), (246, 238), (246, 254)], DUNE)
    p.box(222, 244, 8, 10, TRUNK)
    p.box(225, 218, 2, 14, TRUNK)
    p.poly([(227, 218), (238, 222), (227, 226)], PINK)
    # A swimmer out past the surf.
    p.disc(250, 190, 5, TRUNK)
    p.stroke([(240, 194), (260, 194)], WHITE, 2)
    palm(p, (36, 282), (10, 150), .7)
    palm(p, (96, 282), (146, 112))
    # Gulls over the water, and the morning flight coming in.
    for x, y in [(380, 112), (402, 102), (430, 114)]:
        p.stroke([(x - 8, y - 4), (x, y), (x + 8, y - 5)], WHITE, 2)
    p.box(0, 0, 640, 44, NAVY)
    p.stamp(10, 39, 0x21, (34, 34), SUN)
    p.say(54, 38, 'SUNDRIFT HOLIDAYS', TITLE, PINK, bold=1)
    p.say(626, 34, 'TRAVEL 540', SMALL, WHITE, 'r')
    p.box(0, 282, 640, 164, PANEL)
    p.box(0, 282, 640, 4, SUN)
    p.say(16, 322, 'ISLA CORVANTA', LARGE, SUN, bold=1)
    p.say(16, 350, '7 NIGHTS AT PELLARO INN', SMALL, WHITE)
    for index in range(3):
        rating = []
        for step in range(10):
            reach = 9 if step % 2 == 0 else 3.8
            rating.append((346 + index * 20 + reach * math.sin(step * math.pi / 5),
                           340 - reach * math.cos(step * math.pi / 5)))
        p.poly(rating, SUN)
    plane(p, 30, 376, 1, HAZE)
    p.say(56, 386, 'OUT', BODY, HAZE)
    p.say(132, 386, 'SAT 08:15  SD 204', BODY, WHITE)
    plane(p, 30, 406, -1, HAZE)
    p.say(56, 416, 'BACK', BODY, HAZE)
    p.say(132, 416, 'SAT 19:40  SD 205', BODY, WHITE)
    p.say(16, 443, '6 SEATS LEFT AT THIS PRICE', SMALL, ORANGE)
    # While the panel is read, the morning flight crosses the sky, its trail growing behind it.
    for piece in range(5):
        p.box(290 + piece * 22, 58, 22, 3, WHITE)
        p.pause(2)
    plane(p, 414, 59, 1, WHITE)
    # The price arrives last and pops: a small starburst, then the full sticker, then the key
    # that books it.
    p.pause(8)
    burst(p, 528, 338, 60, 28, 14, ORANGE)
    p.pause(2)
    burst(p, 528, 338, 106, 52, 14, ORANGE)
    burst(p, 528, 338, 98, 46, 14, SUN)
    p.say(528, 322, 'EACH, FROM', SMALL, NAVY, 'c')
    p.say(528, 372, '$489', BANNER, NAVY, 'c', bold=1)
    p.box(430, 392, 196, 44, PINK)
    p.say(528, 426, 'BOOK: PRESS 5', SMALL, WHITE, 'c', bold=1)
    p.box(0, 446, 640, 34, NAVY)
    p.menu(472, [('5', 'BOOK'), ('7', 'MORE ISLANDS'), ('0', 'INDEX')], SUN, WHITE)
    p.flash(PINK, ORANGE, 4, 6)
    # The wave crests catch the light: the pattern's entry shimmers.
    p.flash(SURF, HAZE, 3, 11, 3)
    return p


if __name__ == '__main__':
    save(__file__, build)
