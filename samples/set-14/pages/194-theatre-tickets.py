from _kit import *

META = dict(title='Theatre Tickets',
            purpose='A box office opens its curtain, shows the hall with sold and free seats, and holds the reader\'s chosen pair.',
            style='Red velvet and brass on black, a pleated curtain that opens, a seat plan in small squares',
            techniques=['macros', 'hatch fill', 'filled polygons', 'redrawn animation', 'WAIT', 'BLINK', 'proportional text'],
            animated=True)

BLACK, WHITE, RED, DKRED, GOLD, DKGOLD, GREEN, DKGREEN, WOOD, BEAM, PAPER, SOLDDK, STAGE, GREY, CHOSEN, FLASH = range(16)

SEAT = 0x21
SEAT_W, SEAT_H = 20, 17
PLAN_X, PLAN_Y = 52, 204
PITCH_X, PITCH_Y = 24, 26
AISLE = 22
ROW_BOW = -16
ROWS = 'ABCDEFGH'
CHOSEN_ROW, CHOSEN_SEATS = 'D', (9, 10)


def seat_fragment():
    frag = Encoder()
    frag.cmd(0x35, xy(SEAT_W / 640, 0) + xy(0, -SEAT_H / Y_SCALE) + xy(-SEAT_W / 640, 0))
    return frag


def seat_x(n):
    return PLAN_X + (n - 1) * PITCH_X + (AISLE if n > 8 else 0)


def seat_y(r, n=1):
    """Rows bow toward the stage: the outer seats sit lower than the centre ones."""
    centre = PLAN_X + 8 * PITCH_X + AISLE / 2 - 2
    return PLAN_Y + r * PITCH_Y + round(((seat_x(n) + SEAT_W / 2 - centre) / 200) ** 2 * ROW_BOW)


def is_sold(row_index, n):
    # fixed pseudo-random pattern, denser toward the front
    return (row_index * 7 + n * 5 + (row_index * n) % 4) % 5 < (3 if row_index < 4 else 2)


STAGE_TOP, STAGE_BOTTOM = 56, 164


def curtain_closed(p):
    p.rect(20, STAGE_TOP, 420, STAGE_BOTTOM - STAGE_TOP, DKRED)
    p.fillrect(20, STAGE_TOP, 420, STAGE_BOTTOM - STAGE_TOP, RED, 1, 9)
    for x in range(20, 440, 42):
        p.line([(x, STAGE_TOP), (x, STAGE_BOTTOM)], DKRED, 2)
    p.rect(20, STAGE_TOP, 420, 12, DKGOLD)
    p.rect(20, STAGE_BOTTOM - 8, 420, 8, GOLD)
    for i, x in enumerate(range(30, 440, 30)):
        p.disc(x, STAGE_BOTTOM + 4, 5, GOLD if i % 2 else FLASH)


def platform(p):
    """The set without the engine: a railway platform at night."""
    p.rect(20, STAGE_TOP, 420, STAGE_BOTTOM - STAGE_TOP, STAGE)
    p.rect(20, 130, 420, 34, WOOD)
    p.fillrect(20, 130, 420, 34, DKGOLD, 1, 7)
    p.rect(20, 128, 420, 3, DKGOLD)
    p.ellipse(230, 150, 120, 12, BEAM)
    for x, y in ((60, 74), (150, 66), (340, 70), (400, 80)):
        p.disc(x, y, 1.5, WHITE)
    p.rect(330, 82, 4, 48, GREY)
    p.disc(332, 80, 8, BEAM)
    p.disc(88, 98, 14, WHITE)
    p.disc(88, 98, 11, STAGE)
    p.line([(88, 98), (88, 90)], WHITE, 2)
    p.line([(88, 98), (94, 100)], WHITE, 2)
    p.rect(86, 112, 4, 18, GREY)


def engine(p, x, puffs):
    """The locomotive with its left edge at x, trailing smoke."""
    p.rect(x, 104, 90, 26, BLACK)
    p.rect(x + 50, 88, 40, 18, BLACK)
    p.rect(x + 8, 90, 14, 16, BLACK)
    p.poly([(x + 90, 130), (x + 90, 112), (x + 108, 126), (x + 108, 130)], BLACK)
    for dx in (15, 40, 72):
        p.disc(x + dx, 134, 8, BLACK)
        p.disc(x + dx, 134, 3, GREY)
    p.rect(x + 56, 94, 28, 6, BEAM)
    for dx, dy, r in puffs:
        p.disc(x + dx, dy, r, GREY)


