"""Four schematic stages of mitosis in an animal cell."""
from _drawing import Page, Writer, save

META = dict(title='One Cell Becomes Two', purpose='Follow chromosome condensation, alignment, separation and nuclear reformation',
            style='Numbered rose and lilac fluorescence-style specimens',
            techniques=['native cell discs', 'thick chromatid strokes', 'relative macro'], animated=False)


def build():
    p = Page('302137 f9e9fa 4f3460 854c7e 6f5088 f5a9ce f9e09b b79ce5 3c2949 f4cc92 9de0db c3abff 5d446d d2b5ee')
    p.label(30, 56, 'ONE CELL BECOMES TWO', 50)
    p.label(32, 86, 'MITOSIS IN AN ANIMAL CELL', 25, 13)
    chromosome = Writer()
    chromosome.relpoly([(-7,-11),(0,-5),(7,-11),(10,-7),(4,0),(10,7),
                        (6,11),(0,5),(-6,11),(-10,7),(-4,0),(-10,-7)])
    p.macro(0x21, chromosome)
    # Follow the sequence clockwise.
    for x, y, number, name, action in [
        (33, 99, '1', 'PROPHASE', 'CHROMOSOMES CONDENSE'),
        (333, 99, '2', 'METAPHASE', 'CHROMOSOMES ALIGN'),
        (333, 282, '3', 'ANAPHASE', 'CHROMATIDS SEPARATE'),
        (33, 282, '4', 'TELOPHASE', 'NUCLEI RE-FORM'),
    ]:
        p.rect(x, y, 274, 176, 8)
        p.rect(x, y+148, 274, 28, 12)
        p.label(x+13, y+170, action, 22, 1)
        p.disc(x+20, y+20, 12, 4)
        p.label(x+14, y+27, number, 20)
        p.label(x+44, y+29, name, 25)
    p.arrow((311, 184), (329, 184), 7, 2, 8)
    p.arrow((468, 275), (468, 281), 7, 2, 6)
    p.arrow((329, 368), (311, 368), 7, 2, 8)
    for x, y in [(168,184), (468,184), (468,365)]:
        p.disc(x, y, 65, 4).disc(x, y, 61, 2)
    p.disc(168, 184, 43, 3)
    for side in (-1, 1):
        pole = (168+52*side, 184)
        for dy in (-28, -15, 15, 28):
            p.line([pole, (pole[0]-6*side, 184+dy)], 7, 2)
        p.disc(*pole, 5, 6)
    chromosome_colours = (5, 9, 10, 11)
    positions = [(148,165),(185,166),(151,202),(188,201)]
    for (x, y), ink in zip(positions, chromosome_colours):
        p.call(0x21, x, y, ink)

    for cx, cy, separating in [(468, 184, False), (468, 365, True)]:
        for side in (-1, 1):
            pole = (cx+side*56, cy)
            for offset in (-39, -13, 13, 39):
                centromere = (cx+side*34, cy+offset)
                p.line([pole, centromere if separating else (cx, cy+offset)], 7, 2)
            p.disc(*pole, 5, 6)
        for offset, ink in zip((-39, -13, 13, 39), chromosome_colours):
            y = cy+offset
            if separating:
                for side in (-1, 1):
                    x = cx+side*34
                    p.line([(x-side*11,y-7),(x,y),(x-side*11,y+7)], ink, 5)
            else:
                p.call(0x21, cx, y, ink)

    p.rect(142, 364, 52, 8, 4)
    p.rect(142, 366, 52, 4, 2)
    for x in (109, 227):
        p.ellipse(x, 368, 56, 43, 4, n=120)
        p.ellipse(x, 368, 52, 39, 2, n=120)
    for x in (109, 227):
        p.disc(x, 368, 33, 4).disc(x, 368, 30, 3)
        positions = [(-13,-11,1),(9,-13,-1),(-10,9,-1),(12,11,1)]
        for (dx, dy, tilt), ink in zip(positions, chromosome_colours):
            p.line([(x+dx-3,368+dy-tilt*5),(x+dx+3,368+dy+tilt*5)], ink, 5)
    p.arrow((168, 337), (168, 361), 6, 3, 10)
    p.arrow((168, 399), (168, 375), 6, 3, 10)
    return p


if __name__ == '__main__':
    save(__file__, build())
