"""Travel map for a game in which drained lakes become roads."""
import _local
from encoder import Page, xy
from encoder.screen import Screen, save

META = dict(title='Siltfold', purpose='Travel map showing the footpath unlocked at low water',
            style='Parchment flood chart with indigo pools and vermilion wayfinding',
            techniques=['defined fill texture', 'filled shoreline polygons', 'dashed connected lines', 'native discs'],
            animated=False)

BASIN = [(27, 290), (72, 257), (93, 219), (165, 198), (221, 209), (261, 185),
         (272, 137), (324, 109), (365, 126), (391, 179), (436, 185),
         (478, 155), (532, 150), (582, 180), (609, 226), (577, 269),
         (503, 285), (462, 316), (422, 360), (354, 368), (322, 348),
         (284, 349), (241, 390), (175, 391), (121, 351), (66, 341)]


def build():
    p = Screen('e7d6ab 50362f c4a477 9e805b 29546c 9f4735 fff0c9 795c4d c3a877 78a0a2 af9274 3c6e81')
    for contour in [
        [(9, 251), (65, 214), (74, 189), (161, 171), (220, 183), (241, 159)],
        [(11, 225), (48, 197), (60, 173), (151, 156), (209, 165)],
        [(254, 125), (274, 95), (322, 77), (380, 101), (407, 150)],
        [(402, 136), (460, 119), (519, 114), (578, 137), (625, 173)],
        [(96, 369), (148, 406), (222, 409), (267, 386), (289, 371)],
        [(388, 394), (437, 388), (469, 365), (488, 338)],
    ]:
        p.line(contour, 8, 2)
    p.poly(BASIN, 2)
    ripple = Page().cmd(0x33, xy(.10, .40) + xy(.54, .10))
    p.hatch(b'A', ripple, 19, 12)
    p.poly(BASIN, 3).texture()
    # The old shoreline survives above the residual pools.
    p.texture(line=2).line(BASIN + BASIN[:1], 7, 2).texture()
    for x, y in [(86, 254), (184, 206), (292, 143), (361, 138),
                 (478, 169), (566, 175), (575, 252), (406, 344), (184, 378)]:
        p.line([(x-7, y+2), (x+8, y-3)], 7, 2)
    # A surviving trickle links the two pools across the exposed saddle.
    creek = [(349, 248), (341, 259), (323, 262), (308, 271),
             (307, 288), (324, 298), (347, 299), (370, 313)]
    p.line(creek, 8, 15)
    p.line(creek, 11, 7)
    p.line([(341, 259), (323, 262), (308, 271), (307, 288),
            (324, 298), (347, 299)], 9, 2)
    for pool in [
        [(44, 289), (101, 269), (130, 234), (189, 226), (231, 244), (240, 272),
         (210, 313), (157, 340), (114, 322), (73, 325)],
        [(294, 159), (325, 132), (354, 149), (371, 195), (420, 212), (427, 251),
         (381, 269), (320, 251), (290, 223)],
        [(455, 248), (505, 189), (547, 175), (580, 201), (587, 227), (545, 250), (490, 265)],
        [(342, 304), (392, 291), (444, 306), (415, 339), (364, 347), (339, 325)],
    ]:
        p.poly(pool, 9)
        cx = sum(x for x, _ in pool) / len(pool)
        cy = sum(y for _, y in pool) / len(pool)
        p.poly([(cx+(x-cx)*.93, cy+(y-cy)*.87) for x, y in pool], 11)
        p.poly([(cx+(x-cx)*.82, cy+(y-cy)*.73+3) for x, y in pool], 4)
        for dx, dy, span, ink in [(-30, -9, 23, 9), (-7, 2, 22, 11),
                                   (-18, 9, 13, 11), (9, 8, 19, 9)]:
            p.line([(cx+dx, cy+dy), (cx+dx+span, cy+dy)], ink, 2)
    nodes = [(115, 367), (251, 302), (299, 278), (457, 277), (529, 311)]
    p.line(nodes, 6, 7)
    p.texture(line=2).line(nodes, 5, 3).texture()
    # Masonry across the shallow neck, underneath the ford marker.
    p.poly([(277, 279), (329, 266), (336, 284), (282, 298)], 7)
    for step in range(6):
        x, y = 279+8*step, 282-2*step
        p.poly([(x, y), (x+6, y-1), (x+9, y+8), (x+3, y+10)], 6)
    for x, y in [nodes[i] for i in (0, 4)] + [(300, 263)]:
        p.disk(x, y, 13, 6).disk(x, y, 9, 5).disk(x, y, 3, 6)
    p.text(28, 68, 'SILTFOLD', 52, 62, 1)
    p.text(359, 66, 'LOW WATER', 27, 34, 5)
    p.rect(21, 375, 77, 39, 6)
    p.line([(21, 375), (98, 375), (105, 372)], 5, 2)
    p.text(27, 407, 'WEIR', 24, 30, 1)
    p.rect(236, 205, 83, 38, 6)
    p.line([(236, 243), (319, 243)], 5, 2)
    p.line([(288, 243), (294, 253)], 5, 2)
    p.text(246, 235, 'FORD', 24, 30, 1)
    p.poly([(54, 330), (65, 322), (96, 322), (105, 330)], 6)
    p.rect(55, 330, 49, 5, 5)
    for x in (58, 71, 84, 97):
        p.rect(x, 334, 5, 15, 5)
    p.line([(56, 344), (102, 344)], 6, 2)
    p.poly([(548, 288), (570, 274), (592, 288)], 5)
    p.line([(552, 320), (552, 288), (587, 288), (587, 320)], 5, 3)
    p.rect(560, 302, 19, 13, 5)
    p.line([(569, 288), (569, 302)], 5, 2)
    p.rect(482, 328, 83, 35, 6)
    p.line([(482, 328), (565, 328)], 5, 2)
    p.line([(527, 323), (527, 328)], 5, 2)
    p.text(489, 356, 'LIFT', 24, 30, 1)
    p.line([(27, 429), (611, 429)], 8)
    p.text(28, 461, 'WALK TO THE LIFT', 24, 30, 5)
    return p


if __name__ == '__main__':
    save(__file__, build())
