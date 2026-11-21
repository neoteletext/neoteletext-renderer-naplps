from _kit import *

META = dict(title='Your Balance, Mrs Okafor',
            purpose='A home bank swings its vault door open on a customer\'s balances and paid bills.',
            style='Wheat gold and prairie green, foreshortened steel vault door',
            techniques=['native circles', 'filled polygons', 'clipped sunburst', 'DRCS', 'WAIT', 'BLINK', 'hatch fill', 'proportional text'],
            animated=True)

NIGHT, WHITE, GOLD, DKGOLD, STEEL, MID, DARK, GLOW, PAPER, GREEN, RED, INK, SKY, WHEAT, CAVE, STAMP = range(16)

CX, CY, R = 156, 256, 118


def chord(y, margin=6):
    return max(0.0, math.sqrt(max(0.0, (R - margin) ** 2 - (y - CY) ** 2)))


def interior(p):
    p.disc(CX, CY, R + 14, MID)
    p.disc(CX, CY, R + 8, DARK)
    p.disc(CX, CY, R, CAVE)
    p.disc(CX, CY, R - 10, GLOW)
    p.disc(CX, CY, R - 34, GOLD)
    p.disc(CX, CY, R - 56, GLOW)
    # three shelves cut across the chamber, loaded with bars, bags and boxes
    for shelf_y in (CY - 36, CY + 22, CY + 80):
        half = chord(shelf_y) - 6
        p.rect(CX - half, shelf_y, 2 * half, 7, DARK)
        p.rect(CX - half, shelf_y, 2 * half, 2, MID)
    half = chord(CY - 36) - 10
    for i in range(int(2 * half // 30)):          # gold bars in a pyramid
        x = CX - half + i * 30
        p.poly([(x + 2, CY - 38), (x + 8, CY - 52), (x + 24, CY - 52), (x + 30, CY - 38)], GOLD)
        p.poly([(x + 8, CY - 52), (x + 24, CY - 52), (x + 22, CY - 56), (x + 10, CY - 56)], GLOW)
    for dx in (-30, 0, 30):
        p.poly([(CX + dx - 10, CY - 56), (CX + dx + 10, CY - 56), (CX + dx + 6, CY - 70), (CX + dx - 6, CY - 70)], DKGOLD)
        p.poly([(CX + dx - 6, CY - 70), (CX + dx + 6, CY - 70), (CX + dx + 2, CY - 78), (CX + dx - 2, CY - 78)], GOLD)
    half = chord(CY + 22) - 12
    for i, dx in enumerate(range(int(-half) + 14, int(half) - 10, 34)):   # money bags
        p.ellipse(CX + dx, CY + 8, 15, 14, WHEAT)
        p.poly([(CX + dx - 6, CY - 2), (CX + dx + 6, CY - 2), (CX + dx + 3, CY - 10), (CX + dx - 3, CY - 10)], DKGOLD)
        p.rect(CX + dx - 9, CY - 9, 18, 3, GREEN)
        p.say(CX + dx, CY + 14, '$', SMALL, GREEN, 'c')
    half = chord(CY + 80) - 8
    for i in range(int(2 * half // 24)):          # deposit boxes in the bottom drawer row
        x = CX - half + i * 24
        p.rect(x + 1, CY + 87, 22, 20, [DKGOLD, MID][i % 2])
        p.rect(x + 3, CY + 89, 18, 6, STEEL)
        p.disc(x + 12, CY + 101, 2, GOLD)


def door(p, hinge, rx):
    cx = hinge + rx
    p.ellipse(cx, CY, rx + 12, R + 12, DARK)
    p.ellipse(cx, CY, rx + 6, R + 6, MID)
    p.ellipse(cx, CY, rx, R, STEEL)
    p.ellipse(cx, CY, rx * .86, R * .86, MID)
    p.ellipse(cx, CY, rx * .80, R * .80, STEEL)
    for i in range(16):
        a = i * math.pi / 8
        p.disc(cx + (rx * .93) * math.cos(a), CY + (R * .93) * math.sin(a), max(2, 5 * rx / R), DARK)
    p.ellipse(cx, CY, rx * .32, R * .32, DKGOLD)
    p.ellipse(cx, CY, rx * .26, R * .26, GOLD)
    for i in range(6):
        a = i * math.pi / 3 + .3
        p.line([(cx, CY), (cx + rx * .62 * math.cos(a), CY + R * .62 * math.sin(a))], DKGOLD, 5)
        p.disc(cx + rx * .62 * math.cos(a), CY + R * .62 * math.sin(a), max(3, 8 * rx / R), GOLD)
    p.ellipse(cx, CY, rx * .08, R * .08, DARK)
    # hinge barrels on the left edge
    for y in (CY - 70, CY + 54):
        p.rect(hinge - 12, y, 14, 28, DARK)
        p.rect(hinge - 10, y + 2, 5, 24, GOLD)


def statement(p):
    x, y, w = 318, 66, 312
    p.rect(x, y, w, 370, PAPER)
    p.rect(x, y, w, 40, GREEN)
    p.say(x + 12, y + 28, 'YOUR BALANCE', LARGE, WHITE)
    p.say(x + 12, y + 66, 'MRS A OKAFOR', BODY, GREEN)
    p.say(x + w - 12, y + 66, 'JUNE 3', BODY, GREEN, 'r')
    p.rect(x + 8, y + 74, w - 16, 3, GREEN)
    p.say(x + 12, y + 104, 'CHEQUING', BODY, INK)
    p.say(x + w - 12, y + 104, '$1,184.16', BODY, INK, 'r')
    p.say(x + 12, y + 132, 'SAVINGS', BODY, INK)
    p.say(x + w - 12, y + 132, '$3,902.50', BODY, INK, 'r')
    p.rect(x + 8, y + 144, w - 16, 3, WHEAT)
    p.say(x + 12, y + 172, 'BILLS PAID TODAY', BODY, GREEN)
    for i, (name, amt) in enumerate([('HYDRO', '48.20'), ('TELEPHONE', '22.95'), ('GAS', '31.40'), ('WATER', '17.65')]):
        yy = y + 198 + i * 30
        p.say(x + 12, yy, name, BODY, INK)
        p.say(x + 176, yy, '$' + amt, BODY, INK, 'r')
        p.rect(x + 196, yy - 20, 90, 25, STAMP)
        p.frame(x + 196, yy - 20, 90, 25, RED, 2)
        p.say(x + 241, yy, 'PAID', BODY, WHITE, 'c')
    p.say(x + 12, y + 314, 'SAVINGS, SIX MONTHS', SMALL, GREEN)
    for i, level in enumerate([14, 19, 17, 25, 29, 35]):
        p.rect(x + 12 + i * 18, y + 360 - level, 13, level, GREEN if i < 5 else GOLD)
    p.rect(x + 8, y + 361, 112, 2, INK)
    
    character(p, 0x21, x + w - 12 - 156 - 34, y + 346, 30, 24, RED)
    p.say(x + w - 12, y + 342, 'HYDRO DUE JUNE 9', SMALL, RED, 'r')
    p.say(x + w - 12, y + 362, 'THANK YOU', SMALL, GREEN, 'r')


def build():
    p = Screen('0d2b24 ffffff f2b632 9a6b12 c9d1d6 8794a0 3d4650 ffe9a0 f6efd8 1f7a4d c8352b 1b1b1b 3a7ca5 e3c16f 2a2018 c8352b')
    chrome(p, 'PRAIRIE TRUST HOMEBANK', '188', GREEN, WHITE, DKGOLD, WHITE, '1 TRANSFER  2 PAY BILLS  3 HISTORY', 44, LARGE)
    define_character(p, 0x21, 30, 24, [('poly', [(15, 1), (29, 23), (1, 23)]), ('hole', 15, 17, 1.8), ('hole', 15, 11, 2.2), ('poly', [(14, 8), (16, 8), (16, 14), (14, 14)])])
    p.rect(0, 44, 640, 8, GOLD)
    p.fillrect(0, 52, 640, 394, WHEAT, 1, 6)
    p.rect(0, 52, 300, 394, NIGHT)
    p.disc(CX, CY, R + 24, MID)
    p.disc(CX, CY, R + 16, DARK)
    door(p, CX - R, R)
    p.say(CX, 424, 'YOUR VAULT IS OPEN', BODY, GOLD, 'c')
    p.wait(15)
    # The door swings open in four steps, the interior revealed behind it.
    rays(p, CX, CY, 20, DKGOLD, 0, 52, 300, 446, 4, .45)
    rays(p, CX, CY, 20, WHEAT, 0, 52, 300, 446, 13, .12)
    p.rect(30, 404, 250, 30, NIGHT)
    for rx in (104, 88, 70, 52, 36, 22):
        interior(p)
        door(p, CX - R, rx)
        p.wait(4)
    p.rect(46, 404, 220, 32, DKGOLD)
    p.frame(46, 404, 220, 32, GOLD, 2)
    p.say(CX, 427, 'YOUR VAULT IS OPEN', BODY, WHITE, 'c')
    p.wait(6)
    statement(p)
    p.blink(STAMP, GREEN, 5, 5)
    p.wait(20)
    # a pay deposit lands while she watches
    x, y, w = 318, 66, 312
    p.rect(x + 150, y + 86, 150, 24, PAPER)
    p.say(x + w - 12, y + 104, '$1,284.16', BODY, GREEN, 'r')
    p.poly([(x + 160, y + 102), (x + 172, y + 102), (x + 166, y + 90)], GREEN)
    return p


if __name__ == '__main__':
    save(__file__, build)
