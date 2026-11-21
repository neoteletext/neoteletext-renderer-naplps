from _kit import *

META = dict(title='Build Your Credit',
            purpose='A savings and loan advertisement that stacks coins into a staircase, climbs it and only then says its slogan.',
            style='Royal blue sky, gold coin stacks, a flat figure climbing',
            techniques=['filled polygons', 'native circles', 'WAIT', 'BLINK', 'sequenced drawing', 'proportional text'],
            animated=True)

NAVY, WHITE, GOLD, DKGOLD, PALE, GREEN, DKGREEN, SKY, RED, SKIN, SUIT, INK, CLOUD, ORANGE, SPARK, GLINT = range(16)

GROUND = 428
STEP_W = 64
STEPS = 8
X0 = 56
PITCH = 22


def step_x(i):
    return X0 + i * STEP_W


def step_top(i):
    return GROUND - (i + 1) * PITCH - 6


def coin(p, cx, bottom):
    p.rect(cx - 29, bottom - 14, 58, 14, DKGOLD)
    p.ellipse(cx, bottom, 29, 7, DKGOLD)
    for k in range(-24, 25, 6):
        p.line([(cx + k, bottom - 12), (cx + k, bottom + 2)], GOLD, 1)
    p.ellipse(cx, bottom - 14, 29, 8, GOLD)
    p.ellipse(cx, bottom - 14, 22, 5, PALE)
    p.ellipse(cx, bottom - 14, 17, 3, GOLD)
    p.line([(cx, bottom - 17), (cx, bottom - 11)], DKGOLD, 2)
    p.line([(cx - 5, bottom - 16), (cx, bottom - 12), (cx + 5, bottom - 16)], DKGOLD, 2)


def man(p, x, base, arm_up=False, stride=0):
    p = Scaled(p, x, base, 1.5)
    """A flat figure, feet at (x, base)."""
    lead, trail = (6, -6) if stride else (-3, 3)
    p.poly([(x - 9, base - 24), (x - 3, base - 24), (x - 1 + lead, base), (x - 11 + lead, base)], INK)
    p.poly([(x + 3, base - 24), (x + 9, base - 24), (x + 12 + trail, base), (x + 2 + trail, base)], INK)
    p.poly([(x - 10, base - 52), (x + 10, base - 52), (x + 11, base - 22), (x - 11, base - 22)], SUIT)
    p.poly([(x - 2, base - 52), (x + 2, base - 52), (x + 3, base - 36), (x - 3, base - 36)], WHITE)
    p.rect(x - 1, base - 48, 3, 14, RED)
    if arm_up:
        p.poly([(x + 9, base - 50), (x + 22, base - 68), (x + 27, base - 64), (x + 13, base - 44)], SUIT)
    else:
        p.poly([(x + 9, base - 50), (x + 17, base - 36), (x + 13, base - 33), (x + 7, base - 42)], SUIT)
        p.rect(x + 12, base - 38, 16, 11, DKGOLD)
    p.disc(x, base - 62, 9, SKIN)
    p.poly([(x - 9, base - 63), (x - 6, base - 72), (x + 7, base - 72), (x + 9, base - 62), (x + 4, base - 66)], INK)


BUILDINGS = [(10, 44, 70), (60, 36, 100), (100, 50, 64), (160, 40, 120), (206, 54, 80), (270, 36, 108),
             (312, 50, 70), (368, 40, 130), (414, 48, 84), (468, 38, 104), (510, 54, 66), (570, 60, 92)]


def skyline(p, left, right, top, bottom):
    """Pale town behind the stair, repainted over any strip of sky that is cleared."""
    for x0, w, h in BUILDINGS:
        lo, hi = max(x0, left), min(x0 + w, right)
        y0 = max(GROUND - h, top)
        if lo >= hi or y0 >= bottom:
            continue
        p.rect(lo, y0, hi - lo, bottom - y0, CLOUD)
        for wx in range(x0 + 6, x0 + w - 8, 12):
            for wy in range(GROUND - h + 8, GROUND - 14, 18):
                if left <= wx and wx + 5 <= right and top <= wy and wy + 8 <= bottom:
                    p.rect(wx, wy, 5, 8, SKY)


