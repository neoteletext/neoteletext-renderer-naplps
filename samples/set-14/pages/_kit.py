"""Shared drawing helpers for the videotex-as-promised pictures (set 14).

Builds on the plate writer in _drawing.py. Everything is on the 640 x 480
design canvas; y grows downward and text y is the baseline.
"""
import math
from _drawing import Plate, save, xy, Y_SCALE, Encoder

# Advance of each proportional glyph as a fraction of the cell width, measured
# from the stroke font (every other printable character is 0.75).
_ADVANCE = {' ': 1.0, '!': .25, '"': .5, '#': 1.0, '$': .75, '%': 1.0, '&': 1.0, "'": .25,
            '(': .5, ')': .5, ',': .375, '.': .25, '/': 1.0, ':': .25, ';': .375, '[': .5,
            '\\': 1.0, ']': .5, '_': 1.0, '`': .5, 'f': .625, 'i': .5, 'j': .625, 'l': .5,
            '{': .5, '|': .25, '}': .5, '~': 1.0}

# Text sizes (cell width, cell height) that stay clear at 480 x 460.
SMALL = (12, 18)
BODY = (14, 21)
LARGE = (18, 26)
HEAD = (22, 32)
BIG = (30, 44)
HUGE = (44, 64)


def text_width(s, size):
    return sum(_ADVANCE.get(c, .75) for c in s) * size[0]


class Screen(Plate):
    """A Plate with text alignment, hatching, stacked bands and chrome."""

    def say(self, x, y, s, size=BODY, ink=1, align='l', shade=None):
        """Proportional text; align 'l', 'c' or 'r' about x. shade draws a drop shadow."""
        width = text_width(s, size)
        left = x if align == 'l' else x - width / 2 if align == 'c' else x - width
        if shade is not None:
            self.text(left + 2, y + 2, s, size[0], size[1], shade, prop=True)
        return self.text(left, y, s, size[0], size[1], ink, prop=True)

    def mono(self, x, y, s, size=BODY, ink=1, align='l'):
        width = len(s) * size[0]
        left = x if align == 'l' else x - width / 2 if align == 'c' else x - width
        return self.text(left, y, s, size[0], size[1], ink, prop=False)

    def fillrect(self, x, y, w, h, ink, pattern=0, pel=3):
        """Rectangle with a fill pattern (1 vertical, 2 horizontal, 3 cross hatch)."""
        self.color(ink)
        if pattern:
            self.cmd(0x23, bytes([0x40 | pattern << 3]))
            self.pel(pel)
        else:
            self.pel(1)
        self.cmd(0x33, xy(x / 640, (480 - y - h) / Y_SCALE) + xy(w / 640, h / Y_SCALE))
        if pattern:
            self.cmd(0x23, b'\x40')
        return self

    def fillpoly(self, pts, ink, pattern=0, pel=3):
        self.color(ink)
        if pattern:
            self.cmd(0x23, bytes([0x40 | pattern << 3]))
            self.pel(pel)
        else:
            self.pel(1)
        first = pts[0]
        data = xy(first[0] / 640, (480 - first[1]) / Y_SCALE)
        for a, b in zip(pts, pts[1:]):
            data += xy((b[0] - a[0]) / 640, (a[1] - b[1]) / Y_SCALE)
        self.cmd(0x37, data)
        if pattern:
            self.cmd(0x23, b'\x40')
        return self

    def frame(self, x, y, w, h, ink, width=2):
        self.color(ink).pel(width)
        return self.cmd(0x32, xy(x / 640, (480 - y - h) / Y_SCALE) + xy(w / 640, h / Y_SCALE))

    def box(self, x, y, w, h, fill, edge=None, width=2):
        self.rect(x, y, w, h, fill)
        if edge is not None:
            self.frame(x, y, w, h, edge, width)
        return self

    def bevel(self, x, y, w, h, fill, light, dark, depth=3):
        """A raised key: light top-left, dark bottom-right."""
        self.rect(x, y, w, h, dark)
        self.rect(x, y, w - depth, h - depth, light)
        self.rect(x + depth, y + depth, w - 2 * depth, h - 2 * depth, fill)
        return self

    def dashed_frame(self, x, y, w, h, ink, width=3):
        """An outline in the dashed line texture (a coupon edge)."""
        self.color(ink)
        self.cmd(0x23, bytes([0x40 | 2]))
        self.pel(width)
        self.cmd(0x32, xy(x / 640, (480 - y - h) / Y_SCALE) + xy(w / 640, h / Y_SCALE))
        self.cmd(0x23, b'\x40')
        return self

    def ring(self, x, y, radius, ink, width=2):
        self.color(ink).pel(width)
        return self.cmd(0x2e, xy((x - radius) / 640, (480 - y) / Y_SCALE) + xy(2 * radius / 640, 0))

    def bands(self, x, y, w, heights, inks):
        for h, ink in zip(heights, inks):
            self.rect(x, y, w, h, ink)
            y += h
        return self

    def polyline(self, pts, ink, width=2):
        return self.line(pts, ink, width)

    def burst(self, x, y, outer, inner, points, ink, turn=0):
        """A starburst polygon."""
        pts = []
        for i in range(points * 2):
            r = outer if i % 2 == 0 else inner
            a = math.radians(turn + i * 180 / points)
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
        return self.poly(pts, ink)

    def keycap(self, x, y, label, ink, text_ink, size=LARGE, radius=17):
        self.disc(x, y, radius, ink)
        return self.say(x, y + size[1] * .35, label, size, text_ink, 'c')

    def call(self, num, x=None, y=None, c=None):
        super().call(num, x, y, c)
        self.ink = self.width = None  # the macro changed the colour and pel behind our back
        return self

    def stream(self):
        return bytes(self.data) + b'\x0f'


