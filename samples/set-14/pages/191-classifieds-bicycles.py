from _kit import *

META = dict(title='Classifieds: Bicycles',
            purpose='A neighbourhood classified column on screen, with a drawn ten-speed on top and one advertisement flagged for the reader.',
            style='Slate board with an orange masthead, a bright ten-speed and a blinking cyan ad',
            techniques=['native circles', 'wide pels', 'linework', 'DRCS', 'dashed line texture', 'WAIT', 'BLINK', 'proportional text'],
            animated=True)

SLATE, WHITE, ORANGE, YELLOW, RED, DKRED, CHROME, STEEL, BLACK, SKY, ROW, ROW2, CYAN, HILITE, SADDLE, FLASH = range(16)


def wheel(p, x, y):
    p.disc(x, y, 62, BLACK)
    p.disc(x, y, 58, SLATE)
    p.ring(x, y, 58, YELLOW, 6)
    p.ring(x, y, 52, STEEL, 2)
    for i in range(18):
        a = i * math.pi / 9
        p.line([(x + 9 * math.cos(a), y + 9 * math.sin(a)), (x + 52 * math.cos(a), y + 52 * math.sin(a))], CHROME, 1)
    p.disc(x, y, 9, STEEL)
    p.disc(x, y, 4, WHITE)


def bicycle(p, ox, oy):
    R = (ox + 40, oy + 100)
    F = (ox + 232, oy + 100)
    B = (ox + 118, oy + 100)
    S = (ox + 96, oy + 28)
    H = (ox + 190, oy + 28)
    p.rect(ox - 6, oy + 163, 300, 3, STEEL)
    wheel(p, *R)
    wheel(p, *F)
    # frame in red with a darker shadow edge
    for pts, w in [([R, B], 5), ([R, S], 5), ([B, S], 7), ([S, H], 6), ([B, H], 7), ([H, F], 5)]:
        p.line(pts, DKRED, w + 3)
    for pts, w in [([R, B], 5), ([R, S], 5), ([B, S], 7), ([S, H], 6), ([B, H], 7), ([H, F], 5)]:
        p.line(pts, RED, w)
    # saddle, stem and drop bars
    p.line([S, (S[0] - 2, S[1] - 14)], CHROME, 4)
    p.poly([(S[0] - 22, S[1] - 14), (S[0] + 16, S[1] - 14), (S[0] + 12, S[1] - 20), (S[0] - 20, S[1] - 20)], SADDLE)
    p.line([H, (H[0] - 4, H[1] - 18)], CHROME, 4)
    p.line([(H[0] - 4, H[1] - 18), (H[0] + 16, H[1] - 18), (H[0] + 28, H[1] - 6), (H[0] + 24, H[1] + 14), (H[0] + 10, H[1] + 14)], BLACK, 5)
    # chain ring, crank, pedal, chain
    p.ring(B[0], B[1], 22, CHROME, 3)
    p.ring(B[0], B[1], 16, STEEL, 2)
    p.line([(R[0], R[1] - 10), (B[0], B[1] - 22)], STEEL, 2)
    p.line([(R[0], R[1] + 10), (B[0], B[1] + 22)], STEEL, 2)
    p.line([B, (B[0] - 22, B[1] + 30)], CHROME, 5)
    p.rect(B[0] - 34, B[1] + 28, 24, 6, BLACK)
    p.line([B, (B[0] + 20, B[1] - 28)], CHROME, 5)
    p.rect(B[0] + 10, B[1] - 32, 24, 6, BLACK)
    # cassette of gears at the rear hub
    for r in (14, 11, 8):
        p.ring(R[0], R[1], r, STEEL, 2)


ICON_W, ICON_H = 34, 20


def wheel_shape(x, y, r):
    return [('disc', x, y, r), ('hole', x, y, r - 2.4)]


