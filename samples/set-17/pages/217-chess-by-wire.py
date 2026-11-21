"""Chess by Wire: a correspondence game against another subscriber, played move by move over the line."""
import math

from _screen import CANVAS_WIDTH, Plate, Y_SCALE, fragment, oval, save, xy

META = dict(
    title='Chess by Wire',
    purpose='A subscriber plays chess against another household across the province, one move a night',
    style='Felt-green and parchment board with programmable-character pieces beside a navy score panel',
    techniques=['DRCS chess pieces with outline passes', 'a DRCS knight as the service mark', 'an envelope macro played twice', 'day pips', 'rectangle rows for the board',
                'BLINK on the last move', 'the move shown arriving by WAIT', 'captured pieces as small DRCS', 'BLINK cursor', 'proportional text'],
    animated=True,
)

PALETTE = ('0b1230 fff2d0 1c1612 ecd9a8 4c8a58 7a4a22 1f3f94 ffd23f '
           'ff6a3d 5fd6ff ffffff 26305e e63946 2a8a4a 9aa6cc 151c44')
(NIGHT, IVORY, EBONY, LIGHT_SQUARE, DARK_SQUARE, WOOD, BAND, YELLOW,
 LAST_MOVE, CYAN, WHITE, PANEL, RED, GREEN, GREY, CURSOR) = range(16)

SQUARE = 38
BOARD_X, BOARD_Y = 40, 86
FILES = 'abcdefgh'
BASE = [(18, 80), (82, 80), (82, 94), (18, 94)]

PIECES = {
    'p': [BASE, [(34, 80), (40, 50), (60, 50), (66, 80)], oval(50, 36, 15, 15)],
    'r': [BASE, [(30, 80), (32, 40), (68, 40), (70, 80)],
          [(24, 44), (24, 10), (35, 10), (35, 22), (45, 22), (45, 10), (55, 10), (55, 22),
           (65, 22), (65, 10), (76, 10), (76, 44)]],
    'n': [BASE, [(26, 82), (74, 82), (74, 60), (70, 36), (60, 16), (48, 6), (44, 14), (34, 18),
                 (16, 44), (18, 56), (30, 58), (44, 46), (44, 58), (30, 82)],
          ('clear', oval(44, 28, 5, 5, 8))],
    'b': [BASE, [(32, 80), (40, 56), (60, 56), (68, 80)], oval(50, 38, 16, 22), oval(50, 12, 7, 7, 12),
          ('clear', [(52, 24), (60, 30), (48, 44), (44, 40)])],
    'q': [BASE, [(28, 80), (34, 46), (66, 46), (72, 80)],
          [(26, 50), (14, 14), (34, 32), (40, 6), (50, 28), (60, 6), (66, 32), (86, 14), (74, 50)]],
    'k': [BASE, [(28, 80), (32, 44), (68, 44), (72, 80)], [(26, 46), (26, 28), (74, 28), (74, 46)],
          [(45, 4), (55, 4), (55, 26), (45, 26)], [(36, 10), (64, 10), (64, 18), (36, 18)]],
}
CODES = {'k': 'K', 'q': 'Q', 'r': 'R', 'b': 'B', 'n': 'N', 'p': 'P'}

WHITE_MEN = 'Kg1 Qe2 Rf1 Ra1 Bd3 Nf3 Pa2 Pb2 Pc3 Pd4 Pf2 Pg2 Ph2'
BLACK_MEN = 'Kg8 Qd7 Rf8 Ra8 Bb7 Nc6 Pa7 Pb6 Pc7 Pe6 Pf7 Pg7 Ph7'
LAST_FROM, LAST_TO = 'd3', 'c4'
# What each side has taken, shown beside the player who took it.
TAKEN_BY_WHITE, TAKEN_BY_BLACK = 'bnp', 'bnp'


def square(name):
    """Top-left corner of a square, white's side at the foot of the board."""
    return BOARD_X + FILES.index(name[0]) * SQUARE, BOARD_Y + (8 - int(name[1])) * SQUARE


def piece(p, kind, x, y, size, ink, outline):
    """Four offset passes in the outline colour, then the piece: a hard edge on either square colour."""
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        p.programmable(x + dx, y + dy, CODES[kind], size, size, outline)
    p.programmable(x, y, CODES[kind], size, size, ink)


def place(p, men, ink, outline):
    for man in men.split():
        x, y = square(man[1:])
        piece(p, man[0].lower(), x + 2, y + SQUARE - 3, 34, ink, outline)


def envelope():
    """Macro body: an envelope whose lower left corner is the drawing point, drawn with relative commands."""
    body = fragment()
    width, height = 28, 18
    body.color(YELLOW).cmd(0x31, xy(width / CANVAS_WIDTH, height / Y_SCALE))
    # RECT leaves the point at the lower right; step up to the top right and draw the flap.
    body.cmd(0x25, xy(0, height / Y_SCALE))
    body.color(EBONY).cmd(0x29, xy(-width / 2 / CANVAS_WIDTH, -10 / Y_SCALE) + xy(-width / 2 / CANVAS_WIDTH, 10 / Y_SCALE))
    return body


