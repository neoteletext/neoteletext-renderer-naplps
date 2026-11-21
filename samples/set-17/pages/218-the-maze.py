"""The Maze: a first-person corridor of a dial-up adventure, one keypress a step."""
from _screen import Plate, oval, save

META = dict(
    title='The Maze',
    purpose='A subscriber walks a dungeon adventure one step at a time, choosing a direction by number',
    style='Stone corridor in graded perspective trapezoids, torchlit, with a glowing door and a mosaic map',
    techniques=['perspective trapezoids in graded colour-map entries', 'converging tile and mortar lines',
                'DEF TEXTURE dithered light', 'arched ribs', 'compass rose', 'a shield and a cobweb', 'one DRCS arrow turned by TEXT rotation', 'eyes in the dark by BLINK', 'mosaic mini-map', 'BLINK torch flame', 'BLINK glint on a key', 'WAIT between depths'],
    animated=True,
)

PALETTE = ('05040a 2b2340 3e3458 4a3a2c 7c5e40 b08a5c 1e2a24 3f5c42 '
           '2a1c12 8c3b1e ffd27a ffb020 ff5a1a 141d38 f2f0e6 6fe0ff')
(BLACK, CEILING_FAR, CEILING_NEAR, WALL_FAR, WALL_MID, WALL_NEAR, FLOOR_FAR, FLOOR_NEAR,
 MORTAR, DOOR, GLOW, FLAME, EMBER, HUD, PAPER, CYAN) = range(16)

# The corridor's cross-section at four depths: left, top, right, bottom on the canvas.
DEPTHS = [(20, 64, 620, 384), (130, 112, 510, 336), (215, 152, 425, 296), (262, 178, 378, 270)]
WALL_INKS = (WALL_NEAR, WALL_MID, WALL_FAR)
OPEN_LEFT, OPEN_RIGHT = 1, 2  # segments with a side passage


# The vaults walked so far, one character per corridor cell; the walker stands at WALKER (column, row).
MAP = ('111111111111',
       '100001000001',
       '101101011101',
       '100100010001',
       '111101110111',
       '000100000100',
       '011111101111',
       '010000101000',
       '011110111110')
WALKER = (3, 5)
# A mosaic character is 0x20 plus one bit per cell of its 2 by 3 block, left to right, top to bottom
# (guide section 9).
MOSAIC_BASE = 0x20
MOSAIC_BITS = ((0x01, 0x02), (0x04, 0x08), (0x10, 0x40))


def mosaic_rows(grid):
    """Turn a grid of 1s (lit) and 0s into rows of mosaic codes, two cells across and three down each."""
    rows = []
    for top in range(0, len(grid), 3):
        codes = []
        for left in range(0, len(grid[0]), 2):
            code = MOSAIC_BASE
            for dy in range(3):
                for dx in range(2):
                    if grid[top + dy][left + dx] == '1':
                        code |= MOSAIC_BITS[dy][dx]
            codes.append(code)
        rows.append(codes)
    return rows


def mix(a, b, t):
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


