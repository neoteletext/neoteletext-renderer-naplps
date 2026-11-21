from _page import Plate, save, arc_points

META = dict(title="Last Night's Scores",
            purpose='The morning sports page: last night\'s extra-inning game told by pennants, a ballpark '
                    'and a ten-inning line score, with the other results below.',
            style='Night ballpark in grass green and infield tan, wooden scoreboard with yellow figures',
            techniques=['two defined dot textures for the crowd', 'a third texture of unlit bulbs on the board', 'filled polygons and native circles', 'native hatching for mown grass',
                        'fixed-pitch scoreboard figures', 'BLINK lights the tenth-inning column', 'WAIT replays the line score inning by inning'],
            animated=True)

PALETTE = ('0a1428 ffffff 2f8a3a 3aa046 c9945a f0f0e0 1e5ad8 f07a1a '
           '0d3a24 ffd84a 6a4424 8f99a8 0d3a24 f4e6c4 101820 1a5234').split()
NIGHT, WHITE, GRASS, MOWN, DIRT, CHALK, GULL, FOX, BOARD, LAMP, WOOD, GREY, RED, CREAM, INK, BULB = range(16)


def pennant(p, x, y, length, colour, name, ink, score):
    p.rect(x - 4, y - 6, 6, 70, WOOD)
    p.disc(x - 1, y - 8, 5, LAMP)
    p.poly([(x + 2, y), (x + 2 + length, y + 26), (x + 2, y + 52)], colour)
    p.text(x + 10, y + 34, name, 14, 22, ink, prop=False)
    p.ctext(x + length + 34, y + 44, score, 26, 40, WHITE, prop=False)


