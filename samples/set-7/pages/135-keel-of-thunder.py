"""A boss encounter with an electrical storm folded into a machine."""
import _local
from encoder.screen import Screen, save

META = dict(title='Keel of Thunder', purpose='Boss phase with two charge nodes and their grounding sockets',
            style='Acid citron and steel-blue wireframe with orange charge nodes',
            techniques=['mirrored polygon facets', 'connected lightning lines', 'native rings', 'palette BLINK'],
            animated=True)


def build():
    p = Screen('101620 eef6c9 25394d 35516b 4e7391 d2ed6b ff8751'
               ' a7483c ffc883 52766e 172436 1f3042 121e2c')
    p.text(26, 49, 'KEEL OF THUNDER', 35, 45, 1)
    p.poly([(0, 166), (122, 127), (279, 159), (372, 147), (493, 165),
            (639, 132), (639, 341), (0, 341)], 10)
    p.poly([(0, 292), (107, 265), (224, 297), (377, 263), (500, 281),
            (639, 250), (639, 396), (0, 396)], 12)
    for x, y, length in [(11, 246, 57), (48, 280, 44), (181, 321, 58),
                          (369, 303, 77), (496, 330, 55), (582, 242, 49)]:
        p.line([(x, y), (x+length, y-15)], 11, 2)
    for y in (354, 374, 393):
        p.line([(3, y), (637, y)], 11, 2)
    for x in (43, 113, 177, 463, 527, 597):
        p.line([(320+(x-320)*.56, 337), (x, 394)], 11, 2)
    for i in range(9):
        p.rect(30+i*65, 64, 60, 10, 5 if i < 5 else 2)
    # Cables carry the intercepted charge toward the arena edges.
    for flip in (-1, 1):
        cable = [(320+97*flip, 389), (320+155*flip, 402),
                 (320+222*flip, 402), (320+258*flip, 382),
                 (320+316*flip, 382)]
        p.line(cable, 2, 11)
        p.line(cable, 9, 4)
        for offset in (228, 242, 274, 297):
            x = 320+offset*flip
            y = 402-max(0, min(20, (offset-222)*20/36))
            p.line([(x, y-4), (x, y+4)], 8, 3)
    for flip in (-1, 1):
        def path(points):
            return [(320 + x*flip, y) for x, y in points]

        p.poly(path([(0, 192), (91, 132), (276, 101), (218, 216), (137, 303),
                     (77, 310), (126, 261), (46, 282), (0, 314)]), 2)
        p.poly(path([(0, 192), (91, 132), (276, 101), (175, 169), (126, 261),
                     (46, 282), (0, 314)]), 3)
        p.poly(path([(91, 132), (276, 101), (175, 169), (87, 186)]), 4)
        p.line(path([(276, 101), (175, 169), (126, 261), (46, 282)]), 5, 2)
        p.line(path([(223, 163), (199, 216), (157, 231), (129, 294), (88, 307)]), 4, 2)
        # Cooling fins sit in a recessed bay above the charge node.
        p.poly(path([(111, 148), (240, 119), (205, 151), (105, 177)]), 0)
        for x in range(116, 219, 15):
            y = 149-(x-116)*.22
            p.poly(path([(x, y), (x+9, y-2), (x-8, y+18), (x-16, y+20)]), 4)
            p.line(path([(x, y), (x-16, y+20)]), 9, 2)
        x = 320 + 185*flip
        p.poly(path([(151, 180), (174, 165), (203, 171), (222, 190),
                     (208, 225), (177, 236), (155, 216)]), 0)
        p.poly(path([(157, 182), (175, 171), (202, 176), (215, 190),
                     (204, 220), (178, 230), (161, 213)]), 4)
        p.disk(x, 197, 23, 0).disk(x, 197, 17, 7).disk(x, 197, 10, 6)
        p.disk(x, 197, 4, 1)
        p.line(path([(185, 219), (203, 264), (161, 282), (166, 324),
                     (109, 346), (97, 365)]), 8, 3)
        p.line(path([(161, 282), (146, 293), (150, 313), (138, 324)]), 6, 2)
        p.line(path([(109, 346), (91, 350), (82, 364)]), 6, 2)
        target = 320 + 97*flip
        p.ellipse(target, 387, 48, 17, 9, False)
        p.ellipse(target, 387, 42, 13, 4, False)
        for side in (-1, 1):
            p.line([(target+side*45, 380), (target+side*39, 387),
                    (target+side*45, 394)], 8, 3)
        p.poly(path([(64, 396), (74, 381), (78, 359), (115, 359),
                     (120, 380), (130, 396), (118, 407), (76, 407)]), 0)
        p.line(path([(77, 398), (118, 398)]), 9, 5)
        p.line(path([(80, 375), (84, 362), (110, 362), (115, 375)]), 4, 3)
        p.line(path([(180, 220), (190, 250), (177, 259)]), 7, 2)
        p.poly(path([(68, 385), (80, 371), (114, 371), (126, 385),
                     (116, 399), (78, 399)]), 4)
        p.poly(path([(83, 385), (90, 376), (105, 376), (111, 385),
                     (104, 393), (90, 393)]), 0)
        # Collector prongs bracket the incoming bolt.
        for offset in (-16, 16):
            p.line(path([(97+offset, 389), (97+offset, 374),
                         (97+offset*.65, 366)]), 9, 6)
            p.disk(320+(97+offset*.65)*flip, 366, 4, 8)
        p.line(path([(97, 365), (97, 385)]), 8, 3)
        p.disk(target, 385, 4, 6)
        for offset in (-12, 0, 12):
            p.line(path([(93+offset, 405), (101+offset, 405)]), 9, 2)
    p.poly([(320, 144), (367, 216), (343, 307), (320, 333),
            (297, 307), (273, 216)], 0)
    p.poly([(320, 155), (350, 221), (320, 304), (290, 221)], 9)
    p.poly([(320, 192), (337, 224), (320, 270), (303, 224)], 5)
    p.line([(320, 163), (320, 187)], 1, 2)
    p.line([(320, 273), (320, 298)], 5, 2)
    # The player ship holds both collectors open with lateral links.
    for side in (-1, 1):
        p.line([(320+side*16, 383), (320+side*36, 376),
                (320+side*53, 385), (320+side*69, 383)], 9, 5)
        p.line([(320+side*16, 383), (320+side*36, 376),
                (320+side*53, 385), (320+side*69, 383)], 5, 2)
    p.ellipse(320, 396, 34, 8, 9, False)
    p.poly([(320, 347), (347, 393), (320, 383), (294, 393)], 1)
    p.poly([(320, 354), (328, 382), (320, 378), (312, 382)], 9)
    p.poly([(315, 388), (320, 405), (325, 388)], 8)
    p.text(27, 449, 'GROUND BOTH NODES', 28, 37, 1)
    p.blink(6, 8, 3, 5)
    return p


if __name__ == '__main__':
    save(__file__, build())
