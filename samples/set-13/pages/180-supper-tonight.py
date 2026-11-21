"""Supper Tonight: a recipe page with a dish in section and a timer whose hand is the colour map."""
from math import cos, radians, sin
from _drawing import Plate, save

META = dict(
    title='Supper Tonight',
    purpose='A recipe page for a noodle bake: ingredients, method and a kitchen timer',
    style='Recipe card in cream and tomato, a cutaway casserole and a segmented timer',
    techniques=['16-entry colour map', 'filled polygons', 'segmented timer by colour-map entries',
                'proportional text', 'WAIT between the title, the dish and the timer'],
    animated=True,
)

PALETTE = (
    '1f1a17 fdf6e3 c0392b f39c12 f7d46a e8c9a0 8b5a2b 3d6b35 '
    '2c3e50 7f8c8d fef0b3 5dade2 9b2226 27ae60 dfe6e9 1e2a38'
)
CHARCOAL, CREAM, TOMATO, ORANGE, CHEESE, NOODLE, CRUST, PARSLEY = range(8)
INK, GREY, PALE_CHEESE, DISH_BLUE, SAUCE, LIT, UNLIT, NAVY = range(8, 16)

TIMER_CENTRE = (520, 200)
TIMER_OUTER = 74
TIMER_INNER = 40
SEGMENTS = 12
LIT_SEGMENTS = 8
SEGMENT_GAP_DEGREES = 3
TOP_ANGLE = -90
INGREDIENT_STEP = 26
METHOD_STEP = 24
CURRENT_STEP = 2
BAND_TOP = 456


def wedge(p, centre, outer, inner, first_degrees, last_degrees, ink):
    """A ring segment between two angles, as a closed polygon."""
    cx, cy = centre
    steps = 6
    span = last_degrees - first_degrees
    outline = [(cx + outer * cos(radians(first_degrees + span * i / steps)),
                cy + outer * sin(radians(first_degrees + span * i / steps))) for i in range(steps + 1)]
    outline += [(cx + inner * cos(radians(last_degrees - span * i / steps)),
                 cy + inner * sin(radians(last_degrees - span * i / steps))) for i in range(steps + 1)]
    p.poly(outline, ink)


def bezier(start, control, end, steps=8):
    """Points along a quadratic curve from start to end, pulled toward control."""
    points = []
    for step in range(steps + 1):
        t = step / steps
        x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t ** 2 * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t ** 2 * end[1]
        points.append((x, y))
    return points


