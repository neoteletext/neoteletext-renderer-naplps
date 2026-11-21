import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from encoder import Page, save

META = dict(title='Three Voices', purpose='Typographic cover for an imagined programme of unaccompanied voices',
            style='Oxide, pink, cream and violet diagonal choral setting',
            techniques=['repeated DRCS word', 'tapered duration marks', 'beat ruler', 'proportional TEXT'],
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
    entries = ((57, 176, 67, 59, 3), (179, 263, 74, 66, 2), (301, 357, 80, 71, 1))
    for beat in beats:
        for y in range(110, 381, 10):
            inside_word = any(x-3 <= beat <= x+3*width and
                              base-height-13 <= y <= base
                              for x, base, width, height, _ in entries)
            if not inside_word:
                p.rect(beat-1, y, 2, 4, 4)
        p.rect(beat-1, 376, 2, 14, 2)
    p.rect(57, 381, 488, 2, 2)
    for x, y, width, height, ink in entries:
        p.polygon([(x, y), (x+13, y-3), (x+45, y-6), (545, y-1),
                   (545, y+1), (x+45, y+6), (x+13, y+3)], ink)
        p.rect(x-1, y-5, 2, 11, ink)
        p.text(x-0.05*width, y-12+0.05*height, 'VOX', width, height, ink,
               spacing=0, drcs=True)
    p.line([(545, 107), (545, 381)], 2, 2)
    for y, ink in ((176, 3), (263, 2), (357, 1)):
        p.circle(545, y, 4, ink, fill=True)
    p.text(45, 444, 'Unaccompanied voices', 32, 43)
    return p


if __name__ == '__main__':
    save(__file__, build())
