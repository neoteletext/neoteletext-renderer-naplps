"""Seven-bit NAPLPS primitives on a 640 by 480 design grid."""
from math import cos, pi, sin
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESET = b'\x0e\x20\x7f\x7f'
SETS = b'\x1b(B\x1b)W\x1b+{'
Y_UNIT = 614.4


def coordinate(value):
    return max(-2048, min(2047, round(value * 2048)))


def pair(x, y):
    values = [coordinate(value) & 4095 for value in (x, y)]
    return bytes(64 | ((values[0] >> bit & 7) << 3) | (values[1] >> bit & 7)
                 for bit in (9, 6, 3, 0))


def palette_commands(index, hex_rgb):
    channels = [int(hex_rgb[i:i + 2], 16) for i in (2, 0, 4)]
    color = bytes(64 | sum(((channel >> bit) & 1) << (5 - i)
                           | ((channel >> (bit - 1)) & 1) << (2 - i)
                           for i, channel in enumerate(channels))
                  for bit in (7, 5, 3, 1))
    return bytes((0x3e, 64 + index * 4, 0x3c)) + color


class Page:
    def __init__(self, colors):
        palette = colors.split()
        self.data = bytearray(RESET + SETS)
        self.pen(1)
        for index in range(16):
            self.data.extend(palette_commands(index, palette[min(index, len(palette) - 1)]))
        self.rect(0, 0, 640, 480, 0)

    def command(self, code, operands=b''):
        self.data.append(code)
        self.data.extend(operands)

    def ink(self, index):
        self.command(0x3e, bytes((64 + index * 4,)))

    def pen(self, width):
        self.command(0x21, b'L' + pair(width / 640, width / Y_UNIT))

    @staticmethod
    def point(x, y):
        return pair(x / 640, (480 - y) / Y_UNIT)

    def rect(self, x, y, w, h, ink):
        self.ink(ink)
        self.command(0x33, self.point(x, y + h) + pair(w / 640, h / Y_UNIT))

    def line(self, points, ink, width=1):
        self.ink(ink)
        self.pen(width)
        self.command(0x24, self.point(*points[0]))
        self.command(0x28, b''.join(self.point(*point) for point in points[1:]))

    def polygon(self, points, ink):
        self.ink(ink)
        self._polygon([(x / 640, (480 - y) / Y_UNIT) for x, y in points])

    def _polygon(self, points):
        # Snap vertices before differencing so rounding cannot accumulate along a contour.
        vertices = [(coordinate(x) / 2048, coordinate(y) / 2048) for x, y in points]
        offsets = (pair(bx - ax, by - ay)
                   for (ax, ay), (bx, by) in zip(vertices, vertices[1:]))
        self.command(0x37, pair(*vertices[0]) + b''.join(offsets))

    def circle(self, x, y, r, ink, fill=False, width=1):
        self.ink(ink)
        self.pen(width)
        self.command(0x2f if fill else 0x2e, self.point(x-r, y) + pair(2*r/640, 0))

    def text(self, x, y, value, width, height, ink=1, *, spacing=3, path=0,
             rotation=0, drcs=False):
        self.ink(ink)
        self.field(width / 640, height / Y_UNIT, spacing)
        if path or rotation:
            self.command(0x22, bytes((64 | spacing << 4 | path << 2 | rotation, 64)))
        self.command(0x24, self.point(x, y))
        if drcs:
            self.data.extend(b''.join(b'\x1d' + bytes((code,)) for code in value.encode('ascii')))
        else:
            self.data.extend(b'\x0f' + value.encode('ascii') + b'\x0e')

    def field(self, width, height, spacing=0, path=0, rotation=0):
        self.command(0x22, bytes((64 | spacing << 4 | path << 2 | rotation, 64))
                     + pair(width, height))

    def glyph(self, character, *contours):
        """Define a DRCS outline on a 100 × 100 grid. Contours can clear ink."""
        self.field(.125, .125)
        self.pen(1)
        self.ink(1)
        self.data.extend(b'\x1bC' + character.encode('ascii') + b'\x0e')
        for ink, points in contours:
            self.ink(ink)
            self._polygon([(x / 100, (100 - y) / 100) for x, y in points])
        self.data.extend(b'\x1bE\x0e')

    def stream(self):
        return bytes(self.data) + b'\x0f'


def box(x, y, w, h):
    return [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]


def oval(x, y, rx, ry, steps=20):
    return [(x + rx*cos(i*2*pi/steps), y + ry*sin(i*2*pi/steps)) for i in range(steps)]


def save(script, page):
    (ROOT / 'out' / (Path(script).stem + '.nap')).write_bytes(page.stream())
