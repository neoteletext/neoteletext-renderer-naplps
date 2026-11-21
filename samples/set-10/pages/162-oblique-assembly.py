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
    [(1, [(0, 159), (38, 0), (68, 0), (119, 159), (88, 159),
          (74, 116), (39, 116), (29, 159)]),
     (0, [(44, 91), (67, 91), (53, 34)])],
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
    p.rect(42, 103, 559, 2, 3)

    # Both outlines have the same stem width and height.
    x, top, rise, stem = 450, 339, 100, 23
    run = rise * shear
    p.polygon(box(x, top, stem, rise), 3)
    p.line([(x, top+rise), (x, top), (x+stem, top), (x+stem, top+rise)], 2, 2)
    p.polygon([(x, top+rise), (x+run, top), (x+run+stem, top),
               (x+stem, top+rise)], 1)
    p.line([(x, top-10), (x+run, top-10)], 2, 2)
    for end in (x, x+run):
        p.rect(end-1, top-15, 2, 11, 2)
    p.line([(440, top), (440, top+rise)], 2, 2)
    for y in (top, top+rise):
        p.rect(435, y-1, 10, 2, 2)
    p.text(510, 367, '30 run', 20, 33, 2)
    p.text(510, 429, '100 rise', 19, 33, 2)
    p.text(42, 382, 'Drawing', 34, 45)
    p.text(42, 425, 'italic capitals', 34, 45)
    return p


if __name__ == '__main__':
    save(__file__, build())
