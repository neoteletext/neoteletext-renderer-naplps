import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from encoder import Page, oval, save

META = dict(title='The Quireline', purpose='Cover masthead for a fictional journal of folded matter',
            style='Violet broadside with a large engraved initial and pink rules',
            techniques=['DRCS initial with clear counter', 'proportional TEXT', 'ruled editorial grid'],
            animated=False)


def build():
    p = Page('211747 fff0e7 ffa8bb 6455a1 b5a7ed 3e316e 8170b9')
    p.rect(40, 43, 560, 3, 2)
    p.rect(40, 112, 560, 2, 3)
    p.text(40, 103, 'The Quireline', 42, 53)
    p.text(472, 94, 'Issue 04', 21, 29, 2)
    p.glyph('Q', (1, oval(47, 44, 43, 41, 72)),
            (0, oval(46, 44, 28, 38, 72)),
            (1, [(48, 72), (54, 67), (61, 66), (68, 69), (76, 81),
                 (83, 90), (89, 94), (96, 94), (100, 90), (98, 97),
                 (91, 100), (81, 99), (73, 95), (63, 81), (56, 73)]))
    # The outer sheet, return fold and initial share the spine at x=166.
    p.polygon([(45, 173), (166, 199), (299, 142), (299, 337),
               (166, 392), (45, 364)], 6)
    p.polygon([(45, 173), (166, 199), (166, 380), (45, 352)], 5)
    p.polygon([(166, 199), (299, 142), (299, 325), (166, 380)], 3)
    p.polygon([(166, 199), (203, 183), (200, 366), (166, 380)], 6)
    p.polygon([(262, 158), (299, 142), (299, 199)], 4)
    p.line([(45, 352), (166, 380), (299, 325)], 4, 2)
    p.line([(45, 358), (166, 386), (299, 332)], 5, 2)
    p.line([(166, 199), (166, 380)], 4, 2)
    p.text(55, 375, 'Q', 230, 220, 2, spacing=0, drcs=True)
    p.text(345, 169, 'COVER STORY', 22, 29, 2)
    p.rect(345, 185, 84, 3, 2)
    p.text(345, 242, 'Inside the', 34, 49)
    p.text(345, 294, 'paper fold', 34, 49)
    p.rect(345, 328, 3, 65, 6)
    p.text(358, 354, 'A journal of', 22, 34, 4)
    p.text(358, 389, 'folded matter', 22, 34, 4)
    p.rect(40, 423, 560, 3, 2)
    return p


if __name__ == '__main__':
    save(__file__, build())
