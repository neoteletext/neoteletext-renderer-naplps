"""The Family Message Board: a corkboard of pinned notes, each one drawn in turn."""
from math import cos, radians, sin
from _drawing import Plate, save

META = dict(
    title='The Family Message Board',
    purpose='A household corkboard of messages between parents and children, the newest pin blinking',
    style='Warm cork ground with a dot pattern, tilted sticky notes with pins and drop shadows',
    techniques=['16-entry colour map', 'filled discs as a dot pattern', 'rotated filled polygons',
                'proportional text', 'BLINK on a new pin', 'WAIT between notes'],
    animated=True,
)

PALETTE = (
    '3b2414 f2e3c6 c9975a 6b4423 ffe066 8ee3ef ff8fab b7f5a0 '
    '1d3557 d62828 2a9d8f e76f51 264653 9d6b3f fbf7ee 5a3a1e'
)
DARK_CORK, PAPER, CORK, DEEP_CORK, YELLOW, BLUE, PINK, GREEN = range(8)
INK, PIN, TEAL, ORANGE, SLATE, CORK_MID, WHITE, SHADOW = range(8, 16)

DOT_SPACING = 24
DOT_RADIUS = 2
HEADER_HEIGHT = 58
LINE_STEP = 24
TEXT_SMALL = (12, 18)
TEXT_HEAD = (16, 24)
NOTE_PADDING = 18
SHADOW_OFFSET = 6
PIN_RADIUS = 6
# The first line of text sits below the pin's head and its shadow, so no pin touches a word.
TEXT_TOP = 44


def note(p, cx, cy, width, height, angle, paper, lines, pin_ink=PIN, blink_to=None):
    """A sticky note tilted by angle degrees, with a drop shadow, a pin and its text lines."""
    cosine, sine = cos(radians(angle)), sin(radians(angle))

    def turn(dx, dy):
        return (cx + dx * cosine - dy * sine, cy + dx * sine + dy * cosine)

    corners = [(-width / 2, -height / 2), (width / 2, -height / 2),
               (width / 2, height / 2), (-width / 2, height / 2)]
    p.poly([(x + SHADOW_OFFSET, y + SHADOW_OFFSET) for x, y in map(turn, *zip(*corners))], SHADOW)
    p.poly([turn(x, y) for x, y in corners], paper)
    pin_x, pin_y = turn(0, -height / 2 + 10)
    p.disc(pin_x, pin_y, PIN_RADIUS, pin_ink)
    p.disc(pin_x - 2, pin_y - 2, 2, WHITE)
    if blink_to is not None:
        p.blink(pin_ink, blink_to, on=6, off=9)
    for index, (text, size, ink) in enumerate(lines):
        start_x, start_y = turn(-width / 2 + NOTE_PADDING, -height / 2 + TEXT_TOP + LINE_STEP * index)
        p.text(start_x, start_y, text, size[0], size[1], ink)


def build():
    p = Plate(PALETTE)
    # The cork ground carries a dot pattern in a darker cork.
    p.rect(0, 0, 640, 480, CORK)
    for row in range(HEADER_HEIGHT + 12, 480, DOT_SPACING):
        for column in range(12, 640, DOT_SPACING):
            p.disc(column + (DOT_SPACING // 2) * (row // DOT_SPACING % 2), row, DOT_RADIUS, CORK_MID)

    # The board's header is a paper strip.
    p.rect(0, 0, 640, HEADER_HEIGHT, INK)
    p.text(24, 40, 'THE FAMILY BOARD', 22, 32, YELLOW)
    p.text(430, 40, 'MESSAGES 4', 13, 20, WHITE)
    p.wait(6, 'board')
    # A red heart is pinned to the cork beside the JEN note, and a strip of masking tape holds DAD's corner.
    p.disc(576, 100, 9, PIN)
    p.disc(590, 100, 9, PIN)
    p.poly([(569, 104), (597, 104), (583, 124)], PIN)

    note(p, 150, 170, 200, 150, -2.5, YELLOW,
         [('DAD', TEXT_HEAD, INK), ('PICK UP KEVIN', TEXT_SMALL, INK), ('AT 4 O CLOCK', TEXT_SMALL, INK)])
    p.poly([(196, 100), (252, 92), (254, 108), (198, 116)], WHITE)
    # A polaroid photograph is pinned under DAD: a sky and a hill in its frame.
    p.poly([(16, 262), (84, 262), (84, 338), (16, 338)], WHITE)
    p.rect(22, 268, 56, 46, BLUE)
    p.disc(62, 282, 6, YELLOW)
    p.poly([(22, 314), (46, 292), (66, 306), (78, 298), (78, 314)], TEAL)
    p.disc(50, 262, 5, PIN)
    p.wait(4, 'dad')
    note(p, 370, 150, 200, 170, 2, BLUE,
         [('MUM', TEXT_HEAD, INK), ('CASSEROLE IN', TEXT_SMALL, INK), ('THE OVEN, 350 F', TEXT_SMALL, INK),
          ('BACK BY 6', TEXT_SMALL, INK)], pin_ink=TEAL)
    p.wait(4, 'mum')
    note(p, 540, 230, 170, 170, 3.5, PINK,
         [('JEN', TEXT_HEAD, INK), ('I LOVE YOU!', TEXT_SMALL, INK), ('- DOUG?', TEXT_SMALL, INK)],
         pin_ink=ORANGE, blink_to=PIN)
    p.wait(4, 'jen')
    note(p, 205, 340, 230, 170, -1.5, GREEN,
         [('KEVIN', TEXT_HEAD, INK), ('NEED A RIDE TO', TEXT_SMALL, INK), ('THE GAME, SAT', TEXT_SMALL, INK),
          ('10 AM', TEXT_SMALL, INK)])
    p.wait(4, 'kevin')
    note(p, 470, 390, 240, 110, 1.5, WHITE,
         [('DOUG: YES, I CAN', TEXT_SMALL, INK), ('DRIVE. BRING', TEXT_SMALL, INK), ('THE CAMERA', TEXT_SMALL, INK)], pin_ink=INK)
    p.wait(4, 'doug')
    return p


if __name__ == '__main__':
    save(__file__, build)
