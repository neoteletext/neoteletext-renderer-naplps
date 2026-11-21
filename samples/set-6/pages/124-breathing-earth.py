from _support import Page, Writer, Y_SCALE, save, xy

META = dict(title='Breathing Earth', purpose='A schematic section through a termite mound',
            style='Ochre field-guide cutaway with ink tunnels and cream annotations',
            techniques=['user-defined fill pattern', 'connected lines', 'faceted chamber polygons'],
            animated=False)


def build():
    p = Page('edd8a5 312721 9b5039 cf8053 e7a467 b96643 6d392f'
             ' f9e7ba 40645b'.split())
    dots = Writer()
    for x, y, w, h in [(.08, .15, .13, .13), (.65, .49, .17, .11), (.37, .8, .08, .10)]:
        dots.cmd(0x33, xy(x, y) + xy(w, h))
    tile = xy(21 / 640, 21 / Y_SCALE)
    p.color(1).cmd(0x23, b'\x40' + tile)
    p.mask(b'\x1bD', 0x41, dots)

    p.text(28, 43, 'BREATHING EARTH', 22, 30, 1)
    p.text(29, 76, 'TERMITE MOUND / SECTION', 21, 27, 6)
    p.rect(0, 334, 639.6, 145.6, 2)
    p.poly([(0, 365), (137, 384), (267, 370), (399, 400), (640, 369),
            (640, 480), (0, 480)], 6)
    mound = [(111, 335), (147, 313), (170, 275), (196, 253), (212, 199),
             (245, 189), (260, 117), (287, 102), (311, 119), (321, 167),
             (344, 183), (368, 164), (389, 197), (398, 243), (428, 254),
             (455, 302), (504, 335), (453, 366), (393, 388), (323, 409),
             (246, 394), (166, 372)]
    p.poly(mound, 3)
    p.poly([(138, 335), (186, 301), (221, 254), (237, 211), (267, 193),
            (285, 117), (303, 136), (314, 183), (347, 202), (367, 182),
            (383, 222), (394, 255), (426, 278), (445, 321), (480, 339),
            (413, 359), (358, 375), (275, 389), (212, 367)], 4)
    p.cmd(0x23, b'\x60' + tile)
    p.poly(mound, 5)
    p.texture()

    branches = [
        [(286, 131), (283, 177), (267, 216), (273, 269), (306, 304), (300, 352), (309, 381)],
        [(367, 205), (354, 235), (360, 262), (341, 281), (306, 304)],
        [(217, 297), (238, 276), (273, 269)],
        [(300, 352), (337, 330), (391, 329), (419, 304)],
        [(173, 335), (207, 340), (257, 323), (306, 304)],
        [(357, 374), (341, 359), (300, 352)],
    ]
    for branch in branches:
        p.line(branch, 6, 10)
    for x, y, rx, ry in [(267, 219, 19, 9), (217, 297, 26, 11), (305, 308, 35, 13),
                         (358, 260, 22, 11), (393, 328, 23, 10), (308, 376, 34, 11)]:
        p.ellipse(x, y, rx, ry, 1, n=16)
    p.line([(49, 204), (180, 204), (257, 218)], 1, 2)
    p.text(48, 195, 'AIR SHAFT', 21, 27, 1)
    p.line([(572, 245), (470, 245), (411, 322)], 1, 2)
    p.text(470, 235, 'GARDEN', 21, 27, 1)
    p.line([(309, 383), (387, 443), (598, 443)], 7, 2)
    p.text(389, 433, 'BROOD CHAMBER', 21, 27, 7)
    return p


if __name__ == '__main__':
    save(__file__, build())
