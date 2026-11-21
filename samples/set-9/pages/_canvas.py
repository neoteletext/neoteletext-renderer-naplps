"""Shared protocol setup and a 640 × 480 drawing space."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from encoder import Page as Encoder, Y_SCALE, xy

RESET = b'\x0e\x20\x7f\x7f'
SETS = b'\x1b(B\x1b)W\x1b*z\x1b+{'


class Canvas(Encoder):
    def __init__(self, colours):
        super().__init__()
        palette = colours.split()
        if not 1 <= len(palette) <= 16:
            raise ValueError('Expected one to sixteen palette colours')
        self.data.extend(RESET + SETS)
        self.pel(1)
        for i in range(16):
            self.set_palette(i, palette[min(i, len(palette) - 1)])
        self.rect(0, 0, 639.7, 479.7, 0)

    def circle(self, x, y, radius, ink, fill=True, width=1):
        self.color(ink).pel(width)
        return self.cmd(0x2f if fill else 0x2e,
                        xy((x - radius) / 640, (480 - y) / Y_SCALE)
                        + xy(2 * radius / 640, 0))

    def stream(self):
        return bytes(self.data) + b'\x0f'


def write_page(script, page):
    out = ROOT / 'out'
    out.mkdir(exist_ok=True)
    (out / (Path(script).stem + '.nap')).write_bytes(page.stream())
