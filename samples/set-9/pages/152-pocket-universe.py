from math import pi, sin, sqrt, tanh
from _canvas import Canvas, Y_SCALE, write_page

META = dict(title='Pocket Universe', purpose='Three glass marbles bending the stripes beneath them',
            style='Tinted glass over an apricot striped tabletop',
            techniques=['polygon-clipped refraction bands', 'curved refraction lines', 'window reflections and caustics'],
            animated=False)


def build():
    p = Canvas('ffd9a6 f4bd98 ce826d aa5b59 381f3e 462348 80376c'
               ' c7689e ffacc9 fff1d4 17465b 298f9b 81dbc1 9c4639 ce5c3e ffab51')
    for left in range(-220, 640, 82):
        right = left + 36
        top = max(0, -right / .43)
        bottom = min(480, (640 - left) / .43)
        if top >= bottom:
            continue
        # Insert vertices where either stripe edge meets the viewport.
        levels = sorted({top, bottom, *(y for y in (-left / .43, (640 - right) / .43)
                                       if top < y < bottom)})
        a = [(max(0, left + .43 * y), y) for y in levels]
        b = [(min(639.7, right + .43 * y), y) for y in reversed(levels)]
        p.poly(a + b, 1)

    weave = range(26, 480, 44)
    for y in weave:
        p.line([(0, y), (639, y)], 2, 1)
        p.line([(0, y+4), (639, y+4)], 1, 1)
        for x in range(13, 640, 23):
            p.line([(x-3, y-2), (x+2, y+3)], 2, 1)

    def on_grid(points):
        # Quantize absolute vertices first so relative polygon operands do
        # not accumulate rounding error where the refraction meets the rim.
        x_pel, y_pel = 640/2048, Y_SCALE/2048
        return [(round(x/x_pel)*x_pel, 480-round((480-y)/y_pel)*y_pel)
                for x, y in points]

    def marble(cx, cy, radius, inks, panes, caustic):
        p.ellipse(cx+radius*.27, cy+radius*.69, radius*1.03, radius*.42, 1, n=80)
        p.ellipse(cx+radius*.20, cy+radius*.73, radius*.87, radius*.30, 2, n=80)
        p.ellipse(cx+radius*.05, cy+radius*.81, radius*.60, radius*.16, 3, n=64)
        # Transmitted light falls inside the cast shadow.
        for offset, width, ink in [(-.03, .13, inks[1]), (.02, .065, inks[2]),
                                   (.07, .027, inks[3])]:
            def ray(t, side):
                return (cx+radius*(.30+.76*t),
                        cy+radius*(.75+offset+caustic*t+.11*sin(pi*t)
                                   +side*width*sin(pi*t)**1.4))

            p.poly([ray(i/40, 1) for i in range(41)]
                   + [ray(i/40, -1) for i in range(39, 0, -1)], ink)
        for sweep, width, ink in [(0, 5, inks[2]), (.055, 2, inks[3]), (.10, 1, 9)]:
            points = [(cx+radius*(.54+t*.57),
                       cy+radius*(.94+sweep+caustic*t-.19*t*t))
                      for t in (i/28 for i in range(29))]
            p.line(points, ink, width)
        p.circle(cx, cy, radius, inks[0])
        p.circle(cx, cy, radius*.965, inks[1])
        # Reverse the stripe direction through the centre and bow its edges.
        inner = radius*.94
        phase = cx - .43*cy
        levels = [i/64 for i in range(-64, 65)]

        def edge(boundary):
            points = []
            for v in levels:
                span = sqrt(1-v*v)
                u = (boundary-phase)/inner - .54*v + .18*sin(v*pi)
                u = 1.24*tanh(u/1.16)
                points.append((cx+inner*max(-span, min(span, u)), cy+inner*v))
            return points

        for left in range(-220, 640, 82):
            if left + 36 < phase - 1.4*inner or left > phase + 1.4*inner:
                continue
            p.poly(on_grid(edge(left) + edge(left+36)[::-1]), inks[2])
        for y in weave:
            v = (cy-y)/inner
            if abs(v) >= .91:
                continue
            span = sqrt(1-v*v)*.92
            thread = inks[1] if abs(v) > .56 else inks[0]
            def grid(u, offset=0):
                return (cx+inner*u, cy+inner*(v+.29*(span*span-u*u))+offset)
            p.line([grid(-span+2*span*i/28) for i in range(29)], thread, 1)
            p.line([grid(-span+2*span*i/28, -2) for i in range(29)], inks[2], 1)
            for x in range(13, 640, 46):
                u = .78*(cx-x)/inner
                if abs(u) < span-.04:
                    p.line([grid(u-.015, -2), grid(u+.015, 1)], thread, 1)
        p.pel(3).arc((cx-.58*radius, cy+.62*radius),
                     (cx, cy+.86*radius),
                     (cx+.60*radius, cy+.60*radius), inks[3])
        p.pel(4).arc((cx - .68 * radius, cy - .27 * radius),
                     (cx - .50 * radius, cy - .54 * radius),
                     (cx - .19 * radius, cy - .69 * radius), 9)
        def at(u, v):
            # The reflected window shifts and shears around each sphere.
            shift = (cx - 320)/1250
            return cx+radius*(u-shift*v), cy+radius*(v+shift*u)

        # Each shoulder catches a different portion of the same tall window.
        for left, top, right, bottom in panes:
            p.poly([at(left, top), at((left+right)/2, top-.026),
                    at(right, top-.036), at(right+.019, bottom-.044),
                    at((left+right)/2+.031, bottom-.026), at(left+.036, bottom)], 9)
        p.pel(2).arc(at(.44, .86), at(.72, .94), at(1.03, .80), inks[3])
        p.pel(2).arc(at(.38, .75), at(.56, .59), at(.69, .38), inks[3])
        p.circle(*at(.62, .42), radius*.035, 9)

    marble(433, 120, 81, (13, 14, 15, 2),
           [(-.58, -.40, -.40, -.31), (-.36, -.40, -.26, -.33)], .14)
    marble(147, 222, 88, (10, 11, 12, 9),
           [(-.54, -.45, -.45, -.22), (-.42, -.45, -.35, -.26)], -.03)
    marble(354, 267, 119, (5, 6, 7, 8),
           [(-.56, -.46, -.40, -.33), (-.56, -.29, -.40, -.18),
            (-.36, -.46, -.24, -.35), (-.36, -.31, -.24, -.22)], .21)
    p.rect(0, 400, 639.7, 80, 4)
    p.text(39, 457, 'POCKET UNIVERSE', 34, 46, 9)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
