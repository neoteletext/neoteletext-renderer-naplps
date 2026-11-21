import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from encoder import Page, save

META = dict(title='Silt', purpose='Poster for an exhibition on sediment',
            style='Stratified rust, umber and sand with a cut-paper display face',
            techniques=['DRCS display capitals', 'filled strata polygons', 'proportional TEXT'],
            animated=False)


def build():
    p = Page('efe0c8 30221e b94e32 862e25 ebaa76 c97350')
    # Each bed is drawn from its own upper and lower horizon.
    x_grid = (0, 76, 149, 226, 308, 388, 470, 552, 640)
    horizons = (
        (121, 118, 108, 105, 114, 128, 134, 128, 114),
        (129, 127, 117, 115, 124, 136, 142, 137, 124),
        (138, 134, 125, 125, 132, 144, 149, 144, 132),
        (151, 145, 137, 136, 143, 155, 159, 151, 141),
        (319, 327, 333, 326, 333, 342, 336, 323, 316),
    )
    beds = [list(zip(x_grid, horizon)) for horizon in horizons]
    for upper, lower, ink in zip(beds, beds[1:], (4, 3, 5, 2)):
        p.polygon(upper + lower[::-1], ink)
    # Two blocks share the same sequence of beds across a slipped fault.
    left = beds[-1][:5] + [(361, 339)]
    right = [(361, 339)] + beds[-1][5:]
    for start, fault_index, throw in ((left, -1, 0), (right, 0, 8)):
        edge = [(x, y+throw) for x, y in start]
        fault_vertex = len(edge)-1 if fault_index == -1 else fault_index
        for thick, ink in ((14, 3), (8, 5), (4, 0), (6, 4), (3, 3), (7, 5), (3, 4)):
            lower = [(x - (thick * .45 if index == fault_vertex else 0), y + thick)
                     for index, (x, y) in enumerate(edge)]
            p.polygon(edge + lower[::-1], ink)
            edge = lower
    p.polygon([(361, 339), (361, 347), (341, 392), (341, 384)], 3)
    p.line([(545, 77), (545, 104), (526, 137)], 3, 2)
    p.line([(545, 419), (545, 400), (567, 356)], 3, 2)
    for x, y in ((526, 137), (567, 356)):
        p.circle(x, y, 4, 3, fill=True)
    p.glyph('S', (1, [(10, 0), (92, 0), (80, 19), (34, 19), (28, 27), (29, 39),
                      (76, 39), (90, 51), (90, 82), (75, 98), (3, 98), (14, 79),
                      (61, 79), (67, 71), (66, 60), (18, 60), (5, 47), (5, 14)]))
    p.glyph('I', (1, [(28, 0), (72, 0), (72, 16), (63, 16), (63, 82),
                      (72, 82), (72, 98), (28, 98), (28, 82), (38, 82), (38, 16),
                      (28, 16)]))
    p.glyph('L', (1, [(10, 0), (36, 0), (36, 77), (86, 77), (74, 98), (10, 98)]))
    p.glyph('T', (1, [(3, 0), (98, 0), (86, 19), (62, 19),
                      (62, 98), (36, 98), (36, 19), (3, 19)]))
    for letter, x, width in zip('SILT', (70, 190, 300, 419), (146, 151, 136, 144)):
        p.text(x, 309, letter, width, 145, 0, spacing=0, drcs=True)
    p.text(46, 76, 'Sediment in relief', 30, 40)
    p.text(497, 76, 'BED 01', 24, 34, 3)
    p.rect(46, 407, 430, 2, 2)
    p.text(46, 451, 'Exhibition in layers', 29, 40)
    p.text(497, 450, 'BED 02', 24, 34, 3)
    return p


if __name__ == '__main__':
    save(__file__, build())