ICONS = {
    0x21: wheel_shape(6, 14, 5.5) + wheel_shape(28, 14, 5.5) + [('line', [(6, 14), (14, 14), (20, 6), (10, 6), (6, 14)], 1.6), ('line', [(14, 14), (20, 6), (27, 6), (28, 14)], 1.6), ('line', [(24, 3), (28, 6)], 2)],   # racer
    0x22: wheel_shape(8, 14, 4.5) + wheel_shape(26, 14, 4.5) + [('line', [(8, 14), (16, 8), (26, 14)], 1.8), ('line', [(16, 8), (22, 4), (26, 4)], 1.8)],   # BMX
    0x23: wheel_shape(7, 14, 5.5) + wheel_shape(27, 14, 5.5) + [('line', [(7, 14), (15, 14), (22, 7), (13, 7), (7, 14)], 1.6), ('line', [(22, 7), (27, 14)], 1.6), ('line', [(11, 5), (16, 5)], 2)],   # girls
    0x24: wheel_shape(4, 14, 4) + wheel_shape(17, 14, 4) + wheel_shape(30, 14, 4) + [('line', [(4, 14), (10, 7), (17, 14), (24, 7), (30, 14)], 1.6), ('line', [(10, 7), (24, 7)], 1.6)],   # tandem
    0x25: wheel_shape(7, 14, 5.5) + wheel_shape(27, 14, 5.5) + [('line', [(7, 14), (15, 14), (22, 7), (13, 7), (7, 14)], 1.6), ('line', [(22, 7), (27, 14)], 1.6), ('poly', [(23, 2), (33, 2), (31, 8), (24, 8)])],   # with basket
    0x26: wheel_shape(8, 15, 4) + wheel_shape(24, 15, 4) + wheel_shape(28, 15, 4) + [('line', [(8, 15), (14, 7), (22, 7)], 1.8), ('line', [(22, 7), (26, 15)], 1.8)],   # trike
}


ADS = [
    ('A', '10 SPEED RACER, 23 IN', '$85'),
    ('B', 'BOYS BMX, NEEDS A TIRE', '$25'),
    ('C', 'GIRLS BIKE, RED, CALL AFTER 6', '$40'),
    ('D', 'TANDEM, GOOD SHAPE', '$120'),
    ('E', 'MENS 3 SPEED WITH BASKET', '$55'),
    ('F', 'KIDS TRIKE, BELL AND FLAGS', '$12'),
]


def ad_row(p, i, highlight=False):
    y = 262 + i * 30
    key, text, price = ADS[i]
    fill = HILITE if highlight else (ROW if i % 2 == 0 else ROW2)
    p.rect(14, y, 612, 28, fill)
    p.disc(34, y + 14, 12, ORANGE)
    p.say(34, y + 21, key, BODY, SLATE, 'c')
    character(p, 0x21 + i, 54, y + 25, ICON_W, ICON_H, YELLOW if highlight else CHROME)
    p.say(96, y + 21, text, BODY, WHITE)
    p.say(614, y + 21, price, BODY, YELLOW if highlight else WHITE, 'r')
    if highlight:
        character(p, 0x27, 466, y + 24, 28, 22, YELLOW)
        p.frame(15, y + 1, 610, 26, FLASH, 3)
        


def build():
    p = Screen('18202c ffffff ff8a1c ffd21f e8342a 9a1f1a d7dde5 7f8a99 0b0e14 5aa8e0 25324a 1d283b 3fe0e8 0f5a66 5a3a22 3fe0e8')
    p.rect(0, 0, 640, 480, SLATE)
    p.rect(0, 0, 640, 44, ORANGE)
    p.say(14, 32, 'NEIGHBOURHOOD CLASSIFIEDS', LARGE, SLATE)
    p.say(626, 32, '191', LARGE, SLATE, 'r')
    p.rect(0, 44, 640, 4, YELLOW)
    p.rect(0, 448, 640, 32, ORANGE)
    p.say(14, 472, 'PRESS A-F TO ANSWER AN AD   0 FOR INDEX', BODY, SLATE)
    ICONS[0x27] = [('poly', [(2, 9), (8, 3), (12, 9), (9, 12), (14, 17), (17, 14), (23, 20), (17, 25), (10, 22), (2, 12)]), ('hole', 0, 0, 0.1)]
    for code, shapes in ICONS.items():
        define_character(p, code, ICON_W, ICON_H, shapes)
    rays(p, 190, 160, 18, ROW2, 0, 50, 336, 258, 0, .5)
    p.wait(4)
    p.say(344, 92, 'BICYCLES', HEAD, YELLOW)
    p.say(344, 126, 'FOR SALE', LARGE, WHITE)
    p.say(344, 160, '6 ADS TODAY', BODY, SKY)
    p.dashed_frame(338, 172, 288, 62, YELLOW, 3)
    p.say(482, 198, 'PLACE YOUR OWN AD', BODY, WHITE, 'c')
    p.say(482, 222, '$2 A DAY, PRESS * THEN 5', SMALL, CHROME, 'c')
    bicycle(p, 30, 70)
    for gx, gy in ((52, 124), (290, 112), (178, 106), (250, 196)):
        p.poly([(gx, gy - 14), (gx + 3, gy - 3), (gx + 14, gy), (gx + 3, gy + 3), (gx, gy + 14), (gx - 3, gy + 3), (gx - 14, gy), (gx - 3, gy - 3)], FLASH)
    p.wait(8)
    for i in range(6):
        if i == 2:
            continue
        ad_row(p, i)
        p.wait(3)
    ad_row(p, 2, True)
    p.blink(FLASH, SLATE, 6, 6)
    return p


if __name__ == '__main__':
    save(__file__, build)