def build():
    p = Screen('0b2a66 ffffff ffc928 a87408 fff08a 2fb55a 1b7a3a 5fb4f0 e03a2e f2b88a 1c2740 101010 d9efff ff8c2a ffffff ffc928')
    p.rect(0, 0, 640, 480, SKY)
    p.rect(0, 0, 640, 44, NAVY)
    p.say(14, 32, 'THISTLE & OAK SAVINGS', LARGE, GOLD)
    p.say(626, 32, '189', LARGE, GOLD, 'r')
    p.rect(0, 44, 640, 6, GOLD)
    # sun and clouds behind the stair
    p.disc(590, 94, 42, PALE)
    p.disc(590, 94, 31, GOLD)
    for x, y, s in [(330, 96, 1)]:
        for dx, dy, r in [(0, 0, 22), (24, -8, 26), (52, 2, 20), (26, 10, 22)]:
            p.disc(x + dx * s, y + dy * s, r * s, CLOUD)
    skyline(p, 0, 640, 0, GROUND)
    p.rect(0, GROUND, 640, 52, DKGREEN)
    p.rect(0, GROUND, 640, 8, GREEN)
    for x in range(8, 640, 38):
        p.poly([(x, GROUND), (x + 4, GROUND - 9), (x + 8, GROUND)], GREEN)
    p.wait(6)
    # Step after step, coin on coin.
    for i in range(STEPS):
        p.ellipse(step_x(i) + 8, GROUND + 3, 40, 6, DKGREEN)
        for j in range(i + 1):
            coin(p, step_x(i), GROUND - 6 - j * PITCH)
        p.wait(3)
    # The figure climbs every step, the sky redrawn behind each stage.
    marks = list(range(1, STEPS))
    for n, i in enumerate(marks):
        man(p, step_x(i) - 4, step_top(i) - 14, arm_up=(n == len(marks) - 1), stride=n % 2)
        if n < len(marks) - 1:
            p.wait(2)
            p.rect(step_x(i) - 38, step_top(i) - 150, 76, 138, SKY)
            skyline(p, step_x(i) - 38, step_x(i) + 38, step_top(i) - 150, step_top(i) - 12)
    # a flag on the last step, unfurling in two frames
    top = step_top(7)
    fx = step_x(7) + 18
    p.line([(fx, top - 14), (fx, top - 98)], INK, 3)
    p.poly([(fx, top - 98), (fx + 34, top - 94), (fx + 30, top - 80), (fx, top - 76)], RED)
    p.wait(3)
    p.rect(fx + 2, top - 108, 52, 40, SKY)
    p.poly([(fx, top - 98), (fx + 24, top - 104), (fx + 46, top - 90), (fx + 40, top - 84), (fx + 20, top - 90), (fx, top - 72)], RED)
    p.wait(8)
    # slogan last
    p.say(34, 118, 'BUILD YOUR', BIG, NAVY, shade=WHITE)
    p.say(34, 168, 'CREDIT', BIG, RED, shade=WHITE)
    p.wait(6)
    # confetti over the stair, two falls
    for wave, shades in enumerate(([RED, GOLD, WHITE], [ORANGE, PALE, RED])):
        for k in range(26):
            cx = 150 + (k * 97 + wave * 41) % 430
            cy = 90 + (k * 53 + wave * 29) % 130
            if cx < 340 and cy < 230:
                continue
            p.poly([(cx, cy), (cx + 6, cy + 2), (cx + 4, cy + 8), (cx - 2, cy + 6)], shades[k % 3])
        p.wait(3)
    p.say(36, 208, 'ONE STEP AT A TIME', LARGE, NAVY)
    p.burst(318, 266, 46, 36, 14, GLINT, 6)
    p.say(318, 262, 'LOANS', BODY, NAVY, 'c')
    p.say(318, 282, 'FROM 9.9%', BODY, NAVY, 'c')
    for i in range(3, STEPS):
        sx, sy = step_x(i) + 12, step_top(i) - 6
        p.poly([(sx, sy - 9), (sx + 2, sy - 2), (sx + 9, sy), (sx + 2, sy + 2), (sx, sy + 9), (sx - 2, sy + 2), (sx - 9, sy), (sx - 2, sy - 2)], SPARK)
    p.rect(0, 446, 640, 34, NAVY)
    p.say(14, 470, 'ASK ABOUT A STARTER LOAN - PRESS 1', BODY, WHITE)
    p.blink(GLINT, ORANGE, 5, 5)
    p.blink(SPARK, GOLD, 4, 8, 2)
    return p


if __name__ == '__main__':
    save(__file__, build)