def chrome(p, service, page, top_ink, text_ink, prompt, prompt_ink, prompt_text, height=44,
           size=LARGE, page_ink=None):
    """A service band across the top and a prompt strip along the foot."""
    p.rect(0, 0, 640, height, top_ink)
    p.say(14, height - 12, service, size, text_ink)
    p.say(626, height - 12, str(page), size, page_ink if page_ink is not None else text_ink, 'r')
    p.rect(0, 480 - 34, 640, 34, prompt)
    p.say(14, 480 - 10, prompt_text, BODY, prompt_ink)
    return p



class Scaled:
    """Draws through a Screen with every coordinate scaled about an anchor,
    so one drawing function serves several sizes."""

    def __init__(self, screen, anchor_x, anchor_y, scale):
        self.screen, self.ax, self.ay, self.s = screen, anchor_x, anchor_y, scale

    def _pt(self, x, y):
        return (self.ax + (x - self.ax) * self.s, self.ay + (y - self.ay) * self.s)

    def _pts(self, pts):
        return [self._pt(x, y) for x, y in pts]

    def rect(self, x, y, w, h, c):
        px, py = self._pt(x, y)
        return self.screen.rect(px, py, w * self.s, h * self.s, c)

    def poly(self, pts, c):
        return self.screen.poly(self._pts(pts), c)

    def disc(self, x, y, r, c):
        px, py = self._pt(x, y)
        return self.screen.disc(px, py, r * self.s, c)

    def ellipse(self, x, y, rx, ry, c):
        px, py = self._pt(x, y)
        return self.screen.ellipse(px, py, rx * self.s, ry * self.s, c)

    def line(self, pts, c, w=1):
        return self.screen.line(self._pts(pts), c, max(1, round(w * self.s)))

    def ring(self, x, y, r, c, w=2):
        px, py = self._pt(x, y)
        return self.screen.ring(px, py, r * self.s, c, max(1, round(w * self.s)))

    def frame(self, x, y, w, h, c, width=2):
        px, py = self._pt(x, y)
        return self.screen.frame(px, py, w * self.s, h * self.s, c, max(1, round(width * self.s)))

    def say(self, x, y, text, size, ink, align='l'):
        px, py = self._pt(x, y)
        return self.screen.say(px, py, text, size, ink, align)


