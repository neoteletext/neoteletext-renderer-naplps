#!/usr/bin/env python3
"""Writes fonts/neoteletext.strokes: NeoTeletext's own stroke font for NAPLPS.

The glyphs below were drawn for NeoTeletext on the library's grid, 7 wide
and 10 high with y upward (crates/naplps/src/font.rs): capitals stand on
row 2 and reach row 8, small letters reach row 6, and descenders reach
row 0. Each glyph is a list of pen strokes; a stroke is a list of points
joined in order, and a stroke of one point is a dot. Run from the
repository's root: scripts/make_font.py [OUTPUT]
"""
import pathlib
import sys

# The grid's sides (font.rs: GRID_WIDTH, GRID_HEIGHT) and a glyph's bound (MAX_SEGMENTS).
GRID_WIDTH, GRID_HEIGHT, MAX_SEGMENTS = 7, 10, 64
# The two metric bytes each glyph line carries: the library keeps and does not use them.
METRICS = "0 6"

O = [(1, 2), (0, 3), (0, 7), (1, 8), (4, 8), (5, 7), (5, 3), (4, 2), (1, 2)]
P = [(0, 2), (0, 8), (4, 8), (5, 7), (5, 6), (4, 5), (0, 5)]
SMALL_O = [(1, 2), (0, 3), (0, 5), (1, 6), (4, 6), (5, 5), (5, 3), (4, 2), (1, 2)]

