"""The example pages of docs/guide.md. Run: python3 docs/examples/examples.py OUTDIR

Writes one .nap file per example. docs/examples/build.sh renders them to docs/images/.
"""

import pathlib
import sys

from naplps_page import *  # noqa: F403 - the examples read best with the bare names

# The default 16-entry colour map (reference, "The default colour map").
BLACK, GREY1, GREY2, GREY3, GREY4, GREY5, GREY6, WHITE = range(8)
BLUE, MAGENTA_BLUE, MAGENTA_RED, RED, YELLOW, YELLOW_GREEN, GREEN, CYAN = range(8, 16)


def hello():
    return SO + reset_all() + select(WHITE) + text_at(0.35, 0.4, "Hello, NAPLPS")


def shapes():
    page = SO + reset_all()
    # A filled rectangle: lower left corner, then width and height.
    page += select(BLUE) + pdi(SET_RECT_FILLED, xy(0.05, 0.45), xy(0.25, 0.25))
    # A line from point to point, then on to a third point: POINT SET, then LINE. (SET & LINE
    # takes its points in pairs, one line from each pair.)
    page += select(YELLOW) + pdi(POINT_SET_ABS, xy(0.38, 0.45)) + pdi(LINE_ABS, xy(0.50, 0.70), xy(0.62, 0.45))
    # A filled circle: a point on it, then the step to the opposite point.
    page += select(RED) + pdi(SET_ARC_FILLED, xy(0.70, 0.575), xy(0.25, 0))
    # A filled polygon: first vertex, then the step to each following vertex.
    page += select(GREEN) + pdi(SET_POLY_FILLED, xy(0.05, 0.08), xy(0.30, 0), xy(-0.15, 0.28))
    # An arc through three points, outlined: start, step to a middle point, step to the end.
    page += select(CYAN) + pdi(SET_ARC_OUTLINED, xy(0.40, 0.10), xy(0.11, 0.20), xy(0.11, -0.20))
    # An outlined rectangle.
    page += select(WHITE) + pdi(SET_RECT_OUTLINED, xy(0.70, 0.08), xy(0.25, 0.28))
    return page


def colour_map():
    page = SO + reset_all()
    for entry in range(16):
        column, row = entry % 8, entry // 8
        x, y = 0.04 + column * 0.117, 0.45 - row * 0.32
        page += select(entry) + pdi(SET_RECT_FILLED, xy(x, y), xy(0.10, 0.22))
        page += select(WHITE) + pdi(SET_RECT_OUTLINED, xy(x, y), xy(0.10, 0.22))
        page += text_at(x + 0.03, y - 0.06, str(entry))
    return page


def own_colours():
    page = SO + reset_all()
    palette = [(0x1B, 0x26, 0x4F), (0x27, 0x4C, 0x77), (0x60, 0x96, 0xBA), (0xA3, 0xCE, 0xF1), (0xE7, 0xEC, 0xEF)]
    for index, (red, green, blue) in enumerate(palette):
        page += define(8 + index, red, green, blue)
    for index in range(5):
        page += select(8 + index) + pdi(SET_RECT_FILLED, xy(0, 0.78 - (index + 1) * 0.157), xy(0.999, 0.157))
    page += select(BLACK) + text_at(0.06, 0.05, "five entries of the map, redefined")
    return page


