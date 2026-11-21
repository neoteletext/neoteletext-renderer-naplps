"""Drawing helpers for the game screens."""
from pathlib import Path
from . import Page as Writer, Y_SCALE, xy

ROOT = Path(__file__).resolve().parents[1]
RESET = b'\x0e\x20\x7f\x7f'
SETS = b'\x1b(B\x1b)W\x1b*z\x1b+}'


class Screen(Writer):
    def __init__(self, colours):
        super().__init__()
        palette = colours.split()
        self.data.extend(RESET + SETS)
        self.ink = self.brush = None
        self.pel(1)
        for index in range(16):
            self.set_palette(index, palette[min(index, len(palette) - 1)])
        self.rect(0, 0, 639.6, 479.6, 0)

    def color(self, index):
        if self.ink != index:
            super().color(index)
            self.ink = index
        return self

    def pel(self, width):
        if self.brush != width:
            super().pel(width)
            self.brush = width
        return self

    def disk(self, x, y, radius, ink, fill=True):
        self.color(ink).pel(1)
        return self.cmd(0x2f if fill else 0x2e,
                        xy((x - radius) / 640, (480 - y) / Y_SCALE)
                        + xy(radius * 2 / 640, 0))

    def hatch(self, name, fragment, width, height):
        size = xy(width / 640, height / Y_SCALE)
        self.color(1).cmd(0x23, b'\x40' + size)
        self.data.extend(b'\x1bD' + name + b'\x0e' + fragment.data + b'\x1bE\x0e')
        return self.cmd(0x23, bytes([0x60 + (name[0] - 65) * 8]) + size)

    def stream(self):
        return bytes(self.data) + b'\x0f'


def save(source, screen):
    (ROOT / 'out' / (Path(source).stem + '.nap')).write_bytes(screen.stream())