GLYPHS = {
    "!": [[(3, 8), (3, 4)], [(3, 2)]],
    '"': [[(2, 8), (2, 6)], [(4, 8), (4, 6)]],
    "#": [[(1, 2), (2, 8)], [(4, 2), (5, 8)], [(0, 6), (6, 6)], [(0, 4), (6, 4)]],
    "$": [[(5, 7), (1, 7), (0, 6), (1, 5), (4, 5), (5, 4), (4, 3), (0, 3)], [(3, 8), (3, 2)]],
    "%": [[(0, 2), (6, 8)], [(1, 8), (0, 7), (1, 6), (2, 7), (1, 8)], [(5, 4), (4, 3), (5, 2), (6, 3), (5, 4)]],
    "&": [[(6, 2), (1, 7), (2, 8), (3, 7), (0, 4), (0, 3), (1, 2), (3, 2), (6, 5)]],
    "'": [[(3, 8), (3, 6)]],
    "(": [[(4, 8), (2, 6), (2, 4), (4, 2)]],
    ")": [[(2, 8), (4, 6), (4, 4), (2, 2)]],
    "*": [[(3, 7), (3, 3)], [(1, 6), (5, 4)], [(1, 4), (5, 6)]],
    "+": [[(3, 7), (3, 3)], [(1, 5), (5, 5)]],
    ",": [[(3, 3), (3, 2), (2, 1)]],
    "-": [[(1, 5), (5, 5)]],
    ".": [[(3, 2)]],
    "/": [[(0, 2), (6, 8)]],
    "0": [O, [(1, 3), (4, 7)]],
    "1": [[(1, 6), (3, 8), (3, 2)], [(1, 2), (5, 2)]],
    "2": [[(0, 7), (1, 8), (4, 8), (5, 7), (5, 6), (0, 2), (5, 2)]],
    "3": [[(0, 7), (1, 8), (4, 8), (5, 7), (5, 6), (4, 5), (2, 5)], [(4, 5), (5, 4), (5, 3), (4, 2), (1, 2), (0, 3)]],
    "4": [[(4, 2), (4, 8), (0, 4), (5, 4)]],
    "5": [[(5, 8), (0, 8), (0, 5), (4, 5), (5, 4), (5, 3), (4, 2), (1, 2), (0, 3)]],
    "6": [[(4, 8), (2, 8), (0, 6), (0, 3), (1, 2), (4, 2), (5, 3), (5, 4), (4, 5), (0, 5)]],
    "7": [[(0, 8), (5, 8), (2, 2)]],
    "8": [[(1, 5), (0, 6), (0, 7), (1, 8), (4, 8), (5, 7), (5, 6), (4, 5), (1, 5), (0, 4), (0, 3), (1, 2), (4, 2), (5, 3), (5, 4), (4, 5)]],
    "9": [[(1, 2), (3, 2), (5, 4), (5, 7), (4, 8), (1, 8), (0, 7), (0, 6), (1, 5), (5, 5)]],
    ":": [[(3, 6)], [(3, 3)]],
    ";": [[(3, 6)], [(3, 3), (3, 2), (2, 1)]],
    "<": [[(5, 8), (1, 5), (5, 2)]],
    "=": [[(1, 6), (5, 6)], [(1, 4), (5, 4)]],
    ">": [[(1, 8), (5, 5), (1, 2)]],
    "?": [[(0, 7), (1, 8), (4, 8), (5, 7), (5, 6), (3, 4)], [(3, 2)]],
    "@": [[(5, 3), (4, 2), (1, 2), (0, 3), (0, 7), (1, 8), (4, 8), (5, 7), (5, 4), (3, 4), (2, 5), (3, 6), (5, 6)]],
    "A": [[(0, 2), (0, 6), (2, 8), (3, 8), (5, 6), (5, 2)], [(0, 5), (5, 5)]],
    "B": [P, [(4, 5), (5, 4), (5, 3), (4, 2), (0, 2)]],
    "C": [[(5, 7), (4, 8), (1, 8), (0, 7), (0, 3), (1, 2), (4, 2), (5, 3)]],
    "D": [[(0, 2), (0, 8), (3, 8), (5, 6), (5, 4), (3, 2), (0, 2)]],
    "E": [[(5, 8), (0, 8), (0, 2), (5, 2)], [(0, 5), (4, 5)]],
    "F": [[(5, 8), (0, 8), (0, 2)], [(0, 5), (4, 5)]],
    "G": [[(5, 7), (4, 8), (1, 8), (0, 7), (0, 3), (1, 2), (4, 2), (5, 3), (5, 5), (3, 5)]],
    "H": [[(0, 2), (0, 8)], [(5, 2), (5, 8)], [(0, 5), (5, 5)]],
    "I": [[(1, 8), (5, 8)], [(3, 8), (3, 2)], [(1, 2), (5, 2)]],
    "J": [[(5, 8), (5, 3), (4, 2), (1, 2), (0, 3)]],
    "K": [[(0, 2), (0, 8)], [(5, 8), (0, 5), (5, 2)]],
    "L": [[(0, 8), (0, 2), (5, 2)]],
    "M": [[(1, 2), (1, 8), (3, 5), (5, 8), (5, 2)]],
    "N": [[(0, 2), (0, 8), (5, 2), (5, 8)]],
    "O": [O],
    "P": [P],
    "Q": [O, [(3, 4), (5, 2)]],
    "R": [P, [(2, 5), (5, 2)]],
    "S": [[(5, 7), (4, 8), (1, 8), (0, 7), (0, 6), (1, 5), (4, 5), (5, 4), (5, 3), (4, 2), (1, 2), (0, 3)]],
    "T": [[(1, 8), (5, 8)], [(3, 8), (3, 2)]],
    "U": [[(0, 8), (0, 3), (1, 2), (4, 2), (5, 3), (5, 8)]],
    "V": [[(1, 8), (3, 2), (5, 8)]],
    "W": [[(1, 8), (2, 2), (3, 6), (4, 2), (5, 8)]],
    "X": [[(0, 2), (5, 8)], [(0, 8), (5, 2)]],
    "Y": [[(1, 8), (3, 5), (5, 8)], [(3, 5), (3, 2)]],
    "Z": [[(0, 8), (5, 8), (0, 2), (5, 2)]],
    "[": [[(4, 8), (2, 8), (2, 2), (4, 2)]],
    "\\": [[(0, 8), (6, 2)]],
    "]": [[(2, 8), (4, 8), (4, 2), (2, 2)]],
    "^": [[(1, 6), (3, 8), (5, 6)]],
    "_": [[(0, 1), (6, 1)]],
    "`": [[(2, 8), (4, 6)]],
    "a": [[(1, 6), (4, 6), (5, 5), (5, 2)], [(5, 4), (1, 4), (0, 3), (1, 2), (4, 2), (5, 3)]],
    "b": [[(0, 8), (0, 2), (4, 2), (5, 3), (5, 5), (4, 6), (0, 6)]],
    "c": [[(5, 5), (4, 6), (1, 6), (0, 5), (0, 3), (1, 2), (4, 2), (5, 3)]],
    "d": [[(5, 8), (5, 2), (1, 2), (0, 3), (0, 5), (1, 6), (5, 6)]],
    "e": [[(0, 4), (5, 4), (5, 5), (4, 6), (1, 6), (0, 5), (0, 3), (1, 2), (4, 2)]],
    "f": [[(4, 8), (3, 8), (2, 7), (2, 2)], [(0, 6), (4, 6)]],
    "g": [[(5, 3), (4, 2), (1, 2), (0, 3), (0, 5), (1, 6), (5, 6), (5, 1), (4, 0), (1, 0)]],
    "h": [[(0, 8), (0, 2)], [(0, 5), (1, 6), (4, 6), (5, 5), (5, 2)]],
    "i": [[(3, 8)], [(2, 6), (3, 6), (3, 2)], [(2, 2), (4, 2)]],
    "j": [[(4, 8)], [(3, 6), (4, 6), (4, 1), (3, 0), (1, 0)]],
    "k": [[(0, 8), (0, 2)], [(4, 6), (0, 3)], [(2, 4), (5, 2)]],
    "l": [[(2, 8), (3, 8), (3, 2)], [(2, 2), (4, 2)]],
    "m": [[(1, 2), (1, 6), (2, 6), (3, 5), (3, 2)], [(3, 5), (4, 6), (5, 5), (5, 2)]],
    "n": [[(0, 2), (0, 6)], [(0, 5), (1, 6), (4, 6), (5, 5), (5, 2)]],
    "o": [SMALL_O],
    "p": [[(0, 0), (0, 6), (4, 6), (5, 5), (5, 3), (4, 2), (0, 2)]],
    "q": [[(5, 0), (5, 6), (1, 6), (0, 5), (0, 3), (1, 2), (5, 2)]],
    "r": [[(0, 2), (0, 6)], [(0, 5), (1, 6), (4, 6), (5, 5)]],
    "s": [[(5, 5), (4, 6), (1, 6), (0, 5), (1, 4), (4, 4), (5, 3), (4, 2), (1, 2), (0, 3)]],
    "t": [[(2, 8), (2, 3), (3, 2), (4, 2), (5, 3)], [(0, 6), (4, 6)]],
    "u": [[(0, 6), (0, 3), (1, 2), (4, 2), (5, 3)], [(5, 6), (5, 2)]],
    "v": [[(1, 6), (3, 2), (5, 6)]],
    "w": [[(1, 6), (2, 2), (3, 5), (4, 2), (5, 6)]],
    "x": [[(0, 2), (5, 6)], [(0, 6), (5, 2)]],
    "y": [[(1, 6), (3, 2)], [(5, 6), (2, 0), (1, 0)]],
    "z": [[(0, 6), (5, 6), (0, 2), (5, 2)]],
    "{": [[(4, 8), (3, 8), (3, 6), (2, 5), (3, 4), (3, 2), (4, 2)]],
    "|": [[(3, 8), (3, 2)]],
    "}": [[(2, 8), (3, 8), (3, 6), (4, 5), (3, 4), (3, 2), (2, 2)]],
    "~": [[(0, 5), (1, 6), (2, 6), (4, 4), (5, 4), (6, 5)]],
}


