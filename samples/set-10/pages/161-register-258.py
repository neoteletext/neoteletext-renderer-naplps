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
    p.rect(40, 113, 560, 170, 4)
    for x in (40, 227, 413, 600):
        p.rect(x, 113, 2, 279, 2)
    for y in (111, 283, 391):
        p.rect(40, y, 560, 2, 3)
    for center, display, check in zip((133, 320, 507), '258', '825'):
        for y in range(289, 386, 7):
            p.rect(center, y, 2, 4, 2)
        for y in (111, 283, 391):
            p.rect(center-1, y-5, 2, 12, 3)
        p.text(center-76, 270, display, 152, 148, spacing=0, drcs=True)
        p.text(center-42, 377, check, 84, 76, 3, spacing=0, drcs=True)
    p.text(40, 446, 'Equal advance', 33, 46, 3)
    return p


if __name__ == '__main__':
    save(__file__, build())
