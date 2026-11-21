"""Screen framing, text, programmable characters, macros and time for the set-17 pages.

Every page is designed on a 640 by 480 canvas with y running down; the encoder turns that into
the unit screen of ANSI X3.110-1983, which shows y from 0 to 25/32.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from encoder import Page as Encoder, xy, Y_SCALE  # noqa: E402

# The encoder's pel() is DOMAIN (0x21): one-byte single values, four-byte multi-values (11 fraction bits).

# SO, then RESET with both operand bytes all ones: every attribute to its default, the screen cleared.
RESET = b'\x0e\x20\x7f\x7f'
ESC = b'\x1b'
# Designations (X3.110 section 4): G0 ASCII, G1 PDI, G2 macros, G3 programmable characters (DRCS).
DESIGNATE = ESC + b'(B' + ESC + b')W' + ESC + b'*z' + ESC + b'+{'
MOSAICS_INTO_G3 = ESC + b'+}'
DRCS_INTO_G3 = ESC + b'+{'
DEF_MACRO, DEF_DRCS, END = ESC + b'\x40', ESC + b'\x43', ESC + b'\x45'
REPEAT = ESC + b'\x46'
SS2, SS3 = b'\x19', b'\x1d'
SI, SO = b'\x0f', b'\x0e'
# TEXT's first operand: bits 6 and 5 the spacing (11 proportional), 4 and 3 the path, 2 and 1 the rotation.
PROPORTIONAL_SPACING = 0b110000
PATH_RIGHT, PATH_LEFT, PATH_UP, PATH_DOWN = 0, 1, 2, 3
# A programmable character is drawn on a 100 by 100 grid, its contours given as fractions of the cell.
GLYPH_GRID = 100
CANVAS_WIDTH, CANVAS_HEIGHT = 640, 480
# The right and bottom edges as encodable values: 1.0 itself cannot be written (guide section 4).
FULL_WIDTH, FULL_HEIGHT = 639.6, 479.6
COLOUR_MAP_SIZE = 16


class Plate(Encoder):
    """A page: reset, designations, a 16-entry colour map, then a full-screen background."""

    def __init__(self, colours, background=0):
        super().__init__()
        palette = colours.split()
        if len(palette) != COLOUR_MAP_SIZE:
            raise ValueError('Each page defines all sixteen colour-map entries')
        self.data.extend(RESET + DESIGNATE)
        self.ink = self.width = None
        self.pel(1)
        for index, colour in enumerate(palette):
            self.set_palette(index, colour)
        self.rect(0, 0, FULL_WIDTH, FULL_HEIGHT, background)

    def forget(self):
        """Drop the cached colour and pel after a definition or a macro that may have changed them."""
        self.ink = self.width = None
        return self

    def color(self, index):
        if index != self.ink:
            super().color(index)
            self.ink = index
        return self

    def set_palette(self, index, colour):
        super().set_palette(index, colour)
        self.ink = index
        return self

    def recolour(self, index, colour):
        """SET COLOR on an entry already in use: everything drawn in it changes at once."""
        return self.set_palette(index, colour)

    def pel(self, width):
        if width != self.width:
            super().pel(width)
            self.width = width
        return self

    def disc(self, x, y, radius, ink, fill=True):
        """A circle as a two-point arc: a point on it, then the step across its diameter."""
        self.color(ink).pel(1)
        return self.cmd(0x2f if fill else 0x2e,
                        xy((x - radius) / CANVAS_WIDTH, (CANVAS_HEIGHT - y) / Y_SCALE)
                        + xy(2 * radius / CANVAS_WIDTH, 0))

    def ring(self, x, y, radius, ink, width=2):
        self.color(ink).pel(width)
        return self.cmd(0x2e, xy((x - radius) / CANVAS_WIDTH, (CANVAS_HEIGHT - y) / Y_SCALE)
                        + xy(2 * radius / CANVAS_WIDTH, 0))

    def sector(self, x, y, radius, start, end, ink, steps=None):
        """A filled pie slice as a polygon, angles in degrees clockwise from east on the canvas."""
        steps = steps or max(4, int(abs(end - start) / 4))
        points = [(x, y)] + [polar(x, y, radius, start + (end - start) * i / steps) for i in range(steps + 1)]
        return self.poly(points, ink)

    def text(self, x, y, s, w=10, h=16, c=None, prop=True, rotation=0, path=PATH_RIGHT):
        """Text in a w by h field (canvas units) with its first character's lower left corner at (x, y)."""
        if c is not None:
            self.color(c)
        first = 0x40 | (PROPORTIONAL_SPACING if prop else 0) | (path << 2) | rotation
        self.cmd(0x22, bytes([first, 0x40]) + xy(w / CANVAS_WIDTH, h / Y_SCALE))
        self.pos(x, y)
        self.data.extend(SI + s.encode('ascii') + SO)
        return self

    def centred(self, cx, y, s, w, h, c=None, prop=False):
        """Fixed-pitch text centred on cx: each character advances one field width."""
        return self.text(cx - len(s) * w / 2, y, s, w, h, c, prop=prop)

    def glyph(self, code, *contours, cell=(1, 1)):
        """DEF DRCS: a programmable character from filled contours on the 100 by 100 grid.

        `cell` is the field's width and height ratio; the character takes the shape of the
        field in force when it is defined (guide section 11).
        """
        width, height = cell
        unit = 0.0625
        self.cmd(0x22, bytes([0x40, 0x40]) + xy(unit * width / max(cell), unit * height / max(cell)))
        self.pel(1).color(1)
        self.data.extend(DEF_DRCS + code.encode('ascii') + SO)
        side = max(cell)
        for points in contours:
            # A contour given as ('clear', points) is drawn in entry 0, which clears the bitmap (guide section 11).
            clear = isinstance(points, tuple) and points[0] == 'clear'
            if clear:
                points = points[1]
            self.color(0 if clear else 1)
            fractions = [(px / GLYPH_GRID * width / side, (GLYPH_GRID - py) / GLYPH_GRID * height / side)
                         for px, py in points]
            data = xy(*fractions[0])
            for (ax, ay), (bx, by) in zip(fractions, fractions[1:]):
                data += xy(bx - ax, by - ay)
            self.cmd(0x37, data)
        self.data.extend(END + SO)
        return self.forget()

    def programmable(self, x, y, s, w, h, c=None, repeat=0, rotation=0):
        """A run of programmable characters, each named by its one-letter code, then REPEAT.

        `rotation` turns each character in quarter turns, as TEXT's rotation bits do for letters.
        """
        if c is not None:
            self.color(c)
        self.cmd(0x22, bytes([0x40 | rotation, 0x40]) + xy(w / CANVAS_WIDTH, h / Y_SCALE))
        self.pos(x, y)
        self.data.extend(SI + b''.join(SS3 + bytes([code]) for code in s.encode('ascii')))
        if repeat:
            self.data.extend(REPEAT + bytes([0x40 | repeat]))
        self.data.extend(SO)
        return self

    def pattern(self, letter, mask, *contours):
        """DEF TEXTURE: fill pattern A to D (4 to 7) from filled contours on the 100 by 100 grid.

        `mask` is the pattern's width and height on the canvas; it repeats at that size from the
        screen's origin (guide section 11).
        """
        self.mask = xy(mask[0] / CANVAS_WIDTH, mask[1] / Y_SCALE)
        self.cmd(0x23, bytes([0x40]) + self.mask)
        self.pel(1).color(1)
        self.data.extend(ESC + b'\x44' + letter.encode('ascii') + SO)
        for points in contours:
            fractions = [(px / GLYPH_GRID, (GLYPH_GRID - py) / GLYPH_GRID) for px, py in points]
            data = xy(*fractions[0])
            for (ax, ay), (bx, by) in zip(fractions, fractions[1:]):
                data += xy(bx - ax, by - ay)
            self.cmd(0x37, data)
        self.data.extend(END + SO)
        return self.forget()

    def fill_with(self, number):
        """TEXTURE: fill pattern 0 (solid) to 7 for the shapes that follow, keeping the mask size."""
        return self.cmd(0x23, bytes([0x40 | number << 3]) + getattr(self, 'mask', b''))

    def define_macro(self, code, body):
        """DEF MACRO: record `body` (a Plate fragment built with relative commands) under one name."""
        self.data.extend(DEF_MACRO + code.encode('ascii') + SO + bytes(body.data) + END + SO)
        return self.forget()

    def play(self, code, x=None, y=None, c=None):
        """Invoke a macro at the drawing point, optionally moved to (x, y) and in colour c first."""
        if c is not None:
            self.color(c)
        if x is not None:
            self.pos(x, y)
        self.data.extend(SS2 + code.encode('ascii') + SO)
        return self.forget()

    def mosaics(self, x, y, codes, w, h, c=None):
        """Teletext-style mosaic blocks: G3 holds the mosaic set for the run, then DRCS again."""
        if c is not None:
            self.color(c)
        self.cmd(0x22, bytes([0x40, 0x40]) + xy(w / CANVAS_WIDTH, h / Y_SCALE)).pos(x, y)
        self.data.extend(MOSAICS_INTO_G3 + SI + b''.join(SS3 + bytes([code]) for code in codes)
                         + DRCS_INTO_G3 + SO)
        return self

    def blink(self, src, dest, on=5, off=10, delay=0):
        self.blinks = getattr(self, 'blinks', 0) + 1
        return super().blink(src, dest, on, off, delay)

    def stream(self):
        return bytes(self.data) + SI


def fragment():
    """A bare command buffer for macro bodies: no reset, no colour map."""
    return Encoder()


def polar(x, y, r, degrees):
    a = math.radians(degrees)
    return x + r * math.cos(a), y + r * math.sin(a)


def save(script, build):
    (ROOT / 'out' / (Path(script).stem + '.nap')).write_bytes(build().stream())


def oval(cx, cy, rx, ry, n=24):
    """Points round an ellipse, for polygons on the canvas or contours on the glyph grid."""
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
