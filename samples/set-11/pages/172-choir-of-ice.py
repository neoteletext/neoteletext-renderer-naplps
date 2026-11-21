from _drawing import Plate, save

META = dict(title='Choir of Ice', purpose='A buried glacier sings through tall resonator reeds.',
            style='Pale mineral spires inside a cobalt cavern',
            techniques=['hatched fills', 'filled polygons', 'native arcs', 'stroke text'],
            animated=False)


def build():
    p = Plate('171c55 e3fbf1 283680 374fac 5674c4 80a6dd b1d5ea 79d3cc cf95c4 ffd2ce 23316c 253f77 537eba aac6ec')
    p.poly([(0, 145), (97, 154), (195, 79), (388, 98), (548, 66), (640, 124),
            (640, 354), (534, 401), (280, 347), (105, 405), (0, 362)], 2)
    p.poly([(0, 195), (114, 210), (220, 138), (398, 152), (520, 106), (640, 156),
            (640, 321), (518, 358), (272, 308), (92, 363), (0, 306)], 3)
    # Low hanging shelves echo the fracture planes underfoot.
    p.poly([(0,0),(176,0),(146,34),(112,30),(76,72),(42,55),(0,100)], 2)
    p.poly([(0,0),(155,0),(116,20),(76,57),(46,45),(0,79)], 10)
    p.line([(0,98),(42,55),(76,72),(112,30),(146,34)], 11, 3)
    p.poly([(499,0),(640,0),(640,85),(607,61),(586,71),(555,39),(528,36)], 2)
    p.line([(528,36),(555,39),(586,71),(607,61),(640,85)], 11, 3)
    for points in [[(6,233),(76,252),(99,242),(142,248)],
                   [(146,179),(210,151),(244,161)],[(481,158),(523,134),(554,143),(603,131)],
                   [(451,276),(513,261),(554,270),(618,237)]]:
        p.line(points, 12, 2)
    p.poly([(0,333),(116,312),(231,325),(346,306),(480,323),(640,309),
            (640,380),(536,406),(408,388),(287,417),(162,397),(0,431)], 11)
    p.line([(0,363),(118,341),(260,360),(403,337),(546,354),(640,340)], 12, 2)
    p.line([(17,419),(154,385),(281,405),(410,375),(544,396),(636,370)], 3, 3)
    p.poly([(0,395),(107,368),(170,389),(297,351),(388,381),(511,358),
            (640,377),(640,406),(515,418),(418,396),(282,430),(170,412),(0,445)], 10)
    voices = []
    for x, y, base, width in [(37,248,387,26),(128,213,350,27),(234,170,320,30),
                              (467,178,355,29),(568,214,341,28),(608,203,363,30),
                              (91,166,383,46),(180,124,375,52),(427,145,392,50),
                              (531,153,399,46),(311,80,425,106)]:
        if x == 311:
            p.poly([(211,409),(270,385),(353,391),(423,417),(334,438),(264,434)], 2)
        rear = width <= 32
        p.poly([(x-width*.85,base-12),(x+width*.43,base-21),(x+width,base-12),
                (x+width*.2,base+6),(x-width*.53,base+4)], 2)
        cap = [(x-width/2, y+26), (x+width*.10, y), (x+width/2, y+16)]
        right_edge = [(x+width/2, base-18), (x, base)]
        left_edge = [(x-width/2, base-22)]
        if x == 311:
            right_edge = [(364,218),(351,247),(365,258),(365,350),*right_edge]
            left_edge += [(258,306),(275,270),(258,254)]
        p.poly(cap + right_edge + left_edge, 5)
        shaded = cap[1:] + right_edge
        p.poly(shaded, 3 if rear else 12)
        p.poly([cap[0], cap[1], (x, base), *left_edge], 12 if rear else 6)
        if not rear and x != 311:
            p.texture(fill=3)
            p.poly(shaded, 5)
            p.texture()
        aperture = (x-width*.04, y+33)
        p.disc(*aperture, width*.18, 5)
        p.disc(*aperture, width*.128, 10)
        if not rear:
            ax, ay = aperture
            p.poly([(ax-width*.13,ay+4),(ax+width*.11,ay+7),
                    (ax+width*.03,ay+width*.72),(ax-width*.08,ay+width*.62)], 12)
            p.line([(ax-width*.08,ay+width*.20),(ax-width*.03,ay+width*.60)], 13, 2)
            p.disc(*aperture, width*.13, 10)
        if not rear:
            left = x-width/2
            p.poly([(left+2,base-54),(x-width*.20,base-63),(x-width*.12,base-51),
                    (x-2,base-43),(x-2,base-19),(x-width*.19,base-34),(left+2,base-31)], 13)
            p.line([(left+2,base-54),(x-width*.20,base-63),(x-width*.12,base-51),
                    (x-2,base-43)], 5, 2)
            p.line([(x+width*.07,y+77),(x+width*.25,y+91),(x+width*.40,y+84)], 4, 2)
        if x == 311:
            p.poly([(322,162),(349,151),(355,206),(348,232),(328,249)], 13)
            p.poly([(320,288),(348,277),(359,295),(353,338),(320,304)], 4)
            p.poly([(261,263),(274,270),(265,293),(281,310),(261,306)], 7)
            p.line([(364,218),(351,247),(365,258)], 7, 3)
            # The split passes across the two faces of the soloist.
            p.poly([(258,236),(278,241),(287,257),(303,255),(311,270),
                    (338,252),(364,259),(364,275),(338,265),(311,285),
                    (297,269),(283,272),(271,254),(260,250)], 12)
            p.line([(258,236),(278,241),(287,257),(303,255),(311,270),
                    (338,252),(364,259)], 1, 2)
            p.line([(261,298),(280,304),(289,316),(311,323),(336,310),(362,315)], 5, 3)
            p.poly([(260,325),(280,329),(299,343),(310,342),(309,363),
                    (286,347),(260,344)], 13)
            p.line([(262,327),(281,332),(299,347),(308,346)], 7, 2)
        if x in (180,311,427):
            voices.append(aperture)
    for (x,y), peak, end in zip(sorted(voices),
                              [(248,65),(370,61),(479,103)],
                              [(361,53),(476,86),(572,130)]):
        p.disc(x,y,4,9)
        p.color(8).pel(4)
        p.arc((x,y),peak,end)
        p.color(9).pel(2)
        p.arc((x,y),(peak[0],peak[1]-5),(end[0],end[1]-8))
        p.color(7).pel(1)
        p.arc((x,y),(peak[0],peak[1]+9),(end[0],end[1]+16))
    # Echoes cross above the soloist and reflect from the roof.
    for start, peak, end in [((202,113),(303,32),(427,49)),
                             ((319,112),(415,49),(513,72)),
                             ((391,118),(501,65),(615,102))]:
        p.color(4).pel(2)
        p.arc(start,peak,end)
    # Spaced wavefront segments cross the three travelling crests.
    for start, peak, end in [((180,117),(202,81),(234,64)),
                             ((246,134),(261,85),(291,58)),
                             ((312,145),(335,91),(370,56)),
                             ((383,143),(407,93),(439,72)),
                             ((450,156),(487,116),(513,106))]:
        p.color(8).pel(2)
        p.arc(start,peak,end)
    p.title(283, 465, 'CHOIR OF ICE', 1, 24, 35)
    return p


if __name__ == '__main__':
    save(__file__, build)