def build():
    p = Plate(PALETTE, BLACK)
    p.glyph('V', [(50, 6), (92, 50), (64, 50), (64, 94), (36, 94), (36, 50), (8, 50)])
    p.rect(0, 0, 640, 54, HUD)
    p.text(20, 38, 'QUESTLINE', 18, 28, GLOW, prop=False)
    p.text(208, 36, 'THE VAULTS OF MERROW', 12, 18, PAPER, prop=False)
    p.text(572, 38, '218', 14, 22, PAPER, prop=False)

    # Segment by segment from the viewer outward: ceiling, floor, then the two walls.
    for segment in range(3):
        near, far = DEPTHS[segment], DEPTHS[segment + 1]
        nl, nt, nr, nb = near
        fl, ft, fr, fb = far
        p.poly([(nl, nt), (nr, nt), (fr, ft), (fl, ft)], CEILING_NEAR if segment == 0 else CEILING_FAR)
        p.poly([(nl, nb), (nr, nb), (fr, fb), (fl, fb)], FLOOR_NEAR if segment < 2 else FLOOR_FAR)
        for side, opening in ((0, OPEN_LEFT), (1, OPEN_RIGHT)):
            x_near, x_far = (nl, fl) if side == 0 else (nr, fr)
            if segment == opening:
                # A side passage: its ceiling, its floor, the shadowed wall of the turning,
                # and the corner pillar where the corridor wall breaks off.
                left, right = sorted((x_near, x_far))
                p.rect(left, nt, right - left, ft - nt, CEILING_FAR)
                p.rect(left, fb, right - left, nb - fb, FLOOR_FAR)
                p.rect(left, ft, right - left, fb - ft, MORTAR)
                for t in (0.25, 0.5, 0.75):
                    y = ft + (fb - ft) * t
                    p.line([(left, y), (right, y)], BLACK, 1)
                pillar = 14 if side == 0 else -14
                p.poly([(x_near, nt), (x_near + pillar, nt + 6), (x_near + pillar, nb - 6), (x_near, nb)],
                       WALL_INKS[segment - 1])
                p.line([(x_far, ft), (x_far, fb)], WALL_INKS[segment], 3)
                continue
            ink = WALL_INKS[segment]
            quad = [(x_near, nt), (x_far, ft), (x_far, fb), (x_near, nb)]
            p.poly(quad, ink)
            # Mortar: courses that converge on the far end, and staggered joints.
            for t in (1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6):
                p.line([mix((x_near, nt), (x_near, nb), t), mix((x_far, ft), (x_far, fb), t)], MORTAR, 2)
            for course in range(6):
                for u in ((0.33, 0.8) if course % 2 else (0.55,)):
                    top = mix(mix((x_near, nt), (x_near, nb), course / 6), mix((x_far, ft), (x_far, fb), course / 6), u)
                    bottom = mix(mix((x_near, nt), (x_near, nb), (course + 1) / 6),
                                 mix((x_far, ft), (x_far, fb), (course + 1) / 6), u)
                    p.line([top, bottom], MORTAR, 1)
        # Floor tiles: lines converging on the far edge, and the depth edge.
        for f in (0.2, 0.4, 0.6, 0.8):
            p.line([(nl + (nr - nl) * f, nb), (fl + (fr - fl) * f, fb)], BLACK, 1)
        p.line([(fl, fb), (fr, fb)], BLACK, 1)
        p.line([(fl, ft), (fr, ft)], BLACK, 1)
        p.wait(4, f'depth {segment + 1}')

    # Ribs vault the ceiling at each depth.
    for left, top, right, _ in DEPTHS[1:]:
        p.pel(3)
        p.arc((left, top), ((left + right) / 2, top - (right - left) * 0.1), (right, top), MORTAR)

    # A cobweb across the top left corner of the vault.
    hub = (22, 66)
    spokes = [(22 + 70 * t, 66 + 50 * (1 - t) ** 2 + 2) for t in (0.0, 0.3, 0.6, 1.0)]
    spokes[0] = (22, 128)
    for end in spokes:
        p.line([hub, end], PAPER, 1)
    for f in (0.35, 0.65, 0.9):
        p.line([(hub[0] + (x - hub[0]) * f, hub[1] + (y - hub[1]) * f) for x, y in spokes], PAPER, 1)

    # The end wall and its door, glowing at the edges, with light spilling on the floor.
    el, et, er, eb = DEPTHS[3]
    p.rect(el, et, er - el, eb - et, WALL_FAR)
    for t in (1 / 4, 2 / 4, 3 / 4):
        p.line([(el, et + (eb - et) * t), (er, et + (eb - et) * t)], MORTAR, 1)
    p.rect(296, 206, 48, 64, GLOW)
    p.disc(320, 206, 24, GLOW)
    p.rect(300, 210, 40, 60, DOOR)
    p.disc(320, 210, 20, DOOR)
    p.line([(320, 192), (320, 270)], MORTAR, 1)
    p.disc(332, 242, 3, GLOW)
    # A pool of light before the door, dithered with a programmed dot pattern (fill pattern 4).
    p.pattern('A', (6, 6), [(0, 0), (40, 0), (40, 40), (0, 40)], [(50, 50), (80, 50), (80, 80), (50, 80)])
    p.fill_with(4)
    p.poly([(298, 270), (342, 270), (392, 340), (248, 340)], GLOW)
    p.fill_with(0)
    p.wait(4, 'door')

    # A shield hangs on the right-hand wall, in perspective with it: a chevron and a boss.
    shield = [(548, 152), (594, 144), (594, 206), (572, 238), (550, 212)]
    p.poly([(x + 3, y + 3) for x, y in shield], MORTAR)
    p.poly(shield, DOOR)
    p.poly([(550, 196), (572, 172), (594, 186), (594, 198), (572, 186), (550, 208)], GLOW)
    p.disc(572, 160, 5, GLOW)

    # A key lies on the floor; a star of light glints on it.
    p.disc(250, 356, 11, GLOW)
    p.disc(250, 356, 5, FLOOR_NEAR)
    p.poly([(260, 352), (306, 346), (306, 354), (262, 360)], GLOW)
    p.rect(292, 352, 5, 10, GLOW)
    p.rect(300, 351, 5, 12, GLOW)
    p.poly([(244, 336), (247, 346), (257, 349), (247, 352), (244, 362), (241, 352), (231, 349), (241, 346)], CYAN)
    # Something watches from the left-hand passage; its eyes glint with the key.
    p.disc(160, 222, 4, CYAN)
    p.disc(178, 222, 4, CYAN)
    p.blink(CYAN, PAPER, on=2, off=12)

    # The torch pools its light on the near wall, in the same dithered dots as the door's light.
    p.fill_with(4)
    p.poly(oval(80, 194, 46, 62, 24), GLOW)
    p.fill_with(0)
    # A torch on the near left wall; its flame flickers between two colour-map entries.
    p.poly([(78, 214), (90, 214), (86, 252), (82, 252)], MORTAR)
    p.rect(72, 208, 24, 8, WALL_FAR)
    p.poly([(84, 162), (98, 192), (94, 208), (74, 208), (70, 190)], EMBER)
    p.poly([(84, 176), (92, 196), (88, 206), (80, 206), (76, 194)], FLAME)
    p.blink(FLAME, GLOW, on=2, off=3)
    p.blink(EMBER, FLAME, on=3, off=4, delay=1)

    # The command panel: facing, keys, moves, and a mosaic map of the vaults walked so far.
    p.rect(0, 392, 640, 88, HUD)
    p.rect(0, 392, 640, 3, GLOW)
    p.ring(36, 416, 16, PAPER, 2)
    p.poly([(36, 400), (42, 416), (30, 416)], EMBER)
    p.poly([(36, 432), (42, 416), (30, 416)], PAPER)
    p.text(64, 424, 'NORTH   KEYS 3 OF 9', 13, 20, PAPER, prop=False)
    # One arrow character, turned by TEXT's rotation for each way the keypad offers. A turned
    # character pivots on its lower left corner, so each turn is shifted back into its cell.
    arrow = 22
    shift = {0: (0, 0), 1: (arrow, 0), 3: (0, -arrow)}
    for index, (key, word, turn) in enumerate((('4', 'LEFT', 1), ('8', 'AHEAD', 0), ('6', 'RIGHT', 3))):
        x = 20 + index * 156
        p.text(x, 460, key, 15, 24, PAPER, prop=False)
        dx, dy = shift[turn]
        p.programmable(x + 20 + dx, 460 + dy, 'V', arrow, arrow, GLOW, rotation=turn)
        p.text(x + 48, 460, word, 14, 22, GLOW, prop=False)
    # The map of the vaults walked so far, in mosaic blocks: corridors lit, the walker marked.
    p.rect(494, 402, 120, 66, BLACK)
    for row, codes in enumerate(mosaic_rows(MAP)):
        p.mosaics(500, 424 + row * 18, codes, 18, 18, WALL_MID)
    p.disc(500 + 9 * WALKER[0] + 4.5, 406 + 6 * WALKER[1] + 3, 4, EMBER)
    return p


if __name__ == '__main__':
    save(__file__, build)
