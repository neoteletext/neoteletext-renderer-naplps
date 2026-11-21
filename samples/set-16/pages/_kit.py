"""Drawing kit shared by the ten pages of set 16.

Coordinates are a 640 by 480 design canvas with y downward; the encoder turns
them into unit-screen fractions.  Text sizes are named here once so that every
page uses sizes that were checked for legibility at 480 by 460.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from encoder import Page as Writer, Y_SCALE, xy  # noqa: E402

RESET = b'\x0e\x20\x7f\x7f'
# G0 ASCII, G1 PDI, G2 DRCS (reached by SS2), G3 macros (reached by SS3).
SETS = b'\x1b(B\x1b)W\x1b*\x7b\x1b+\x7a'
SS2, SS3 = b'\x19', b'\x1d'
FONT = ROOT.parents[1] / 'fonts' / 'neoteletext.strokes'

# Character fields (width, height) on the design canvas.  The stroke font's
# capitals are 6/10 of the field high and its pen 1/12 of it.  At 480 by 460 a
# field 20 high gets a two-pixel pen, and 16 wide keeps the counters of small
# letters open under that pen, so SMALL is the smallest size a page may use.
SMALL = (16, 20)
BODY = (18, 24)
LARGE = (22, 30)
# A service's name in its title band: LARGE made wider, so that an overstruck W or M stays open.
TITLE = (26, 30)
HEAD = (28, 40)
BANNER = (38, 54)
# A key top in a foot band, and the space between it and its caption.
KEY_TOP, KEY_GAP = 22, 8


def _glyph_extents():
    """Leftmost and rightmost grid column of each primary glyph, for measuring."""
    extents, section = {}, None
    for row in FONT.read_text().splitlines():
        if row.startswith('['):
            section = row
            continue
        parts = row.split()
        if section != '[primary]' or len(parts) < 4 or row.startswith('#'):
            continue
        columns = [int(v) for seg in parts[3:] for v in seg.split(',')[0::2]]
        extents[int(parts[0], 16)] = (min(columns), max(columns))
    return extents


EXTENTS = _glyph_extents()


def measure(caption, width, proportional=True):
    """Advance of a caption in design units, by the renderer's spacing rule."""
    if not proportional:
        return len(caption) * width
    total = 0.0
    for char in caption:
        low, high = EXTENTS.get(ord(char), (0, 6))
        total += width if char == ' ' else (high - low + 2) * width / 8
    return total


