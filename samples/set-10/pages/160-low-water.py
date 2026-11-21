import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from math import exp, sin

from encoder import Page, save

META = dict(title='Low Water', purpose='A short original concrete poem about a falling tide',
            style='Staggered shoreline verse on a blue-green two-ink field',
            techniques=['proportional TEXT', 'stepped baselines', 'filled polygons'],
            animated=False)


def build():
    p = Page('dce7d2 153f45 aac9b8 256671 74a4a4 94b7a9')
    def tide(x):
        return 401 - .285*x + 12*sin(x / 88) - 7*sin(x / 49)

    shore = [(x, tide(x)) for x in range(0, 641, 5)]
    p.polygon(shore + [(640, 480), (0, 480)], 3)
    p.polygon([(x, y - 11 - 5*sin(x/78)) for x, y in shore] + shore[::-1], 2)
    for depth, drift, thickness in ((22, 6, 3), (42, 8, 3), (64, 9, 4),
                                    (92, 10, 4), (128, 11, 5), (153, 12, 4)):
        # Let the upper traces break along a curved dry interval around the setting.
        ends = (199+depth*1.12, 665-depth*.45)
        runs = ([(x, y) for x, y in shore if x <= ends[0]],
                [(x, y) for x, y in shore if x >= ends[1]]) if depth < 128 else (shore,)
        for run in runs:
            trace = [(x, y + depth + drift*sin(x/88 + depth/33)
                      + 28*exp(-((x-510)/145)**2)) for x, y in run]
            trace = [(x, y) for x, y in trace if y <= 484]
            if len(trace) < 2:
                continue
            edge = []
            for x, y in trace:
                taper = 1
                if depth < 128:
                    taper = min(1, max((ends[0]-x)/60, (x-ends[1])/45))
                edge.append((x, y + thickness*taper))
            p.polygon(trace + edge[::-1], 4)
    p.text(49, 85, 'Low water', 57, 76)
    p.text(51, 150, 'The tide takes', 38, 49)
    p.text(117, 198, 'its blue back', 34, 44)
    p.text(190, 237, 'one syllable', 31, 40)
    p.text(330, 371, 'at a time.', 35, 47, 0)
    return p


if __name__ == '__main__':
    save(__file__, build())
