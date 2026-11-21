import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from encoder import Page, save

META = dict(title='Three Voices', purpose='Typographic cover for an imagined programme of unaccompanied voices',
            style='Oxide, pink, cream and violet diagonal choral setting',
            techniques=['repeated DRCS word', 'graded display fields', 'beat ruler', 'proportional TEXT'],
            animated=False)


def build():
    p = Page('8d263e ffdaac f9adb0 d9bded a95664')
    p.glyph('V', (1, [(5, 5), (27, 5), (51, 73), (75, 5), (97, 5),
                      (62, 95), (40, 95)]))
    p.glyph('O', (1, [(24, 5), (75, 5), (95, 23), (95, 77), (75, 95),
                      (24, 95), (4, 77), (4, 23)]),
            (0, [(34, 26), (66, 26), (74, 34), (74, 66), (66, 74),
                  (34, 74), (25, 66), (25, 34)]))
    p.glyph('X', (1, [(5, 5), (29, 5), (95, 95), (71, 95)]),
            (1, [(71, 5), (95, 5), (29, 95), (5, 95)]))
    p.text(45, 78, 'Three Voices', 45, 62)
    p.rect(46, 94, 548, 2, 2)
    beats = (57, 179, 301, 423, 545)
    p.rect(57, 381, 488, 2, 2)
    for x in beats:
        p.rect(x-1, 376, 2, 14, 2)
    for y in (170, 253, 351):
        for x in beats:
            p.rect(x, y-9, 2, 8, 4)
    for x, y, width, height, ink in ((57, 170, 67, 59, 3),
                                     (179, 253, 74, 66, 2),
                                     (301, 351, 80, 71, 1)):
        p.rect(x, y, 545-x, 3, ink)
        p.rect(x, y-6, 3, 13, ink)
        p.text(x-0.05*width, y-5+0.05*height, 'VOX', width, height, ink,
               spacing=0, drcs=True)
    p.line([(545, 115), (545, 381)], 2, 2)
    for y, ink in ((171, 3), (254, 2), (352, 1)):
        p.circle(545, y, 4, ink, fill=True)
    p.text(45, 444, 'Unaccompanied voices', 32, 43)
    return p


if __name__ == '__main__':
    save(__file__, build())
