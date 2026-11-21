import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from encoder import Page, save

META = dict(title='Register 258', purpose='Tabular numeral specimen for imaginary mechanical counters',
            style='Amber stencil numerals on a divided blue instrument face',
            techniques=['DRCS tabular numerals', 'knockout polygons', 'fixed-width cells'],
            animated=False)

NUMERALS = {
    '2': [
        (1, [(7, 26), (9, 14), (22, 4), (73, 4), (90, 13), (94, 24),
             (94, 37), (86, 48), (32, 74), (30, 80), (89, 80), (94, 85), (94, 96),
             (7, 96), (7, 78), (15, 65), (70, 37), (73, 32), (73, 25),
             (68, 20), (30, 20), (27, 26), (27, 32), (7, 32)]),
        (0, [(51, 76), (59, 76), (52, 100), (44, 100)]),
    ],
    '5': [
        (1, [(11, 4), (86, 4), (91, 9), (91, 20), (31, 20), (29, 40), (70, 40),
             (86, 46), (94, 58), (94, 77), (86, 90), (72, 96), (24, 96),
             (10, 88), (6, 75), (6, 68), (27, 68), (27, 74), (32, 80),
             (67, 80), (73, 74), (73, 61), (68, 56), (8, 56)]),
        (0, [(51, 76), (59, 76), (52, 100), (44, 100)]),
    ],
    '8': [
        (1, [(24, 4), (75, 4), (89, 12), (93, 23), (93, 36), (85, 47),
             (94, 57), (96, 76), (91, 87), (76, 96), (24, 96), (9, 87),
             (4, 76), (6, 57), (15, 47), (7, 36), (7, 23), (11, 12)]),
        (0, [(29, 20), (72, 20), (74, 24), (74, 34), (69, 40), (30, 40), (26, 34), (26, 24)]),
        (0, [(29, 55), (70, 55), (76, 61), (76, 74), (71, 80), (28, 80), (24, 74), (24, 61)]),
        (0, [(57, 0), (65, 0), (58, 23), (50, 23)]),
        (0, [(51, 76), (59, 76), (52, 100), (44, 100)]),
    ],
}


def build():
    p = Page('1a2940 ffca71 283c57 8ebacb 142035')
    p.text(40, 88, 'Register', 61, 77)
    p.text(428, 80, 'Tabular', 31, 46, 3)
    for digit, contours in NUMERALS.items():
        p.glyph(digit, *contours)
    left, advance = 40, 186
    boundaries = [left + i*advance for i in range(4)]
    p.rect(left, 117, 3*advance, 127, 4)
    for x in boundaries:
        p.rect(x, 113, 2, 259, 2)
        p.rect(x-1, 377, 2, 18, 3)
    for y in (113, 244, 372, 386):
        p.rect(left, y, 3*advance, 2, 3)
    for y, word, ink in ((227, '258', 1), (360, '825', 3)):
        for x, digit in zip(boundaries, word):
            p.text(x+32, y, digit, 122, 109, ink, spacing=0, drcs=True)
    for start, end in zip(boundaries, boundaries[1:]):
        middle = (start+end)/2
        for x, direction in ((start+3, 1), (end-3, -1)):
            p.polygon([(x, 387), (x+direction*10, 382), (x+direction*10, 392)], 3)
        p.rect(middle-1, 376, 2, 7, 3)
    p.text(40, 446, 'Equal advance', 33, 46, 3)
    return p


if __name__ == '__main__':
    save(__file__, build())
