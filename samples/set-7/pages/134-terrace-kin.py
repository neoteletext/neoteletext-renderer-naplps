"""A settlement game played on an ascending chain of garden terraces."""
import _local
from encoder.screen import Screen, save

META = dict(title='Terrace Kin', purpose='Building screen with a terrace selected for planting',
            style='Axonometric clay gardens on a bright apricot field',
            techniques=['axonometric polygon tiles', 'occlusion order', 'connected contour lines', 'logical pels'],
            animated=False)

# Row order is also depth order. Heights are lifted from a common base plane.
PLOTS = [
    (319, 148, 45, 6), (225, 196, 33, 7), (413, 196, 44, 6),
    (131, 244, 17, 7), (319, 244, 58, 8), (507, 244, 14, 7),
    (225, 292, 25, 6), (413, 292, 23, 7), (319, 340, 18, 8),
]


def build():
    p = Screen('f4be83 432756 70425d be6d61 ee9473 f9dfa8'
               ' 478578 a9ae65 f2b95c 31605f fbebc2 9f555c 79b8b3 376b74 af875f 74475d')
    p.text(26, 56, 'TERRACE KIN', 42, 51, 1)
    p.poly([(13, 288), (319, 129), (626, 288), (626, 303),
            (319, 418), (13, 303)], 11)
    p.poly([(319, 406), (626, 288), (626, 303), (319, 418)], 2)
    p.poly([(13, 288), (319, 129), (626, 288), (319, 406)], 4)
    p.line([(24, 288), (319, 139), (615, 288), (319, 401), (24, 288)], 14, 3)
    for x, y in [(82, 307), (105, 325), (146, 344), (180, 366),
                 (241, 379), (367, 382), (432, 369), (497, 340), (556, 308)]:
        p.poly([(x-8, y+2), (x-4, y-3), (x+6, y-3), (x+11, y+1)], 14)
    p.line([(31, 292), (319, 398), (605, 294)], 9, 8)
    p.line([(31, 292), (319, 398), (605, 294)], 12, 4)
    for x, base, elevation, ink in PLOTS:
        y = base - elevation
        top, right, near, left = (x, y-44), (x+86, y), (x, y+44), (x-86, y)
        p.poly([left, near, (x, base+44), (x-86, base)], 2)
        p.poly([near, right, (x+86, base), (x, base+44)], 3)
        for course in range(9, elevation-3, 10):
            p.line([(left[0], left[1]+course), (near[0], near[1]+course)], 15, 2)
            p.line([(near[0], near[1]+course), (right[0], right[1]+course)], 11, 2)
        p.poly([top, right, near, left], 14 if ink == 6 else ink)
        if ink == 6:
            for offset in (-21, 0, 21):
                start = (x-43+offset, y-offset/2)
                end = (x+offset, y+21-offset/2)
                p.line([start, end], 11, 7)
                p.line([(start[0]+2, start[1]-3), (end[0], end[1]-3)], 5, 2)
                if base != 148:
                    for fraction in (.18, .48, .78):
                        sx = start[0] + (end[0]-start[0])*fraction
                        sy = start[1] + (end[1]-start[1])*fraction - 3
                        p.line([(sx, sy), (sx, sy-8)], 9, 2)
                        p.poly([(sx, sy-4), (sx-6, sy-11), (sx+1, sy-9),
                                (sx+6, sy-13), (sx+4, sy-6)], 6)
        if ink == 7:
            for offset in (-38, 0, 38):
                p.line([(x+offset, y+6), (x+offset, y-14)], 9, 3)
                for side in (-1, 1):
                    p.poly([(x+offset, y-4), (x+offset+side*15, y-11),
                            (x+offset+side*17, y-20), (x+offset, y-14)], 6)
                if x in (131, 413):
                    p.disk(x+offset, y-18, 5, 5)
                    p.disk(x+offset, y-18, 2, 3)
                else:
                    p.line([(x+offset, y-14), (x+offset+4, y-23)], 9, 2)
        if (x, base) == (319, 244):
            p.poly([(x, y-32), (x+62, y), (x, y+32), (x-62, y)], 13)
            p.poly([(x, y-24), (x+48, y), (x, y+24), (x-48, y)], 12)
            p.line([(x-27, y), (x-8, y+10), (x+24, y+10)], 10, 2)
            p.ellipse(x, y-8, 24, 11, 13, False)
            p.ellipse(x, y-8, 13, 6, 10, False)
            p.line([(x, y-8), (x, y-38)], 12, 4)
            for side in (-1, 1):
                p.pel(2).arc((x, y-37), (x+side*13, y-33),
                             (x+side*22, y-15), 10)
                p.disk(x+side*22, y-13, 2, 10)
            p.poly([(x-13, y+25), (x, y+32), (x, y+74), (x-13, y+67)], 13)
            p.line([(x+21, y+24), (x+51, y+9)], 12, 3)
        if (x, base) == (319, 340):
            p.line([top, right, near, left, top], 10, 4)
            p.line([(x-69, y+8), (x-38, y-7), (x+25, y+24)], 9, 7)
            p.line([(x-69, y+8), (x-38, y-7), (x+25, y+24)], 12, 3)
            # Ghosted crop row shows what the planting action will place.
            for dx, dy in [(-23, -11), (0, 0), (23, 11)]:
                sx, sy = x+dx, y+dy
                p.ellipse(sx, sy+3, 10, 5, 14, n=16)
                p.line([(sx, sy+4), (sx, sy-12)], 9, 3)
                p.poly([(sx, sy-3), (sx-11, sy-8), (sx-12, sy-14),
                        (sx-4, sy-12)], 10)
                p.poly([(sx, sy-7), (sx+3, sy-16), (sx+11, sy-19),
                        (sx+8, sy-11)], 5)
    # Follow the exposed edge of the lower bed before joining the foot channel.
    spillway = [(311, 218), (311, 264), (225, 309), (225, 338), (194, 352)]
    p.line(spillway, 9, 9)
    p.line(spillway, 12, 4)
    for x, y in [(311, 231), (311, 247), (225, 318), (225, 328)]:
        p.line([(x, y), (x, y+6)], 10, 2)
    # A sluice branches into the selected bed at its exposed corner.
    p.line([(225, 329), (236, 324), (236, 332), (250, 330)], 9, 8)
    p.line([(225, 329), (236, 324), (236, 332), (250, 330)], 12, 4)
    p.line([(235, 322), (240, 326)], 10, 3)
    p.ellipse(194, 352, 12, 5, 9)
    p.ellipse(194, 352, 7, 3, 12)
    p.rect(0, 423, 639.6, 56.6, 1)
    p.text(26, 460, 'A  PLANT', 28, 36, 10)
    p.text(445, 460, 'SEED  06', 26, 34, 10)
    return p


if __name__ == '__main__':
    save(__file__, build())
