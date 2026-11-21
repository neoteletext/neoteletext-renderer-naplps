from _support import Page, save

META = dict(title='Fault Line', purpose='A poster for an imagined letterpress exhibition',
            style='Fractured block lettering in bone, oxide red and carbon',
            techniques=['polygonal letterforms', 'overpainting', 'proportional TEXT'],
            animated=False)

# Letter components in a local 90 × 166 design space.
LETTERS = [
    [[(0, 0), (89, 0), (89, 29), (30, 29), (30, 66), (74, 66),
      (74, 96), (30, 96), (30, 166), (0, 166)]],
    [[(0, 166), (28, 0), (61, 0), (90, 166), (60, 166), (52, 115),
      (37, 115), (29, 166)], [(30, 88), (60, 88), (60, 115), (30, 115)]],
    [[(0, 0), (30, 0), (30, 130), (38, 137), (52, 137), (60, 130),
      (60, 0), (90, 0), (90, 143), (68, 166), (22, 166), (0, 143)]],
    [[(0, 0), (31, 0), (31, 136), (90, 136), (90, 166), (0, 166)]],
    [[(0, 0), (90, 0), (90, 30), (60, 30), (60, 166), (29, 166),
      (29, 30), (0, 30)]],
]


def build():
    p = Page('e7d8ba 252022 aa3026 ff6945 f8ecd2 6d3b36'.split())
    p.poly([(0, 310), (111, 287), (253, 262), (391, 226), (501, 201),
            (640, 165), (640, 480), (0, 480)], 2)

    def rupture(x):
        return 309 - x * .22

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

    for upper, offset_x, offset_y, ink in [(True, 12, -10, 1), (False, -15, 18, 4)]:
        for i, letter in enumerate(LETTERS):
            for path in letter:
                points = [(77 + i * 98 + x, 147 + y) for x, y in path]
                piece = fragment(points, upper)
                if len(piece) >= 3:
                    p.poly([(x + offset_x, y + offset_y) for x, y in piece], ink)

    p.poly([(229, 185), (238, 219), (220, 219)], 0)

    p.text(55, 66, 'LETTERPRESS IN DISPLACEMENT', 22, 30, 1)
    p.line([(55, 81), (291, 81)], 2, 2)
    p.text(56, 394, 'FAULT LINE', 22, 27, 4)
    p.text(57, 433, 'INK / PAPER / SHEAR', 21, 27, 4)
    p.line([(454, 392), (580, 392), (580, 418)], 3, 2)
    p.line([(454, 407), (563, 407), (563, 433)], 4, 2)
    return p


if __name__ == '__main__':
    save(__file__, build())
