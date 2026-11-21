"""Enlarged plan view of open and closed stomata with paired guard cells."""
from math import cos, pi, sin
from _drawing import Page, save

META = dict(title='A Leaf Breathes', purpose='Compare paired guard cells at high and low turgor',
            style='Jade microscopy plate with inked epidermal seams',
            techniques=['nested contour polygons', 'native circles', 'knockout pore'], animated=False)


def build():
    p = Page('102d2b e6fac9 23574a 34705a 469267 98d373 bbe883 407f56 152622 609f60 81b66b 45936c')
    p.label(33, 66, 'A LEAF BREATHES', 54)
    p.label(35, 102, 'STOMATA IN THE LEAF EPIDERMIS', 26, 6)

    def cell_wall(x, y, opening, side, inset):
        outer = []
        inner = []
        for i in range(65):
            t = i*pi/64
            bulge = sin(t)
            outer.append((x+side*(6+(66-inset+opening*.5)*bulge**.83),
                          y-(101-inset)*cos(t)))
            inner.append((x+side*((1+(opening+inset)*bulge**1.7) if opening else 0),
                          y-(88-inset)*cos(t)))
        return outer + inner[::-1]

    def specimen(x, opening):
        y = 244
        p.rect(x-133, 112, 266, 265, 2)
        seams = [
            [(-133,-78),(-69,-65),(-31,-104),(-35,-132)],
            [(-69,-65),(-81,-16),(-133,12)],
            [(-81,-16),(-106,33),(-75,72),(-133,105)],
            [(-75,72),(-39,94),(-38,132)],
            [(8,-132),(28,-105),(71,-72),(133,-84)],
            [(71,-72),(98,-34),(133,-23)],
            [(98,-34),(83,15),(110,60),(133,57)],
            [(110,60),(83,97),(104,132)],
            [(83,97),(39,105),(26,132)],
        ]
        for seam in seams:
            if not opening:
                seam = [(-sx, -sy) for sx, sy in seam]
            points = [(x+seam[0][0], y+seam[0][1])]
            for (ax, ay), (bx, by) in zip(seam, seam[1:]):
                for i in range(1, 25):
                    t = i/24
                    lobe = (.21*sin(2*pi*t) if opening else .15*sin(4*pi*t)) * sin(pi*t)
                    points.append((x+ax+(bx-ax)*t-(by-ay)*lobe,
                                   y+ay+(by-ay)*t+(bx-ax)*lobe))
            p.line(points, 3, 6).line(points, 4, 2)
        if opening:
            p.ellipse(x, y, opening+9, 92, 8, n=96)
        for side in (-1, 1):
            p.poly(cell_wall(x, y, opening, side, 0), 7)
            p.poly(cell_wall(x, y, opening, side, 5), 5 if opening else 10)
            inner_wall = cell_wall(x, y, opening, side, 3)[65:]
            if opening:
                p.line(inner_wall[5:-5], 6, 5)
            else:
                wall = [(x+side*(1+7*sin(pi*i/40)**.7), y-82+164*i/40)
                        for i in range(41)]
                p.line(wall, 9, 8)
            for dx, dy, radius in [(38,-60,5),(49,-30,7),(52,-12,5),
                                   (53,22,6),(44,44,7),(31,59,5)]:
                px = x+side*(dx+opening*.22)
                p.disc(px, y+dy+side*4, radius, 7)
                p.disc(px-2, y+dy+side*4-2, radius*.46, 11)
            p.ellipse(x+side*(37+opening*.25), y+side*9, 10, 15, 9, n=36)

    specimen(174, 30)
    specimen(466, 0)
    p.line([(466,159),(466,329)], 7, 3)
    p.label(34, 409, 'OPEN / HIGH TURGOR', 24, 6)
    p.label(332, 409, 'CLOSED / LOW TURGOR', 24, 6)
    p.line([(34,424),(607,424)], 3, 2)
    for x, label, target, path in [
        (34, '1 GUARD CELL', (119,273), [(84,287)]),
        (228, '2 NUCLEUS', (218,253), [(272,255)]),
        (374, '3 INNER WALL', (158,296), [(119,327)]),
    ]:
        p.line([target, *path], 1, 2)
        p.disc(*target, 4, 1)
        bx, by = path[-1]
        p.disc(bx, by, 12, 0)
        p.label(bx-7, by+7, label[0], 21)
        p.label(x, 452, label, 25)

    p.label(374, 476, 'THICKENED', 21, 6)
    return p


if __name__ == '__main__':
    save(__file__, build())
