"""The House That Orders Its Own Paper Towels: a cutaway pantry, a low-stock flag and a standing order."""
from math import cos, radians, sin
from _drawing import Plate, save

META = dict(
    title='The House That Orders Its Own Paper Towels',
    purpose='A cutaway house whose pantry shelves report low stock and place a standing order',
    style='Cutaway house in flat colour, a pantry with stocked shelves and a paper order form',
    techniques=['16-entry colour map', 'filled polygons and rectangles', 'proportional text',
                'BLINK from red to green for the low-stock flag', 'WAIT between rooms and the van'],
    animated=True,
)

PALETTE = (
    '1b263b fcf8ec e63946 2a9d8f 06d6a0 ffb703 8ecae6 023047 '
    'c77d4a e9d8a6 606c38 fb8500 5c677d adb5bd 264653 ffffff'
)
NIGHT, CREAM, ALERT, TEAL, GO, YELLOW, SKY, DEEP_NAVY = range(8)
WOOD, WALL, OLIVE, ORANGE, SLATE_BLUE, STEEL, INK, WHITE = range(8, 16)

HOUSE_LEFT = 80
HOUSE_RIGHT = 560
HOUSE_TOP = 150
HOUSE_FLOOR = 420
VAN_LEFT = 12
SHELVES = (232, 302, 372)


def roll(p, x, y):
    """A roll of paper towels, drawn as a disc with its core showing."""
    p.disc(x, y, 18, STEEL)
    p.disc(x, y, 7, CREAM)


def pantry(p):
    """The pantry is the cutaway room on the left, with three shelves of stock."""
    p.rect(100, 176, 210, 244, WALL)
    for shelf in SHELVES:
        p.rect(100, shelf, 210, 6, WOOD)
    # Shelf one holds tins, shelf two the paper towels, shelf three cereal boxes.
    for x in range(116, 296, 30):
        p.rect(x, 196, 20, 36, ORANGE)
        p.rect(x, 196, 20, 6, STEEL)
    for x in (126, 170, 214, 258):
        roll(p, x, SHELVES[1] - 18)
    for x in range(118, 290, 44):
        p.rect(x, 318, 28, 54, YELLOW)
        p.rect(x + 4, 326, 20, 10, TEAL)
    p.wait(6, 'pantry')


def shelf_counts(p):
    """A white count tag at the left of each shelf, giving the number of items on it."""
    for shelf, count in ((SHELVES[0], 'x6'), (SHELVES[1], 'x4'), (SHELVES[2], 'x12')):
        p.rect(280, shelf - 26, 28, 18, WHITE)
        p.text(284, shelf - 12, count, 9, 12, INK)


def low_stock_flag(p):
    """A flag on the paper towel shelf, red for low stock, which blinks to green once it is delivered."""
    p.rect(278, 246, 34, 20, ALERT)
    p.text(283, 260, 'LOW', 9, 13, WHITE)
    p.blink(ALERT, GO, on=5, off=6)


