"""Story Time: The Garden, a children's story picture that grows as it draws: seed, shoot, leaves, flower."""
from _screen import Plate, oval, polar, save

META = dict(
    title='Story Time: The Garden',
    purpose="A children's story page whose picture draws itself as an animation while the line of text waits below",
    style='Picture-book flat colour: a soil cross-section, a kneeling child and a flower that opens',
    techniques=['WAIT growth stages', 'petals hidden in sky colour then revealed by SET COLOR',
                'filled arcs and rotated petal polygons', 'soil cross-section in layered polygons',
                'a bee arriving in the last stage', 'page dots', 'a picket fence, cottage and clouds for setting', 'drop capital', 'grass tufts and a snail', 'proportional story text'],
    animated=True,
)

PALETTE = ('9fdcff 2d6a4f fff6e0 7a4a26 4e2e17 3aa655 1f7a3a 9fdcff '
           '9fdcff ffd23f ffe066 f1c39a 3a6fd8 5a2e1a 1d2433 4fa3c8')
(SKY, BAND, CREAM, SOIL, DEEP_SOIL, STEM, LEAF, PETAL,
 PETAL_EDGE, CENTRE, SUN, SKIN, DRESS, HAIR, INK, WATER) = range(16)

PLANT_X = 360
GROUND = 262


def leaf(p, x, y, length, angle, ink):
    tip = polar(x, y, length, angle)
    left = polar(x, y, length * 0.55, angle - 25)
    right = polar(x, y, length * 0.55, angle + 25)
    p.poly([(x, y), left, tip, right], ink)


