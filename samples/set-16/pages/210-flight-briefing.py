"""210: the pilots' terminal at a small airport: where the cloud is, and what is closed."""
import math

from _kit import BODY, SMALL, TITLE, Screen, save

META = dict(title='Flight Briefing',
            purpose='An airport terminal for pilots maps cloud ceilings at the region\'s airfields and lists the notices.',
            style='Dark chart of lakes and uplands with signal-coloured airfields',
            techniques=['filled polygons', 'defined fill pattern', 'cross-hatching', 'dotted line texture',
                        'native circles', 'wind barbs', 'runways on their headings', 'WAIT-drawn route',
                        'proportional text', 'BLINK'],
            animated=True)

NIGHT, WHITE, LOW, HIGH, WATER, RIDGE, CLEAR, MARGINAL = range(8)
CLOSED, CLOUD, ROUTE, CYAN, AMBER, PANEL, BAND, GREY = range(8, 16)

# ident, x, y, state, where its plate goes (r right, l left, d below), cloud ceiling in feet.
# The plates keep out of the way of the route.
# and the heading of its runway in degrees.
FIELDS = [('CBL', 150, 112, CLEAR, 'r', '4500', 80), ('DNM', 92, 236, CLEAR, 'l', '6000', 40),
          ('HLT', 300, 204, CLEAR, 'd', '3500', 130), ('WRN', 420, 104, MARGINAL, 'r', '1200', 10),
          ('AST', 520, 232, CLOSED, 'r', '300', 60)]
NOTICES = [('CBL', CLEAR, 'RUNWAY 08 CLOSED TO 1800'), ('WRN', MARGINAL, 'NO FUEL UNTIL FRIDAY'),
           ('AST', CLOSED, 'FOG.  CEILING 300 FEET')]


def chart(p):
    p.box(0, 44, 640, 256, LOW)
    # Uplands in the north-east, with a line of peaks.
    p.poly([(330, 44), (640, 44), (640, 190), (590, 170), (540, 120), (470, 96), (400, 80)], HIGH)
    p.poly([(470, 44), (640, 44), (640, 120), (580, 96), (520, 66)], RIDGE)
    for x, y in [(520, 60), (560, 74), (604, 70), (590, 100)]:
        p.poly([(x - 12, y + 12), (x, y - 8), (x + 12, y + 12)], WHITE)
        p.poly([(x - 12, y + 12), (x, y - 8), (x - 2, y + 12)], GREY)
    # The highest ground, in feet, where a pilot under the cloud needs it.
    p.poly([(432, 66), (438, 54), (444, 66)], WHITE)
    p.say(448, 70, '7200', SMALL, WHITE)
    # The big lake, a second one, and the river between them and the western sea.
    lake = [(176, 76), (236, 60), (296, 78), (318, 116), (280, 150), (222, 160), (190, 132), (160, 104)]
    pond = [(350, 240), (396, 226), (440, 244), (430, 276), (380, 284)]
    coast = [(60, 44), (40, 90), (52, 140), (26, 200), (40, 260), (20, 300)]
    p.poly(lake, WATER)
    p.poly(pond, WATER)
    p.poly([(0, 44)] + coast + [(0, 300)], WATER)
    # Shorelines in a fine light line, as a chart draws them.
    p.stroke(lake + lake[:1], CYAN, 1)
    p.stroke(pond + pond[:1], CYAN, 1)
    p.stroke(coast, CYAN, 1)
    # Sandbanks off the coast.
    for x, y, w in [(8, 110, 18), (4, 168, 14), (10, 236, 16)]:
        p.box(x, y, w, 2, CYAN)
    p.stroke([(222, 160), (210, 190), (150, 210), (120, 262), (40, 262)], WATER, 4)
    p.stroke([(280, 150), (330, 190), (372, 232)], WATER, 4)
    # The chart's graticule, dotted.
    p.pattern(line=1)
    for x in (160, 320, 480):
        p.stroke([(x, 46), (x, 298)], GREY, 2)
    for y in (128, 214):
        p.stroke([(0, y), (640, y)], GREY, 2)
    p.pattern()
    # A deck of low cloud over the east, drawn as a pattern the ground shows through.
    p.weave('A', (12, 10), lambda cell: cell.box(0, 0, 55, 30))
    p.pattern(4, mask=(12, 10))
    edge = [(640, 146), (596, 140), (552, 138), (508, 146), (470, 160), (446, 188), (440, 222),
            (450, 256), (438, 286), (436, 300)]
    p.poly(edge + [(640, 300)], CLOUD)
    p.pattern(0)
    # Its edge is a bank of scallops: solid lumps, each with a shadow under it.
    for index, (x, y) in enumerate(edge[1:-1]):
        radius = 12 + index % 3 * 3
        p.disc(x + 3, y + 4, radius, GREY)
        p.disc(x, y, radius, CLOUD)
    for index in range(len(edge) - 2):
        (x1, y1), (x2, y2) = edge[index + 1], edge[index + 2]
        p.disc((x1 + x2) / 2 + 4, (y1 + y2) / 2 + 2, 9, CLOUD)
    # A danger area, cross-hatched with a real pel, and the chart's scale.
    p.pattern(3)
    p.disc(170, 268, 22, AMBER, width=3)
    p.pattern()
    p.disc(170, 268, 22, AMBER, fill=False, width=2)
    p.box(56, 286, 80, 4, WHITE)
    for x in (56, 96, 134):
        p.box(x, 280, 2, 10, WHITE)
    p.say(60, 278, '50 NM', SMALL, WHITE)
    # North arrow.
    p.poly([(16, 104), (26, 70), (36, 104), (26, 96)], WHITE)
    p.say(26, 68, 'N', SMALL, WHITE, 'c')


