from _support import Page, Writer, Y_SCALE, save, xy

META = dict(title='Selvedge Moth', purpose='A moth woven from programmable character tiles',
            style='Symmetrical pixel tapestry in indigo, clay and glacier blue',
            techniques=['DRCS triangular half-tiles', 'fixed-size character fields', 'reflected tile map'],
            animated=False)

# Half the moth, read from the outside edge towards the centre.
# Lowercase tiles are diagonally cut; the glyph is reflected on the right.
LEFT_WING = [
    '           ',
    '           ',
    ' a         ',
    'aIIc       ',
    'aIPPIc    I',
    'aIPSSPIc  I',
    ' aPSEESPIaI',
    '  aPSSPPIII',
    '   aPPPIIII',
    '   aITTIaII',
    '  aITTITIII',
    '  aITETTIII',
    '   aITTIIII',
    '    aTTIIaI',
    '     aIIa  ',
    '      Ia   ',
]
INK = dict(I=3, P=4, S=5, E=6, T=7, a=3, c=3)


def build():
    p = Page('101e33 20324b 394966 647599 a34e58 cd725d f6cd8b'
             ' 68a5a5 dbe5cf'.split())
    p.rect(35, 25, 570, 430, 1)
    p.rect(43, 33, 554, 414, 2, False)
    size = 22

    # Define masks in unit-square coordinates. The renderer scales them to TEXT.
    for index, corners in enumerate([
        [(0, 0), (.999, 0), (.999, .999), (0, .999)],
        [(0, 0), (.999, 0), (.999, .999)],
        [(0, 0), (.999, 0), (0, .999)],
        [(0, .999), (0, 0), (.999, .999)],
        [(0, .999), (.999, 0), (.999, .999)],
    ]):
        glyph = Writer()
        glyph.poly([(x * 640, 480 - y * Y_SCALE) for x, y in corners])
        p.color(1).cmd(0x22, b'\x40\x40' + xy(.065, .065))
        p.mask(b'\x1bC', 0x21 + index, glyph)
    p.cmd(0x22, b'\x40\x40' + xy(size / 640, size / Y_SCALE))

    for row, left in enumerate(LEFT_WING):
        for column, tile in enumerate(left + left[::-1]):
            if tile == ' ':
                continue
            right = column >= len(left)
            code = {'a': 0x22 + right, 'c': 0x24 + right}.get(tile, 0x21)
            p.color(INK[tile]).pos(78 + column * size, 76 + row * size)
            p.data.extend(bytes([0x1d, code]))

    p.poly([(320, 137), (332, 158), (331, 268), (327, 351),
            (320, 365), (313, 351), (309, 268), (308, 158)], 8)
    for direction in (-1, 1):
        p.line([(320, 149), (320 + 11 * direction, 115), (320 + 37 * direction, 89),
                (320 + 56 * direction, 89)], 7, 3)
        p.rect(318 + 56 * direction, 86, 6, 6, 6)

    for x in (54, 582):
        for y in range(66, 423, 12):
            p.rect(x, y, 4, 5, 2)
    p.text(75, 438, 'SELVEDGE MOTH', 22, 29, 8)
    return p


if __name__ == '__main__':
    save(__file__, build())
