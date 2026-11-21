import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from encoder import Page, oval, save

META = dict(title='Ink and Air', purpose='Specimen showing reciprocal counters and strokes',
            style='Mint and deep green diptych with isolated counters',
            techniques=['DRCS outline', 'cleared and isolated counterforms', 'registration rules'],
            animated=False)


def build():
    p = Page('152521 c4f6d9 51856b 66977d')
    p.rect(320, 0, 320, 480, 1)
    p.text(38, 89, 'INK', 61, 77)
    p.text(362, 89, 'AIR', 61, 77, 0)
    def bowl(cx, cy, rx, ry):
        arc = oval(cx, cy, rx, ry, 48)
        return arc[-12:] + arc[:13]

    outline = [(8, 3)] + bowl(53, 25, 36, 22) + bowl(56, 72, 41, 25) + [(8, 97)]
    upper = [(34, 20)] + bowl(54, 27, 11, 7) + [(34, 34)]
    lower = [(34, 58)] + bowl(58, 68.5, 13, 10.5) + [(34, 79)]
    p.glyph('B', (1, outline), (0, upper), (0, lower))
    p.glyph('C', (1, upper), (1, lower))
    for x, ink in ((32, 1), (352, 0)):
        for y in (106, 374):
            p.rect(x, y, 256, 2, ink)
    for y, number in ((189, '1'), (280, '2')):
        for x, ink, rule in ((29, 1, 3), (598, 0, 2)):
            p.text(x, y-8, number, 23, 29, ink)
        for start, end, rule in ((29, 211, 3), (431, 614, 2)):
            for x in range(start, end, 12):
                p.rect(x, y, 7, 2, rule)
    p.text(43, 349, 'B', 226, 219, spacing=0, drcs=True)
    p.line([(363 + 2.26*x, 130 + 2.19*y) for x, y in outline + outline[:1]], 3, 2)
    p.text(363, 349, 'C', 226, 219, 0, spacing=0, drcs=True)
    p.text(38, 437, 'Printed B', 29, 40)
    p.text(358, 437, 'Counterforms', 28, 40, 0)
    return p


if __name__ == '__main__':
    save(__file__, build())