class Screen(Writer):
    """One page: full reset, sets, sixteen colours, then drawing."""

    def __init__(self, colours):
        super().__init__()
        palette = colours.split()
        if len(palette) != 16:
            raise ValueError('a page defines all sixteen colours')
        self.palette = palette
        self.data.extend(RESET + SETS)
        self.ink = self.brush = self.type = self.fill = None
        self.blinking = False
        self.pel(1)
        for index, colour in enumerate(palette):
            self.set_palette(index, colour)
        self.ink = 15
        self.rect(0, 0, 639.6, 479.6, 0)

    # -- state, sent only when it changes ---------------------------------
    def color(self, index):
        if index != self.ink:
            super().color(index)
            self.ink = index
        return self

    def pel(self, width):
        if width != self.brush:
            super().pel(width)
            self.brush = width
        return self

    def recolour(self, index, colour):
        """Give a map entry a new colour: everything drawn in it changes."""
        self.ink = None
        return self.set_palette(index, colour)

    def pattern(self, fill=0, highlight=False, mask=None, line=0):
        """Fill pattern 0 solid, 1 to 3 hatching, 4 to 7 the defined ones; line
        texture 0 solid, 1 dotted, 2 dashed, 3 dot-dash, measured in the pel."""
        key = (fill, highlight, mask, line)
        if key != self.fill:
            operand = bytes([0x40 | fill << 3 | (4 if highlight else 0) | line])
            if mask:
                operand += xy(mask[0] / 640, mask[1] / Y_SCALE)
            self.cmd(0x23, operand)
            self.fill = key
        return self

    # -- shapes -----------------------------------------------------------
    def box(self, x, y, w, h, ink, fill=True):
        return self.rect(x, y, w, h, ink, fill)

    def frame(self, x, y, w, h, ink, width=2):
        """An outline whose thickness is drawn inward with filled bars."""
        self.rect(x, y, w, width, ink)
        self.rect(x, y + h - width, w, width, ink)
        self.rect(x, y, width, h, ink)
        return self.rect(x + w - width, y, width, h, ink)

    def disc(self, x, y, radius, ink, fill=True, width=1):
        self.color(ink).pel(width)
        return self.cmd(0x2f if fill else 0x2e,
                        xy((x - radius) / 640, (480 - y) / Y_SCALE)
                        + xy(2 * radius / 640, 0))

    def bow(self, start, middle, end, ink, fill=False, width=1):
        """An arc through three points; filled, it closes on its chord."""
        self.pel(width)
        return self.arc(start, middle, end, ink, fill)

    def oval(self, x, y, rx, ry, ink, steps=28, fill=True):
        return self.ellipse(x, y, rx, ry, ink, fill, steps)

    def wedge(self, x, y, radius, start, end, ink, steps=None):
        """A pie slice from angle start to end, degrees clockwise from north."""
        steps = steps or max(3, int(abs(end - start) / 6))
        points = [(x, y)]
        for step in range(steps + 1):
            angle = math.radians(start + (end - start) * step / steps)
            points.append((x + radius * math.sin(angle), y - radius * math.cos(angle)))
        return self.poly(points, ink)

    def stroke(self, points, ink, width=1):
        return self.line(points, ink, width)

    # -- text -------------------------------------------------------------
    def say(self, x, y, caption, size=BODY, ink=None, align='l', proportional=True,
            bold=0, fit=None):
        """Write a caption whose field stands on the line y (baseline two tenths up).

        align is l, c or r about x; fit is the room the caption must stay within;
        a caption that leaves the screen or its room is an error.  bold overstrikes the caption that many
        design units to the right, which thickens the vertical strokes.
        """
        width, height = size
        if ink is not None:
            self.color(ink)
        advance = measure(caption, width, proportional)
        if align == 'c':
            x -= advance / 2
        elif align == 'r':
            x -= advance
        if x < 0 or x + advance > 640 or (fit is not None and advance > fit):
            raise ValueError(f'caption does not fit: {caption!r} is {advance:.0f} wide at x {x:.0f}')
        key = (width, height, proportional)
        if key != self.type:
            self.cmd(0x22, bytes([0x70 if proportional else 0x40, 0x40])
                     + xy(width / 640, height / Y_SCALE))
            self.type = key
        for shift in ([0, bold] if bold else [0]):
            self.pos(x + shift, y)
            self.data.extend(b'\x0f' + caption.encode('ascii') + b'\x0e')
        return self

    def keycap(self, x, y, digit, label, cap, ink, align='l'):
        """A keypad choice in the foot band: the digit on a key top, then what it does.

        y is the line the SMALL caption stands on; align l, c or r places the
        whole choice about x.  Returns the choice's width.
        """
        width = KEY_TOP + KEY_GAP + measure(label, SMALL[0])
        left = x - {'l': 0, 'c': width / 2, 'r': width}[align]
        self.rect(left, y - SMALL[1] - 1, KEY_TOP, SMALL[1] + 3, cap)
        self.say(left + KEY_TOP / 2, y, digit, SMALL, 0, 'c')
        self.say(left + KEY_TOP + KEY_GAP, y, label, SMALL, ink)
        return width

    def menu(self, y, choices, cap, ink):
        """Up to three keypad choices across the foot band: left, centre, right."""
        places = {1: [(628, 'r')], 2: [(12, 'l'), (628, 'r')], 3: [(12, 'l'), (320, 'c'), (628, 'r')]}
        for (digit, label), (x, align) in zip(choices, places[len(choices)]):
            self.keycap(x, y, digit, label, cap, ink, align)
        return self

    # -- definitions ------------------------------------------------------
    def glyph(self, code, size, draw):
        """Define DRCS character `code`; draw(pen) works in a 640-unit square.

        The definition takes the shape of the field `size`; inside it the
        longer side is one unit, which the helper pen maps from 0..100.
        """
        width, height = size
        self.cmd(0x22, bytes([0x40, 0x40]) + xy(width / 640, height / Y_SCALE))
        self.type = None
        self.color(15)
        self.data.extend(b'\x1bC' + bytes([code]) + b'\x0e')
        pen = Cell()
        draw(pen)
        self.data.extend(pen.data + b'\x1bE\x0e')
        self.brush = self.ink = None
        return self

    def stamp(self, x, y, code, size, ink, count=1):
        """Draw DRCS characters at a field size, lower left corner at (x, y)."""
        width, height = size
        self.color(ink)
        key = (width, height, False)
        if key != self.type:
            self.cmd(0x22, bytes([0x40, 0x40]) + xy(width / 640, height / Y_SCALE))
            self.type = key
        self.pos(x, y)
        self.data.extend(SS2 + bytes([code]))
        if count > 1:
            self.data.extend(b'\x1bF' + bytes([0x40 | (count - 1)]))
        return self

    def weave(self, letter, mask, draw):
        """Define fill pattern A to D (pattern 4 to 7) at a mask size."""
        size = xy(mask[0] / 640, mask[1] / Y_SCALE)
        self.color(15).cmd(0x23, b'\x40' + size)
        self.data.extend(b'\x1bD' + letter.encode() + b'\x0e')
        pen = Cell()
        draw(pen)
        self.data.extend(pen.data + b'\x1bE\x0e')
        self.fill = self.brush = self.ink = None
        return self

    def routine(self, name, body):
        """Define macro `name` from a fragment drawn with relative commands."""
        self.data.extend(b'\x1b@' + bytes([name]) + b'\x0e' + body.data + b'\x1bE\x0e')
        return self

    def run(self, name, x, y, ink=None):
        if ink is not None:
            self.color(ink)
        self.pos(x, y)
        self.data.extend(SS3 + bytes([name]))
        return self

    # -- time -------------------------------------------------------------
    def pause(self, tenths):
        while tenths > 0:
            step = min(63, tenths)
            self.cmd(0x3d, bytes([0x5c, 0x40 | step]))
            tenths -= step
        return self

    def flash(self, entry, other, on=5, off=5, delay=1):
        """Entry shows the other entry's colour for `on` tenths, its own for `off`.

        A blink begins in its ON interval, and a start delay counts from the
        blink defined before it.  So that a still of the page shows every
        entry in its own colour, the first flash of a page is preceded by a
        blink of the background to itself, which changes nothing, and every
        real blink starts at least a tenth after it.
        """
        if not self.blinking:
            self.blinking = True
            self.color(0).cmd(0x3f, bytes([0x40, 0x41, 0x41, 0x40]))
        self.color(entry)
        return self.cmd(0x3f, bytes([0x40 | other << 2, 0x40 | on, 0x40 | off, 0x40 | max(1, delay)]))

    def stream(self):
        return bytes(self.data) + b'\x0f'


