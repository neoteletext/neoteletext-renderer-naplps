from random import Random

from _support import Page, save

META = dict(title='The Lure', purpose='An anglerfish materialising beyond a dive light',
            style='Abyssal silhouettes in petrol blue and acid green',
            techniques=['WAIT staging', 'palette redefinition', 'open arcs', 'layered polygons'],
            animated=True)


def build():
    p = Page('060c1a 0d192b 142b41 1b4050 245c65 3d8882'
             ' 9ac7a0 ebffc4 6b5577 94678c 1b4050'.split())
    p.poly([(0, 65), (515, 160), (605, 315), (0, 446)], 1)
    p.poly([(0, 127), (448, 198), (523, 303), (0, 366)], 2)
    rng = Random(122)
    for _ in range(34):
        x, y = rng.randrange(8, 468), rng.randrange(152, 342)
        if 130 + x / 7 < y < 364 - x / 9:
            p.rect(x, y, rng.choice([1, 2, 3]), 2, rng.choice([3, 4]))
    p.text(28, 43, 'THE LURE', 25, 32, 6)
    p.text(29, 462, 'BATHYPELAGIC / 1400 M', 21, 27, 6)
    p.wait(10)

    # The tail and belly arrive as one dark shape.
    p.poly([(93, 248), (130, 245), (195, 264), (239, 229), (291, 200),
            (358, 191), (408, 206), (454, 228), (478, 259), (478, 288),
            (454, 319), (398, 350), (341, 361), (280, 343), (220, 319),
            (183, 289), (139, 302), (94, 325), (117, 281)], 0)
    p.poly([(206, 274), (254, 230), (316, 204), (363, 201), (407, 215),
            (458, 239), (399, 233), (344, 242), (293, 265), (254, 288)], 10)
    p.poly([(197, 281), (146, 263), (104, 255), (131, 279), (111, 307),
            (154, 289)], 3)
    p.poly([(223, 240), (238, 210), (226, 170), (267, 189), (287, 168),
            (309, 187), (337, 153), (343, 194)], 3)
    p.poly([(292, 297), (225, 316), (267, 326), (246, 349), (304, 341),
            (335, 313)], 4)
    p.poly([(309, 306), (372, 277), (432, 266), (490, 265),
            (468, 304), (417, 331), (363, 335)], 8)
    p.poly([(327, 307), (391, 283), (478, 273), (449, 304), (405, 322),
            (370, 325)], 0)
    p.wait(7)

    # A single new entry changes the whole back as the lure lights up.
    p.pel(2).arc((367, 211), (454, 111), (536, 185), 5)
    p.set_palette(10, '357575')
    p.circle(538, 187, 25, 3)
    p.circle(538, 187, 15, 5, False)
    p.circle(538, 187, 8, 7)
    for start, end in [((538, 151), (538, 158)), ((567, 169), (575, 164)),
                       ((568, 203), (577, 208)), ((538, 217), (538, 225))]:
        p.line([start, end], 6, 2)
    p.circle(410, 241, 14, 5)
    p.circle(413, 240, 8, 6)
    p.circle(416, 238, 4, 0)
    for x, y, length in [(374, 287, 12), (401, 281, 19), (429, 277, 22),
                         (454, 273, 17), (394, 324, 11), (421, 316, 13),
                         (447, 305, 12)]:
        direction = 1 if y < 290 else -1
        p.poly([(x - 5, y), (x + 5, y), (x + 4, y + length * direction)], 7)
    for x, y in [(258, 267), (283, 253), (312, 238), (336, 232), (355, 226)]:
        p.circle(x, y, 2.5, 6)
    return p


if __name__ == '__main__':
    save(__file__, build())
