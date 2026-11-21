"""Native drawing conveniences in a 640 by 480 design space."""
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from encoder import Page as Writer, Y_SCALE, xy

RESET = b'\x0e\x20\x7f\x7f'
SETUP = b'\x1b(B\x1b)W\x1b*z\x1b+{'


class Page(Writer):
    def __init__(self, colours):
        super().__init__()
        self.data.extend(RESET + SETUP)
        self.ink = self.width = None
        palette = colours.split()
        palette.extend([palette[0]] * (16 - len(palette)))
        self.pel(1)
        for index, colour in enumerate(palette):
            self.set_palette(index, colour)
        self.rect(0, 0, 639.7, 479.7, 0)

    def color(self, index):
        if index != self.ink:
            self.ink = index
            super().color(index)
        return self

    def pel(self, width):
        if width != self.width:
            self.width = width
            super().pel(width)
        return self

    def disc(self, x, y, r, colour, fill=True):
        self.color(colour).pel(1).cmd(
            0x2f if fill else 0x2e,
            xy((x-r)/640, (480-y)/Y_SCALE) + xy(2*r/640, 0))
        return self

    def label(self, x, y, value, size=28, colour=1):
        return self.text(x, y, value, size * 0.69, size, colour)

    def arrow(self, start, end, colour, width=3, head=13):
        self.line([start, end], colour, width)
        x, y = end
        a = math.atan2(y-start[1], x-start[0])
        self.poly([end, (x-head*math.cos(a-.46), y-head*math.sin(a-.46)),
                   (x-head*math.cos(a+.46), y-head*math.sin(a+.46))], colour)
        return self

    def stream(self):
        return bytes(self.data) + b'\x0f'


def save(script, page):
    (ROOT / 'out' / (Path(script).stem + '.nap')).write_bytes(page.stream())
