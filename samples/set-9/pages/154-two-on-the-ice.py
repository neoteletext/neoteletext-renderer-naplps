from math import atan2, cos, hypot, pi, sin
from random import Random
from _canvas import Canvas, write_page

META = dict(title='Two on the Ice', purpose='An overhead view of two skaters cutting intersecting tracks',
            style='Blue-white negative space with two tiny saturated figures',
            techniques=['graded figure-eight cuts', 'directional ice scores', 'native spray circles'],
            animated=False)


def build():
    p = Canvas('c7e9ea d7f5ee a6dce0 78b8cc 5596a9 143f59 e4383d ff7d59 3f4a96 f5edc6 b9e0e4 e5f9f5 326e88 bcebea 98293e 273465')
    p.poly([(0, 14), (94, 94), (268, 146), (390, 120), (640, 37),
            (640, 0), (0, 0)], 1)
    p.poly([(0, 393), (145, 455), (294, 467), (496, 431), (640, 347),
            (640, 480), (0, 480)], 2)
    rng = Random(154)
    for _ in range(260):
        x, y = rng.randrange(5, 615), rng.randrange(14, 395)
        length = rng.randrange(3, 25)
        drift = rng.uniform(-.29, -.07)*length
        p.line([(x, y), (x+.6*length, y+.8*drift), (x+length, y+drift)],
               rng.choice((1, 10, 13)), 1)
    for bank in [[(0, 28), (72, 85), (153, 124), (262, 147), (359, 121), (441, 89), (639, 55)],
                 [(0, 376), (97, 412), (201, 447), (292, 458), (452, 430), (560, 397), (639, 354)]]:
        p.line(bank, 13, 3)

    def track(cx, cy, start, stop, tilt, ink):
        def point(t):
            a, b = 185*sin(t), 113*sin(2*t)
            return (cx+a*cos(tilt)-b*sin(tilt), cy+a*sin(tilt)+b*cos(tilt))

        def direction(t):
            x, y = point(t)
            xx, yy = point(t + (.001 if stop > start else -.001))
            return xx-x, yy-y

        grooves = [], []
        for i in range(125):
            t = start + (stop-start)*i/124
            x, y = point(t)
            dx, dy = direction(t)
            length = hypot(dx, dy)
            for offset, groove in zip((-2.3, 2.3), grooves):
                groove.append((x-offset*dy/length, y+offset*dx/length))
        # The fresh pass displaces the old cut at each crossing.
        if ink == 12:
            p.line(grooves[0], 0, 8)
        p.line(grooves[0][:66], 1, 1.5)
        p.line(grooves[0][65:], 11, 2)
        p.line(grooves[1][:43], 3, 1.5)
        p.line(grooves[1][42:96], ink, 1.5)
        p.line(grooves[1][95:], ink, 2.5)
        dx, dy = direction(stop)
        return (*point(stop), atan2(dy, dx) + pi/2)

    a = track(272, 225, .19, 2*pi-.78, -.24, 4)
    b = track(366, 253, 6.05, 1.03, .21, 12)

    def skater(x, y, tilt, coat, scarf, shade, stride, arms, bend):
        def at(u, v):
            return x + u*cos(tilt) - v*sin(tilt), y + u*sin(tilt) + v*cos(tilt)

        for _ in range(32):
            u, v = rng.uniform(-12, 18), rng.uniform(3, 45)
            xx, yy = at(u, v)
            p.circle(xx, yy, rng.uniform(.65, 1.45), 11)
        p.ellipse(*at(6, 15), 15, 7, 2, n=32)
        p.poly([at(-8, -9), at(7, -11), at(23, 22), at(13, 25)], 2)
        heel, toe = at(-stride-3, 27), at(-stride+8, 23)
        p.line([at(-4, 7), at(-12, 14), at(-stride, 23)], 5, 8)
        p.line([at(5, 5), at(12, 12), at(6, 23)], shade, 8)
        p.line([at(6, 9), at(9, 13), at(6, 19)], coat, 2)
        p.line([heel, toe], 5, 6)
        p.line([at(-stride-4, 30), at(-stride+8, 26)], 11, 2)
        p.line([at(3, 20), at(8, 28)], 5, 6)
        p.line([at(5, 21), at(11, 30)], 11, 2.5)
        p.line([at(u, v) for u, v in arms], coat, 8)
        for u, v in (arms[0], arms[-1]):
            p.circle(*at(u, v), 3.1, scarf)
        p.poly([at(-10, -7), at(5, -12), at(11, -3), at(8, 11),
                at(-4, 13), at(-9, 7)], coat)
        p.poly([at(2, -10), at(11, -3), at(8, 11), at(0, 12)], shade)
        p.line([at(-6, -9), at(2, -5), at(11, 3), at(19, 13)], scarf, 3)
        p.circle(*at(bend, -15), 8, 5)
        p.circle(*at(bend-1, -17), 4, shade)
        p.line([at(bend-4, -19), at(bend+2, -19)], scarf, 2)

    skater(*a, 6, 7, 14, 25,
           [(-27, 10), (-18, 1), (-7, -1), (8, -6), (18, -16), (25, -22)], -2)
    skater(*b, 8, 9, 15, 10,
           [(-24, -11), (-17, -4), (-6, 1), (7, -4), (20, -11), (29, -22)], 4)
    p.text(36, 452, 'TWO ON THE ICE', 32, 42, 5)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
