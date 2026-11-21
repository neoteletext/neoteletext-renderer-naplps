import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from math import cos, pi, sin

from encoder import Page, oval, save

META = dict(title='Quarter Turn', purpose='Poster for a rotating print installation',
            style='Acid lime and orchid on a black reading circuit with four edge indexes',
            techniques=['rotated TEXT on four paths', 'DRCS numerals', 'graduated dial'],
            animated=False)


def build():
    p = Page('1d1722 dfff75 ebadf0 786480 48354e')
    for x, y, dx, dy in ((320, 37, 70, 0), (320, 443, 70, 0),
                         (71, 240, 0, 70), (569, 240, 0, 70)):
        p.line([(x-dx, y-dy), (x+dx, y+dy)], 3, 2)
        p.rect(x-3, y-3, 6, 6, 2)

    def polar(radius, angle):
        return 320 + radius*cos(angle), 239 + radius*sin(angle)

    start, finish = -pi/2, 0
    p.polygon([polar(117, start+i*pi/128) for i in range(65)]
              + [(320, 239)], 4)
    p.line([polar(116, i*pi/96) for i in range(193)], 3, 2)
    for tick in range(48):
        angle = tick*pi/24
        major = tick % 12 == 0
        middle = tick % 6 == 0
        active = tick >= 36 or tick == 0
        inner = 92 if major else 98 if middle else 109
        p.line([polar(inner, angle), polar(116, angle)],
               1 if major else 2 if active else 3, 3 if major else 2)
    arc = [polar(132, start+i*pi/128) for i in range(60)]
    p.line(arc, 2, 4)
    p.circle(*arc[0], 4, 2, fill=True)
    p.polygon([polar(132, finish), polar(124, -.11), polar(140, -.11)], 2)
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
