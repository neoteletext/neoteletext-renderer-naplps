from math import cos, sin
from random import Random
from _canvas import Canvas, write_page

META = dict(title='Updraft of Umbrellas', purpose='A flock of runaway umbrellas escapes a rain shower',
            style='Ink-green storm bands with bright canopies at staggered scales',
            techniques=['transformed canopy polygons', 'open handle arcs', 'gust filaments and directional rain'],
            animated=False)


def build():
    p = Canvas('123439 195055 23716a 2f8b7c 80ad8f dbe3aa 112930'
               ' fbb34f fa7555 c13f58 ffcbd1 b182c0 6b5394 f6eed0 59ae9a 16464a')
    def gust(x, shift):
        return 310 + shift + .23*x - .00108*x*x

    rng = Random(155)
    # Each group follows a slightly different path around a canopy.
    for x0, x1, shift, curl, ink in [
        (0, 232, -101, -12, 15), (29, 278, -26, 30, 1),
        (122, 454, 35, -27, 2), (233, 535, -55, 40, 1),
        (382, 610, -132, -25, 15), (468, 638, 15, 23, 2),
        (493, 638, -50, -38, 1),
    ]:
        for lane in range(4):
            left = x0 + lane*9
            right = x1 - lane*11
            points = []
            for x in range(left, right, 4):
                t = (x-x0)/(x1-x0)
                y = gust(x, shift) + curl*sin(t*5.2) + lane*(3+9*t)
                if 4 < y < 366:
                    points.append((x, y))
            if len(points) > 1:
                p.line(points, ink, 1.4)
    for _ in range(60):
        x = rng.uniform(0, 619)
        span = rng.uniform(13, min(66, 640-x))
        shift = rng.uniform(-168, 62)
        points = [(xx, gust(xx, shift)+9*sin(xx/49+shift/43))
                  for xx in (x+span*i/14 for i in range(15))]
        if points[-1][1] > 9 and points[0][1] < 375:
            p.line(points, rng.choice((1, 2, 3, 15)), rng.uniform(1.2, 2))
    for _ in range(100):
        x, y = rng.uniform(10, 634), rng.uniform(10, 370)
        length = rng.uniform(4, 14)
        p.line([(x, y), (x-length*.37, y+length)], rng.choice((1, 2, 14)), 1)

    def umbrella(x, y, scale, tilt, inks, pitch=1):
        def at(u, v):
            return (x + scale * (u * cos(tilt) - v * sin(tilt)),
                    y + scale * (u * sin(tilt) + v * cos(tilt)))
        p.line([at(0, min(0, -62*pitch)), at(0, 61)], 13, max(2, 4 * scale))
        p.arc(at(0, 61), at(13, 75), at(25, 62), 13)
        p.poly([at(u, pitch*v) for u, v in
                [(-100, 0), (-90, -22), (-72, -40), (-47, -53), (-20, -60),
                 (0, -62), (28, -58), (57, -49), (80, -34), (95, -16),
                 (101, 0), (74, -10), (53, 0), (26, -11), (0, 0),
                 (-24, -11), (-52, 0), (-77, -10)]], inks[0])
        p.poly([at(u, pitch*v) for u, v in
                [(0, -62), (-25, -48), (-40, -27), (-52, 0),
                 (-24, -11), (0, 0), (14, -15), (26, -11), (15, -43)]], inks[1])
        p.poly([at(u, pitch*v) for u, v in
                [(0, -62), (27, -52), (45, -30), (53, 0),
                 (74, -10), (101, 0), (80, -34), (57, -49), (28, -58)]], inks[2])

        ribs = [(-100, 0), (-52, 0), (0, 0), (53, 0), (101, 0)]
        if pitch < 0:
            p.line([at(0, -62*pitch), at(0, 58)], 12, 3)
        for u, v in ribs:
            rib = [at(0, -62*pitch), at(u*.39, -55*pitch),
                   at(u*.78, -26*pitch), at(u, v)]
            p.line(rib, 13 if pitch < 0 else inks[2], 2 if scale > .7 else 1.5)
            p.line([at(u, v), at(u*1.04, v+3)], 13, 2)
        if scale > 1:
            for u in (-76, -26, 23, 73):
                p.line([at(u*.07, -60), at(u*.43-2, -49),
                        at(u*.77-2, -29), at(u, -11)], inks[1], 1.5)
            p.line([at(-99, -1), at(-79, -11), at(-54, -3),
                    at(-24, -12), at(0, -2), at(26, -12),
                    at(52, -2), at(74, -11), at(100, -1)], 13, 1)
        if pitch < 0:
            p.poly([at(-94, 1), at(-54, 11), at(-29, 21), at(0, 24),
                    at(29, 21), at(58, 11), at(96, 1), at(57, 16),
                    at(0, 34), at(-57, 17)], 11)
            for u in (-100, -52, 53, 101):
                p.line([at(0, 16), at(u*.62, -35*pitch)], 12, 2.5)
            p.circle(*at(0, 16), 2.7, 13)
        x_tip, y_tip = at(0, -62*pitch)
        p.circle(x_tip, y_tip, 2.4*scale, 13)

    umbrella(557, 67, .37, -.43, (11, 10, 12), .65)
    umbrella(442, 107, .65, .23, (7, 10, 8), -.85)
    umbrella(545, 209, .58, -.18, (8, 7, 9), .42)
    umbrella(318, 131, .60, -.62, (14, 5, 3))
    umbrella(177, 229, .79, .34, (11, 10, 12))
    umbrella(371, 268, 1.22, -.49, (8, 7, 9))
    p.text(27, 420, 'UPDRAFT OF', 28, 37, 13)
    p.text(28, 465, 'UMBRELLAS', 30, 42, 13)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
