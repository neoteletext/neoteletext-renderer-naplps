"""Schematic ascending paper chromatography with an origin above the bath."""
from math import cos, pi, sin
from _drawing import Page, save

META = dict(title='Ink in Flight', purpose='Show three dye components separating as solvent climbs paper',
            style='Warm laboratory print with three pigment tracks',
            techniques=['layered pigment contours', 'native hatch', 'WAIT staging'], animated=True)


def build():
    p = Page('ede3cb 292c38 fdf5df bbc1af 6440a3 a63858 107775 b9dbd7 52635d b0a38b dccbe8 e7bdca b4d7c5 a786c6 c97f9c 66a99a')
    p.rect(0, 0, 242, 479.7, 1)
    p.label(27, 76, 'INK IN', 56, 2)
    p.label(27, 129, 'FLIGHT', 56, 2)
    p.label(29, 194, 'PAPER', 29, 2)
    p.label(29, 227, 'CHROMATOGRAPHY', 26, 2)

    def strip(x):
        p.rect(x+5, 77, 80, 340, 9)
        p.rect(x, 72, 80, 340, 2)
        p.rect(x-8, 378, 96, 41, 7)
        p.texture(fill=2).rect(x-8, 378, 96, 41, 3).texture()
        p.line([(x-8, 365), (x-8, 419), (x+88, 419), (x+88, 365)], 8, 2)
        p.line([(x, 349), (x+80, 349)], 8, 2)
    strip(266)
    p.label(270, 452, 'START', 27)
    p.ellipse(306, 349, 10, 6, 1, n=24)
    p.wait(11)
    p.label(29, 274, 'RETENTION FACTOR', 22, 7)
    p.label(29, 304, 'Rf = DYE TRAVEL', 24, 2)
    p.label(29, 331, '/ SOLVENT TRAVEL', 23, 2)
    dyes = [(151, 28, 4), (220, 24, 5), (287, 18, 6)]
    solvent_travel = 349-112
    top_travel = 349-dyes[0][0]
    p.line([(29,349),(212,349)], 7, 2)
    p.disc(38,372,6,13)
    p.label(52, 382, 'TOP DYE', 25, 2)
    dye_cm = 10 * top_travel / solvent_travel
    p.label(29, 414, f'{dye_cm:.1f}/10.0 = {top_travel/solvent_travel:.2f}', 24, 2)
    p.label(29, 445, 'DISTANCES IN CM', 21, 7)
    strip(408)
    p.label(393, 452, 'DEVELOPED', 27)
    p.arrow((357, 85), (399, 85), 8, 3, 11)
    p.texture(line=2).line([(408, 112), (507, 112)], 8, 2).texture()
    p.label(514, 103, 'SOLVENT', 24).label(514, 130, 'FRONT', 24)
    p.line([(488, 349), (550, 349)], 8, 2)
    p.label(557, 367, 'ORIGIN', 24)
    p.label(514, 408, 'BATH', 24)
    p.line([(400,112),(393,112),(393,349),(400,349)], 8, 2)
    p.rect(381, 218, 24, 28, 0)
    p.label(382, 240, '10', 20, 8)
    # The dye-centre ticks share the origin and solvent front used in the key.

    for index, (y, width, ink) in enumerate(dyes):
        x = 503 + index*14
        p.line([(488,y),(x,y),(x,349)], ink, 2)
        p.line([(x-4,349),(x+4,349)], ink, 2)
        p.disc(x,y,3,ink)
        p.label(557, y+8, f'{(349-y)/(349-112):.2f}', 24, ink)
        for scale, colour in [(1, ink+6), (.77, ink+9), (.55, ink)]:
            outline = []
            for i in range(72):
                t = 2*pi*i/72
                ripple = 1+.12*sin(3*t+ink)+.08*cos(7*t)
                tail = 1+(.95-.3*index)*max(0, sin(t+index*.55))**4
                outline.append((447+scale*width*cos(t)*ripple,
                                y+scale*(9+2*index)*sin(t)*ripple*tail))
            p.poly(outline, colour)
    return p


if __name__ == '__main__':
    save(__file__, build())
