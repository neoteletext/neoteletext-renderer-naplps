from math import hypot
from random import Random
from _canvas import Canvas, write_page

META = dict(title='Rabbit in the Wall', purpose='A hand and its improbable shadow share one stage',
            style='Amber shadow theatre on a plaster wall',
            techniques=['dithered radial illumination', 'rounded silhouette polygons', 'open crease arcs'],
            animated=False)


def build():
    p = Canvas('231822 35232a 85432f f4be79 ffcf86 ffdf9d a65338 cf7150'
               ' f7a676 5a3734 aa684a d99763 e7b475 302027 3b292e 1a151e')
    p.poly([(0, 267), (640, 138), (640, 401), (0, 401)], 13)
    rng = Random(149)
    ramp = (1, 9, 2, 10, 11, 12, 3, 4, 5)
    # Short plaster grains bridge the palette steps. The same light field
    # determines both the base colour and the probability of a brighter grain.
    for row in range(6, 399, 2):
        last = None
        for x in range(0, 642, 2):
            distance = hypot((x-400)/220, (row-201)/181)
            light = max(0, min(8, (1.06-distance)*12.4))
            level = int(light)
            if rng.random() < light-level:
                level += 1
            ink = ramp[level] if distance < 1.12 and level else None
            if ink != last:
                if last is not None:
                    p.rect(start, row, min(639.7, x)-start, 2, last)
                start, last = x, ink
    for _ in range(550):
        x, y = rng.uniform(8, 631), rng.uniform(10, 392)
        distance = hypot((x-400)/220, (y-201)/181)
        ink = 4 if distance < .35 else 14 if distance > 1.05 else None
        if ink is not None:
            p.line([(x, y), (x+rng.uniform(1, 5), y-.7)], ink, 1)

    def rounded(points, ink):
        corners = []
        for a, b in zip(points, points[1:] + points[:1]):
            corners.extend((tuple(.86*x+.14*y for x, y in zip(a, b)),
                            tuple(.14*x+.86*y for x, y in zip(a, b))))
        p.poly(corners, ink)
    # A rabbit formed entirely by the shadow, with a sliver of light for an eye.
    p.poly([(0, 370), (159, 333), (277, 325), (331, 304),
            (321, 353), (260, 372), (133, 379), (0, 401)], 9)
    rounded([(-14, 398), (-14, 380), (149, 344), (216, 335), (278, 333), (313, 315), (343, 295), (360, 251), (381, 217),
            (363, 145), (363, 106), (372, 84), (388, 94), (404, 133),
            (415, 194), (432, 119), (450, 81), (464, 78), (472, 95),
            (467, 124), (450, 207), (478, 229), (500, 235), (514, 251),
            (497, 269), (470, 278), (464, 294), (439, 305), (415, 302),
            (416, 322), (441, 330), (455, 342), (441, 350), (402, 355), (358, 354), (324, 349), (266, 365), (204, 362), (126, 367)], 15)
    p.pel(2).arc((455, 243), (459, 238), (466, 240), 4)
    # Foreground fingers overlap in a simpler silhouette, lit from the right.
    rounded([(-25, 334), (103, 283), (142, 249), (158, 206), (151, 148),
            (156, 128), (170, 124), (182, 142), (192, 200), (202, 188),
            (217, 122), (232, 106), (246, 113), (244, 143), (231, 204),
            (254, 215), (264, 232), (252, 249), (226, 253), (209, 282),
            (186, 301), (139, 315), (-25, 412)], 6)
    p.poly([(-10, 327), (103, 283), (142, 249), (158, 206), (151, 148),
            (156, 128), (170, 124), (163, 157), (174, 212), (159, 264),
            (126, 297), (-10, 361)], 7)
    p.poly([(202, 188), (217, 122), (232, 106), (246, 113),
            (229, 125), (211, 194)], 8)
    p.pel(3).arc((186, 240), (207, 216), (234, 222), 8)
    p.pel(3).arc((170, 268), (187, 246), (205, 245), 2)
    p.line([(236, 219), (247, 225), (249, 233), (239, 239), (219, 240)], 2, 3)
    p.line([(206, 254), (224, 253), (235, 247)], 8, 2)
    p.line([(157, 159), (168, 157)], 8, 2)
    p.line([(224, 151), (237, 154)], 8, 2)
    p.line([(144, 298), (172, 275), (182, 252)], 2, 3)
    p.line([(223, 169), (226, 157), (231, 143)], 7, 2)
    p.ellipse(165, 136, 10, 13, 7, n=40)
    p.ellipse(233, 119, 11, 13, 8, n=40)
    p.pel(3).arc((163, 192), (167, 211), (161, 238), 8)
    p.pel(4).arc((187, 270), (204, 257), (225, 254), 7)
    p.pel(3).arc((201, 230), (218, 224), (231, 232), 7)
    p.text(39, 458, 'RABBIT IN THE WALL', 29, 37, 5)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
