import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from math import hypot

from encoder import Page, save

META = dict(title='A Room After Dark', purpose='An illuminated title for an imagined all-night reading room',
            style='Cobalt and apricot marquee with inline lettering and phased lamps',
            techniques=['proportional TEXT', 'optically spaced vector capitals', 'layered tube strokes', 'palette BLINK'],
            animated=True)


# Centerlines and advances for the sign lettering on an 80-unit cap grid.
TUBES = {
    'O': (73, [[(10, 14), (23, 2), (51, 2), (64, 14), (64, 66),
                (51, 78), (23, 78), (10, 66), (10, 14)]]),
    'P': (67, [[(10, 78), (10, 2), (47, 2), (59, 14), (59, 29),
                (47, 40), (10, 40)]]),
    'E': (64, [[(56, 2), (10, 2), (10, 78), (56, 78)], [(10, 40), (48, 40)]]),
    'N': (74, [[(10, 78), (10, 2), (64, 78), (64, 2)]]),
    'L': (59, [[(10, 2), (10, 78), (52, 78)]]),
    'A': (76, [[(9, 78), (34, 2), (42, 2), (67, 78)], [(19, 52), (57, 52)]]),
    'T': (70, [[(8, 2), (62, 2)], [(35, 2), (35, 78)]]),
}


def round_bends(path, reach=7):
    closed = path[0] == path[-1]
    vertices = path[:-1] if closed else path
    rounded = []
    for index, (x, y) in enumerate(vertices):
        if not closed and index in (0, len(vertices)-1):
            rounded.append((x, y))
            continue
        ends = []
        for nx, ny in (vertices[index-1], vertices[(index+1) % len(vertices)]):
            distance = hypot(nx-x, ny-y)
            amount = min(reach, distance/3) / distance
            ends.append((x + amount*(nx-x), y + amount*(ny-y)))
        start, end = ends
        for step in range(7):
            t = step/6
            rounded.append(((1-t)**2*start[0] + 2*t*(1-t)*x + t*t*end[0],
                            (1-t)**2*start[1] + 2*t*(1-t)*y + t*t*end[1]))
    if closed:
        rounded.append(rounded[0])
    return rounded


def sign(p, word, top, scale, height):
    kerning = {'LA': -5, 'AT': -8}
    layout = []
    advance = 0
    for previous, letter in zip(' '+word, word):
        advance += kerning.get(previous+letter, 0)
        width, strokes = TUBES[letter]
        layout.extend([[(advance + px, py) for px, py in path] for path in strokes])
        advance += width
    left = min(x for path in layout for x, _ in path)
    right = max(x for path in layout for x, _ in path)
    center = (left + right) / 2
    paths = [round_bends([(320+(px-center)*scale, top+py*height) for px, py in path])
             for path in layout]
    for ink, radius in ((4, 11), (8, 7.5), (1, 4), (6, 1.5)):
        for path in paths:
            for (ax, ay), (bx, by) in zip(path, path[1:]):
                dx, dy = bx-ax, by-ay
                length = hypot(dx, dy)
                nx, ny = -dy*radius/length, dx*radius/length
                p.polygon([(ax+nx, ay+ny), (bx+nx, by+ny),
                           (bx-nx, by-ny), (ax-nx, ay-ny)], ink)
            for px, py in dict.fromkeys(path):
                p.circle(px, py, radius, ink, fill=True)


def build():
    p = Page('192249 ffd4a7 313e79 8796cd 454177 f4ae89 fff4df 6977ae 977385 f4ae89')
    p.polygon([(57, 82), (583, 82), (602, 101), (602, 365),
               (583, 385), (57, 385), (38, 365), (38, 101)], 7)
    p.polygon([(61, 89), (579, 89), (594, 104), (594, 360),
               (579, 376), (61, 376), (46, 360), (46, 104)], 0)
    p.polygon([(69, 97), (571, 97), (586, 112), (586, 351),
               (571, 367), (69, 367), (54, 351), (54, 112)], 2)
    p.line([(61, 89), (579, 89), (594, 104)], 3, 2)
    p.text(42, 63, 'A room after dark', 39, 53)
    sign(p, 'OPEN', 126, 1.49, 1.20)
    sign(p, 'LATE', 263, 1.11, .87)
    for x, direction in ((77, 1), (563, -1)):
        p.line([(x+28*direction, 112), (x, 112), (x, 351),
                (x+28*direction, 351)], 4, 3)
        for index, y in enumerate(range(122, 350, 25)):
            p.circle(x, y, 6, 0, fill=True)
            p.circle(x, y, 3, 5 if (index + (direction == 1)) % 2 else 9, fill=True)
    for x, ink in ((307, 9), (320, 5), (333, 9)):
        p.circle(x, 242, 4.5, 0, fill=True)
        p.circle(x, 242, 2.7, ink, fill=True)
    for ink, delay in ((5, 0), (9, 8)):
        p.ink(ink)
        p.command(0x3f, bytes((64+7*4, 64+8, 64+8, 64+delay)))
    p.text(43, 451, 'Read until dawn', 32, 44)
    return p


if __name__ == '__main__':
    save(__file__, build())
