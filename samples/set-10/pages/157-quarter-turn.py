import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from math import cos, pi, sin

from encoder import Page, oval, save

META = dict(title='Quarter Turn', purpose='Poster for a rotating print installation',
            style='Acid lime and orchid on a black reading circuit with corner registers',
            techniques=['rotated TEXT on four paths', 'DRCS numerals', 'graduated dial'],
            animated=False)


def build():
    p = Page('1d1722 dfff75 ebadf0 786480 48354e')
    for x, dx in ((71, 1), (569, -1)):
        for y, dy in ((37, 1), (443, -1)):
            p.line([(x, y + 79*dy), (x, y), (x + 58*dx, y)], 3, 2)
            p.rect(x-3, y-3, 6, 6, 2)
    for y in (37, 443):
        p.rect(129, y-1, 382, 2, 4)
    for x in (71, 569):
        p.rect(x-1, 120, 2, 240, 4)

    def polar(radius, angle):
        return 320 + radius*cos(angle), 239 + radius*sin(angle)

    p.line([polar(116, i*pi/64) for i in range(129)], 3, 2)
    for tick in range(24):
        angle = tick*pi/12
        cardinal = tick % 6 == 0
        inner = 93 if cardinal else 106
        p.line([polar(inner, angle), polar(116, angle)],
               1 if cardinal else 3, 3 if cardinal else 2)
    p.line([polar(130, -i*pi/64) for i in range(32)], 2, 4)
    p.polygon([polar(130, -pi/2), polar(124, -1.45), polar(136, -1.45)], 2)
    p.line([polar(r, 0) for r in (117, 130)], 2, 2)
    p.circle(*polar(130, 0), 4, 2, fill=True)
    p.glyph('9', (1, oval(47, 31, 39, 29, 32)),
            (1, [(65, 29), (86, 30), (80, 64), (65, 85), (42, 96), (22, 96),
                 (22, 79), (40, 78), (55, 68), (64, 53)]),
            (0, oval(47, 31, 20, 13, 24)))
    p.glyph('0', (1, oval(46, 49, 39, 47, 40)), (0, oval(46, 49, 20, 31, 32)))
    p.text(263, 269, '90', 53, 66, 1, spacing=0, drcs=True)
    p.circle(371, 216, 6, 1, width=3)
    p.text(160, 111, 'QUARTER', 47, 67, 1, spacing=0)
    p.text(466, 125, 'TURN', 59, 70, 2, spacing=0, path=3, rotation=3)
    p.text(482, 370, 'QUARTER', 47, 67, 1, spacing=0, path=1, rotation=2)
    p.text(175, 352, 'TURN', 59, 70, 2, spacing=0, path=2, rotation=1)
    return p


if __name__ == '__main__':
    save(__file__, build())
