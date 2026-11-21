"""Neighbourhood Calendar, Maple Ridge Estates: a month of events, drawn a week at a time."""
from math import cos, radians, sin
from _drawing import Plate, save

META = dict(
    title='Neighbourhood Calendar, Maple Ridge Estates',
    purpose='A month grid of a residential estate: bake sale, league games, the block party and a garage sale',
    style='Flat month grid on navy, with coloured event blocks, a legend and a blinking today marker',
    techniques=['16-entry colour map', 'filled rectangles', 'proportional text',
                'BLINK on the day marker', 'WAIT between weeks'],
    animated=True,
)

PALETTE = (
    '1d3557 fefae0 e63946 f4a261 2a9d8f 457b9d e9c46a 264653 '
    'a8dadc f1faee 9b5de5 6c757d ffb4a2 2b2d42 06d6a0 000814'
)
NAVY, PAPER, RED, ORANGE, TEAL, STEEL, MUSTARD, SLATE = range(8)
PALE_TEAL, WHITE, VIOLET, GREY, CORAL, DARK, MINT, BLACK = range(8, 16)

GRID_LEFT = 24
GRID_WIDTH = 592
COLUMNS = 7
ROW_TOP = 98
ROW_HEIGHT = 50
ROWS = 5
CELL_GAP = 4
DAY_TODAY = 14
# Each event is (day, colour, short label on its block); the legend names them in full.
EVENTS = (
    (6, TEAL, 'BAKE'),
    (9, RED, 'LG GAME'),
    (11, RED, 'LG GAME'),
    (16, RED, 'LG GAME'),
    (21, VIOLET, 'PARTY'),
    (27, ORANGE, 'GARAGE'),
)
LEGEND = (
    (TEAL, 'BAKE SALE'),
    (RED, 'LEAGUE GAME'),
    (VIOLET, 'BLOCK PARTY'),
    (ORANGE, 'GARAGE SALE'),
    (GREY, 'BIN DAY'),
)
LEGEND_SPACING = 122
WEEKDAYS = ('SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT')
WEEKEND_COLUMNS = (0, COLUMNS - 1)
THURSDAY_COLUMN = 4
# The coming-up panel lists dated events in full words, below the grid.
COMING_UP = (
    '6  BAKE SALE AT THE HALL, 10 AM',
    '16 LEAGUE GAME, HOME, 6 PM',
    '27 GARAGE SALE, 9 AM TO NOON',
)


def cell(day):
    """The top-left corner and the size of the cell for a day of the month, numbered from 1."""
    column_width = GRID_WIDTH / COLUMNS
    row, column = divmod(day - 1, COLUMNS)
    return GRID_LEFT + column * column_width, ROW_TOP + row * ROW_HEIGHT, column_width, ROW_HEIGHT


def build():
    p = Plate(PALETTE)
    p.rect(0, 0, 640, 480, NAVY)
    p.rect(0, 0, 640, 64, TEAL)
    p.title(24, 46, 'MAPLE RIDGE ESTATES', WHITE, 20, 30)
    p.text(502, 46, 'JUNE', 16, 24, MUSTARD)
    for column, name in enumerate(WEEKDAYS):
        x = GRID_LEFT + column * GRID_WIDTH / COLUMNS + 8
        p.text(x, 88, name, 11, 16, PALE_TEAL)
    p.wait(4, 'header')

    days = 30
    for day in range(1, days + 1):
        x, y, width, height = cell(day)
        column = (day - 1) % COLUMNS
        ground = PALE_TEAL if column in WEEKEND_COLUMNS else PAPER
        p.rect(x + 2, y + 2, width - CELL_GAP, height - CELL_GAP, ground)
        p.text(x + 8, y + 17, str(day), 10, 14, SLATE)
        if column == THURSDAY_COLUMN:
            bin_x, bin_y = x + 60, y + 28
            p.rect(bin_x, bin_y, 14, 16, GREY)
            p.rect(bin_x - 2, bin_y - 3, 18, 4, GREY)
        if day == DAY_TODAY:
            p.rect(x + 2, y + 2, width - CELL_GAP, height - CELL_GAP, CORAL)
            p.rect(x + 6, y + 6, width - 12, height - 12, ground)
            p.text(x + 8, y + 17, str(day), 10, 14, SLATE)
            p.text(x + 34, y + 17, 'TODAY', 9, 12, RED)
            p.blink(CORAL, RED, on=5, off=8)
        if day % COLUMNS == 0 or day == days:
            p.wait(2, f'week to day {day}')

    for day, colour, label in EVENTS:
        x, y, width, height = cell(day)
        p.rect(x + 6, y + 24, width - 16, 18, colour)
        p.text(x + 10, y + 38, label, 9, 13, WHITE)
    # Weather marks: a sun on the 3rd, a cloud on the 8th and rain on the 16th.
    x, y, _, _ = cell(3)
    p.disc(x + 66, y + 16, 7, ORANGE)
    for step in range(8):
        angle = radians(45 * step)
        p.line([(x + 66 + 10 * cos(angle), y + 16 + 10 * sin(angle)),
                (x + 66 + 14 * cos(angle), y + 16 + 14 * sin(angle))], ORANGE, 2)
    x, y, _, _ = cell(8)
    p.disc(x + 60, y + 18, 6, GREY)
    p.disc(x + 68, y + 14, 8, GREY)
    p.disc(x + 76, y + 18, 6, GREY)
    p.rect(x + 54, y + 18, 28, 8, GREY)
    x, y, _, _ = cell(16)
    for offset in (54, 60, 66, 72):
        p.line([(x + offset, y + 6), (x + offset - 4, y + 16)], STEEL, 2)
    # Balloons tie the block party to its day, and a small board marks the garage sale.
    x, y, _, _ = cell(21)
    for offset, colour in ((48, VIOLET), (60, TEAL), (72, ORANGE)):
        p.disc(x + offset, y + 10, 5, colour)
    x, y, _, _ = cell(27)
    p.rect(x + 56, y + 4, 20, 10, ORANGE)
    p.rect(x + 60, y + 14, 2, 6, GREY)
    p.rect(x + 70, y + 14, 2, 6, GREY)

    p.rect(24, 358, 592, 80, PALE_TEAL)
    p.text(36, 378, 'COMING UP', 11, 15, DARK)
    for index, line in enumerate(COMING_UP):
        p.text(36, 398 + 18 * index, line, 10, 14, DARK)
    p.wait(4, 'coming up')

    # The legend names each event in full, on a navy band.
    p.rect(0, 440, 640, 40, DARK)
    for index, (colour, name) in enumerate(LEGEND):
        left = 20 + index * LEGEND_SPACING
        p.rect(left, 452, 16, 16, colour)
        p.text(left + 24, 466, name, 9, 13, PALE_TEAL)
    return p


if __name__ == '__main__':
    save(__file__, build)
