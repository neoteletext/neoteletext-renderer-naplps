import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from encoder import Page, box, save

META = dict(title='Oblique Assembly', purpose='Poster for an imagined workshop on drawing italic capitals',
            style='Black oblique letters over a blue construction grid on lemon',
            techniques=['sheared vector capitals', 'negative-space polygons', 'proportional TEXT'],
            animated=False)

FORMS = [
    [(1, box(0, 0, 30, 159)), (1, box(0, 132, 94, 27))],
    [(1, box(0, 0, 30, 159)), (1, box(0, 0, 96, 27)),
     (1, box(0, 66, 78, 25)), (1, box(0, 132, 96, 27))],
    [(1, [(0, 159), (38, 0), (65, 0), (127, 159), (96, 159),
          (79, 116), (41, 116), (29, 159)]),
     (0, [(47, 91), (70, 91), (55, 36)])],
    [(1, box(0, 0, 28, 159)), (1, box(76, 0, 28, 159)),
     (1, [(0, 0), (28, 0), (104, 159), (76, 159)])],
]


def build():
    p = Page('f4ed66 1e2026 2944b9 d1c754')
    p.text(42, 79, 'Oblique Assembly', 42, 61)
    cap, baseline = 141, 300
    shear = .30
    starts = (47, 173, 300, 449)
    for y in (cap, baseline):
        p.line([(42, y), (601, y)], 2, 2)
        for left in starts:
            x = left + (baseline-y)*shear
            p.rect(x-1, y-9, 2, 18, 2)
    for left, contours in zip(starts, FORMS):
        for ink, points in contours:
            p.polygon([(left+x+(159-y)*shear, cap+y) for x, y in points], ink)
        for y in (cap, baseline):
            away = -17 if y == cap else 17
            p.line([(left+(baseline-v)*shear, v) for v in (y, y+away)], 2, 2)
    for y in range(112, cap, 6):
        p.rect(starts[-1], y, 2, 3, 2)
    p.line([(starts[-1], cap-11), (starts[-1]+159*shear, cap-11)], 2, 2)
    p.rect(42, 103, 559, 2, 3)

    x, top, rise, stem = 435, 340, 108, 24
    run = rise * shear
    p.line([(x, top+rise), (x, top), (x+stem, top), (x+stem, top+rise)], 2, 2)
    p.polygon([(x, top+rise), (x+run, top), (x+run+stem, top),
               (x+stem, top+rise)], 1)
    p.line([(x-19, top), (x-19, top+rise)], 2, 2)
    for y in (top, top+rise):
        p.line([(x-23, y), (x+stem+run+7, y)], 2, 2)
    for end in (x, x+run):
        p.rect(end-1, top-17, 2, 17, 2)
    p.line([(x, top-14), (x+run, top-14)], 2, 2)
    p.text(489, 333, '30 run', 22, 29, 2)
    p.text(491, 425, '100 rise', 22, 33, 2)
    p.text(42, 382, 'Drawing', 34, 45)
    p.text(42, 425, 'italic capitals', 34, 45)
    return p


if __name__ == '__main__':
    save(__file__, build())
