from math import cos, radians, sin

from _support import Page, save

META = dict(title='Afterimage', purpose='A mechanical iris with a travelling pulse',
            style='Radial precision instrument in teal, violet and lime',
            techniques=['relative polygon vertices', 'native circles', 'phase-offset BLINK'],
            animated=True)


def build():
    p = Page('101325 252943 423968 305363 7c68a2 b4ffe6 f3fb9d'
             ' 454475 524276 584477 514378 43447a 3e467e 1c243b 506f80 302a54'.split())
    cx, cy = 320, 220
    scale = .91

    def at(radius, angle):
        a = radians(angle)
        return cx + scale * radius * cos(a), cy + scale * radius * sin(a)

    for radius, ink in [(220, 13), (217, 14), (214, 1), (205, 13),
                        (201, 2), (198, 1), (186, 3), (177, 0)]:
        p.circle(cx, cy, radius * scale, ink)
    # Cut the ring gear into the outer edge of the housing.
    for i in range(48):
        angle = i * 7.5
        p.poly([at(r, angle + d) for r, d in
                [(215, -2.7), (223, -2.2), (225, -.9),
                 (225, 1.2), (222, 2.2), (215, 2.7)]], 3)
        p.line([at(221, angle - 1.8), at(224, angle - .8),
                at(224, angle + 1.1)], 14)
    for i in range(12):
        angle = i * 30
        p.poly([at(r, angle + d) for r, d in
                [(186, -2), (197, -2), (197, 2), (186, 2)]], 14)
        for delta in (-7, 7):
            p.line([at(191, angle + delta), at(196, angle + delta)], 0, 2)
        p.circle(*at(202, angle + 15), 2.5, 0)
        p.line([at(201, angle + 15), at(203, angle + 15)], 4)
    for i in range(96):
        a = i * 3.75
        major = i % 8 == 0
        p.line([at(206 if major else 210, a), at(214, a)],
               5 if major else 14, 2 if major else 1)
    for i in range(12):
        a = 30 * i

        def blade(points, ink):
            p.poly([at(r, a + offset) for r, offset in points], ink)

        blade([(172, 0), (172, 26), (142, 37), (106, 51), (69, 79),
               (47, 109), (49, 79), (81, 47), (123, 21)], 15)
        blade([(166, 3), (166, 25), (139, 36), (103, 50), (68, 77),
               (51, 100), (56, 72), (83, 44), (124, 20)], 1 if i % 2 else 15)
        blade([(169, 24), (142, 36), (106, 50), (68, 78), (50, 104),
               (55, 83), (76, 66), (108, 44), (143, 31)], 2)
        blade([(164, 5), (161, 8), (127, 24), (93, 42), (66, 65),
               (83, 44), (124, 20)], 4)
        blade([(157, 11), (139, 18), (118, 30), (100, 44),
               (114, 31), (138, 16)], 15)
        p.line([at(161, a + 13), at(148, a + 18), at(131, a + 25),
                at(114, a + 35), at(97, a + 48)], 3, 2)
        for radius, offset in [(156, 15), (139, 21), (121, 31)]:
            p.circle(*at(radius, a + offset), 2.8, 13)
            p.circle(*at(radius + 1, a + offset), 1.2, 14)
        # Recessed lamp channels stay inside the blade face.
        blade([(164, 15), (161, 23), (137, 32), (111, 45), (84, 61),
               (70, 73), (82, 55), (107, 38), (135, 25)], 0)
        blade([(158, 17), (156, 21), (134, 30), (108, 43), (81, 64),
               (107, 40), (135, 27)], 7 + i % 6)
        p.line([at(150, a + 22), at(128, a + 32), at(105, a + 45),
                at(89, a + 56)], 7 + (i + 1) % 6)
        for radius, offset in [(152, 18), (138, 24), (123, 32)]:
            p.line([at(radius, a + offset), at(radius, a + offset + 5)], 0)
        p.line([at(158, a + 8), at(126, a + 21), at(99, a + 36),
                at(75, a + 55)], 14, 2)
        for r, offset in [(146, 14), (134, 19), (122, 25)]:
            p.line([at(r, a + offset), at(r, a + offset + 3)], 13, 2)
    for radius, ink in [(46, 13), (43, 14), (40, 2), (36, 0), (30, 3), (27, 0)]:
        p.circle(cx, cy, radius * scale, ink)
    for angle in range(0, 360, 60):
        p.circle(*at(34, angle), 2, 14)
    for radius, ink in [(25, 15), (21, 2), (16, 13), (12, 3), (6, 0)]:
        p.circle(cx, cy, radius * scale, ink)
    for radius, start, end, ink in [(23, 202, 285, 4), (19, 20, 111, 14),
                                     (14, 190, 252, 5)]:
        p.line([at(radius, angle) for angle in range(start, end, 4)], ink, 2)
    p.circle(cx - 5, cy - 6, 2.2, 5)
    for angle in range(0, 360, 60):
        p.line([at(25, angle), at(29, angle)], 14, 2)
    for side in (-1, 1):
        def mount(points, ink):
            p.poly([(cx + side * x, cy + y) for x, y in points], ink)

        mount([(200, -19), (216, -19), (223, -43), (254, -43), (269, -32),
               (269, 32), (254, 43), (223, 43), (216, 19), (200, 19)], 3)
        mount([(205, -11), (222, -11), (230, -37), (251, -37), (262, -28),
               (262, 28), (251, 37), (230, 37), (222, 11), (205, 11)], 13)
        mount([(202, -7), (236, -7), (247, -16), (253, -16), (253, 16),
               (247, 16), (236, 7), (202, 7)], 14)
        p.line([(cx + side * x, cy + y) for x, y in
                [(207, -3), (238, -3), (248, -12)]], 5, 2)
        for y in (-26, 26):
            x = cx + side * 241
            p.circle(x, cy + y, 6, 14)
            p.circle(x, cy + y, 4, 0)
            p.line([(x - 3, cy + y + 2), (x + 3, cy + y - 2)], 4)

        for y in (-16, 16):
            p.line([(cx + side * 208, cy + y), (cx + side * 226, cy + y),
                    (cx + side * 237, cy + 2 * y)], 14)
            p.rect(cx + side * 251 - 2, cy + y - 2, 4, 4, 5)

    p.text(24, 454, 'AFTERIMAGE', 22, 30, 5)
    p.text(441, 449, 'PHASE / 06', 22, 28, 5)
    for i in range(6):
        x = 444 + 27 * i
        p.rect(x - 2, 453, 25, 12, 14)
        p.rect(x - 1, 454, 23, 10, 13)
        p.rect(x + 1, 457, 19, 4, 7 + i)
        p.line([(x + 11, 456), (x + 11, 462)], 13)
        p.blink(7 + i, 6, on=2, off=10, delay=2 if i else 0)
    return p


if __name__ == '__main__':
    save(__file__, build())
