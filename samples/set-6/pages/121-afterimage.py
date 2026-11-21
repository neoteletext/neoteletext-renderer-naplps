from math import cos, radians, sin

from _support import Page, save

META = dict(title='Afterimage', purpose='A mechanical iris with a travelling pulse',
            style='Radial precision instrument in teal, violet and lime',
            techniques=['relative polygon vertices', 'native circles', 'phase-offset BLINK'],
            animated=True)


def build():
    p = Page('101325 252943 423968 305363 7c68a2 b4ffe6 f3fb9d'
             ' 454475 524276 584477 514378 43447a 3e467e'.split())
    cx, cy = 320, 230

    def at(radius, angle):
        a = radians(angle)
        return cx + radius * cos(a), cy + radius * sin(a)

    for radius, ink in [(204, 2), (198, 1), (186, 3), (177, 0)]:
        p.circle(cx, cy, radius, ink)
    for i in range(48):
        a = i * 7.5
        p.line([at(189 if i % 4 == 0 else 193, a), at(197, a)], 4, 1)
    for i in range(12):
        a = 30 * i
        # The side of each blade sweeps farther round at smaller radii.
        outline = [(170, 0), (171, 26), (142, 37), (106, 51), (69, 79),
                   (47, 109), (49, 79), (81, 47), (123, 21)]
        p.poly([at(r, a + offset) for r, offset in outline], 7 + i % 6)
        p.poly([at(r, a + offset) for r, offset in outline[4:9]] +
               [at(122, a + 27), at(83, a + 57)], 2)
        p.line([at(167, a + 6), at(123, a + 24), at(82, a + 50)], 5, 1)
    p.circle(cx, cy, 38, 4, False)
    p.circle(cx, cy, 27, 3, False)
    p.poly([at(r, a) for r, a in [(18, 270), (6, 0), (18, 90), (6, 180)]], 6)

    p.text(24, 454, 'AFTERIMAGE', 22, 30, 5)
    p.text(441, 449, 'PHASE / 06', 22, 28, 5)
    for i in range(6):
        p.rect(444 + 27 * i, 456, 22, 5, 7 + i)
        p.blink(7 + i, 6, on=2, off=10, delay=2 if i else 0)
    return p


if __name__ == '__main__':
    save(__file__, build())
