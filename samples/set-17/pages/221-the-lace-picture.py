"""The Lace Picture: a twelvefold lace of small shapes, revealed ring by ring, with light running outward."""
import math

from _screen import Plate, oval, polar, save

META = dict(
    title='The Lace Picture',
    purpose='A decorative gallery piece: geometry, the thing the new terminals drew best, made into lace',
    style='Cream and gold lace on midnight blue with ground-colour cut-outs',
    techniques=['twelvefold rotated polygons', 'filled arcs as scallops', 'ground-colour cut-outs', 'radial thread bars', 'DEF TEXTURE basket weave', 'dotted line texture for running stitches',
                'one colour-map entry per ring', 'staggered BLINK chase outward', 'WAIT between rings'],
    animated=True,
)

PALETTE = ('0d1440 f6ecd0 f6ecd0 f6ecd0 f6ecd0 f6ecd0 f6ecd0 ffc847 '
           '1a2660 f6ecd0 7fd0e8 ffffff 2a3a80 ffc847 0d1440 b8c4f0')
(GROUND, RING0, RING1, RING2, RING3, RING4, RING5, GOLD,
 DEEP, CORNER, ICE, WHITE, BLUE, GOLD2, HOLE, CAPTION) = range(16)

CX, CY = 320, 222
FOLD = 12


def turned(points, degrees):
    """Rotate canvas points about the centre."""
    a = math.radians(degrees)
    return [(CX + (x - CX) * math.cos(a) - (y - CY) * math.sin(a),
             CY + (x - CX) * math.sin(a) + (y - CY) * math.cos(a)) for x, y in points]


def around(p, points, ink, count=FOLD, offset=0):
    for k in range(count):
        p.poly(turned(points, offset + k * 360 / count), ink)


def build():
    p = Plate(PALETTE, GROUND)
    # The cloth: a basket weave programmed as fill pattern 4 and laid over the ground.
    p.pattern('A', (10, 10), [(0, 8), (46, 8), (46, 38), (0, 38)], [(54, 54), (92, 54), (92, 100), (54, 100)],
              [(54, 0), (92, 0), (92, 4), (54, 4)])
    p.fill_with(4)
    p.rect(0, 0, 639.6, 479.6, DEEP)
    p.fill_with(0)
    p.disc(CX, CY, 214, DEEP)
    p.ring(CX, CY, 214, BLUE, 3)
    p.ring(CX, CY, 208, GOLD2, 1)

    # Ring 0: a rosette of twelve petals with a gold eye.
    around(p, oval(CX + 26, CY, 22, 7, 14), RING0)
    # A second, smaller layer of petals turned half a petal, in a cream that does not blink.
    around(p, oval(CX + 17, CY, 12, 5, 12), CORNER, offset=15)
    p.disc(CX, CY, 12, GOLD)
    p.disc(CX, CY, 5, HOLE)
    p.wait(5, 'rosette')

    # Ring 1: a threaded circle and twenty-four beads, gold and cream in turn.
    p.ring(CX, CY, 56, RING1, 3)
    for k in range(24):
        p.disc(*polar(CX, CY, 66, k * 15), 5, RING1 if k % 2 else GOLD2)
    p.wait(5, 'beads')

    # Ring 2: lozenges pointing outward with cut-out centres, small gold diamonds between.
    lozenge = [(CX + 76, CY), (CX + 100, CY - 11), (CX + 124, CY), (CX + 100, CY + 11)]
    around(p, lozenge, RING2)
    around(p, [(CX + 90, CY), (CX + 100, CY - 4), (CX + 110, CY), (CX + 100, CY + 4)], HOLE)
    around(p, [(CX + 92, CY), (CX + 100, CY - 5), (CX + 108, CY), (CX + 100, CY + 5)], GOLD, offset=15)
    p.wait(5, 'lozenges')

    # Ring 3: twenty-four scallops, each a half circle facing outward.
    for k in range(24):
        a = k * 15
        start, mid, end = polar(CX, CY, 136, a - 6), polar(CX, CY, 148, a), polar(CX, CY, 136, a + 6)
        p.arc(start, mid, end, RING3, fill=True)
    p.ring(CX, CY, 134, RING3, 2)
    p.wait(5, 'scallops')

    # Ring 4: teardrops with holes, ice-blue picots between them.
    tear = [(CX + 152, CY)] + [(CX + 174 + 12 * math.cos(math.radians(t)), CY + 12 * math.sin(math.radians(t)))
                               for t in range(-120, 121, 20)]
    around(p, tear, RING4)
    for k in range(FOLD):
        p.disc(*polar(CX, CY, 176, k * 30), 5, HOLE)
        p.disc(*polar(CX, CY, 166, k * 30 + 15), 4, ICE)
    p.wait(5, 'teardrops')

    # Ring 5: the picot edge: a fine thread and forty-eight loops.
    p.ring(CX, CY, 196, RING5, 1)
    for k in range(48):
        p.disc(*polar(CX, CY, 202, k * 7.5), 5, RING5)
        p.disc(*polar(CX, CY, 202, k * 7.5), 2, DEEP)
    for k in range(FOLD):
        p.disc(*polar(CX, CY, 196, k * 30), 6, GOLD2)
    p.wait(5, 'edge')

    # Bars of thread join the rings, as needle lace is joined.
    for k in range(FOLD):
        a = k * 30 + 15
        p.line([polar(CX, CY, 58, a), polar(CX, CY, 90, a)], CORNER, 2)
        p.line([polar(CX, CY, 110, a), polar(CX, CY, 134, a)], CORNER, 2)
        p.line([polar(CX, CY, 148, a), polar(CX, CY, 196, a)], CORNER, 1)

    # Running stitches: two circles in the dotted line texture (TEXTURE line bits 01) with a two-unit pel,
    # whose dots and gaps are measured in pels (guide section 7).
    p.cmd(0x23, bytes([0x40 | 1]) + p.mask)
    p.ring(CX, CY, 129, ICE, 2)
    p.ring(CX, CY, 189, GOLD2, 2)
    p.cmd(0x23, bytes([0x40]) + p.mask)

    # Small lace corners: a quarter of scallops and beads round a gold boss.
    for cx, cy, start in ((0, 0, 0), (640, 0, 90), (0, 444, 270), (640, 444, 180)):
        for k in range(7):
            a = start + k * 15
            first, middle, last = polar(cx, cy, 58, a - 6), polar(cx, cy, 68, a), polar(cx, cy, 58, a + 6)
            p.arc(first, middle, last, ICE, fill=True)
            p.disc(*polar(cx, cy, 40, a), 4, CORNER)
            p.line([polar(cx, cy, 20, a), polar(cx, cy, 56, a)], CORNER, 1)
        p.ring(cx, cy, 58, ICE, 2)
        p.disc(cx, cy, 18, GOLD)

    # Light runs outward ring by ring: each ring's entry blinks to gold a step after the one inside it.
    for step, ring in enumerate((RING0, RING1, RING2, RING3, RING4, RING5)):
        p.blink(ring, GOLD, on=3, off=15, delay=step * 3)

    # The caption in a cartouche with gold rules.
    p.disc(90, 461, 17, GOLD)
    p.disc(550, 461, 17, GOLD)
    p.rect(90, 444, 460, 34, GOLD)
    p.disc(90, 461, 15, GROUND)
    p.disc(550, 461, 15, GROUND)
    p.rect(90, 446, 460, 30, GROUND)
    p.text(84, 470, 'GALLERY 221  LACE No. 4  TWELVEFOLD', 13, 20, CAPTION, prop=False)
    return p


if __name__ == '__main__':
    save(__file__, build)
