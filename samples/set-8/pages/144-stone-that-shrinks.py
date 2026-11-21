"""Columnar basalt section and a plan reconstructed from the same joints."""
from _drawing import Page, save

META = dict(title='Stone That Shrinks', purpose='Show polygonal cooling joints continuing down through a lava flow',
            style='Basalt cross-section in slate and apricot',
            techniques=['shared-edge polygons', 'oblique projection', 'indexed facet shading'], animated=False)


def build():
    p = Page('f1d0a6 292936 d6896b e9ab82 393f52 4b5365 62677a 828696 a0a0a5 343348 dca484 665663 767a8b cac0af f7d9af ffb977')
    p.label(32, 65, 'STONE THAT SHRINKS', 51)
    p.label(35, 106, 'COLUMNAR BASALT', 28)
    p.poly([(0,257),(111,204),(179,225),(298,170),(414,207),
            (547,153),(639,194),(639,435),(0,435)], 3)
    p.poly([(0,377),(125,363),(262,386),(431,350),(639,367),
            (639,435),(0,435)], 2)

    # Integer corner keys preserve shared joints when both projections distort them.
    cells = []
    for row in range(3):
        for col in range(6-row//2):
            u, v = 2*col+row%2, 3*row
            cells.append([(u+du,v+dv) for du,dv in
                          [(1,1),(0,2),(-1,1),(-1,-1),(0,-2),(1,-1)]])
    edges = {}
    for cell in cells:
        for a, b in zip(cell, cell[1:]+cell[:1]):
            key = tuple(sorted((a,b)))
            edges[key] = edges.get(key, 0)+1

    def distort(point):
        u,v = point
        return u+((u*13+v*17)%7-3)*.076, v+((u*19+v*11)%7-3)*.12

    def cliff(point):
        u,v = distort(point)
        return 67+27*u+4*v, 205+9*v-1.8*u

    def plan(point):
        u,v = distort(point)
        return 469+11*u, 238+7.5*v

    p.poly([(38,377),(343,350),(429,389),(368,412),(61,420),(30,406)], 11)
    p.line([(39,400),(86,411),(260,400),(370,403)], 10, 3)
    highlighted = cells[-3]
    highlighted_edges = {tuple(sorted((a,b)))
                         for a, b in zip(highlighted, highlighted[1:]+highlighted[:1])}
    faces = []
    for cell in cells:
        for side, (a,b) in enumerate(zip(cell, cell[1:]+cell[:1])):
            if side in (0,1,2,5) and edges[tuple(sorted((a,b)))] == 1:
                faces.append((a,b,side))
    for a,b,side in sorted(faces, key=lambda face: sum(cliff(v)[1] for v in face[:2])):
        x,y = cliff(a)
        u,v = cliff(b)
        bottom_a = 394-(x-62)*.038
        bottom_b = 394-(u-62)*.038
        selected = tuple(sorted((a,b))) in highlighted_edges
        face_colour = {0:7, 1:8, 2:7, 5:8}[side] if selected else {0:4, 1:5, 2:4, 5:6}[side]
        p.poly([(x,y),(u,v),(u,bottom_b),(x,bottom_a)], face_colour)
        p.line([(x,y),(x,bottom_a)], 9, 2)
        p.line([(u,v),(u,bottom_b)], 9, 2)
        for index in range(2 + (a[0]+a[1]) % 2):
            depth = .27 + index*.21 + (a[0]*13+a[1]*7)%11*.013

            def on_face(t, d):
                return (x+(u-x)*t, (y+(bottom_a-y)*d)*(1-t)+(v+(bottom_b-v)*d)*t)

            middle = on_face(.53, depth+.025)
            p.line([on_face(.05,depth), middle, on_face(.95,depth-.025)],
                   4 if selected else 12, 2)
            if (a[0]+index)%3 == 0:
                p.line([middle, on_face(.72,depth+.08)], 12, 1)

    for index, cell in enumerate(cells):
        p.poly([cliff(v) for v in cell], 7+index%2)
    for a,b in edges:
        p.line([cliff(a),cliff(b)], 9, 2)
    p.poly([cliff(v) for v in highlighted], 13)
    p.poly([cliff(v) for v in highlighted], 9, False)

    p.label(58, 154, 'COOLING FACE', 25)
    p.line([(223,145),(250,145),(257,193)], 1, 2)
    p.disc(257,193,4,1)
    ax, ay = cliff(highlighted[1])
    guide = ax-17
    p.arrow((guide,ay+13),(guide,ay+106),1,3,12)
    p.rect(45, 341, 139, 27, 1)
    p.label(51, 364, 'JOINT GROWTH', 21, 14)
    p.line([(184,354),(guide,354),(guide,ay+109)], 1, 2)

    p.rect(443, 157, 176, 233, 0)
    p.rect(443, 157, 176, 233, 11, fill=False)
    p.label(466, 188, 'TOP VIEW', 25)
    for index, cell in enumerate(cells):
        p.poly([plan(v) for v in cell], 13 if cell == highlighted else 7+index%2)
    for a,b in edges:
        p.line([plan(a),plan(b)], 9, 2)
    p.label(457, 365, 'SAME COLUMN', 23)
    corners = [plan(vertex) for vertex in highlighted]
    joint = tuple(sum(axis)/len(corners) for axis in zip(*corners))
    p.line([(554,351),(554,327),joint], 1, 2)
    p.disc(*joint, 3, 1)

    p.rect(0,432,639.7,47.7,1)
    p.label(35, 464, 'COOLING LAVA CONTRACTS AND CRACKS', 27, 0)
    return p


if __name__ == '__main__':
    save(__file__, build())
