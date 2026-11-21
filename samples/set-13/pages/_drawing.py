"""Screen coordinates, text, programmable characters and stream framing for the set-13 pictures."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from encoder import Page as Encoder, xy, Y_SCALE

RESET = b'\x0e\x20\x7f\x7f'
# A programmable character is drawn on a 100 by 100 grid; its contours are fractions of its cell.
GLYPH_GRID = 100
# The programmable character's cell, as a fraction of the 640 by 480 design canvas (set-10 uses the same cell).
GLYPH_CELL = 0.125


class Plate(Encoder):
    def __init__(self, colours):
        super().__init__()
        palette = colours.split()
        if not 1 <= len(palette) <= 16:
            raise ValueError('Expected one to sixteen colours')
        # G3 is designated to the programmable characters' set (\x1b+{), as set-10 does; the renderer draws
        # nothing for them under the set-11 designation (\x1b+}).
        self.data.extend(RESET + b'\x1b(B\x1b)W\x1b*z\x1b+{')
        self.ink = self.width = None
        self.pel(1)
        for index, colour in enumerate(palette + [palette[-1]] * (16 - len(palette))):
            self.set_palette(index, colour)
        self.rect(0, 0, 639.6, 479.6, 0)

    def color(self, index):
        if index != self.ink:
            super().color(index)
            self.ink = index
        return self

    def pel(self, width):
        if width != self.width:
            super().pel(width)
            self.width = width
        return self

    def disc(self, x, y, radius, ink, fill=True):
        self.color(ink).pel(1)
        return self.cmd(0x2f if fill else 0x2e,
                        xy((x - radius) / 640, (480 - y) / Y_SCALE)
                        + xy(2 * radius / 640, 0))

    def title(self, x, y, caption, ink, width=22, height=36):
        self.pel(2).text(x, y, caption, width, height, ink, prop=False)

    def glyph(self, character, *contours):
        """Define a programmable character from (ink, points) contours on the 100 by 100 grid."""
        self.cmd(0x22, bytes([0x40, 0x40]) + xy(GLYPH_CELL, GLYPH_CELL))
        self.pel(1)
        self.data.extend(b'\x1bC' + character.encode('ascii') + b'\x0e')
        for ink, points in contours:
            # The renderer takes the ink from the last colour select, which the definition has just ended, so select it again.
            self.ink = None
            self.color(ink)
            fractions = [(x / GLYPH_GRID, (GLYPH_GRID - y) / GLYPH_GRID) for x, y in points]
            data = xy(*fractions[0])
            for (ax, ay), (bx, by) in zip(fractions, fractions[1:]):
                data += xy(bx - ax, by - ay)
            self.cmd(0x37, data)
        self.data.extend(b'\x1bE\x0e')
        return self

    def programmable(self, x, y, s, w, h, c=None):
        """Draw a run of programmable characters, each named by its one-letter code."""
        if c is not None:
            # A definition ends in its own colour state, so the run's colour is selected again.
            self.ink = None
            self.color(c)
        self.cmd(0x22, bytes([0x40, 0x40]) + xy(w / 640, h / Y_SCALE))
        self.pos(x, y)
        self.data.extend(b''.join(b'\x1d' + bytes([code]) for code in s.encode('ascii')))
        return self

    def along(self, points, s, w, h, c=None, prop=True):
        """Set each character of s at its own point, so a caption can follow a curve."""
        if len(points) != len(s):
            raise ValueError('One point for each character')
        for (x, y), letter in zip(points, s):
            self.text(x, y, letter, w, h, c, prop=prop)
        return self

    def stream(self):
        return bytes(self.data) + b'\x0f'


def save(script, build):
    (ROOT / 'out' / (Path(script).stem + '.nap')).write_bytes(build().stream())
