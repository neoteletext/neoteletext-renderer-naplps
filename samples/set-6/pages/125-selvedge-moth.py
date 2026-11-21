from _support import Page, Writer, Y_SCALE, save, xy

META = dict(title='Selvedge Moth', purpose='A moth woven from programmable character tiles',
            style='Symmetrical pixel tapestry in indigo, clay and glacier blue',
            techniques=['DRCS triangular half-tiles', 'fixed-size character fields', 'reflected embroidery masks', 'vector satin stitching'],
            animated=False)

# Half the moth, read from the outside edge towards the centre.
# Lowercase tiles are diagonally cut; the glyph is reflected on the right.
LEFT_WING = [
    '           ',
    '           ',
    ' a         ',
    'aIIVc      ',
    'aVPPVc    I',
    'aVPSSPVc  I',
    ' aPSSSSPVII',
    '  aPSSPPVVI',
    '   aVIVVIVI',
    '     cVIVVI',
    '    cITTVII',
    '   cVTTGTVI',
    '   IVTGGVVI',
    '   aIVTVVII',
    '    aIVVIA ',
    '      IIA  ',
]
INK = dict(I=3, V=2, P=4, S=5, T=7, G=10, a=3, c=3, A=3)
PATTERN = dict(I=(0, 15), V=(4, 3), P=(0, 11), S=(1, 12),
               T=(2, 13), G=(5, 7))



