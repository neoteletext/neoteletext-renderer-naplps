"""A Card for Grandma: an electronic greeting card that opens its tulips as it draws."""
from math import cos, pi, radians, sin
from _drawing import Plate, save

META = dict(
    title='A Card for Grandma',
    purpose='An electronic greeting card for a seventieth birthday, billed to the sender account',
    style='Cream card on plum, rounded tulips opening in turn and a greeting set along an arc',
    techniques=['16-entry colour map', 'filled polygons with curved cups', 'discs for the frame and rosettes',
                'characters placed along an arc', 'proportional text', 'WAIT between opening steps'],
    animated=True,
)

PALETTE = (
    '2a1f3d fff4e0 ffb3c1 ff7aa2 e0457b ffd23f 2ec4b6 1a7f74 '
    'a7e8a1 3c9d4e 7b5ea7 402c5c f9a03f 6a4c93 ffe6ee 4a3560'
)
PLUM, CREAM, BLUSH, ROSE, RASPBERRY, GOLD, TEAL, DEEP_TEAL = range(8)
LEAF_PALE, LEAF, VIOLET, DEEP_VIOLET, ORANGE, LILAC, PINK_PALE, PLUM_LIGHT = range(8, 16)
# The stroke font's pen is drawn at this width, in design units, for the greeting and the name.
HEAVY_PEN = 3

GREETING = 'HAPPY 70TH,'
ARC_CENTRE = (320, 340)
ARC_RADIUS = 200
ARC_SPAN_DEGREES = 124
GREETING_WIDTH = 28
GREETING_HEIGHT = 40
CUP_HALF_WIDTH = 24
CUP_CURVE_STEPS = 12
FRAME_INSET = 18
ROSETTE_SPACING = 26
PRICE_CHARACTER = (13, 18)


def greeting_points(count):
    """Baselines of count characters spaced evenly along the arc, so the spacing is by length, not angle."""
    step_degrees = ARC_SPAN_DEGREES / (count - 1)
    points = []
    for index in range(count):
        angle = radians(90 + ARC_SPAN_DEGREES / 2 - step_degrees * index)
        x = ARC_CENTRE[0] + ARC_RADIUS * cos(angle) - GREETING_WIDTH / 2
        y = ARC_CENTRE[1] - ARC_RADIUS * sin(angle)
        points.append((x, y))
    return points


def tulip(p, centre_x, top, base, ink):
    """A bud opens into a rounded cup with three tips, a pale facet, and a stem with two crossed leaves."""
    p.poly([(centre_x - 10, top + 26), (centre_x, top + 8), (centre_x + 10, top + 26),
            (centre_x + 8, top + 40), (centre_x - 8, top + 40)], ink)
    p.wait(4, 'bud')
    cup = [(centre_x - CUP_HALF_WIDTH, top), (centre_x - 12, top + 10), (centre_x - 6, top + 2),
           (centre_x, top + 12), (centre_x + 6, top + 2), (centre_x + 12, top + 10),
           (centre_x + CUP_HALF_WIDTH, top)]
    for step in range(CUP_CURVE_STEPS + 1):
        angle = pi * step / CUP_CURVE_STEPS
        cup.append((centre_x + CUP_HALF_WIDTH * cos(angle), top + 16 + 24 * sin(angle)))
    p.poly(cup, ink)
    p.poly([(centre_x - 12, top + 14), (centre_x - 6, top + 18), (centre_x - 8, top + 36), (centre_x - 14, top + 30)],
           PINK_PALE)
    p.line([(centre_x, top + 40), (centre_x, base)], LEAF, 4)
    p.poly([(centre_x, base - 60), (centre_x + 32, base - 42), (centre_x, base - 26)], LEAF)
    p.poly([(centre_x, base - 76), (centre_x - 30, base - 58), (centre_x, base - 42)], LEAF_PALE)


def leaf(p, base, tip, width, ink):
    """A slim leaf: a lens from base to tip, with its widest point at the middle."""
    (bx, by), (tx, ty) = base, tip
    mid_x, mid_y = (bx + tx) / 2, (by + ty) / 2
    length = ((tx - bx) ** 2 + (ty - by) ** 2) ** 0.5
    off_x, off_y = -(ty - by) / length * width, (tx - bx) / length * width
    p.poly([(bx, by), (mid_x + off_x, mid_y + off_y), (tx, ty), (mid_x - off_x, mid_y - off_y)], ink)