def textures():
    page = SO + reset_all() + select(WHITE)
    # DOMAIN: one-byte single values, three-byte coordinates, and a logical pel of 1/256 by 1/256.
    # Line textures and hatching are measured in pels: with the default pel, lines stay solid.
    page += pdi(DOMAIN, fixed(0b001000), xy(1 / 256, 1 / 256))
    # Line textures 0 to 3: solid, dotted, dashed, dot-dash.
    for texture in range(4):
        y = 0.72 - texture * 0.05
        page += pdi(TEXTURE, fixed(texture)) + pdi(SET_LINE_ABS, xy(0.05, y), xy(0.95, y))
    # Fill patterns 0 to 3: solid, vertical, horizontal and cross hatching.
    for pattern in range(4):
        x = 0.05 + pattern * 0.235
        page += select(YELLOW) + pdi(TEXTURE, fixed(pattern << 3))
        page += pdi(SET_RECT_FILLED, xy(x, 0.30), xy(0.19, 0.19))
    # The same with highlight: the outline drawn in black (in mode 2, in the background colour).
    for pattern in range(4):
        x = 0.05 + pattern * 0.235
        page += select(CYAN) + pdi(TEXTURE, fixed(pattern << 3 | 0b100))
        page += pdi(SET_ARC_FILLED, xy(x, 0.14), xy(0.19, 0))
    return page


def text():
    page = SO + reset_all() + select(WHITE)
    page += text_at(0.04, 0.70, "Normal text: 40 columns by 20 rows")
    page += SI + SMALL_TEXT + SO + text_at(0.04, 0.65, "SMALL TEXT: 80 columns")
    page += SI + MEDIUM_TEXT + SO + text_at(0.04, 0.59, "MEDIUM TEXT: 32 columns")
    page += SI + DOUBLE_HEIGHT + SO + text_at(0.04, 0.49, "DOUBLE HEIGHT")
    page += SI + DOUBLE_SIZE + SO + text_at(0.04, 0.39, "DOUBLE SIZE")
    page += SI + NORMAL_TEXT + SO
    page += select(YELLOW) + pdi(POINT_SET_ABS, xy(0.04, 0.32)) + SI
    page += UNDERLINE_START + b"underlined" + UNDERLINE_STOP + b"  " + REVERSE_VIDEO + b"reversed" + NORMAL_VIDEO + SO
    # TEXT: proportional spacing (first byte, bits 6 and 5 = 11) and a 1/16 by 1/10 field.
    page += select(CYAN) + pdi(TEXT, fixed(0b110000, 0), xy(1 / 16, 1 / 10))
    page += text_at(0.04, 0.17, "Proportional")
    # TEXT: rotated a quarter turn (bits 2 and 1 = 01) and running upward (bits 4 and 3 = 10).
    page += select(GREEN) + pdi(TEXT, fixed(0b001001, 0), xy(1 / 32, 3 / 64))
    page += text_at(0.97, 0.08, "rotated, path up")
    # Colour mode 2: text on a background colour.
    page += pdi(TEXT, fixed(0, 0), xy(1 / 40, 5 / 128)) + select(BLACK, YELLOW)
    page += text_at(0.04, 0.05, " black on yellow, colour mode 2 ")
    return page


