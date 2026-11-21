from _canvas import Canvas, write_page

META = dict(title='Paper Thermal', purpose='A folded bird climbing out of its own shadow',
            style='Lemon paper sculpture on a violet gallery wall',
            techniques=['faceted polygons', 'layered projected shadow', 'connected crease lines'],
            animated=False)


def build():
    p = Canvas('392354 4d2972 281c41 38214f ffe58c ffb83e f58242 fff4c1 d3a8ff 542d72 5e367d 69428a 80549a 9b613d')
    p.poly([(0, 292), (640, 190), (640, 480), (0, 480)], 1)
    p.line([(0, 292), (639, 190)], 3, 2)

    def floor(u, v):
        return 83+410*u+127*v, 302-84*u+124*v

    # A raking window projection fixes the direction of the gallery light.
    p.poly([floor(-.04, -.04), floor(1, -.04), floor(1, 1), floor(-.04, 1)], 9)
    for left, right in [(0, .48), (.50, .98)]:
        for top, bottom in [(0, .45), (.49, .95)]:
            p.poly([floor(left, top), floor(right, top),
                    floor(right, bottom), floor(left, bottom)], 11)
            p.line([floor(left, bottom), floor(right, bottom)], 12, 2)
    for u in (.19, .72):
        p.line([floor(u, -.03), floor(u, .97)], 10, 1)

    outline = [(68, 101), (279, 152), (347, 237), (402, 85), (550, 39),
               (466, 140), (449, 174), (490, 145), (514, 122), (579, 126),
               (543, 146), (504, 169), (421, 278), (369, 292), (262, 303),
               (99, 281), (240, 259)]
    for offset, ink in [(8, 10), (4, 3), (0, 2)]:
        p.poly([(38 + .94*x + .10*y + offset, 257 + .39*y + .012*x + offset*.5)
                for x, y in outline], ink)
    p.poly([(240, 259), (68, 101), (279, 152), (347, 237)], 4)
    p.poly([(68, 101), (229, 181), (240, 259)], 7)
    p.poly([(229, 181), (279, 152), (347, 237), (240, 259)], 5)
    p.poly([(240, 259), (99, 281), (262, 303), (369, 264), (347, 237)], 6)
    p.poly([(240, 259), (347, 237), (449, 174), (490, 145), (519, 132),
            (557, 132), (543, 146), (504, 169), (421, 278), (369, 292),
            (262, 303)], 4)
    p.poly([(369, 292), (421, 278), (504, 169), (543, 146), (492, 160),
            (403, 227)], 5)
    p.poly([(490, 145), (514, 122), (535, 126), (579, 126),
            (546, 144), (526, 145), (492, 160)], 7)
    p.poly([(535, 126), (579, 126), (546, 144), (531, 138)], 6)
    p.poly([(508, 142), (524, 131), (531, 138), (515, 150)], 5)
    p.circle(524, 133, 2.2, 13)
    p.poly([(347, 237), (402, 85), (550, 39), (466, 140), (421, 233),
            (369, 292)], 5)
    p.poly([(402, 85), (550, 39), (435, 121), (369, 292), (347, 237)], 7)
    p.poly([(435, 121), (550, 39), (466, 140), (421, 233), (369, 292)], 6)
    p.line([(99, 281), (240, 259), (369, 292), (435, 121)], 7, 2)
    p.poly([(421, 278), (466, 196), (504, 169), (492, 160), (437, 218)], 13)
    p.poly([(104, 110), (229, 181), (240, 259), (217, 198)], 4)
    p.line([(274, 283), (305, 275), (352, 274)], 5, 2)
    p.line([(373, 266), (402, 227), (434, 142), (506, 70)], 4, 2)
    p.line([(493, 159), (515, 150), (546, 143)], 5, 2)
    # The back wing has a tuck and the front wing exposes the cut edge.
    p.poly([(68, 101), (209, 145), (251, 186), (229, 181)], 5)
    p.line([(77, 105), (209, 145), (251, 186), (280, 208)], 7, 1.5)
    p.poly([(435, 121), (466, 140), (421, 233), (369, 292), (428, 208)], 6)
    p.line([(548, 41), (468, 139), (423, 233), (370, 291)], 4, 2)
    p.line([(109, 281), (262, 301), (369, 291), (421, 278)], 7, 1.5)
    p.text(40, 464, 'PAPER THERMAL', 31, 47, 7)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