def barb(p, x, y, bearing, knots):
    """A wind barb: the staff points to where the wind comes from, one feather for each ten knots."""
    angle = math.radians(bearing)
    ux, uy = math.sin(angle), -math.cos(angle)
    tail = (x + ux * 30, y + uy * 30)
    p.stroke([(x, y), tail], WHITE, 2)
    p.disc(x, y, 3, WHITE)
    for feather in range(knots // 10):
        root = (tail[0] - ux * feather * 7, tail[1] - uy * feather * 7)
        p.stroke([root, (root[0] + uy * 11 + ux * 4, root[1] - ux * 11 + uy * 4)], WHITE, 2)


def leg(p, start, end, ink, plate, above=True):
    """One leg of a route in dashes, with its length on a plate at the middle."""
    (x1, y1), (x2, y2) = start, end
    for step in range(0, 10, 2):
        a, b = step / 10 + .08, (step + 1) / 10 + .08
        p.stroke([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], ink, 3)
        p.pause(1)
    x, y = (x1 + x2) / 2, (y1 + y2) / 2 + (-14 if above else 36)
    p.box(x - 20, y - 20, 40, 22, NIGHT)
    p.say(x, y, plate, SMALL, ink, 'c', fit=40)


def airfield(p, ident, x, y, state, side, ceiling, runway):
    """The field's symbol with its runway laid on its heading, and a plate with its ident
    and its ceiling in feet."""
    p.disc(x, y, 15, NIGHT)
    p.disc(x, y, 12, state)
    angle = math.radians(runway)
    along, up = 9 * math.sin(angle), -9 * math.cos(angle)
    p.stroke([(x - along - 1, y - up - 1), (x + along - 1, y + up - 1)], NIGHT, 3)
    width = 62
    left = {'r': x + 22, 'l': x - 18 - width, 'd': x - width / 2 + 4}[side]
    top = y + 20 if side == 'd' else y - 22
    p.box(left - 4, top, width, 44, NIGHT)
    p.box(left - 4, top, 3, 44, state)
    p.say(left + 3, top + 21, ident, SMALL, WHITE, fit=width)
    p.say(left + 3, top + 42, ceiling, SMALL, state, fit=width)


def build():
    p = Screen('06101e ffffff 1c5438 2f7448 1a4aa0 8a7c52 40e060 ffd020 '
               'ff4040 c4ccdc ff60d0 40d0f0 ffa820 10284a 0c4c6c 8094ac')
    chart(p)
    for field in FIELDS:
        airfield(p, *field)
    p.say(198, 284, 'D4', SMALL, AMBER)
    # Winds over the lake, the western plain and the uplands, and what the plates' figures are.
    barb(p, 250, 132, 250, 10)
    barb(p, 60, 150, 230, 10)
    barb(p, 380, 60, 200, 20)
    barb(p, 584, 258, 150, 30)
    p.box(206, 46, 150, 22, NIGHT)
    p.say(281, 67, 'CEILINGS, FT', SMALL, GREY, 'c', fit=146)
    p.box(0, 0, 640, 44, BAND)
    p.say(14, 38, 'CORBEL LAKE', TITLE, AMBER, bold=1)
    p.say(626, 34, 'PILOT BRIEFING 0715', SMALL, WHITE, 'r')
    p.box(0, 300, 640, 146, NIGHT)
    p.box(0, 300, 640, 3, AMBER)
    p.say(14, 328, 'NOTICES TO AIRMEN', SMALL, CYAN)
    for row, (ident, state, notice) in enumerate(NOTICES):
        y = 356 + row * 28
        p.say(14, y, ident, BODY, state, bold=1)
        p.say(84, y, notice, BODY, WHITE)
    p.box(0, 446, 640, 34, BAND)
    x = 14
    for state, word in [(CLEAR, 'CLEAR'), (MARGINAL, 'LOW CLOUD'), (CLOSED, 'BELOW LIMITS')]:
        p.disc(x + 8, 463, 8, state)
        p.say(x + 24, 472, word, SMALL, WHITE)
        x += 24 + {'CLEAR': 96, 'LOW CLOUD': 150, 'BELOW LIMITS': 0}[word]
    p.say(626, 472, '0 INDEX', SMALL, WHITE, 'r')
    # The route asked for is drawn leg by leg; its destination is below limits and flashes;
    # then the terminal offers the alternate.
    p.pause(6)
    # The pilot's aircraft, at the field the briefing was asked from, nose along the route.
    p.poly([(96, 208), (122, 204), (128, 207), (122, 211)], WHITE)
    p.poly([(112, 207), (104, 194), (100, 195), (106, 208)], WHITE)
    p.poly([(112, 208), (108, 222), (104, 222), (106, 208)], WHITE)
    p.poly([(98, 208), (94, 201), (92, 202), (94, 209)], WHITE)
    leg(p, (108, 232), (284, 206), ROUTE, '84')
    leg(p, (316, 206), (504, 230), ROUTE, '92', above=False)
    p.flash(CLOSED, NIGHT, 4, 8)
    p.pause(12)
    leg(p, (311, 193), (408, 114), AMBER, '61')
    p.say(14, 440, 'ALT', BODY, AMBER, bold=1)
    p.say(84, 440, 'FOR AST USE WRN, 61 NM', BODY, WHITE)
    return p


if __name__ == '__main__':
    save(__file__, build)
