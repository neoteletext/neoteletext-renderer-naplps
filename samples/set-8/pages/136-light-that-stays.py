"""Total internal reflection above the glass–air critical angle."""
from math import asin, atan2, cos, sin, tan
from _drawing import Page, save

META = dict(title='Light That Stays', purpose='Compare incidence below and above the glass–air critical angle',
            style='Cobalt optical slab with cyan and amber rays',
            techniques=['textured normals', 'native angle arcs', 'WAIT reveal'], animated=True)


def build():
    p = Page('111b32 f4f3db 244782 5579ab 77f3f2 ffc45b c4d9f2 385581')
    p.rect(0, 233, 639.7, 175, 2)
    p.rect(0, 233, 639.7, 4, 3)
    p.label(34, 72, 'LIGHT THAT STAYS', 52)
    p.label(36, 116, 'TOTAL INTERNAL REFLECTION', 28, 4)
    p.label(39, 211, 'AIR', 25)
    p.label(39, 273, 'GLASS', 25)
    p.label(405, 152, 'GLASS N = 1.50', 23)
    p.label(405, 181, 'CRITICAL 42 DEG', 23)
    p.line([(293,235),(293,406)], 7, 2)
    p.label(40, 477, 'LIGHT SPLITS', 22, 4)
    p.label(374, 477, 'LIGHT STAYS IN GLASS', 22, 5)
    p.label(39, 448, '25 DEG < 42 DEG', 27, 4)
    p.label(373, 448, '44 DEG > 42 DEG', 27, 5)
    for x in (180, 446):
        p.texture(line=2).line([(x, 122 if x == 180 else 200), (x, 397)], 3, 2)
        p.texture()
    for x, offset, colour in [(180, 73, 4), (446, 143, 5)]:
        p.arrow((x-offset, 389), (x, 233), colour, 4)
        angle = atan2(offset, 156)
        points = [(x-67*sin(angle*i/2), 233+67*cos(angle*i/2)) for i in range(3)]
        p.pel(2).arc(*points, colour)
    p.wait(10)
    # For n=1.5, sin(theta_air) = 1.5 sin(theta_glass).
    refraction = asin(1.5*sin(atan2(73, 156)))
    p.arrow((180, 233), (180+77*tan(refraction), 156), 4, 4)
    p.arrow((180, 233), (253, 389), 6, 2, 11)
    p.arrow((446, 233), (589, 389), 5, 4)
    points = [(180+57*sin(refraction*i/2), 233-57*cos(refraction*i/2))
              for i in range(3)]
    p.pel(2).arc(*points, 4)
    p.label(262, 151, '39 DEG', 24, 4)
    p.label(262, 179, 'REFRACTED', 24, 4)
    p.line([(253,174),(235,174),(211,191)], 4, 2)
    p.label(225, 271, 'PARTIAL', 23, 6)
    p.label(225, 297, 'REFLECTION', 23, 6)
    p.line([(245,304),(245,324),(223,324)], 6, 2)
    angle = atan2(143, 156)
    reflection_arc = [(446+67*sin(angle*i/2), 233+67*cos(angle*i/2))
                      for i in range(3)]
    p.pel(2).arc(*reflection_arc, 5)
    p.label(104, 301, '25', 22, 4)
    p.line([(133,294),(147,294),(158,284)], 4, 2)
    p.label(454, 286, '44', 22, 5)
    p.label(411, 286, '44', 22, 5)
    p.label(417, 342, 'TOTAL', 24, 5)
    p.label(391, 367, 'REFLECTION', 23, 5)
    return p


if __name__ == '__main__':
    save(__file__, build())
