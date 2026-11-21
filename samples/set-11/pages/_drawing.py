"""Screen coordinates and stream framing for the illustrated plates."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from encoder import Page as Encoder, xy, Y_SCALE

RESET = b'\x0e\x20\x7f\x7f'


class Plate(Encoder):
    def __init__(self, colours):
        super().__init__()
        palette = colours.split()
        if not 1 <= len(palette) <= 16:
            raise ValueError('Expected one to sixteen colours')
        self.data.extend(RESET + b'\x1b(B\x1b)W\x1b*z\x1b+}')
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

    def stream(self):
        return bytes(self.data) + b'\x0f'


def save(script, build):
    (ROOT / 'out' / (Path(script).stem + '.nap')).write_bytes(build().stream())
