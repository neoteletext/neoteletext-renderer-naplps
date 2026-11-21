import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from math import sin

from encoder import Page, save

META = dict(title='Silt', purpose='Poster for an exhibition on sediment',
            style='Stratified rust, umber and sand with a cut-paper display face',
            techniques=['DRCS display capitals', 'filled strata polygons', 'proportional TEXT'],
            animated=False)


def build():
    p = Page('efe0c8 30221e b94e32 862e25 ebaa76 c97350')
    grid = list(range(0, 641, 8))
    def horizon(x):
        return 118 + 11*sin(x/53 + .8) + 4*sin(x/29)

    edge = [(x, horizon(x)) for x in grid]
    for depth, ink, phase in ((5, 4, 0), (7, 3, 1), (4, 4, 2), (13, 5, 3)):
        lower = [(x, y+depth+2.4*sin(x/69+phase)) for x, y in edge]
        p.polygon(edge + lower[::-1], ink)
        edge = lower

    def floor(x):
        return 328 + 8*sin(x/72) + 3*sin(x/33)

    base = [(x, floor(x)) for x in grid]
    p.polygon(edge + base[::-1], 2)
    fault = 368
    for left, slip in ((True, 0), (False, 15)):
        xs = grid[:47] if left else grid[46:]
        fault_vertex = -1 if left else 0
        edge = [(x, floor(x)+slip) for x in xs]
        edge[fault_vertex] = (fault-slip*.57, floor(fault)+slip)
        for depth, ink, phase in ((8, 3, 0), (5, 5, 1), (3, 0, 2), (9, 4, 3),
                                  (6, 2, 4), (4, 5, 5), (6, 3, 6), (7, 4, 7)):
            lower = [(x, y+depth+1.7*sin(x/55+phase)) for x, y in edge]
            _, fault_y = lower[fault_vertex]
            lower[fault_vertex] = (fault-(fault_y-floor(fault))*.57, fault_y)
            p.polygon(edge + lower[::-1], ink)
            edge = lower
    p.line([(fault, floor(fault)), (fault-36, floor(fault)+63)], 3, 2)
    for points in (((545, 80), (545, 99), (525, horizon(525)+8)),
                   ((545, 419), (545, 405), (568, floor(568)+25))):
        p.line(points, 3, 2)
        p.circle(*points[-1], 4, 3, fill=True)
    p.glyph('S', (1, [(10, 0), (92, 0), (80, 19), (34, 19), (28, 27), (29, 39),
                      (76, 39), (90, 51), (90, 82), (75, 98), (3, 98), (14, 79),
                      (61, 79), (67, 71), (66, 60), (18, 60), (5, 47), (5, 14)]))
    p.glyph('I', (1, [(28, 0), (72, 0), (72, 16), (63, 16), (63, 82),
                      (72, 82), (72, 98), (28, 98), (28, 82), (38, 82), (38, 16),
                      (28, 16)]))
    p.glyph('L', (1, [(10, 0), (36, 0), (36, 77), (86, 77), (74, 98), (10, 98)]))
    p.glyph('T', (1, [(3, 0), (98, 0), (86, 19), (62, 19),
                      (62, 98), (36, 98), (36, 19), (3, 19)]))
    for letter, x, width in zip('SILT', (70, 205, 319, 433), (146, 151, 136, 144)):
        p.text(x, 309, letter, width, 145, 0, spacing=0, drcs=True)
    p.text(46, 76, 'Sediment in relief', 30, 40)
    p.text(497, 76, 'BED 01', 24, 34, 3)
    p.rect(46, 413, 430, 2, 2)
    p.text(46, 451, 'Exhibition in layers', 29, 40)
    p.text(497, 450, 'BED 02', 24, 34, 3)
    return p


if __name__ == '__main__':
    save(__file__, build())