def define_character(screen, code, width, height, shapes):
    """Define a DRCS character in a width x height pixel field (spec: DEF DRCS,
    drawn on a unit square whose longer side is 1). shapes use pixel coordinates
    with the origin at the top left of the field: ('poly', pts), ('disc', x, y, r),
    ('hole', x, y, r) which clears, ('line', pts, thickness) and ('cut', pts, thickness), a line that clears."""
    longer = max(width, height)

    def design(x, y):
        return (x / longer * 640, 480 - (height - y) / longer * Y_SCALE)

    def points(pts):
        return [design(x, y) for x, y in pts]

    def circle(x, y, r):
        return [design(x + r * math.cos(i * math.pi / 8), y + r * math.sin(i * math.pi / 8)) for i in range(16)]

    frag = Encoder()
    for shape in shapes:
        kind = shape[0]
        if kind == 'poly':
            frag.poly(points(shape[1]), 1)
        elif kind == 'disc':
            frag.poly(circle(*shape[1:]), 1)
        elif kind == 'hole':
            frag.poly(circle(*shape[1:]), 0)
        elif kind == 'line':
            frag.line(points(shape[1]), 1, max(1, round(shape[2] / longer * 640)))
        elif kind == 'cut':
            frag.line(points(shape[1]), 0, max(1, round(shape[2] / longer * 640)))
    screen.data.extend(b'\x1b+{')  # DRCS into G3, reached with SS3
    screen.cmd(0x22, b'\x40\x40' + xy(width / 640, height / Y_SCALE))
    screen.color(1)
    screen.data.extend(b'\x1bC' + bytes([code]) + b'\x0e' + bytes(frag.data) + b'\x1bE\x0e')
    screen.ink = screen.width = None  # the definition changed the colour and pel
    return screen


def character(screen, code, x, y, width, height, ink):
    """Set a DRCS character with its baseline-left corner at (x, y)."""
    screen.mosaic(x, y, [code], width, height, ink)
    return screen


def define_texture(screen, name, tile, polygons):
    """Define fill pattern 4 + (name - 0x41) on a square tile of `tile` design
    pixels; polygons are lists of (u, v) in the unit square, y up."""
    screen.cmd(0x23, b'\x40' + xy(tile / 640, tile / Y_SCALE))
    frag = Encoder()
    frag.pel(1)
    frag.color(1)
    for pts in polygons:
        frag.poly([(u * 640, 480 - v * Y_SCALE) for u, v in pts], 1)
    screen.data.extend(b'\x1bD' + bytes([name]) + b'\x0e' + bytes(frag.data) + b'\x1bE\x0e')
    screen.ink = screen.width = None
    return screen


def pattern_rect(screen, x, y, w, h, ink, pattern, tile):
    """Fill a rectangle with a custom pattern (4 to 7) tiled every `tile` pixels."""
    screen.color(ink)
    screen.cmd(0x23, bytes([0x40 | pattern << 3]) + xy(tile / 640, tile / Y_SCALE))
    screen.cmd(0x33, xy(x / 640, (480 - y - h) / Y_SCALE) + xy(w / 640, h / Y_SCALE))
    screen.cmd(0x23, b'\x40' + xy(1 / 16, 1 / 16))
    return screen


def clip_polygon(points, left, top, right, bottom):
    """Sutherland-Hodgman clip of a polygon to a rectangle (y down)."""
    def clip(pts, inside, cross):
        out = []
        for i, current in enumerate(pts):
            previous = pts[i - 1]
            if inside(current):
                if not inside(previous):
                    out.append(cross(previous, current))
                out.append(current)
            elif inside(previous):
                out.append(cross(previous, current))
        return out

    def at_x(x):
        return lambda a, b: (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))

    def at_y(y):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]), y)

    pts = list(points)
    for inside, cross in ((lambda q: q[0] >= left, at_x(left)), (lambda q: q[0] <= right, at_x(right)),
                          (lambda q: q[1] >= top, at_y(top)), (lambda q: q[1] <= bottom, at_y(bottom))):
        if pts:
            pts = clip(pts, inside, cross)
    return pts


def rays(screen, cx, cy, count, ink, left, top, right, bottom, turn=0.0, fraction=.5):
    """Alternate wedges of `ink` radiating from (cx, cy), clipped to a rectangle."""
    reach = 1500
    for i in range(count):
        a = math.radians(turn + i * 360 / count)
        b = a + math.radians(360 / count * fraction)
        wedge = clip_polygon([(cx, cy), (cx + reach * math.cos(a), cy + reach * math.sin(a)),
                              (cx + reach * math.cos(b), cy + reach * math.sin(b))], left, top, right, bottom)
        if len(wedge) >= 3:
            screen.poly(wedge, ink)