# A glyph's stems stand on columns 1 to 5. Column 0 lies on the character
# field's left edge, which the renderer cuts at small sizes, and column 6
# is the space before the next character. The glyphs above are drawn six
# columns wide from column 0 for ease of drawing, so each that uses column
# 0 is brought in here: columns 0 to 5 become 1, 2, 3, 3, 4, 5, which keeps
# a symmetric glyph symmetric about column 3. Glyphs drawn across the
# whole field on purpose, whose ends may be cut without harm, are left.
ACROSS_THE_FIELD = set("#%&/\\_~")
BROUGHT_IN = {0: 1, 1: 2, 2: 3, 3: 3, 4: 4, 5: 5}


def placed(character: str, strokes: list) -> list:
    columns = [x for stroke in strokes for x, _ in stroke]
    if character in ACROSS_THE_FIELD or min(columns) > 0:
        return strokes
    assert max(columns) <= 5, character
    return [[(BROUGHT_IN[x], y) for x, y in stroke] for stroke in strokes]


# The supplementary set (ANSI X3.110-1983 section 5.2 and its Figure 8,
# page 23, which this follows; Dillon's "NAPLPS technical specs", 1993,
# describes the same 94 characters), drawn for NeoTeletext on the same grid. These are
# drawn where they stand: their stems are on columns 1 to 5 already, and the
# few that reach column 0 or 6 (box drawing, the em dash, the full-field
# diagonals and triangles, a bar across a stem) do so on purpose.
#
# The non-spacing accents, 4/0 to 4/15, are drawn over the letter that
# follows them in the same field (REQ-5780 item 9), so they keep clear of
# the letters: those above a letter stand on rows 8 and 9, above the small
# letters (which reach row 6) and touching the capitals' top row at most;
# those below (cedilla, ogonek, underscore) reach rows 0 and 1, below the
# baseline at row 2. The grid has no row above 9, so an accent over a
# capital meets the capital's top stroke: the price of a ten-row grid.


