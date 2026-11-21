"""A rearrangement proof of the Pythagorean theorem."""
from _drawing import Page, save

META = dict(title='A Square Moves', purpose='Prove the Pythagorean theorem by rearranging four congruent right triangles',
            style='Ultramarine and saffron geometric proof poster',
            techniques=['congruent polygon dissection', 'colour pairing', 'WAIT reveal'], animated=True)


def build():
    p = Page('f1eddb 232e50 244cbe f2b642 de6744 97b4f1 fef7df 83c8ae be9fe0')
    p.label(30, 72, 'A SQUARE MOVES', 55)
    p.label(33, 117, 'PYTHAGORAS BY REARRANGEMENT', 26, 2)
    a,b = 82,138
    s = a+b

    def triangle(x, vertices, ink):
        p.poly([(x+u,169+v) for u,v in vertices], ink)

    def identity(x, positions):
        for letter, (u, v) in zip('ABCD', positions):
            p.label(x+u, 169+v, letter, 23, 1)

    # Four triangles wrap around the hypotenuse square.
    p.rect(38,169,s,s,2)
    left = [[(0,0),(a,0),(0,b)],[(s,0),(a,0),(s,a)],
            [(s,s),(s,a),(b,s)],[(0,s),(b,s),(0,b)]]
    right = [[(0,0),(b,0),(0,a)],[(b,a),(b,0),(0,a)],
             [(b,a),(s,a),(s,s)],[(b,a),(b,s),(s,s)]]
    for vertices, ink in zip(left,(3,4,7,8)):
        triangle(38,vertices,ink)
    p.label(123,292,'c',42,6).label(146,272,'2',27,6)
    identity(38, [(34,55), (159,30), (186,167), (36,202)])
    def dimension(x):
        p.line([(x,162),(x,150),(x+s,150),(x+s,162)], 1, 2)
        p.rect(x+77, 136, 66, 27, 0)
        p.label(x+84, 158, 'a+b', 25)

    def right_angles(x, corners):
        for u, v, sx, sy in corners:
            ax, ay = x+u, 169+v
            p.line([(ax+3*sx,ay+14*sy),(ax+14*sx,ay+14*sy),
                    (ax+14*sx,ay+3*sy)], 1, 2)

    p.label(71, 197, 'a', 25).label(52, 246, 'b', 25)
    p.label(88, 259, 'c', 25, 6)
    p.line([(56,178),(104,178)], 1, 2)
    p.line([(45,191),(45,285)], 1, 2)
    p.line([(121,181),(51,299)], 6, 2)
    dimension(38)
    right_angles(38, [(0,0,1,1),(s,0,-1,1),(s,s,-1,-1),(0,s,1,-1)])
    for u, v, du, dv in [(a,0,b,a),(s,a,-a,b),(b,s,-b,-a),(0,b,a,-b)]:
        corner = (38+u, 169+v)
        dx, dy = 15*du/(a*a+b*b)**.5, 15*dv/(a*a+b*b)**.5
        x, y = corner
        p.line([(x+dx,y+dy),(x+dx-dy,y+dy+dx),(x-dy,y+dx)], 6, 2)
    p.wait(12)
    p.label(280, 227, 'SAME', 24)
    p.label(279, 250, 'FRAME', 23)
    p.arrow((282,273),(350,273),1,4,17)
    p.label(280, 303, 'SAME', 24)
    p.label(281, 326, '4 TRI.', 22)
    p.rect(378,169,s,s,2)
    for vertices, ink in zip(right,(3,4,7,8)):
        triangle(378,vertices,ink)
    p.label(541,221,'a',36,6).label(561,205,'2',25,6)
    p.label(424,326,'b',42,6).label(447,306,'2',27,6)
    identity(378, [(33,31), (93,65), (196,128), (154,195)])
    dimension(378)
    right_angles(378, [(0,0,1,1),(b,a,-1,-1),(s,a,-1,1),(b,s,1,-1)])
    for x, y, length in [(378,251,b),(516,169,a)]:
        p.line([(x,y+length),(x+length,y+length),
                (x+length,y),(x,y),(x,y+length)], 1, 2)
    p.label(39, 416, 'ACUTE ANGLES ADD TO 90', 22)
    p.label(378, 416, 'EQUAL AREA LEFT OVER', 22)
    p.line([(39,429),(598,429)], 5, 2)
    p.label(220, 463, 'a', 38).label(242, 445, '2', 24)
    p.label(264, 461, '+', 34)
    p.label(294, 463, 'b', 38).label(317, 445, '2', 24)
    p.label(341, 461, '=', 34)
    p.label(373, 463, 'c', 38).label(395, 445, '2', 24)
    return p


if __name__ == '__main__':
    save(__file__, build())