def build():
    p = Plate(PALETTE, NIGHT)
    for kind, contours in PIECES.items():
        p.glyph(CODES[kind], *contours)
    p.define_macro('E', envelope())

    # Title band: the games service and its page number.
    p.rect(0, 0, 640, 54, BAND)
    p.rect(0, 54, 640, 4, YELLOW)
    p.rect(0, 58, 640, 3, DARK_SQUARE)
    # The service's mark: the board's own knight, large, in the band.
    piece(p, 'n', 14, 50, 44, IVORY, EBONY)
    p.text(66, 40, 'WIREPLAY', 20, 30, YELLOW, prop=False)
    p.text(244, 38, 'CHESS BY WIRE', 14, 22, WHITE, prop=False)
    p.text(560, 38, '217', 16, 24, CYAN, prop=False)

    # The board draws rank by rank, as it would arrive down the line.
    p.rect(BOARD_X - 10, BOARD_Y - 10, 8 * SQUARE + 20, 8 * SQUARE + 20, WOOD)
    p.rect(BOARD_X - 6, BOARD_Y - 6, 8 * SQUARE + 12, 8 * SQUARE + 12, YELLOW, fill=False)
    for rank in range(8):
        y = BOARD_Y + rank * SQUARE
        for file in range(8):
            ink = LIGHT_SQUARE if (rank + file) % 2 == 0 else DARK_SQUARE
            p.rect(BOARD_X + file * SQUARE, y, SQUARE, SQUARE, ink)
    for index, letter in enumerate(FILES):
        p.text(BOARD_X + index * SQUARE + 12, BOARD_Y + 8 * SQUARE + 32, letter.upper(), 14, 18, GREY, prop=False)
    for rank in range(8):
        p.text(14, BOARD_Y + rank * SQUARE + 28, str(8 - rank), 14, 18, GREY, prop=False)
    p.wait(8, 'board')

    place(p, WHITE_MEN, IVORY, EBONY)
    place(p, BLACK_MEN, EBONY, IVORY)
    p.wait(8, 'pieces')

    # The score panel: the two households, the last moves, and whose turn it is.
    p.rect(372, 76, 252, 324, PANEL)
    p.text(388, 106, 'GAME 0417', 14, 20, CYAN, prop=False)
    p.text(388, 140, 'WHITE: PLAYER 1', 12, 18, IVORY, prop=False)
    p.text(404, 162, 'PINE HOLLOW', 12, 18, GREY, prop=False)
    p.text(388, 192, 'BLACK: PLAYER 2', 12, 18, IVORY, prop=False)
    p.text(404, 214, 'ASHFORD BAY', 12, 18, GREY, prop=False)
    # The two households and the telephone line that carries the moves between them.
    for hx in (392, 572):
        p.rect(hx, 244, 34, 22, IVORY)
        p.poly([(hx - 5, 245), (hx + 17, 228), (hx + 39, 245)], RED)
        p.rect(hx + 12, 250, 10, 9, YELLOW)
    p.line([(420, 236), (436, 224)], WOOD, 3)
    p.line([(576, 236), (560, 224)], WOOD, 3)
    p.arc((436, 224), (498, 236), (560, 224), GREY)
    # The move in transit: an envelope on the line.
    p.pel(1).play('E', 484, 244)
    for index, kind in enumerate(TAKEN_BY_WHITE):
        piece(p, kind, 548 + index * 22, 166, 20, EBONY, IVORY)
    for index, kind in enumerate(TAKEN_BY_BLACK):
        piece(p, kind, 548 + index * 22, 218, 20, IVORY, EBONY)
    p.wait(10, 'the move arrives')

    # The opponent's move lands: its squares light, the bishop is lifted from d3 to c4, an arrow shows the way.
    for name in (LAST_FROM, LAST_TO):
        x, y = square(name)
        p.rect(x, y, SQUARE, SQUARE, LAST_MOVE)
    tx, ty = square(LAST_TO)
    piece(p, 'b', tx + 2, ty + SQUARE - 3, 34, IVORY, EBONY)
    fx, fy = square(LAST_FROM)
    start, end = (fx + SQUARE / 2, fy + SQUARE / 2), (tx + SQUARE / 2 + 4, ty + SQUARE / 2 + 4)
    # The head points along the move: a triangle on the line's direction, its base across it.
    length = math.dist(start, end)
    ux, uy = (end[0] - start[0]) / length, (end[1] - start[1]) / length
    base = (end[0] - ux * 16, end[1] - uy * 16)
    p.line([start, base], RED, 6)
    p.poly([end, (base[0] - uy * 9, base[1] + ux * 9), (base[0] + uy * 9, base[1] - ux * 9)], RED)
    p.disc(*start, 7, RED)
    p.text(388, 290, '21. Nf3   Qd7', 13, 20, WHITE)
    p.text(388, 316, '22. Bc4   ...', 13, 20, YELLOW)
    p.rect(380, 334, 236, 54, RED)
    p.text(392, 358, 'YOUR MOVE,', 14, 20, WHITE, prop=False)
    p.text(392, 380, 'PLAYER 2', 14, 20, YELLOW, prop=False)

    # The prompt band with a blinking cursor; the last move flashes on the board.
    p.rect(0, 420, 640, 60, BAND)
    p.text(20, 448, 'YOUR REPLY:', 13, 20, WHITE, prop=False)
    p.rect(176, 428, 150, 28, NIGHT)
    p.text(186, 450, 'E6-E5', 15, 22, YELLOW, prop=False)
    p.rect(266, 432, 14, 20, CURSOR)
    p.text(480, 448, '# SEND', 13, 20, WHITE, prop=False)
    # Five days to reply, three gone.
    p.text(20, 474, 'DAYS TO REPLY', 12, 18, GREY, prop=False)
    for day in range(5):
        p.rect(188 + day * 22, 460, 16, 14, GREY if day < 3 else YELLOW)
    p.text(520, 474, '0 INDEX', 12, 18, GREY, prop=False)
    p.play('E', 440, 452)
    p.recolour(CURSOR, 'ffd23f')
    p.blink(CURSOR, WHITE, on=5, off=5)
    p.blink(LAST_MOVE, YELLOW, on=6, off=6)
    return p


if __name__ == '__main__':
    save(__file__, build)
