"""Oblique view of a conventional rock-salt cell."""
from itertools import product
from _drawing import Page, save

META = dict(title='Salt in Three Dimensions', purpose='Show alternating sodium and chloride sites and six nearest neighbours',
            style='Ivory crystallographic plate with coral and teal ions',
            techniques=['oblique projection', 'depth ordering', 'native circles'], animated=False)


def build():
    p = Page('f2ead6 202a31 117f80 963f39 c8dbd1 7abeb0 e58372 657771 e5dcc6 534839 0e6467 a75149 b7782e a1c6bc 80aaa5 fff4d7')
    p.rect(430, 0, 209.7, 479.7, 4)
    p.label(29, 65, 'SALT IN THREE', 43)
    p.label(29, 108, 'DIMENSIONS', 43)
    p.label(34, 149, 'ROCK SALT / NaCl', 27, 2)

    def project(i, j, k):
        return 78+116*i+42*j, 227-23*j+99*k

    sites = list(product(range(3), repeat=3))
    for i, j, k in sites:
        for axis, coordinate in enumerate((i, j, k)):
            if coordinate < 2:
                end = [i, j, k]
                end[axis] += 1
                fixed = [value for dim, value in enumerate((i, j, k)) if dim != axis]
                boundary = all(value in (0, 2) for value in fixed)
                front = j == 0 and axis != 1
                p.line([project(i, j, k), project(*end)],
                       7 if boundary and front else 14 if boundary else 8,
                       2 if boundary else 1)
    centre_site = (1, 1, 1)
    neighbours = {site for site in sites
                  if sum(abs(a-b) for a, b in zip(site, centre_site)) == 1}
    for site in sorted(neighbours):
        p.line([project(*centre_site), project(*site)], 12, 4)
    for i, j, k in sorted(sites, key=lambda site: -site[1]):
        x, y = project(i, j, k)
        sodium = (i+j+k) % 2
        radius = 11 if sodium else 17
        if (i, j, k) in neighbours or (i, j, k) == centre_site:
            p.disc(x, y, radius+4, 12)
        p.disc(x, y, radius, (3 if sodium else 2) if j == 0 else (11 if sodium else 10))
        p.disc(x-3, y-4, radius*.56, 6 if sodium else 5)
    p.label(35, 465, 'ONE CUBIC UNIT CELL', 25, 2)
    p.disc(463, 57, 11, 3).disc(460, 53, 6, 6)
    p.label(487, 67, 'Na+', 31)
    p.disc(463, 106, 17, 2).disc(460, 102, 9, 5)
    p.label(487, 116, 'Cl-', 31)

    p.line([(449,141),(620,141)], 12, 3)
    p.label(449, 170, 'Na+ CENTRE', 23)
    p.label(449, 190, 'ENLARGED', 21, 9)
    p.line([(357,315),(378,333),(422,333)], 12, 2)
    p.arrow((422,333),(490,333),12,2,9)
    # Six chloride neighbours about a sodium ion, in an octahedron.
    centre = (535, 286)
    ring = [(463, 286), (509, 328), (607, 286), (561, 244)]
    tips = [(535, 194), (535, 378)]
    left, front, right, back = ring
    top, bottom = tips
    for a, b, tip, shade in [(left, front, top, 13), (front, right, top, 4),
                              (left, front, bottom, 14), (front, right, bottom, 13)]:
        p.poly([a, b, tip], shade)
        p.line([a, tip, b], 7, 2)
    p.line([left, front, right], 7, 2)
    p.texture(line=2)
    for path in ([left, back, right], [top, back, bottom]):
        p.line(path, 2, 2)
    p.texture()
    for site in [left, right, top, bottom, back, front]:
        p.texture(line=2 if site == back else 0).line([centre, site], 12, 3).texture()
        p.disc(*site, 13, 12).disc(*site, 10, 10 if site == back else 2)
    p.disc(*centre, 12, 12).disc(*centre, 8, 3)
    p.label(450, 424, '6 CHLORIDE', 25)
    p.label(450, 453, 'NEIGHBOURS', 25)
    return p


if __name__ == '__main__':
    save(__file__, build())