def fraction_slash():
    return [(1, 2), (5, 8)]


# The small figures of the fractions: numerators on columns 1 and 2, rows 5
# to 8, left of the slash; denominators on columns 3 to 5, rows 2 to 4,
# right of it.
NUMERATOR = {
    1: [[(1, 8), (1, 5)]],
    3: [[(1, 8), (2, 8), (2, 5), (1, 5)], [(1, 7), (2, 7)]],
    5: [[(2, 8), (1, 8), (1, 7), (2, 7), (2, 5), (1, 5)]],
    7: [[(1, 8), (2, 8), (1, 5)]],
}
DENOMINATOR = {
    2: [[(3, 4), (5, 4), (5, 3), (3, 3), (3, 2), (5, 2)]],
    4: [[(5, 2), (5, 4)], [(3, 4), (3, 3), (5, 3)]],
    8: [[(3, 2), (5, 2), (5, 4), (3, 4), (3, 2)], [(3, 3), (5, 3)]],
}


def fraction(numerator: int, denominator: int) -> list:
    return NUMERATOR[numerator] + [fraction_slash()] + DENOMINATOR[denominator]


# A circle large enough to hold a letter: an octagon across the whole grid,
# leaving columns 2 to 4 and rows 3 to 7 inside for the letter.
RING = [(1, 9), (5, 9), (6, 8), (6, 2), (5, 1), (1, 1), (0, 2), (0, 8), (1, 9)]
# O and o as the primary set places them (brought in to columns 1 to 5).
CAPITAL_O = [(2, 2), (1, 3), (1, 7), (2, 8), (4, 8), (5, 7), (5, 3), (4, 2), (2, 2)]
LITTLE_O = [(2, 2), (1, 3), (1, 5), (2, 6), (4, 6), (5, 5), (5, 3), (4, 2), (2, 2)]


