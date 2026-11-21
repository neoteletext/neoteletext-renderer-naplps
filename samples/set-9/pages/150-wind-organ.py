from math import sin
from random import Random
from _canvas import Canvas, write_page

META = dict(title='Wind Organ', purpose='A fictional instrument played by air rushing along a cliff',
            style='Terracotta pipework on a luminous chartreuse landscape',
            techniques=['extruded polygons', 'native airflow arcs', 'layered rock strata'],
            animated=False)


def build():
    p = Canvas('dedf90 edeea9 bdc472 8e9b5c 505c40 263d32'
               ' 9d493c d4754e f4a965 ffdb8f 79363b 152c27 f6f3be 687451 b1674f 37473a')
    p.poly([(0, 282), (102, 302), (245, 256), (354, 272), (460, 220),
            (640, 209), (640, 480), (0, 480)], 2)
    p.poly([(0, 394), (107, 357), (184, 366), (271, 314), (399, 291),
            (495, 252), (640, 240), (640, 480), (0, 480)], 3)
    p.poly([(0, 443), (116, 409), (163, 411), (266, 345), (394, 327),
            (479, 291), (640, 272), (640, 480), (0, 480)], 4)
    p.poly([(168, 414), (279, 354), (400, 341), (493, 303), (640, 290),
            (640, 480), (189, 480)], 5)
    p.poly([(167, 415), (279, 355), (400, 341), (493, 303), (640, 290),
            (640, 320), (490, 330), (403, 369), (285, 385), (183, 444)], 15)
    strata = [(165, 420), (244, 385), (279, 367), (397, 352), (490, 317), (638, 301)]
    for dy, ink, width in [(0, 13, 4), (10, 4, 3), (21, 11, 4), (32, 15, 5)]:
        p.line([(x, y+dy) for x, y in strata], ink, width)
    rng = Random(150)
    for _ in range(110):
        x = rng.uniform(207, 631)
        crest = max(332, 455-.21*x)
        y = rng.uniform(crest+8, 468)
        length = min(638-x, rng.uniform(6, 37))
        p.line([(x, y), (x+.57*length, y-.24*length-2),
                (x+length, y-.31*length)], rng.choice((11, 15, 4)), 1)
    for x, y in [(227, 431), (316, 411), (414, 382), (517, 358), (610, 340)]:
        p.poly([(x, y), (x+18, y-7), (x+7, y+13),
                (x+15, y+31), (x-3, y+23)], 11)
    p.poly([(194, 423), (584, 314), (600, 345), (214, 461)], 15)
    p.line([(212, 449), (599, 340)], 4, 3)
    p.poly([(188, 395), (538, 294), (589, 307), (237, 415)], 13)
    p.poly([(237, 415), (589, 307), (588, 321), (240, 429)], 11)
    pipes = [(215, 239, 407, 27), (275, 204, 384, 35), (343, 153, 365, 45),
             (411, 175, 351, 31), (468, 105, 326, 39), (539, 65, 309, 51)]
    for x, _, base, w in pipes:
        p.poly([(x-9, base-6), (x+w+4, base-9), (x+w+23, base+10),
                (x+w+9, base+19), (x-4, base+13)], 11)
        p.poly([(x-10, base-5), (x+w+7, base-8), (x+w+10, base+4),
                (x-8, base+8)], 4)
        p.poly([(x-8, base+8), (x+w+10, base+4), (x+w+10, base+10),
                (x-8, base+14)], 15)
        p.line([(x-9, base+7), (x+w+9, base+3)], 13, 2)
        for bolt in (x-4, x+w+3):
            p.circle(bolt, base+2-(bolt-x)/w*3, 2, 9)
    for x, top, base, w in pipes:
        p.poly([(x, top+15), (x+w, top+15), (x+w, base-5),
                (x+w*.55, base+5), (x, base)], 6)
        p.poly([(x, top+15), (x+w*.55, top+21), (x+w*.55, base+5),
                (x, base)], 7)
        p.poly([(x+w*.28, top+17), (x+w*.47, top+20),
                (x+w*.47, base+4), (x+w*.28, base+2)], 14)
        p.line([(x+w*.83, top+23), (x+w*.83, base-10)], 14, 2)
        p.ellipse(x+w/2, top+17, w*.64, 10, 8, n=18)
        p.ellipse(x+w/2, top+10, w*.61, 8, 9, n=18)
        p.ellipse(x+w/2, top+10, w*.49, 5, 10, n=16)
        p.pel(2).arc((x+.10*w, top+10), (x+.51*w, top+13),
                     (x+.89*w, top+10), 6)
        p.pel(2).arc((x-.01*w, top+15), (x+.50*w, top+21),
                     (x+.98*w, top+15), 9)
        p.line([(x+7, top+37), (x+7, base-14)], 8, 2)
        port = base - (base-top)*.43
        p.poly([(x+4, port), (x+w*.63, port-5), (x+w*.63, port+11), (x+4, port+14)], 10)
        p.poly([(x+7, port+3), (x+w*.59, port-1), (x+w*.59, port+6), (x+7, port+10)], 11)
        p.line([(x+4, port+14), (x+w*.63, port+11)], 8, 2)
        p.ellipse(x+w/2, base-9, w*.61, 7, 14, n=28)
        p.ellipse(x+w/2, base-12, w*.58, 5, 8, n=24)
        p.rect(x+4, base-14, w-8, 4, 7)
    for height, ink in [(174, 1), (196, 1), (212, 12)]:
        points = [(x, height-.19*x+15*sin(x/71+height/37))
                  for x in range(0, 640, 5)]
        segment = []
        for x, y in points:
            blocked = (x < 190 and y < 146) or any(
                px-9 < x < px+pw+9 and pt < y < pb for px, pt, pb, pw in pipes)
            if blocked:
                if len(segment) > 1:
                    p.line(segment, ink, 1)
                segment = []
            else:
                segment.append((x, y))
        if len(segment) > 1:
            p.line(segment, ink, 1)
    for x, top, _, w in pipes:
        mouth = x+w/2
        for lift, span, ink in [(0, 82, 3), (-22, 114, 12)]:
            points = []
            for i in range(32):
                t = i/31
                xx = mouth-span*(1-t)
                yy = top+8+lift+(1-t)*(31+18*sin(4*t+x/96))
                if xx > 184 or yy > 145:
                    if not any(px-4 < xx < px+pw+4 and pt+6 < yy < pb
                               for px, pt, pb, pw in pipes):
                        points.append((xx, yy))
                        continue
                if len(points) > 1:
                    p.line(points, ink, 2)
                points = []
            if len(points) > 1:
                p.line(points, ink, 2)
    for x, top, _, w in pipes:
        centre = x+w/2
        # A tight curl lifts from each bore, separate from the long wind lines.
        p.pel(2).arc((centre+3, top+6), (centre+19, top-11),
                     (centre+46, top-19), 13)
        p.pel(2).arc((centre+9, top-1), (centre+27, top-19),
                     (centre+47, top-21), 12)
        p.line([(centre+48, top-22), (centre+60, top-23)], 1, 1.5)
    for _ in range(34):
        x, y = rng.uniform(8, 550), rng.uniform(70, 248)
        if (x < 186 and y < 150) or any(px-10 <= x <= px+w+12 and y > top-9
                                        for px, top, _, w in pipes):
            continue
        p.line([(x, y), (x+7, y-2), (x+13, y-2)], 1, 2)
    p.text(35, 81, 'WIND', 40, 54, 5)
    p.text(34, 132, 'ORGAN', 39, 52, 5)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