class Cell:
    """Drawing inside a DRCS character or a fill pattern: 0..100 on each axis,
    y upward, 100 being the longer side of the field."""

    def __init__(self):
        self.data = bytearray()

    def _pt(self, x, y):
        return xy(min(x, 99.9) / 100, min(y, 99.9) / 100)

    def cut(self):
        """What is drawn next clears the pels it covers (drawing in entry 0)."""
        self.data.extend(b'\x3e\x40')
        return self

    def ink(self):
        """What is drawn next sets pels again."""
        self.data.extend(b'\x3e\x7c')
        return self

    def box(self, x, y, w, h):
        self.data.extend(b'\x33' + self._pt(x, y) + self._pt(w, h))
        return self

    def poly(self, points):
        data = self._pt(*points[0])
        for a, b in zip(points, points[1:]):
            data += xy((b[0] - a[0]) / 100, (b[1] - a[1]) / 100)
        self.data.extend(b'\x37' + data)
        return self

    def disc(self, x, y, radius):
        self.data.extend(b'\x2f' + self._pt(x - radius, y) + self._pt(2 * radius, 0))
        return self


class Fragment(Writer):
    """Relative drawing for a macro body."""

    def fan(self, steps, fill=True):
        self.cmd(0x35 if fill else 0x34,
                 b''.join(xy(dx / 640, -dy / Y_SCALE) for dx, dy in steps))
        return self


def furrow_mark(cell):
    """The mark of the farm service on pages 207 and 208: a low sun over furrows that run to it."""
    cell.disc(50, 54, 30)
    cell.box(0, 0, 99, 50)
    cell.cut()
    cell.box(0, 46, 99, 5)
    for left, right in [(12, 24), (38, 46), (56, 64), (78, 90)]:
        cell.poly([(left, 0), (right, 0), (51, 46), (49, 46)])
    cell.ink()


def save(script, build):
    (ROOT / 'out' / (Path(script).stem + '.nap')).write_bytes(build().stream())