def build():
    p = Page('101e33 20324b 394966 647599 a34e58 cd725d f6cd8b'
             ' 68a5a5 dbe5cf 263b53 425573 ba6265 ed9675 84b9b3 a58b6e 53677e'.split())
    p.rect(35, 25, 570, 430, 1)
    p.rect(43, 33, 554, 414, 2, False)
    for x in range(61, 583, 5):
        p.line([(x, 50), (x, 405)], 9 if x % 10 == 1 else 1)
    for row, y in enumerate(range(51, 406, 4)):
        for x in range(62 + 5 * (row % 2), 578, 10):
            p.line([(x, y), (x + 5, y)], 9)
    size = 22

    # Define masks in unit-square coordinates. The renderer scales them to TEXT.
    for index, corners in enumerate([
        [(0, 0), (.999, 0), (.999, .999), (0, .999)],
        [(0, 0), (.999, 0), (.999, .999)],
        [(0, 0), (.999, 0), (0, .999)],
        [(0, .999), (0, 0), (.999, .999)],
        [(0, .999), (.999, 0), (.999, .999)],
        # Bottom edges use the other diagonal of the square.
        [(0, 0), (.999, 0), (0, .999)],
        [(0, 0), (.999, 0), (.999, .999)],
    ]):
        glyph = Writer()
        glyph.poly([(x * 640, 480 - y * Y_SCALE) for x, y in corners])
        p.color(1).cmd(0x22, b'\x40\x40' + xy(.065, .065))
        p.mask(b'\x1bC', 0x21 + index, glyph)
    stitches = [
        # Running stitches, satin stitches and diagonal edge stitches.
        [(.20, .24, .25, .12), (.40, .44, .25, .12), (.60, .64, .25, .12)],
        [(.16, .23, .12, .35), (.37, .20, .12, .49),
         (.58, .29, .12, .48), (.79, .46, .10, .30)],
        [(.22, .22, .11, .52), (.46, .14, .11, .70), (.69, .33, .11, .47)],
        [(.14, .23, .15, .13), (.30, .38, .18, .13), (.47, .53, .18, .13),
         (.65, .68, .18, .13)],
        [(.07, .10, .24, .12), (.27, .26, .25, .13),
         (.48, .43, .25, .14), (.69, .60, .24, .16), (.84, .79, .15, .10)],
        [(.14, .23, .15, .52), (.43, .12, .15, .73), (.71, .23, .15, .52)],
    ]
    for pattern, threads in enumerate(stitches):
        for right in (False, True):
            glyph = Writer()
            for x, y, w, h in threads:
                if right:
                    x = 1 - x - w
                glyph.rect(x * 640, 480 - (y + h) * Y_SCALE, w * 640, h * Y_SCALE)
            p.color(1).cmd(0x22, b'\x40\x40' + xy(.065, .065))
            p.mask(b'\x1bC', 0x28 + 2 * pattern + right, glyph)
    p.cmd(0x22, b'\x40\x40' + xy(size / 640, size / Y_SCALE))

    for row, left in enumerate(LEFT_WING):
        for column, tile in enumerate(left + left[::-1]):
            if tile == ' ':
                continue
            right = column >= len(left)
            code = {'a': 0x22 + right, 'c': 0x24 + right, 'A': 0x26 + right}.get(tile, 0x21)
            x, y = 78 + column * size, 72 + row * size
            p.color(INK[tile]).pos(x, y)
            p.data.extend(bytes([0x1d, code]))
            if tile in PATTERN:
                pattern, thread = PATTERN[tile]
                p.color(thread).pos(x, y)
                p.data.extend(bytes([0x1d, 0x28 + 2 * pattern + right]))
            elif tile == 'a':
                p.color(10).pos(x, y)
                p.data.extend(bytes([0x1d, 0x2e + right]))

    # Long embroidery crosses the block joins to give each wing a grain.
    for side in (-1, 1):
        for path in [[(11, 131), (65, 109), (91, 91), (112, 66)],
                     [(13, 153), (68, 148), (104, 154), (141, 169)],
                     [(13, 183), (41, 201), (64, 224), (84, 266)]]:
            for (ax, ay), (bx, by) in zip(path, path[1:]):
                for start in (0, .25, .5, .75):
                    p.line([(320 + side * (ax + (bx - ax) * t), 72 + ay + (by - ay) * t)
                            for t in (start, start + .16)], 13, 2)
        for offset, y, rx, ry, dark, mid, bright in [
            (122, 201, 34, 19, 4, 12, 6), (68, 327, 26, 18, 9, 7, 13)
        ]:
            x = 320 + side * offset
            # Satin stitch the eyespot from edge to edge; a knot sits over the pupil.
            for ox in range(-rx + 2, rx, 3):
                height = ry * (1 - (ox / rx) ** 2) ** .5
                p.line([(x + ox - side * 2, y - height),
                        (x + ox + side * 2, y + height)], dark, 3)
                if abs(ox) < rx * .77:
                    p.line([(x + ox - side, y - height * .78),
                            (x + ox + side, y + height * .78)], mid, 2)
                if abs(ox) < rx * .52:
                    p.line([(x + ox - side, y - height * .48),
                            (x + ox + side, y + height * .48)], bright, 2)
            p.poly([(x - 5, y), (x, y - 6), (x + 5, y), (x, y + 6)], dark)
            p.line([(x - side, y - 3), (x - side * 3, y - 1)], 8, 2)

    p.poly([(320, 135), (331, 149), (333, 191), (329, 266),
            (326, 342), (320, 365), (314, 342), (311, 266),
            (307, 191), (309, 149)], 10)
    p.poly([(320, 140), (328, 153), (327, 192), (320, 212),
            (313, 192), (312, 153)], 14)
    for side in (-1, 1):
        p.poly([(320 + side * x, y) for x, y in
                [(6, 158), (22, 175), (30, 201), (24, 226),
                 (14, 240), (7, 249), (10, 208)]], 10)
        for y, length in [(177, 14), (185, 20), (193, 23), (201, 24),
                          (209, 23), (217, 20), (225, 15), (233, 10)]:
            p.line([(320 + side * 8, y + 6), (320 + side * length, y)],
                   13 if y % 16 == 1 else 15, 2)
    for y, w in [(155, 13), (168, 14), (181, 14), (195, 10),
                 (211, 17), (228, 16), (245, 15), (262, 14),
                 (279, 13), (296, 12), (313, 11), (330, 9), (345, 6)]:
        p.poly([(320 - w / 2, y - 4), (320, y), (320 + w / 2, y - 4),
                (320 + w / 2, y + 3), (320, y + 7), (320 - w / 2, y + 3)],
               8 if y < 211 else 14)
        for dx in range(-int(w / 2) + 2, int(w / 2), 3):
            p.line([(320 + dx, y), (321 + dx, y + 3)], 15)
    for direction in (-1, 1):
        p.line([(320, 149), (320 + 11 * direction, 115), (320 + 37 * direction, 89),
                (320 + 56 * direction, 89)], 7, 3)
        p.rect(318 + 56 * direction, 86, 6, 6, 6)

    for x, outward in [(53, -1), (587, 1)]:
        p.line([(x, 50), (x, 437)], 10, 6)
        p.line([(x + 3 * outward, 50), (x + 3 * outward, 437)], 14, 2)
        for y in range(52, 433, 8):
            p.line([(x - 5 * outward, y + 4), (x + 4 * outward, y + 1),
                    (x + 5 * outward, y - 2)], 14 if y % 24 == 4 else 15, 2)
    for y in (46, 445):
        for x in range(68, 580, 16):
            p.line([(x - 5, y), (x, y - 3), (x + 5, y), (x, y + 3), (x - 5, y)],
                   14 if (x - 68) % 64 == 0 else 15)
    for x in range(54, 595, 7):
        for y, direction in [(26, -1), (455, 1)]:
            length = 5 + (x * 3) % 8
            p.line([(x - 2, y - direction * 2), (x, y + direction * 2),
                    (x + (x % 3 - 1), y + direction * length)],
                   15 if x % 4 else 14, 2)
            p.rect(x - 1, y + direction * 2, 3, 2, 14)
    p.line([(75, 407), (565, 407)], 10)
    p.text(75, 438, 'SELVEDGE MOTH', 22, 29, 8)
    return p


if __name__ == '__main__':
    save(__file__, build())