def build():
    p = Plate(PALETTE, SKY)
    p.rect(0, 0, 640, 52, BAND)
    p.text(18, 36, 'BEDTIME', 18, 26, SUN, prop=False)
    p.text(166, 34, 'THE GARDEN', 14, 20, CREAM, prop=False)
    # Five page dots, the third lit: page 3 of 5.
    for k in range(5):
        if k == 2:
            p.disc(440 + k * 24, 27, 8, SUN)
        else:
            p.disc(440 + k * 24, 27, 5, CREAM)
    p.text(580, 34, '222', 12, 18, SUN, prop=False)

    # Two soft clouds.
    for cx, cy in ((96, 92), (300, 70)):
        p.poly(oval(cx, cy, 44, 14, 20), CREAM)
        p.disc(cx - 14, cy - 8, 16, CREAM)
        p.disc(cx + 12, cy - 12, 20, CREAM)
    # Sun, hills and the soil in cross-section, with stones and a worm.
    p.disc(560, 104, 34, SUN)
    for k in range(12):
        a = k * 30
        p.line([polar(560, 104, 42, a), polar(560, 104, 56, a)], SUN, 3)
    # A picture-book sun with a face.
    p.disc(548, 98, 4, SOIL)
    p.disc(572, 98, 4, SOIL)
    p.arc((546, 114), (560, 122), (574, 114), SOIL)
    p.poly(oval(120, GROUND, 180, 40, 32), STEM)
    p.poly(oval(560, GROUND, 160, 30, 32), LEAF)
    # Wren's cottage on the far hill, and the garden's picket fence.
    p.rect(470, 206, 44, 30, CREAM)
    p.poly([(464, 208), (492, 186), (520, 208)], PETAL_EDGE)
    p.rect(504, 188, 7, 12, SOIL)
    p.rect(478, 214, 10, 10, CENTRE)
    p.rect(496, 220, 10, 16, SOIL)
    p.rect(412, 238, 228, 4, CREAM)
    p.rect(412, 250, 228, 4, CREAM)
    for x in range(418, 640, 22):
        p.poly([(x, 262), (x, 232), (x + 5, 226), (x + 10, 232), (x + 10, 262)], CREAM)
    p.rect(0, GROUND, 640, 92, SOIL)
    p.poly([(0, 300), (160, 292), (320, 306), (480, 294), (640, 304), (640, 354), (0, 354)], DEEP_SOIL)
    for x, y in ((60, 320), (210, 334), (520, 326), (600, 286)):
        p.poly(oval(x, y, 12, 7, 10), INK)
    # Tufts of grass along the edge of the soil.
    for x in range(10, 640, 34):
        if abs(x - PLANT_X) > 20:
            p.poly([(x, GROUND + 2), (x + 4, GROUND - 10), (x + 7, GROUND - 2), (x + 11, GROUND - 13),
                    (x + 13, GROUND - 1), (x + 18, GROUND - 8), (x + 18, GROUND + 2)], LEAF)
    # A snail on its way across the soil by the fence.
    p.poly([(570, GROUND + 1), (612, GROUND + 1), (606, GROUND - 6), (576, GROUND - 6)], SKIN)
    p.line([(608, GROUND - 4), (614, GROUND - 16)], INK, 1)
    p.line([(604, GROUND - 4), (606, GROUND - 16)], INK, 1)
    p.disc(588, GROUND - 12, 11, CENTRE)
    p.arc((588, GROUND - 19), (595, GROUND - 12), (588, GROUND - 5), SOIL)
    p.arc((588, GROUND - 5), (583, GROUND - 11), (589, GROUND - 15), SOIL)
    p.line([(470, 282), (480, 278), (490, 284), (500, 278), (510, 284)], PETAL_EDGE, 4)
    p.recolour(PETAL_EDGE, 'ff9ab8')
    p.wait(6, 'soil')

    # The seed and its roots.
    p.poly(oval(PLANT_X, 300, 12, 8, 12), CENTRE)
    for end in ((PLANT_X - 30, 336), (PLANT_X + 4, 344), (PLANT_X + 28, 330)):
        p.line([(PLANT_X, 306), end], CREAM, 2)
    p.wait(8, 'seed')

    # The shoot, then the stem and leaves.
    p.line([(PLANT_X, 296), (PLANT_X, 236)], STEM, 6)
    leaf(p, PLANT_X, 246, 26, -150, STEM)
    p.wait(8, 'shoot')
    p.line([(PLANT_X, 236), (PLANT_X + 4, 170), (PLANT_X, 128)], STEM, 6)
    leaf(p, PLANT_X + 2, 214, 56, -160, LEAF)
    leaf(p, PLANT_X + 4, 186, 60, -20, LEAF)
    p.disc(PLANT_X, 126, 14, LEAF)
    # A ladybird on the upper leaf.
    p.disc(404, 172, 7, PETAL_EDGE)
    p.line([(404, 165), (404, 179)], INK, 1)
    p.disc(410, 168, 3, INK)
    p.disc(401, 175, 2, INK)
    p.disc(407, 177, 2, INK)
    p.wait(8, 'bud')

    # The petals are drawn already, in entries the colour of the sky; SET COLOR opens the flower.
    for k in range(10):
        a = k * 36
        cx, cy = polar(PLANT_X, 120, 30, a)
        p.poly([(x, y) for x, y in oval(cx, cy, 22, 11, 16)], PETAL)
    for k in range(10):
        a = k * 36 + 18
        cx, cy = polar(PLANT_X, 120, 22, a)
        p.poly(oval(cx, cy, 14, 8, 12), PETAL_EDGE)
    p.recolour(PETAL, 'ff6fa8')
    p.recolour(PETAL_EDGE, 'e0306f')
    p.disc(PLANT_X, 120, 16, CENTRE)
    for k in range(6):
        p.disc(*polar(PLANT_X, 120, 8, k * 60), 2, SOIL)
    p.wait(6, 'flower')

    # A bee comes to the open flower, its path dotted behind it.
    for k in range(6):
        p.disc(470 - k * 14, 70 + (k % 2) * 8 + k * 3, 2, INK)
    p.poly(oval(410, 96, 14, 9, 14), CENTRE)
    for x in (404, 412):
        p.line([(x, 88), (x, 104)], INK, 3)
    p.poly(oval(408, 84, 7, 10, 10), CREAM)
    p.poly(oval(418, 84, 7, 10, 10), CREAM)
    p.disc(397, 96, 4, INK)
    p.wait(6, 'bee')

    # Wren kneels on the grass with her watering can: shoe, shin, skirt, smock, arm, head.
    p.poly([(132, GROUND - 2), (146, GROUND - 16), (156, GROUND - 2)], INK)
    p.rect(146, GROUND - 14, 64, 12, SKIN)
    p.poly([(186, 198), (214, 198), (232, 252), (166, 252)], DRESS)
    p.poly([(190, 232), (244, 236), (248, GROUND - 2), (186, GROUND - 2)], DRESS)
    p.poly([(190, 198), (210, 198), (200, 210)], CREAM)
    p.line([(206, 206), (228, 222), (250, 214)], SKIN, 8)
    p.disc(252, 214, 6, SKIN)
    p.disc(200, 172, 24, SKIN)
    p.poly([(174, 176), (174, 154), (190, 142), (212, 142), (226, 154), (226, 164), (206, 160), (190, 164),
            (184, 186)], HAIR)
    p.poly([(186, 142), (176, 130), (174, 146)], PETAL_EDGE)
    p.poly([(186, 142), (198, 130), (198, 146)], PETAL_EDGE)
    p.disc(186, 142, 4, PETAL_EDGE)
    p.disc(212, 172, 3, INK)
    p.arc((206, 184), (213, 188), (220, 183), INK)
    p.disc(204, 182, 4, PETAL)

    # The can, tipped toward the plant, and its water.
    p.poly([(244, 198), (284, 194), (290, 230), (246, 234)], WATER)
    p.line([(282, 204), (318, 184)], WATER, 5)
    p.rect(314, 178, 10, 10, WATER)
    p.arc((248, 198), (262, 178), (278, 196), INK)
    for x, y in ((326, 194), (334, 208), (322, 216), (338, 224), (330, 238)):
        p.line([(x, y), (x + 2, y + 8)], WATER, 2)

    # The line of the story on a paper panel.
    p.rect(0, 354, 640, 84, CREAM)
    # A picture-book drop capital, then the rest of the line.
    p.rect(20, 362, 52, 68, DRESS)
    p.text(28, 422, 'E', 36, 56, CREAM, prop=False)
    p.text(84, 388, 'very morning Wren watered the seed.', 15, 24, INK)
    p.text(84, 422, 'On the fifth day, it opened.', 15, 24, DRESS)
    p.rect(0, 438, 640, 42, BAND)
    p.text(24, 466, 'PRESS # TO TURN THE PAGE', 13, 20, CREAM, prop=False)
    return p


if __name__ == '__main__':
    save(__file__, build)
