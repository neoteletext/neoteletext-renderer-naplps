import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from math import sin

from encoder import Page, save

META = dict(title='Low Water', purpose='A short original concrete poem about a falling tide',
            style='Staggered shoreline verse on a blue-green two-ink field',
            techniques=['proportional TEXT', 'stepped baselines', 'filled polygons'],
            animated=False)


def build():
    p = Page('dce7d2 153f45 aac9b8 256671 74a4a4 94b7a9')
    def tide(x):
        return 390 - .30*x + 15*sin(x / 86) - 9*sin(x / 47)

    shore = [(x, tide(x)) for x in range(0, 641, 8)]
    p.polygon(shore + [(640, 480), (0, 480)], 3)
    p.polygon([(x, y - 8 - 4*sin(x/78)) for x, y in shore] + shore[::-1], 2)
    for start, end, depth, thickness in ((0, 584, 29, 4), (0, 306, 65, 3),
                                         (70, 310, 95, 4), (322, 640, 174, 5),
                                         (487, 640, 196, 3)):
        trace = [(x, tide(x) + depth + 5*sin(x/66))
                 for x in range(start, end+1, 8)]
        edge = [(x, y + thickness*min(1, (x-start)/48, (end-x)/48))
                for x, y in trace]
        p.polygon(trace + edge[::-1], 4)
    p.text(49, 85, 'Low water', 57, 76)
    p.text(55, 158, 'The tide takes', 39, 49)
    p.text(109, 211, 'its blue back', 35, 44)
    p.text(165, 248, 'one syllable', 31, 40)
    p.text(327, 357, 'at a time.', 35, 47, 0)
    return p


if __name__ == '__main__':
    save(__file__, build())