def bow(p, centre_x, centre_y):
    """A ribbon bow where the stems meet, two loops and a knot."""
    p.poly([(centre_x, centre_y), (centre_x - 30, centre_y - 16), (centre_x - 28, centre_y + 14)], TEAL)
    p.poly([(centre_x, centre_y), (centre_x + 30, centre_y - 16), (centre_x + 28, centre_y + 14)], TEAL)
    p.disc(centre_x, centre_y, 6, DEEP_TEAL)


def rosettes(p):
    """A row of small rosettes round the inside of the frame, drawn as discs."""
    left, top = 40 + FRAME_INSET, 30 + FRAME_INSET
    right, bottom = 600 - FRAME_INSET, 400 - FRAME_INSET
    x, count = left, 0
    while x <= right:
        p.disc(x, top, 4, GOLD if count % 2 else RASPBERRY)
        x += ROSETTE_SPACING
        count += 1
    y, count = top, 0
    while y <= bottom:
        p.disc(left, y, 4, GOLD if count % 2 else RASPBERRY)
        p.disc(right, y, 4, GOLD if count % 2 else RASPBERRY)
        y += ROSETTE_SPACING
        count += 1


def build():
    p = Plate(PALETTE)
    # The card is cream on plum, with a raspberry frame and rosettes inside it.
    p.rect(40, 30, 560, 420, CREAM)
    p.rect(40, 30, 560, 6, RASPBERRY)
    p.rect(40, 444, 560, 6, RASPBERRY)
    p.rect(40, 30, 6, 420, RASPBERRY)
    p.rect(594, 30, 6, 420, RASPBERRY)
    rosettes(p)
    # A printed dot pattern of blush discs covers the cream, as a card's paper would.
    for row in range(60, 400, 28):
        for column in range(64, 580, 28):
            p.disc(column + (row // 28 % 2) * 14, row, 2, BLUSH)

    # The greeting is set along the arc, one character at a time, with a heavy pen so its strokes stand out.
    p.pel(HEAVY_PEN)
    for index, ((x, y), letter) in enumerate(zip(greeting_points(len(GREETING)), GREETING)):
        p.text(x, y, letter, GREETING_WIDTH, GREETING_HEIGHT, ROSE if index % 2 else RASPBERRY)
    p.wait(6, 'greeting')

    # Slim leaves stand behind the outer tulips, so the bouquet sits on foliage.
    for centre_x, sign in ((214, -1), (426, 1)):
        leaf(p, (centre_x, 350), (centre_x + sign * 40, 318), 7, LEAF_PALE)
        leaf(p, (centre_x, 350), (centre_x + sign * 24, 304), 5, LEAF)
    # The bouquet opens tulip by tulip, the centre bloom last.
    tulip(p, 214, 262, 352, ROSE)
    tulip(p, 426, 262, 352, GOLD)
    tulip(p, 320, 240, 352, RASPBERRY)
    bow(p, 320, 352)
    p.wait(6, 'bouquet')

    # Sparkles are four-armed crosses, set beside the bouquet and the greeting.
    for x, y, size in ((150, 300, 14), (494, 300, 16), (104, 170, 12), (540, 150, 12)):
        p.line([(x - size, y), (x + size, y)], GOLD, 3)
        p.line([(x, y - size), (x, y + size)], GOLD, 3)
    # A small heart sits above the bouquet: two discs and a point.
    p.disc(311, 200, 9, RASPBERRY)
    p.disc(329, 200, 9, RASPBERRY)
    p.poly([(302, 204), (338, 204), (320, 226)], RASPBERRY)

    # The name, in the same heavy pen, sits under the bouquet.
    p.text(206, 402, 'NANA RUTH', 26, 36, DEEP_VIOLET)
    p.pel(1)

    # The price line is a band at the foot of the card.
    p.rect(60, 412, 520, 26, PLUM)
    p.text(74, 432, '$2.00 CHARGED TO YOUR ACCOUNT', *PRICE_CHARACTER, CREAM)
    p.wait(4, 'price')
    return p


if __name__ == '__main__':
    save(__file__, build)
