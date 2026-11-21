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
    for offset in (19, 15, 11, 6, 0):
        p.polygon([(41+offset/3, 164+offset), (149, 179+offset),
                   (308-offset/4, 144+offset), (307-offset/4, 342+offset),
                   (149, 376+offset), (41+offset/3, 350+offset)], 6)
        p.line([(41+offset/3, 350+offset), (149, 376+offset),
                (307-offset/4, 342+offset)], 5, 2)
    p.polygon([(41, 164), (149, 179), (149, 376), (41, 350)], 5)
    p.polygon([(149, 179), (170, 174), (166, 373), (149, 376)], 3)
    p.line([(149, 179), (149, 376)], 4, 2)
    p.polygon([(267, 153), (308, 144), (308, 195)], 5)
    p.polygon([(267, 153), (285, 182), (308, 195)], 4)
    p.text(43, 399, 'Q', 268, 256, 2, spacing=0, drcs=True)
    p.text(347, 179, 'COVER STORY', 23, 29, 2)
    p.rect(347, 193, 253, 2, 6)
    p.text(347, 243, 'Inside the', 31, 44)
    p.text(347, 302, 'paper fold', 32, 46)
    p.rect(347, 323, 253, 2, 3)
    p.text(347, 363, 'A journal of', 23, 34, 4)
    p.text(347, 396, 'folded matter', 23, 34, 4)
    p.rect(40, 423, 560, 3, 2)
    return p


if __name__ == '__main__':
    save(__file__, build())