def dish(p):
    """A round-sided dish cut away to show its layers: sauce, noodles, cheese with a browned edge, and parsley."""
    rim = bezier((30, 140), (22, 230), (42, 292)) + bezier((42, 292), (180, 330), (318, 292)) \
        + bezier((318, 292), (338, 230), (330, 140))
    p.poly(rim, DISH_BLUE)
    p.poly([(42, 164), (318, 164), (306, 284), (54, 284)], NOODLE)
    p.rect(42, 150, 288, 14, PALE_CHEESE)
    p.poly([(42, 164), (318, 164), (318, 194), (42, 194)], CHEESE)
    p.rect(42, 164, 276, 6, ORANGE)
    for x in range(58, 310, 22):
        p.disc(x + (x // 22) % 2 * 9, 180, 4, ORANGE)
    p.poly([(54, 210), (306, 210), (300, 236), (60, 236)], NOODLE)
    p.poly([(54, 236), (306, 236), (300, 262), (60, 262)], SAUCE)
    for x in range(72, 300, 22):
        p.disc(x, 249, 4, TOMATO)
    p.poly([(54, 262), (306, 262), (304, 284), (56, 284)], PARSLEY)
    p.rect(30, 140, 300, 8, GREY)
    # Steam climbs from the dish, drawn as three lines beneath the title.
    for offset in (100, 170, 240):
        p.line([(offset, 136), (offset - 6, 128), (offset + 4, 120), (offset - 2, 112)], GREY, 3)


def timer(p):
    """A dial of twelve segments: the lit segments are the time gone, and the colour map changes them."""
    centre_x, centre_y = TIMER_CENTRE
    p.disc(centre_x, centre_y, TIMER_OUTER + 10, NAVY)
    segment_span = 360 / SEGMENTS
    for segment in range(SEGMENTS):
        first = TOP_ANGLE + segment * segment_span + SEGMENT_GAP_DEGREES / 2
        last = first + segment_span - SEGMENT_GAP_DEGREES
        ink = LIT if segment < LIT_SEGMENTS else UNLIT
        wedge(p, TIMER_CENTRE, TIMER_OUTER, TIMER_INNER, first, last, ink)
    # Tick marks at the outer edge of each segment give the dial its clock face.
    for segment in range(SEGMENTS):
        angle = radians(TOP_ANGLE + segment * segment_span)
        p.line([((centre_x + (TIMER_OUTER + 4) * cos(angle)), centre_y + (TIMER_OUTER + 4) * sin(angle)),
                ((centre_x + (TIMER_OUTER + 10) * cos(angle)), centre_y + (TIMER_OUTER + 10) * sin(angle))],
               NAVY, 2)
    p.disc(centre_x, centre_y, TIMER_INNER - 4, CREAM)
    p.text(centre_x - 24, centre_y + 12, '25', 24, 32, NAVY)
    p.text(centre_x - 36, centre_y + 100, 'MIN LEFT', 10, 15, NAVY)


def ingredients(p):
    p.text(30, 336, 'INGREDIENTS', 16, 24, TOMATO)
    items = ('12 OZ NOODLES', '2 CUPS CHEDDAR', '1 CAN TOMATOES', '1 CUP MILK')
    for index, item in enumerate(items):
        baseline = 368 + INGREDIENT_STEP * index
        p.text(30, baseline, f'{index + 1}', 12, 18, TOMATO)
        p.text(52, baseline, item, 12, 18, NAVY)
        # A tick box at the right of each ingredient, for the cook to tick.
        p.rect(290, baseline - 14, 14, 14, NAVY)
        p.rect(292, baseline - 12, 10, 10, CREAM)


def method(p):
    p.text(360, 316, 'METHOD', 16, 24, TOMATO)
    steps = ('BOIL NOODLES 8 MIN', 'DRAIN, STIR IN SAUCE', 'SPREAD IN DISH', 'TOP WITH CHEESE',
             'BAKE 25 MIN AT 375 F')
    for index, step in enumerate(steps):
        baseline = 352 + METHOD_STEP * index
        if index == CURRENT_STEP:
            # The current step sits on a band of the cheese colour.
            p.rect(356, baseline - 16, 262, 22, CHEESE)
        p.text(360, baseline, f'{index + 1}', 12, 18, TOMATO)
        p.text(382, baseline, step, 12, 18, NAVY)


def build():
    p = Plate(PALETTE)
    # The recipe card: cream ground under a tomato header.
    p.rect(0, 0, 640, 480, CREAM)
    p.rect(0, 0, 640, 70, TOMATO)
    p.title(24, 48, 'SUPPER TONIGHT', CREAM, 24, 34)
    p.text(462, 46, 'KITCHENFAX', 12, 18, CHEESE)
    p.text(30, 102, 'CHEDDAR NOODLE BAKE', 16, 24, NAVY)
    p.text(330, 102, 'SERVES 4 - COOK 25 MIN', 11, 16, TOMATO)
    p.wait(6, 'title')
    dish(p)
    p.wait(6, 'dish')
    timer(p)
    p.wait(4, 'timer')
    ingredients(p)
    method(p)
    p.rect(0, BAND_TOP, 640, 480 - BAND_TOP, NAVY)
    p.text(24, 474, 'PRESS 5 FOR THE SHOPPING LIST     0 FOR INDEX', 12, 18, CHEESE)
    return p


if __name__ == '__main__':
    save(__file__, build)
