from random import Random

from _support import Page, Y_SCALE, save

META = dict(title='Fault Line', purpose='A poster for an imagined letterpress exhibition',
            style='Fractured block lettering in bone, oxide red and carbon',
            techniques=['polygonal letterforms', 'overpainting', 'proportional TEXT'],
            animated=False)

# Letter components in a local 90 × 166 design space.
LETTERS = [
    [[(0, 0), (89, 0), (89, 29), (30, 29), (30, 66), (74, 66),
      (74, 96), (30, 96), (30, 166), (0, 166)]],
    [[(0, 166), (28, 0), (61, 0), (90, 166), (60, 166), (52, 115),
      (37, 115), (29, 166)]],
    [[(0, 0), (30, 0), (30, 130), (38, 137), (52, 137), (60, 130),
      (60, 0), (90, 0), (90, 143), (68, 166), (22, 166), (0, 143)]],
    [[(0, 0), (31, 0), (31, 136), (90, 136), (90, 166), (0, 166)]],
    [[(0, 0), (90, 0), (90, 30), (60, 30), (60, 166), (29, 166),
      (29, 30), (0, 30)]],
]


def build():
    p = Page('e7d8ba 252022 aa3026 ff6945 f8ecd2 6d3b36'
             ' d9c6a1 ee9770 8e291f 3a3030 d1b18a e0ccab c04130 f3e3c7 76231d'.split())
    rng = Random(123)

    def rupture(x):
        return 309 - x * .22

    # Long offsets carry the shear. Irregular short fibres break its edge.
    def jog(x):
        return sum(step * max(0, 1 - abs(x - centre) / width)
                   for centre, width, step in [(126, 58, 10), (287, 38, -8),
                                               (430, 56, 12), (544, 36, -8)])

    edge = [(x, rupture(x) + jog(x) + rng.uniform(-1.8, 1.8))
            for x in [*range(0, 640, 4), 639.6]]
    # Snap absolute vertices before encoding their relative deltas, so
    # rounding along the long tear cannot move the page edges.
    def snap(value, scale):
        return round(value / scale * 2048) * scale / 2048

    def fold(x):
        return sum(height * max(0, 1 - abs(x - centre) / width) ** 1.4
                   for centre, width, height in [(124, 58, 12), (297, 44, 9),
                                                 (438, 59, 15), (554, 41, 10)])

    for depth, ink in [(0, 6), (2, 4), (4, 10), (6, 7), (10, 14), (15, 2)]:
        layer = [(x, y + depth * (.72 + fold(x) / 16)) for x, y in edge]
        layer += [(639.6, 479.8), (320, 479.8), (0, 479.8)]
        p.poly([(snap(x, 640), snap(y, Y_SCALE)) for x, y in layer], ink)
    for centre, side, span in [(72, 1, 45), (141, -1, 61), (286, 1, 53),
                               (431, -1, 46), (548, 1, 54), (589, -1, 35)]:
        x, y = edge[centre // 4]
        y += 10 if side > 0 else 0
        points = [(x, y), (x + span * .22, y + side * 9),
                  (x + span * .45, y + side * 12),
                  (x + span * .66, y + side * 21), (x + span, y + side * 24)]
        p.poly(points + [(x + span * .58, y + side * 18),
                         (x + span * .19, y + side * 13)], 14 if side > 0 else 10)
        p.line(points[:4], 7 if side > 0 else 13)
    for x, y in edge[1:-1]:
        for _ in range(1 + int(fold(x) / 4)):
            dx = rng.uniform(-3, 3)
            depth = rng.uniform(2, 7 + fold(x) * .36)
            p.line([(x + dx, y + depth - 3), (x + dx - 2, y + depth),
                    (x + dx - rng.uniform(4, 8), y + depth + rng.uniform(1, 7))],
                   rng.choice([4, 6, 7, 10]))
    for _ in range(425):
        x, y = rng.uniform(5, 624), rng.uniform(7, 472)
        seam = rupture(x) + jog(x)
        if abs(y - seam) > 20:
            length = rng.uniform(2, 11)
            p.line([(x, y), (x + length * .55, y - 1),
                    (x + length, y - 1 - length * .10)], 11 if y < seam else 12)

    def fragment(points, upper):
        """Clip a polygon to one side of the fault in design coordinates."""
        result = []
        for a, b in zip(points[-1:] + points[:-1], points):
            d_a = a[1] - rupture(a[0])
            d_b = b[1] - rupture(b[0])
            inside_a, inside_b = (d_a <= 0, d_b <= 0) if upper else (d_a >= 0, d_b >= 0)
            if inside_a != inside_b:
                t = d_a / (d_a - d_b)
                result.append(tuple(v + t * (w - v) for v, w in zip(a, b)))
            if inside_b:
                result.append(b)
        return result

    # The upper U has two disconnected arms. Clip those as separate polygons.
    upper_u = [[(0, 0), (30, 0), (30, 130), (0, 130)],
               [(60, 0), (90, 0), (90, 130), (60, 130)]]
    for upper, offset_x, offset_y, ink, impression in [
        (True, 8, -8, 1, 5), (False, -3, 23, 4, 8)
    ]:
        for i, letter in enumerate(LETTERS):
            for path in upper_u if upper and i == 2 else letter:
                points = [(77 + i * 98 + x, 147 + y) for x, y in path]
                piece = fragment(points, upper)
                if len(piece) >= 3:
                    face = [(x + offset_x,
                             y + offset_y + jog(x) * max(0, 1 - abs(y - rupture(x)) / 32)
                             + (0 if upper else fold(x) * .45))
                            for x, y in piece]
                    p.poly([(x - 2, y + 1) for x, y in face], 2 if upper else 7)
                    p.poly([(x + 3, y + 4) for x, y in face], impression)
                    p.poly(face, ink)
                    left, right = min(x for x, _ in face), max(x for x, _ in face)
                    top, bottom = min(y for _, y in face), max(y for _, y in face)
                    clusters = [(rng.uniform(left, right), rng.uniform(top, bottom))
                                for _ in range(18)]
                    for _ in range(int((right - left) * (bottom - top) / 95)):
                        cx, cy = rng.choice(clusters)
                        x = rng.gauss(cx, 7)
                        y = rng.gauss(cy, 4)
                        # Keep both ends of an ink fleck inside the same filled span.
                        crossings = sorted(
                            ax + (bx - ax) * (y - ay) / (by - ay)
                            for (ax, ay), (bx, by) in zip(face, face[1:] + face[:1])
                            if (ay > y) != (by > y)
                        )
                        if any(start + 2 < x < end - 4
                               for start, end in zip(crossings[::2], crossings[1::2])):
                            p.line([(x, y), (x + rng.uniform(1, 3), y - .4)], 9 if upper else 10)

    # The unprinted counter follows the upper A's displacement.
    counter = [(228, 173), (240, 229), (214, 229)]
    p.poly(counter, 0)
    p.line([(228, 175), (216, 228), (239, 228)], 6)
    for x, y in [(231, 189), (229, 205), (234, 211), (226, 219), (237, 221)]:
        p.rect(x - 4, y + 4, 2, 1, 6)

    p.text(55, 66, 'LETTERPRESS IN DISPLACEMENT', 22, 30, 1)
    p.line([(55, 81), (291, 81)], 2, 2)
    p.text(56, 394, 'FAULT LINE', 22, 27, 4)
    p.text(57, 433, 'INK / PAPER / SHEAR', 21, 27, 4)
    p.line([(460, 392), (540, 392), (552, 411), (594, 411)], 7)
    p.line([(460, 428), (540, 428), (552, 411)], 7)
    for x, ink in [(464, 14), (479, 5), (494, 3), (509, 7), (524, 4)]:
        p.rect(x, 403, 12, 15, ink)
        p.line([(x + 3, 424), (x + 9, 424)], 7)
    for x, y, ink in [(573, 411, 4), (570, 414, 14)]:
        p.circle(x, y, 11, ink, False)
        p.line([(x, y - 17), (x, y + 17)], ink)
    return p


if __name__ == '__main__':
    save(__file__, build())