def filled_triangle(right_angle_at_right: bool) -> list:
    """A filled right triangle under the full-field diagonal, drawn as a
    stroke on every column and every row, which the pen (1/12 of the
    field's height) closes between."""
    strokes = []
    for x in range(GRID_WIDTH):
        reach = (x * (GRID_HEIGHT - 1)) // (GRID_WIDTH - 1)
        column = x if right_angle_at_right else GRID_WIDTH - 1 - x
        strokes.append([(column, 0), (column, reach)])
    for y in range(GRID_HEIGHT):
        start = -(-y * (GRID_WIDTH - 1) // (GRID_HEIGHT - 1))
        if right_angle_at_right:
            strokes.append([(start, y), (GRID_WIDTH - 1, y)])
        else:
            strokes.append([(0, y), (GRID_WIDTH - 1 - start, y)])
    return strokes


SUPPLEMENTARY = {
    0x21: [[(3, 6)], [(3, 4), (3, 0)]],  # inverted exclamation mark
    0x22: [[(5, 5), (4, 6), (2, 6), (1, 5), (1, 3), (2, 2), (4, 2), (5, 3)], [(3, 7), (3, 1)]],  # cent
    0x23: [[(5, 7), (4, 8), (3, 8), (2, 7), (2, 2)], [(1, 5), (4, 5)], [(1, 2), (5, 2)]],  # pound
    0x24: placed("$", GLYPHS["$"]),  # dollar
    0x25: [[(1, 8), (3, 5), (5, 8)], [(3, 5), (3, 2)], [(1, 4), (5, 4)], [(1, 3), (5, 3)]],  # yen
    0x26: placed("#", GLYPHS["#"]),  # number sign
    0x27: [[(5, 8), (2, 8), (1, 7), (2, 6), (4, 6), (5, 5), (4, 4)], [(2, 6), (1, 5), (2, 4), (4, 4), (5, 3), (4, 2), (1, 2)]],  # section
    0x28: [[(3, 7), (5, 5), (3, 3), (1, 5), (3, 7)], [(1, 7), (2, 6)], [(5, 7), (4, 6)], [(1, 3), (2, 4)], [(5, 3), (4, 4)]],  # currency
    0x29: [[(4, 6), (3, 7), (3, 8)]],  # left single quotation mark
    0x2A: [[(3, 6), (2, 7), (2, 8)], [(5, 6), (4, 7), (4, 8)]],  # left double quotation mark
    0x2B: [[(3, 7), (1, 5), (3, 3)], [(5, 7), (3, 5), (5, 3)]],  # left guillemet
    0x2C: [[(1, 5), (5, 5)], [(3, 7), (1, 5), (3, 3)]],  # left arrow
    0x2D: [[(3, 2), (3, 8)], [(1, 6), (3, 8), (5, 6)]],  # up arrow
    0x2E: [[(1, 5), (5, 5)], [(3, 7), (5, 5), (3, 3)]],  # right arrow
    0x2F: [[(3, 8), (3, 2)], [(1, 4), (3, 2), (5, 4)]],  # down arrow
    0x30: [[(3, 8), (2, 7), (3, 6), (4, 7), (3, 8)]],  # degree
    0x31: [[(3, 7), (3, 3)], [(1, 5), (5, 5)], [(1, 2), (5, 2)]],  # plus or minus
    0x32: [[(2, 8), (4, 8), (4, 7), (2, 5), (4, 5)]],  # superscript two
    0x33: [[(2, 8), (4, 8), (3, 7), (4, 6), (3, 5), (2, 5)]],  # superscript three
    0x34: [[(1, 3), (5, 7)], [(1, 7), (5, 3)]],  # multiplication
    0x35: [[(1, 0), (1, 6)], [(1, 3), (2, 2), (4, 2), (5, 3)], [(5, 6), (5, 2)]],  # micro
    0x36: [[(5, 2), (5, 8), (2, 8), (1, 7), (1, 6), (2, 5), (4, 5)], [(4, 8), (4, 2)]],  # pilcrow
    0x37: [[(3, 5)]],  # middle dot
    0x38: [[(3, 7)], [(1, 5), (5, 5)], [(3, 3)]],  # division
    0x39: [[(3, 6), (4, 7), (4, 8)]],  # right single quotation mark
    0x3A: [[(2, 6), (3, 7), (3, 8)], [(4, 6), (5, 7), (5, 8)]],  # right double quotation mark
    0x3B: [[(1, 7), (3, 5), (1, 3)], [(3, 7), (5, 5), (3, 3)]],  # right guillemet
    0x3C: [[(1, 8), (1, 5)], fraction_slash(), [(5, 2), (5, 4)], [(3, 4), (3, 3), (5, 3)]],  # one quarter
    0x3D: fraction(1, 2),  # one half
    0x3E: fraction(3, 4),  # three quarters
    0x3F: [[(3, 8)], [(3, 6), (3, 5), (1, 3), (1, 2), (2, 1), (4, 1), (5, 2)]],  # inverted question mark
    # Non-spacing accents.
    0x40: [[(1, 9), (5, 9), (4, 8)]],  # vector overbar
    0x41: [[(2, 9), (4, 8)]],  # grave
    0x42: [[(2, 8), (4, 9)]],  # acute
    0x43: [[(1, 8), (3, 9), (5, 8)]],  # circumflex
    0x44: [[(1, 8), (2, 9), (4, 8), (5, 9)]],  # tilde
    0x45: [[(1, 9), (5, 9)]],  # macron
    0x46: [[(1, 9), (2, 8), (4, 8), (5, 9)]],  # breve
    0x47: [[(3, 9)]],  # dot above
    0x48: [[(2, 9)], [(4, 9)]],  # diaeresis
    0x49: [[(1, 2), (5, 8)]],  # overprinting slash
    0x4A: [[(2, 9), (4, 9), (4, 8), (2, 8), (2, 9)]],  # ring above
    0x4B: [[(3, 2), (3, 1), (4, 1), (4, 0), (2, 0)]],  # cedilla
    0x4C: [[(1, 1), (5, 1)]],  # underscore
    0x4D: [[(2, 8), (3, 9)], [(4, 8), (5, 9)]],  # double acute
    0x4E: [[(4, 2), (3, 1), (4, 0), (5, 0)]],  # ogonek
    0x4F: [[(1, 9), (3, 8), (5, 9)]],  # caron
    0x50: [[(0, 4), (6, 4)]],  # em dash
    0x51: [[(2, 7), (3, 8), (3, 5)], [(2, 5), (4, 5)]],  # superscript one
    0x52: [RING, [(2, 3), (2, 7), (3, 7), (4, 6), (3, 5), (2, 5)], [(3, 5), (4, 3)]],  # registered
    0x53: [RING, [(4, 7), (2, 7), (2, 3), (4, 3)]],  # copyright
    0x54: [[(0, 8), (2, 8)], [(1, 8), (1, 6)], [(3, 6), (3, 8), (4, 7), (5, 8), (5, 6)]],  # trade mark
    0x55: [[(4, 8), (4, 3), (3, 2), (2, 2), (1, 3), (2, 4), (3, 4), (4, 3)], [(4, 8), (5, 7), (5, 6)]],  # eighth note
    0x56: [[(0, 5), (6, 5)]],  # box drawing, horizontal
    0x57: [[(3, 0), (3, 9)]],  # box drawing, vertical
    0x58: [[(0, 0), (6, 9)]],  # diagonal, lower left to upper right
    0x59: [[(0, 9), (6, 0)]],  # diagonal, upper left to lower right
    0x5A: filled_triangle(True),  # filled triangle below 5/8
    0x5B: filled_triangle(False),  # filled triangle below 5/9
    0x5C: fraction(1, 8),  # one eighth
    0x5D: fraction(3, 8),  # three eighths
    0x5E: fraction(5, 8),  # five eighths
    0x5F: fraction(7, 8),  # seven eighths
    0x60: [[(1, 2), (2, 2), (2, 3), (1, 4), (1, 7), (2, 8), (4, 8), (5, 7), (5, 4), (4, 3), (4, 2), (5, 2)]],  # ohm
    0x61: [[(1, 2), (1, 7), (2, 8), (5, 8)], [(3, 8), (3, 2), (5, 2)], [(1, 5), (4, 5)]],  # capital AE
    0x62: [[(1, 2), (1, 8), (3, 8), (5, 6), (5, 4), (3, 2), (1, 2)], [(0, 5), (2, 5)]],  # capital D with stroke
    0x63: [[(2, 8), (4, 8), (4, 5)], [(4, 7), (2, 7), (1, 6), (2, 5), (4, 5)], [(1, 4), (5, 4)]],  # feminine ordinal
    0x64: [[(1, 2), (1, 8)], [(5, 2), (5, 8)], [(1, 5), (5, 5)], [(0, 7), (6, 7)]],  # capital H with stroke
    0x65: [[(0, 5), (6, 5)], [(3, 0), (3, 9)]],  # box drawing, crossing
    0x66: [[(1, 2), (1, 8)], [(5, 8), (5, 3), (4, 2), (3, 2), (3, 3)]],  # capital IJ
    0x67: [[(1, 8), (1, 2), (5, 2)], [(3, 5)]],  # capital L with middle dot
    0x68: [[(2, 8), (2, 2), (5, 2)], [(1, 4), (3, 6)]],  # capital L with stroke
    0x69: [CAPITAL_O, [(1, 2), (5, 8)]],  # capital O with stroke
    0x6A: [[(5, 8), (2, 8), (1, 7), (1, 3), (2, 2), (5, 2)], [(3, 8), (3, 2)], [(3, 5), (5, 5)]],  # capital OE
    0x6B: [[(2, 8), (4, 8), (4, 5), (2, 5), (2, 8)], [(1, 4), (5, 4)]],  # masculine ordinal
    0x6C: [[(1, 2), (1, 8)], [(1, 7), (4, 7), (5, 6), (5, 5), (4, 4), (1, 4)]],  # capital thorn
    0x6D: [[(1, 8), (5, 8)], [(3, 8), (3, 2)], [(2, 5), (4, 5)]],  # capital T with stroke
    0x6E: [[(1, 2), (1, 8)], [(1, 7), (2, 8), (4, 8), (5, 7), (5, 1), (4, 0), (3, 0)]],  # capital eng
    0x6F: [[(1, 8), (1, 7)], [(2, 2), (2, 6)], [(2, 5), (3, 6), (4, 6), (5, 5), (5, 2)]],  # n preceded by apostrophe
    0x70: [[(1, 2), (1, 6)], [(5, 6), (1, 4), (5, 2)]],  # kra
    0x71: [[(1, 6), (3, 6), (3, 2), (2, 2), (1, 3), (2, 4), (3, 4)], [(3, 4), (5, 4), (5, 6), (3, 6)], [(3, 2), (5, 2)]],  # small ae
    0x72: [[(5, 8), (5, 2), (2, 2), (1, 3), (1, 5), (2, 6), (5, 6)], [(3, 7), (6, 7)]],  # small d with stroke
    0x73: [LITTLE_O, [(5, 5), (5, 6), (3, 8)], [(3, 6), (5, 8)]],  # small eth
    0x74: [[(1, 8), (1, 2)], [(1, 5), (2, 6), (4, 6), (5, 5), (5, 2)], [(0, 7), (3, 7)]],  # small h with stroke
    0x75: [[(2, 6), (3, 6), (3, 2)], [(2, 2), (4, 2)]],  # dotless i
    0x76: [[(2, 8)], [(2, 6), (2, 2)], [(4, 8)], [(4, 6), (4, 1), (3, 0), (2, 0)]],  # small ij
    0x77: [[(2, 8), (2, 2)], [(4, 5)]],  # small l with middle dot
    0x78: [[(2, 8), (3, 8), (3, 2)], [(2, 2), (4, 2)], [(1, 4), (5, 6)]],  # small l with stroke
    0x79: [LITTLE_O, [(1, 1), (5, 7)]],  # small o with stroke
    0x7A: [[(3, 6), (2, 6), (1, 5), (1, 3), (2, 2), (3, 2), (3, 6)], [(3, 4), (5, 4), (5, 5), (4, 6), (3, 6)], [(3, 2), (5, 2)]],  # small oe
    0x7B: [[(1, 2), (1, 7), (2, 8), (4, 8), (5, 7), (5, 6), (4, 5), (5, 4), (5, 3), (4, 2), (3, 2)]],  # sharp s
    0x7C: [[(1, 0), (1, 8)], [(1, 6), (4, 6), (5, 5), (5, 3), (4, 2), (1, 2)]],  # small thorn
    0x7D: [[(3, 8), (3, 3), (4, 2), (5, 3)], [(1, 6), (5, 6)], [(2, 4), (4, 4)]],  # small t with stroke
    0x7E: [[(1, 2), (1, 6)], [(1, 5), (2, 6), (4, 6), (5, 5), (5, 1), (4, 0), (3, 0)]],  # small eng
}


def segments_of(name: str, strokes: list) -> list:
    segments = []
    for stroke in strokes:
        points = stroke if len(stroke) > 1 else [stroke[0], stroke[0]]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if (x1, y1) == (x2, y2) and len(stroke) > 1:
                continue  # two points brought onto one column: no segment between them
            assert 0 <= min(x1, x2) and max(x1, x2) < GRID_WIDTH and 0 <= min(y1, y2) and max(y1, y2) < GRID_HEIGHT, name
            segments.append(f"{x1},{y1},{x2},{y2}")
    assert 0 < len(segments) <= MAX_SEGMENTS, name
    return segments


def main() -> None:
    # The file to write: fonts/neoteletext.strokes, or the path given, which
    # the commit gate uses to check the committed file against this source.
    target = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "fonts/neoteletext.strokes")
    lines = [
        "# NeoTeletext's stroke font for NAPLPS: the primary and supplementary sets, drawn for NeoTeletext.",
        "# Written by scripts/make_font.py, which holds each glyph's strokes; edit that, not this.",
        "[primary]",
    ]
    for code in range(0x21, 0x7F):
        lines.append(f"{code:02x} {METRICS} " + " ".join(segments_of(chr(code), placed(chr(code), GLYPHS[chr(code)]))))
    lines.append("[supplementary]")
    assert sorted(SUPPLEMENTARY) == list(range(0x21, 0x7F))
    for code in range(0x21, 0x7F):
        lines.append(f"{code:02x} {METRICS} " + " ".join(segments_of(f"supplementary {code:02x}", SUPPLEMENTARY[code])))
    target.write_text("\n".join(lines) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