def mosaics():
    page = SO + reset_all() + select(GREEN) + SI + DOUBLE_SIZE + MOSAICS_INTO_G3 + SO
    rows = ["0000111100", "0011111110", "0110110110", "1111111111", "0011001100", "0110000110"]
    # Each mosaic character is two cells wide and three high.
    cells = [row.ljust(10, "0") for row in rows]
    for line in range(0, len(cells), 3):
        page += pdi(POINT_SET_ABS, xy(0.35, 0.50 - (line // 3) * (5 / 64)))
        for column in range(0, 10, 2):
            bits = 0
            for r in range(3):
                for c in range(2):
                    if cells[line + r][column + c] == "1":
                        bits |= [1, 2, 4, 8, 16, 64][r * 2 + c]
            page += SS3 + bytes([0x20 | bits])
    page += SI + NORMAL_TEXT + SO + select(WHITE) + text_at(0.27, 0.22, "mosaics: 2 by 3 cells each")
    return page


def macros():
    page = SO + reset_all() + MACROS_INTO_G3
    # Macro 2/1: a small four-pointed star at the drawing point, using relative PDIs only.
    star = pdi(POLY_FILLED, xy(0.012, 0.03), xy(0.012, -0.03), xy(-0.012, -0.03), xy(-0.012, 0.03))
    star += pdi(POINT_SET_REL, xy(-0.012, -0.012))
    star += pdi(POLY_FILLED, xy(0.012, 0.012), xy(0.012, -0.012), xy(0.012, 0.012), xy(-0.012, 0.012), xy(-0.012, -0.012))
    page += DEF_MACRO + b"\x21" + SO + star + END
    page += define(8, 0x0B, 0x13, 0x40) + pdi(SET_RECT_FILLED, xy(0, 0), xy(0.999, 0.78))
    positions = [(0.10, 0.62), (0.22, 0.30), (0.31, 0.55), (0.45, 0.68), (0.52, 0.22), (0.60, 0.47), (0.74, 0.63), (0.83, 0.33), (0.90, 0.12), (0.15, 0.10)]
    for index, (x, y) in enumerate(positions):
        page += select(WHITE if index % 3 else YELLOW) + pdi(POINT_SET_ABS, xy(x, y)) + SS3 + b"\x21"
    return page


def drcs():
    page = SO + reset_all() + DRCS_INTO_G3 + select(RED)
    # DEF DRCS 2/1: a heart, drawn in a unit square that becomes the character field.
    heart = pdi(SET_ARC_FILLED, xy(0.10, 0.65), xy(0.40, 0)) + pdi(SET_ARC_FILLED, xy(0.50, 0.65), xy(0.40, 0))
    heart += pdi(SET_POLY_FILLED, xy(0.12, 0.56), xy(0.76, 0), xy(-0.38, -0.50))
    page += pdi(TEXT, fixed(0, 0), xy(1 / 16, 1 / 16)) + DEF_DRCS + b"\x21" + SO + heart + END
    for row in range(4):
        page += select([RED, MAGENTA_RED, YELLOW, WHITE][row]) + pdi(POINT_SET_ABS, xy(0.12 + row * 0.03, 0.60 - row * 0.15))
        page += SS3 + b"\x21" + REPEAT + fixed(9)
    return page


def scribble():
    page = SO + reset_all() + select(GREEN)
    # INCREMENTAL LINE: a step size, then two-bit moves: 01 dx, 10 dy, 11 both, 00 an escape.
    moves = []
    for _ in range(6):
        moves += [3, 3, 3, 3, 1, 1, 0, 2, 3, 3, 3, 3, 1, 1, 0, 2]  # up-right, flat, flip dy, ...
    while len(moves) % 3:
        moves.append(1)
    data = bytes(OPERAND | moves[i] << 4 | moves[i + 1] << 2 | moves[i + 2] for i in range(0, len(moves), 3))
    page += pdi(POINT_SET_ABS, xy(0.05, 0.30)) + pdi(INCREMENTAL_LINE, xy(1 / 64, 1 / 32)) + data
    return page


def animation():
    page = SO + reset_all()
    page += define(8, 0x10, 0x10, 0x30) + pdi(SET_RECT_FILLED, xy(0, 0), xy(0.999, 0.78))
    page += define(9, 0xFF, 0xD0, 0x40) + pdi(SET_ARC_FILLED, xy(0.38, 0.39), xy(0.24, 0))
    page += select(WHITE) + text_at(0.36, 0.12, "blinking beacon")
    # BLINK: entry 9 (selected) takes entry 8's colour for 5 tenths, then its own for 5.
    page += select(9) + pdi(BLINK, fixed(8 << 2, 5, 5, 0))
    return page


def postcard():
    page = SO + reset_all() + MACROS_INTO_G3
    sky, sun, far, near, sea, foam, ink = 8, 9, 10, 11, 12, 13, 14
    for entry, colour in [(sky, (0xF6, 0xB2, 0x6B)), (sun, (0xFF, 0xF1, 0xC1)), (far, (0xB5, 0x65, 0x76)), (near, (0x6D, 0x59, 0x7A)), (sea, (0x35, 0x50, 0x70)), (foam, (0xEA, 0xAC, 0x8B)), (ink, (0x2A, 0x2D, 0x43))]:
        page += define(entry, *colour)
    page += select(sky) + pdi(SET_RECT_FILLED, xy(0, 0), xy(0.999, 0.78))
    page += select(sun) + circle(0.68, 0.47, 0.13)
    page += select(far) + polygon([(0, 0.30), (0.14, 0.44), (0.27, 0.36), (0.40, 0.52), (0.58, 0.34), (0.72, 0.43), (0.86, 0.33), (0.999, 0.40), (0.999, 0.25), (0, 0.25)])
    page += select(near) + polygon([(0, 0.25), (0.10, 0.34), (0.22, 0.27), (0.34, 0.38), (0.50, 0.26), (0.999, 0.30), (0.999, 0.20), (0, 0.20)])
    page += select(sea) + pdi(SET_RECT_FILLED, xy(0, 0), xy(0.999, 0.26))
    # Macro 2/1: one ripple, a thin bar at the drawing point.
    page += DEF_MACRO + b"\x21" + SO + pdi(RECT_FILLED, xy(0.07, 0.006)) + END
    page += select(foam)
    for x, y in [(0.60, 0.22), (0.64, 0.19), (0.56, 0.16), (0.66, 0.13), (0.52, 0.10), (0.70, 0.07), (0.12, 0.17), (0.30, 0.11), (0.86, 0.15)]:
        page += pdi(POINT_SET_ABS, xy(x, y)) + SS3 + b"\x21"
    page += select(ink) + pdi(TEXT, fixed(0b110000, 0), xy(1 / 14, 1 / 9)) + text_at(0.05, 0.62, "DUSK")
    page += pdi(TEXT, fixed(0b110000, 0), xy(1 / 40, 5 / 128)) + select(sun) + text_at(0.05, 0.03, "a NAPLPS postcard, 1 kilobyte")
    return page


def own_texture():
    page = SO + reset_all()
    # TEXTURE's second operand is the mask size: the pattern repeats every 1/16 of the screen.
    page += pdi(TEXTURE, fixed(0), xy(1 / 16, 1 / 16))
    # DEF TEXTURE A (fill pattern 4): a diagonal stripe drawn in the unit square.
    page += DEF_TEXTURE + b"\x41" + SO + pdi(SET_POLY_FILLED, xy(0, 0), xy(0.3, 0), xy(0.69, 0.999), xy(-0.3, 0)) + END
    page += select(BLUE) + pdi(SET_RECT_FILLED, xy(0.10, 0.14), xy(0.80, 0.50))
    page += select(YELLOW) + pdi(TEXTURE, fixed(4 << 3), xy(1 / 16, 1 / 16)) + pdi(SET_RECT_FILLED, xy(0.10, 0.14), xy(0.80, 0.50))
    return page


def supplementary():
    page = SO + reset_all()
    for row in range(6):
        for column in range(16):
            code = 0x20 + row * 16 + column
            x, y = 0.05 + column * 0.058, 0.66 - row * 0.115
            page += select(GREY4) + SI + SMALL_TEXT + SO + text_at(x, y - 0.04, f"{code:02X}")
            page += select(WHITE) + SI + DOUBLE_SIZE + SO + pdi(POINT_SET_ABS, xy(x, y)) + SI
            # 40 to 4F are accents that do not move the cursor: show each over a space.
            page += SS2 + bytes([code]) + (b" " if 0x40 <= code <= 0x4F else b"") + SO
    return page


EXAMPLES = [hello, shapes, colour_map, own_colours, textures, text, mosaics, macros, drcs, scribble, animation, postcard, own_texture, supplementary]

if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for number, example in enumerate(EXAMPLES, start=1):
        data = example()
        (out / f"{number:02d}-{example.__name__.replace('_', '-')}.nap").write_bytes(data)
        print(f"{number:02d}-{example.__name__}: {len(data)} bytes")
