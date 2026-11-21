import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from encoder import Page, save

META = dict(title='The Fi Join', purpose='A drawing plate for an original lowercase ligature',
            style='Ivory drafting paper and a vermilion calligraphic detail',
            techniques=['DRCS ligature', 'overlaid construction rules', 'proportional TEXT'],
            animated=False)


def build():
    p = Page('f5edda 302329 b8452e d9c8aa 78604e')
    p.text(42, 75, 'The fi join', 51, 64)
    p.rect(42, 95, 555, 2, 1)
    stem = [(7, 90), (19, 86), (27, 79), (34, 57), (37, 47), (43, 28),
            (49, 17), (57, 9), (67, 5), (77, 5), (86, 8), (92, 14),
            (95, 21), (94, 28), (88, 30), (81, 33), (75, 31), (72, 27),
            (74, 25), (81, 21), (81, 17), (78, 14), (71, 13), (64, 17),
            (58, 27), (51, 47), (48, 57), (39, 81), (32, 90), (22, 95), (8, 97)]
    bar = [(12, 57), (15, 48), (68, 47), (65, 56)]
    downstroke = [(70, 56), (58, 56), (61, 47), (85, 47), (90, 50), (89, 56),
                  (77, 81), (77, 85), (82, 87), (95, 80), (97, 86),
                  (86, 93), (77, 96), (68, 96), (62, 93), (58, 87), (60, 78)]
    dot = [(92, 37), (97, 34), (100, 38), (99, 43), (94, 45), (90, 42)]
    p.glyph('F', (1, stem), (1, bar), (1, downstroke), (1, dot))
    p.glyph('f', (1, stem), (1, bar))
    p.glyph('i', *((1, [(x-36, y) for x, y in contour])
                   for contour in (downstroke, dot)))
    for y in (136, 235, 356):
        p.rect(42, y, 338, 2, 3)
    p.text(58, 366, 'F', 307, 244, 2, spacing=0, drcs=True)
    for point, elbow, end in (((327, 171), (383, 171), (411, 153)),
                              ((226, 240), (378, 240), (411, 222))):
        p.line([point, elbow, end], 4, 2)
        p.circle(*point, 4, 0, fill=True)
        p.circle(*point, 4, 4, width=1)
    p.text(429, 166, 'Hook', 32, 39)
    p.text(429, 234, 'Join', 32, 39)
    p.rect(401, 354, 76, 2, 3)
    p.rect(526, 354, 73, 2, 3)
    p.text(399, 354, 'f', 56, 79, 2, spacing=0, drcs=True)
    p.text(442, 354, 'i', 56, 79, 2, spacing=0, drcs=True)
    p.line([(487, 320), (515, 320)], 4, 2)
    p.polygon([(515, 320), (507, 315), (507, 325)], 4)
    p.text(528, 354, 'F', 68, 79, 2, spacing=0, drcs=True)
    p.rect(42, 395, 555, 2, 1)
    p.text(42, 447, 'One stroke, two letters', 32, 43)
    return p


if __name__ == '__main__':
    save(__file__, build())
