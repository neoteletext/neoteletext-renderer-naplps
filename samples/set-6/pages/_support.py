"""A 640 × 480 design space over the set's NAPLPS writer."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from encoder import Page as Writer, Y_SCALE, xy

RESET = b'\x0e\x20\x7f\x7f'


class Page(Writer):
    def __init__(self, palette):
        super().__init__()
        self.data.extend(RESET + b'\x1b(B\x1b)W\x1b*z\x1b+{')
        self._ink = self._pel = None
        self.pel(1)
        for index, colour in enumerate(palette + [palette[-1]] * (16 - len(palette))):
            self.set_palette(index, colour)
        self.rect(0, 0, 639.6, 479.6, 0)

    def color(self, index):
        if index != self._ink:
            self._ink = index
            super().color(index)
        return self

    def pel(self, width):
        if width != self._pel:
            self._pel = width
            super().pel(width)
        return self

    def circle(self, x, y, radius, ink, fill=True):
        self.color(ink).pel(1)
        return self.cmd(0x2f if fill else 0x2e,
                        xy((x - radius) / 640, (480 - y) / Y_SCALE)
                        + xy(2 * radius / 640, 0))

    def mask(self, operation, code, fragment):
        self.data.extend(operation + bytes([code]) + b'\x0e' + fragment.data + b'\x1bE\x0e')
        self._ink = self._pel = None

    def stream(self):
        return bytes(self.data) + b'\x0f'


def save(script, page):
    (ROOT / 'out' / (Path(script).stem + '.nap')).write_bytes(page.stream())
