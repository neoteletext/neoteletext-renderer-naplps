from math import pi, sin, cos
from _canvas import Canvas, write_page

META = dict(title='Soap Film', purpose='Interference bands draining through a stretched film',
            style='Chromatic contours in an oblique wire frame',
            techniques=['nested contour polygons', 'thin-film islands', 'native droplet highlight'], animated=False)


def build():
    p = Canvas('171d26 36414e a6a9a3 f9efcb 171626 382450 72396d c65b83'
               ' f69387 ffc67c d9dd9a 7ac098 418c99 45648f 638084 e4d0af')
    frame = [(143, 132), (496, 46), (552, 298), (221, 361)]

    def at(u, v):
        a, b, c, d = frame
        return tuple((1-v)*((1-u)*a[i]+u*b[i])+v*((1-u)*d[i]+u*c[i])
                     for i in (0, 1))

    def boundary(u, step):
        wave = .09*sin(2*pi*u + .34*step) + .025*cos(6*pi*u - .46*step)
        drain = .054*sin(pi*u)**2 * sin(.48*step-.4)
        return .13 + .66*(step/10)**1.23 + wave*(1-step/17) + drain

    p.poly(frame, 4)
    # Bands converge on the nearly black, thinnest part of the film.
    for step, ink in enumerate((5, 6, 7, 8, 9, 10, 11, 12, 13, 5, 6)):
        contour = []
        for i in range(65):
            u = i / 64
            contour.append(at(u, boundary(u, step)))
        p.poly(contour + frame[2:], ink)
    # The black film advances in uneven tongues along the thinning front.
    for u, v, w, h, phase in [(.29, .17, .076, .034, 1),
                              (.67, .11, .12, .052, 0),
                              (.85, .22, .054, .028, 2)]:
        for scale, ink in [(1, 7), (.90, 6), (.74, 5), (.66, 4)]:
            points = []
            for i in range(64):
                a = i*pi/32
                lobe = 1+.20*sin(3*a+phase)+.11*cos(5*a)
                points.append(at(u+w*scale*lobe*cos(a),
                                 v+h*scale*lobe*sin(a)+.016*cos(a)))
            p.poly(points, ink)
    for step, ink in enumerate((5, 13, 12, 14)):
        pool = [at(u, .89+.022*step+.037*sin(pi*u)**2
                   +.015*sin(4*pi*u+step*.65))
                for u in (i/90 for i in range(91))]
        p.poly(pool + frame[2:], ink)
    for start, end, step, ink in [(.12, .54, 3, 9), (.43, .90, 6, 10), (.04, .36, 8, 11)]:
        points = []
        for i in range(49):
            t = i/48
            u = start+(end-start)*t
            points.append(at(u, boundary(u, step)+.027*sin(pi*t)))
        p.line(points, ink, 2)
    for side, direction in [(0, 1), (1, -1)]:
        for width, ink in [(.048, 13), (.024, 14), (.010, 15)]:
            fringe = []
            for i in range(41):
                v = i/40
                swell = sin(pi*v)**2*(.65+.35*cos(10*v+side))
                fringe.append(at(side + direction*width*swell, v))
            p.poly([at(side, 0), *fringe, at(side, 1)], ink)
    p.line(frame + frame[:1], 1, 9)
    p.line([(x-1.5, y) for x, y in (at(0, 0), at(0, 1))], 1, 13)
    p.line([at(.02, .97), at(.23, .985), at(.54, .975), at(.79, .99), at(.99, .965)], 14, 3)
    x, y = at(.71, 1)
    p.poly([(x-7, y), (x-3, y+8), (x-5, y+15), (x-2, y+21),
            (x+4, y+23), (x+10, y+20), (x+11, y+14), (x+6, y+5), (x+6, y-1)], 14)
    p.pel(2).arc((x+8, y+14), (x+6, y+19), (x+1, y+20), 15)
    for u, rx, ry in [(.62, 3.2, 5.4), (.78, 2.3, 3.8), (.88, 1.8, 2.6)]:
        x, y = at(u, 1)
        p.ellipse(x, y+ry+3, rx, ry, 14, n=24)
        p.circle(x+.7, y+2*ry+1, 1.25, 15)
    p.line(frame[:2], 2, 4)
    p.line(frame[2:], 2, 4)
    p.line([(143, 132), (74, 102), (31, 65)], 1, 12)
    p.line([(143, 129), (75, 98), (33, 63)], 2, 3)
    for x, y in frame:
        p.circle(x, y, 4, 2)
    p.text(38, 447, 'SOAP FILM', 38, 50, 3)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
