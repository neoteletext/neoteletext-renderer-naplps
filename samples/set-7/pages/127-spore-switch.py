"""A side-view platform game played inside a rotting log."""
from math import cos, pi, sin

import _local
from encoder import Page
from encoder.screen import Screen, save

META = dict(title='Spore Switch', purpose='Live platform screen with two spore lamps still to light',
            style='Peach and hot pink fungi over a plum forest of silhouettes',
            techniques=['relative sprite macros', 'stepped silhouettes', 'native arcs', 'logical pels'],
            animated=False)


def build():
    p = Screen('210d26 ffe4b0 3e1841 623457 912d61 d84672 ff876e aae66f 55203a b083a0 455d46 552750 7c3860 e5ffab')
    p.poly([(0, 85), (138, 85), (172, 114), (273, 114), (325, 84),
            (493, 84), (555, 118), (639, 118), (639, 410), (0, 410)], 2)
    # Bark hangs in overlapping slabs above the playable route.
    p.poly([(0, 70), (152, 74), (175, 87), (246, 95), (312, 70),
            (502, 66), (551, 92), (639, 100), (639, 122), (573, 123),
            (509, 98), (379, 101), (312, 116), (261, 126), (169, 120),
            (122, 97), (0, 92)], 8)
    for grain in [
        [(5, 77), (104, 80), (156, 88), (181, 105), (245, 109)],
        [(264, 110), (311, 94), (374, 87), (481, 81), (522, 93)],
        [(531, 94), (566, 111), (631, 113)],
    ]:
        p.line(grain, 12, 3)
    # The exposed end grain surrounds the sealed exit.
    for rx, ry, ink in [(105, 141, 8), (94, 130, 12), (88, 124, 8),
                        (75, 110, 12), (69, 104, 2), (56, 90, 3)]:
        p.poly(
            [(min(639, 620+rx*cos(i*pi/24)), 194+ry*sin(i*pi/24))
             for i in range(48)], ink)
    for x, y, length in [(14, 126, 177), (32, 149, 111), (236, 142, 150),
                          (370, 154, 102), (467, 128, 132), (7, 266, 143),
                          (146, 306, 134), (402, 309, 103), (487, 272, 150)]:
        p.line([(x, y), (x+length*.28, y-9), (x+length*.58, y+4),
                (x+length, y-7)], 11, 2)
    for x, y in [(108, 182), (199, 235), (422, 178), (579, 256), (468, 227)]:
        p.disk(x, y, 2, 9)
    for x, y in [(10, 161), (191, 177), (331, 164), (487, 166)]:
        p.line([(x, 407), (x+26, 333), (x+30, y+43), (x+56, y)], 3, 13)
        p.line([(x+28, y+111), (x+68, y+75), (x+94, y+63)], 3, 7)
    p.poly([(0, 326), (77, 349), (138, 333), (225, 359), (315, 337),
            (405, 368), (493, 330), (566, 351), (639, 325), (639, 413), (0, 413)], 8)
    # The last lamp powers a gate recessed into the end grain.
    p.poly([(579, 165), (579, 121), (590, 105), (618, 105), (632, 122),
            (632, 165)], 0)
    for x in (588, 599, 610, 621):
        p.line([(x, 121), (x, 162)], 9, 3)
    p.line([(580, 141), (631, 141)], 12, 4)
    p.line([(548, 133), (562, 133), (562, 143), (579, 143)], 9, 2)
    p.line([(563, 173), (633, 173)], 6, 4)
    p.disk(605, 139, 7, 8).disk(605, 139, 3, 9)
    for x, y, r, bottom in [(73, 333, 66, 407), (235, 281, 65, 365),
                            (391, 227, 68, 385), (543, 171, 66, 349)]:
        p.poly([(x-13, y+13), (x+13, y+13), (x+8, bottom), (x-19, bottom)], 4)
        p.poly([(x-12, y+14), (x, y+16), (x-3, bottom), (x-13, bottom-5)], 12)
        p.poly([(x-34, bottom+4), (x-12, bottom-16), (x+5, bottom-15),
                (x+26, bottom+4)], 4)
        p.poly([(x-r, y), (x-r+12, y-15), (x-29, y-26), (x+26, y-26),
                (x+r-15, y-13), (x+r, y), (x+r-13, y+12), (x-r+13, y+12)], 5)
        if x < 300:
            for dx, dy in [(-30, -11), (-13, -17), (14, -15), (32, -9)]:
                p.ellipse(x+dx, y+dy, 7, 3, 6)
        else:
            p.rect(x-29, y-4, 58, 5, 8)
            for dx in (-25, -13, 0, 13, 25):
                p.rect(x+dx-3, y-4, 6, 5, 1)
        if x < 300:
            p.line([(x-r+8, y-1), (x+r-8, y-1)], 6, 4)
        p.line([(x-r+18, y+7), (x+r-19, y+7)], 4, 5)
        for mark in (-36, -18, 0, 18, 36):
            p.line([(x+mark, y+5), (x+mark-4, y+11)], 1, 2)
    spore = Page()
    spore.relpoly([(-5, 0), (-5, -7), (-14, -15), (-12, -25),
                   (0, -32), (12, -25), (14, -15), (5, -7), (5, 0)])
    p.macro(0x21, spore)
    for x, y, ink in [(75, 306, 7), (240, 254, 7), (405, 201, 9), (548, 145, 9)]:
        if ink == 7:
            p.disk(x, y-18, 22, 10)
        p.call(0x21, x, y, ink)
        p.disk(x, y-19, 6, 13 if ink == 7 else 2)
    p.pel(2).arc((268, 253), (326, 177), (383, 202), 6)
    p.poly([(383, 202), (371, 198), (380, 191)], 6)
    p.poly([(297, 187), (306, 167), (330, 163), (344, 180), (332, 193), (306, 195)], 7)
    p.poly([(299, 184), (308, 170), (322, 166), (325, 184), (309, 190)], 10)
    p.line([(303, 181), (320, 177)], 13, 2)
    p.disk(332, 174, 4, 0)
    p.line([(309, 192), (303, 200), (291, 200)], 7, 3)
    p.line([(324, 192), (321, 204), (331, 202)], 7, 3)
    p.line([(335, 167), (345, 156), (357, 156)], 7, 2)
    p.text(24, 50, 'SPORE SWITCH', 36, 45, 1)
    p.text(24, 450, 'LAMPS', 25, 30, 1)
    for i in range(4):
        p.disk(145+i*31, 440, 9, 7 if i < 2 else 9)
        if i >= 2:
            p.disk(145+i*31, 440, 5, 0)
    p.text(394, 450, 'CROWN LOG', 29, 33, 6)
    return p


if __name__ == '__main__':
    save(__file__, build())