def build():
    p = Plate('201', PALETTE)
    p.rect(0, 0, 640, 40, INK)
    p.text(16, 31, 'FIELDHOUSE SPORTS', 18, 28, CREAM)
    p.rtext(624, 30, 'p 140', 14, 22, LAMP, prop=False)
    # Stands full of fans: two defined dot textures over the dark terraces.
    p.rect(0, 40, 404, 50, INK)
    p.define_texture('A', 10, [[(0.1, 0.1), (0.4, 0.1), (0.4, 0.45), (0.1, 0.45)]])
    p.define_texture('B', 10, [[(0.6, 0.55), (0.9, 0.55), (0.9, 0.9), (0.6, 0.9)]])
    p.cmd(0x23, b'\x60')
    p.rect(0, 46, 404, 40, CREAM)
    p.cmd(0x23, b'\x68')
    p.rect(0, 46, 404, 40, GULL)
    p.solid()
    for y in (58, 72):
        p.line([(0, y), (404, y)], NIGHT, 1)
    # Ballpark from behind home plate.
    field = [(0, 214), (0, 112), (90, 90), (314, 90), (404, 112), (404, 214)]
    p.poly(field, GRASS)
    p.hatch(1)
    p.poly(field, MOWN)
    p.solid()
    p.poly([(200, 118), (330, 168), (200, 212), (70, 168)], DIRT)
    p.poly([(200, 140), (290, 170), (200, 202), (110, 170)], GRASS)
    p.disc(200, 170, 9, DIRT)
    for bx, by in [(200, 132), (306, 170), (94, 170)]:
        p.poly([(bx, by - 5), (bx + 8, by), (bx, by + 5), (bx - 8, by)], CHALK)
    p.poly([(192, 204), (208, 204), (208, 210), (200, 212), (192, 210)], CHALK)
    p.line([(200, 210), (0, 124)], CHALK, 2)
    p.line([(200, 210), (404, 124)], CHALK, 2)
    p.poly([(0, 112), (90, 90), (314, 90), (404, 112), (404, 102), (314, 82), (90, 82), (0, 102)], WOOD)
    # Advertising boards along the wall and yellow foul poles at its ends.
    for i in range(5):
        p.rect(100 + i * 42, 83, 34, 6, [GULL, CREAM, FOX, CREAM, GULL][i])
    for fx, top_y in ((8, 70), (396, 70)):
        p.line([(fx, 112), (fx, top_y)], LAMP, 3)
    for lx in (24, 380):
        p.line([(lx, 100), (lx, 50)], GREY, 3)
        p.rect(lx - 14, 44, 28, 10, LAMP)
    # The winning run slides home past the catcher, the umpire behind.
    p.disc(124, 176, 6, GULL)
    p.poly([(156, 206), (182, 194), (190, 202), (162, 214)], GULL)
    p.line([(184, 198), (196, 206)], GULL, 3)
    p.disc(152, 204, 7, GULL)
    # The dust of the slide.
    for dx, dy, r in [(176, 210, 6), (188, 206, 5), (166, 212, 4)]:
        p.disc(dx, dy, r, DIRT)
    p.disc(218, 190, 8, INK)
    p.poly([(206, 214), (230, 214), (228, 196), (210, 196)], INK)
    p.disc(244, 176, 7, GREY)
    p.poly([(236, 214), (254, 214), (252, 184), (238, 184)], GREY)
    pennant(p, 422, 52, 132, GULL, 'GULLS', WHITE, '5')
    pennant(p, 422, 126, 132, FOX, 'FOXES', INK, '3')
    p.text(420, 212, 'FINAL  10 INN', 14, 22, LAMP, prop=False)
    p.wait(8)
    # Line score on a wooden board.
    top = 228
    p.rect(0, top, 640, 150, WOOD)
    p.rect(8, top + 8, 624, 134, BOARD)
    # The board's face is a field of unlit bulbs: a defined texture of square lamps.
    p.define_texture('C', 8, [[(0.2, 0.2), (0.7, 0.2), (0.7, 0.7), (0.2, 0.7)]])
    p.cmd(0x23, b'\x70')
    p.rect(8, top + 8, 624, 134, BULB)
    p.solid()
    cols = [130 + i * 36 for i in range(10)]
    # The tenth inning's column: its own entry, the board's colour, lit by BLINK.
    p.rect(cols[9] - 17, top + 12, 34, 126, RED)
    for i, x in enumerate(cols):
        p.ctext(x, top + 36, str(i + 1), 13, 20, CREAM, prop=False)
    for j, label in enumerate('RHE'):
        p.ctext(510 + j * 46, top + 36, label, 15, 22, CREAM, prop=False)
    p.line([(16, top + 46), (624, top + 46)], GREY, 1)
    rows = [('GULLS', GULL, '0010200002', ('5', '11', '0')),
            ('FOXES', FOX, '2000010000', ('3', '7', '2'))]
    ys = [top + 86 + r * 44 for r in range(2)]
    for (name, colour, innings, totals), y in zip(rows, ys):
        p.rect(16, y - 26, 8, 30, colour)
        p.text(32, y, name, 15, 24, WHITE, prop=False)
    # The game is replayed inning by inning, as it came over the wire.
    for i, x in enumerate(cols):
        p.wait(3 if i < 9 else 8)
        for (name, colour, innings, totals), y in zip(rows, ys):
            p.ctext(x, y, innings[i], 15, 24, WHITE if i == 9 else LAMP, prop=False)
    for (name, colour, innings, totals), y in zip(rows, ys):
        for j, value in enumerate(totals):
            p.ctext(510 + j * 46, y, value, 17, 26, WHITE, prop=False)
    p.blink(RED, FOX, 6, 6)
    p.wait(8)
    # Around the league: each team's colour chip, the winner in white.
    results = [(('Harbour Kings', '2', FOX), ('Plainsmen', '7', GULL)),
               (('Rivermen', '6', GULL), ('Ospreys', '4', FOX))]
    for r, pair in enumerate(results):
        y = 410 + r * 30
        winner = max(range(2), key=lambda k: int(pair[k][1]))
        for k, (team, score, chip) in enumerate(pair):
            x = 16 + k * 312
            p.rect(x, y - 18, 10, 20, chip)
            p.text(x + 18, y, team, 15, 23, WHITE if k == winner else GREY)
            p.rtext(x + 290, y, score, 15, 23, WHITE if k == winner else GREY, prop=False)
    p.rect(0, 448, 640, 32, INK)
    p.text(16, 472, 'STANDINGS 141   BOX SCORE 142', 14, 22, LAMP, prop=False)
    return p


if __name__ == '__main__':
    save(__file__, build)