def curtains_and_plaque(p):
    p.rect(150, 142, 160, 20, GOLD)
    p.frame(150, 142, 160, 20, DKGOLD, 2)
    p.say(230, 158, 'NOW PLAYING', SMALL, STAGE, 'c')
    for side in (0, 1):
        x0 = 20 if side == 0 else 440
        sign = 1 if side == 0 else -1
        pts = [(x0, STAGE_TOP), (x0 + sign * 84, STAGE_TOP), (x0 + sign * 52, 104), (x0 + sign * 70, STAGE_BOTTOM), (x0, STAGE_BOTTOM)]
        p.poly(pts, DKRED)
        p.fillpoly(pts, RED, 1, 7)
    p.rect(20, STAGE_TOP, 420, 12, DKGOLD)
    p.rect(20, STAGE_BOTTOM - 4, 420, 4, GOLD)


def stage_open(p):
    """The engine rolls in over three frames, its smoke drifting back."""
    for step, x in enumerate((96, 160, 228)):
        platform(p)
        engine(p, x, [(16 - 4 * step, 80, 8), (6 - 4 * step, 70, 10), (-8 - 5 * step, 62, 12)])
        curtains_and_plaque(p)
        if step < 2:
            p.wait(4)


def seats_row(p, r):
    letter = ROWS[r]
    p.say(PLAN_X - 8, seat_y(r, 1) + 15, letter, SMALL, GOLD, 'r')
    for n in range(1, 17):
        chosen = letter == CHOSEN_ROW and n in CHOSEN_SEATS
        sold = is_sold(r, n)
        colour = CHOSEN if chosen else SOLDDK if sold else GREEN
        back = FLASH if chosen else RED if sold else DKGREEN
        p.call(SEAT, seat_x(n), seat_y(r, n), colour)
        p.color(back)
        p.pos(seat_x(n), seat_y(r, n))
        p.cmd(0x35, xy(SEAT_W / 640, 0) + xy(0, -6 / Y_SCALE) + xy(-SEAT_W / 640, 0))


def legend(p):
    for i, (label, colour, back) in enumerate([('FREE', GREEN, DKGREEN), ('SOLD', SOLDDK, RED), ('YOURS', CHOSEN, FLASH)]):
        x = 458
        y = 312 + i * 28
        p.rect(x, y, 20, 17, colour)
        p.rect(x, y, 20, 6, back)
        p.say(x + 30, y + 15, label, BODY, WHITE)


def build():
    p = Screen('0a0608 ffffff c4202e 6f0f1c f3c34a a8801e 2fa84f 14602c 6b4524 fff1b0 f6efd8 7a2b32 241830 8a8f99 ffd84a ffd84a')
    p.rect(0, 0, 640, 480, BLACK)
    p.rect(0, 0, 640, 44, DKRED)
    p.say(14, 32, 'CIVIC PLAYHOUSE BOX OFFICE', LARGE, GOLD)
    p.say(626, 32, '194', LARGE, GOLD, 'r')
    p.rect(0, 44, 640, 5, GOLD)
    p.rect(0, 446, 640, 34, DKRED)
    p.say(14, 470, '1 BUY THESE SEATS  2 OTHER SEATS  3 SHOWS', BODY, GOLD)
    p.macro(SEAT, seat_fragment())
    curtain_closed(p)
    p.say(458, 84, 'TONIGHT 8 PM', BODY, GOLD)
    p.wait(14)
    stage_open(p)
    p.say(458, 110, 'THE LAST TRAIN', BODY, WHITE)
    p.say(458, 134, 'TO MERRIDALE', BODY, WHITE)
    p.say(458, 160, 'CURTAIN 8 PM', SMALL, GREY)
    p.wait(8)
    p.rect(PLAN_X - 24, PLAN_Y - 8, 16 * PITCH_X + AISLE + 28, 8 * PITCH_Y + 40, 0)
    for r in range(8):
        seats_row(p, r)
        p.wait(3)
    p.rect(PLAN_X + 8 * PITCH_X - 4, PLAN_Y - 6, AISLE + 4, 8 * PITCH_Y + 24, 0)
    p.say(PLAN_X + 8 * PITCH_X + AISLE / 2 - 2, PLAN_Y + 8 * PITCH_Y + 22, 'AISLE', SMALL, GREY, 'c')
    for n in (1, 8, 9, 16):
        p.say(seat_x(n) + SEAT_W / 2, seat_y(7, n) + SEAT_H + 16, str(n), SMALL, GOLD, 'c')
    p.say(458, 210, 'YOUR SEATS', BODY, GOLD)
    p.say(458, 234, 'ROW D, 9-10', BODY, WHITE)
    p.say(458, 260, '$14.00 EACH', BODY, WHITE)
    p.say(458, 288, 'TOTAL $28.00', BODY, CHOSEN)
    legend(p)
    p.frame(seat_x(9) - 4, seat_y(3, 9) - 4, 2 * PITCH_X + 4, SEAT_H + 8, FLASH, 3)
    p.blink(FLASH, DKRED, 5, 5)
    return p


if __name__ == '__main__':
    save(__file__, build)