def house(p):
    """The house in section: a pitched roof, its walls, the living room and the kitchen counter."""
    p.rect(470, 96, 22, 50, WOOD)
    p.poly([(54, 156), (320, 66), (586, 156), (568, 156), (320, 84), (72, 156)], SLATE_BLUE)
    p.rect(50, 150, 540, 10, WOOD)
    p.rect(HOUSE_LEFT, HOUSE_TOP, HOUSE_RIGHT - HOUSE_LEFT, HOUSE_FLOOR - HOUSE_TOP, WALL)
    # The walls are cut away: the cut edges are shadowed and a beam crosses the ceiling.
    p.rect(HOUSE_LEFT, HOUSE_TOP, 14, HOUSE_FLOOR - HOUSE_TOP, WOOD)
    p.rect(HOUSE_RIGHT - 14, HOUSE_TOP, 14, HOUSE_FLOOR - HOUSE_TOP, WOOD)
    p.rect(HOUSE_LEFT + 14, HOUSE_TOP, 8, HOUSE_FLOOR - HOUSE_TOP, SLATE_BLUE)
    p.rect(HOUSE_RIGHT - 22, HOUSE_TOP, 8, HOUSE_FLOOR - HOUSE_TOP, SLATE_BLUE)
    p.rect(HOUSE_LEFT + 22, HOUSE_TOP + 4, HOUSE_RIGHT - HOUSE_LEFT - 44, 10, WOOD)
    p.rect(330, 176, 4, 244, WOOD)
    # Kitchen counter with the terminal and its screen.
    # A window with a blind sits in the back wall above the counter.
    p.rect(360, 186, 120, 46, SKY)
    p.rect(360, 186, 120, 8, WOOD)
    p.line([(420, 194), (420, 232)], WOOD, 2)
    p.rect(344, 318, 200, 14, WOOD)
    p.rect(352, 332, 10, 88, WOOD)
    p.rect(514, 332, 10, 88, WOOD)
    p.rect(378, 244, 128, 74, DEEP_NAVY)
    p.rect(386, 252, 112, 58, SKY)
    p.text(394, 272, 'STOCK', 13, 18, DEEP_NAVY)
    p.text(394, 294, '1 LOW', 13, 18, ALERT)
    p.line([(312, 196), (378, 262)], INK, 3)
    # Three arcs beside the terminal show it sending the order.
    for radius in (12, 20, 28):
        p.line([(500 + radius * cos(radians(angle)), 262 + radius * sin(radians(angle))) for angle in range(-45, 46, 15)],
               INK, 2)
    p.wait(6, 'house')


def order_form(p):
    """The standing order, on paper, under the terminal."""
    p.rect(344, 340, 260, 72, CREAM)
    p.rect(344, 340, 260, 22, TEAL)
    p.text(354, 356, 'STANDING ORDER', 10, 14, CREAM)
    p.text(354, 380, '2 ROLLS PAPER TOWELS', 10, 14, INK)
    p.text(354, 402, 'DELIVER THU 8 AM', 10, 14, INK)
    p.wait(4, 'order')
    # The order is confirmed with a green tick, drawn last.
    p.line([(556, 396), (564, 404), (580, 386)], GO, 4)
    p.wait(4, 'confirmed')


def sun(p):
    """A sun with eight rays in the upper right of the sky."""
    p.disc(606, 92, 16, YELLOW)
    for step in range(8):
        angle = radians(45 * step)
        p.line([(606 + 22 * cos(angle), 92 + 22 * sin(angle)), (606 + 32 * cos(angle), 92 + 32 * sin(angle))],
               YELLOW, 3)


def delivery_van(p):
    """A delivery van on the lawn, which arrives last: its body, its window and its wheels."""
    left = VAN_LEFT
    p.rect(left, 384, 70, 36, TEAL)
    p.rect(left + 54, 392, 16, 28, TEAL)
    p.rect(left + 58, 396, 10, 10, SKY)
    p.text(left + 6, 404, 'SHELF', 9, 13, CREAM)
    p.disc(left + 16, 422, 7, INK)
    p.disc(left + 60, 422, 7, INK)
    p.wait(6, 'van')


def build():
    p = Plate(PALETTE)
    # The sky and the lawn, with a title band across the top.
    p.rect(0, 0, 640, 480, SKY)
    p.rect(0, 0, 640, 52, DEEP_NAVY)
    p.title(24, 38, 'SHELFWISE HOME', YELLOW, 20, 28)
    p.text(402, 38, 'ORDERS', 12, 18, CREAM)
    sun(p)
    house(p)
    pantry(p)
    low_stock_flag(p)
    shelf_counts(p)
    order_form(p)
    p.rect(0, 420, 640, 20, OLIVE)
    delivery_van(p)
    p.rect(0, 440, 640, 40, DEEP_NAVY)
    p.text(24, 466, 'NEXT DELIVERY THU 8 AM   PRESS 2 TO CANCEL', 11, 16, YELLOW)
    return p


if __name__ == '__main__':
    save(__file__, build)
