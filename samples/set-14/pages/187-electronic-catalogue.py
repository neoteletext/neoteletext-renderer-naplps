from _kit import *

META = dict(title='The Electronic Catalogue',
            purpose='A department store shows three goods and takes an order with one key press.',
            style='Saturated primaries on navy, bold flat product drawings with price tags',
            techniques=['filled polygons', 'native circles', 'hatch fill', 'user-defined fill pattern', 'WAIT', 'BLINK', 'proportional text'],
            animated=True)

NAVY, WHITE, YELLOW, RED, ORANGE, SKY, BLUE, CREAM, CHROME, STEEL, GREEN, INK, PINK, BROWN, PANEL, BLINKER = range(16)


def toaster(p, x, y):
    # Chrome body with two slots, a warm glow and two slices of bread.
    p.poly([(x+14, y+118), (x+14, y+62), (x+30, y+44), (x+158, y+44), (x+174, y+62), (x+174, y+118)], STEEL)
    p.poly([(x+20, y+112), (x+20, y+64), (x+34, y+50), (x+154, y+50), (x+168, y+64), (x+168, y+112)], CHROME)
    p.poly([(x+20, y+64), (x+34, y+50), (x+154, y+50), (x+168, y+64), (x+150, y+70), (x+38, y+70)], WHITE)
    for sx in (x+40, x+100):
        p.rect(sx, y+46, 48, 11, INK)
        p.poly([(sx+4, y+46), (sx+4, y+14), (sx+10, y+6), (sx+22, y+10), (sx+34, y+6), (sx+44, y+14), (sx+44, y+46)], BROWN)
        p.poly([(sx+10, y+46), (sx+10, y+20), (sx+14, y+14), (sx+24, y+17), (sx+34, y+14), (sx+38, y+20), (sx+38, y+46)], ORANGE)
        p.poly([(sx+14, y+46), (sx+14, y+24), (sx+34, y+24), (sx+34, y+46)], CREAM)
    p.rect(x+8, y+118, 172, 8, STEEL)
    p.rect(x+26, y+126, 20, 8, INK)
    p.rect(x+142, y+126, 20, 8, INK)
    p.rect(x+176, y+66, 10, 40, RED)           # lever
    p.rect(x+176, y+76, 10, 8, YELLOW)
    p.disc(x+40, y+93, 9, INK)
    p.disc(x+40, y+93, 6, ORANGE)
    p.line([(x+40, y+93), (x+44, y+88)], INK, 2)
    p.rect(x+70, y+88, 80, 10, STEEL)
    for i in range(5):
        p.rect(x+76+i*15, y+90, 8, 6, [GREEN, YELLOW, ORANGE, RED, INK][i])


def radio(p, x, y):
    p.line([(x+130, y+50), (x+176, y+4)], CHROME, 3)
    p.disc(x+177, y+4, 4, YELLOW)
    for r in (9, 16, 23):                      # broadcast waves from the aerial
        p.arc((x+177-r*.7, y+4-r*.7), (x+177+r*.25, y+4-r), (x+177+r*.9, y+4-r*.1), YELLOW)
    p.box(x+12, y+46, 172, 92, BROWN, INK, 3)
    p.rect(x+16, y+50, 164, 84, ORANGE)
    p.rect(x+16, y+50, 164, 8, YELLOW)
    # speaker grille in horizontal hatch
    p.rect(x+24, y+66, 70, 60, INK)
    p.fillrect(x+24, y+66, 70, 60, CREAM, 2, 4)
    p.frame(x+24, y+66, 70, 60, STEEL, 3)
    # tuning window with a scale and needle
    p.rect(x+104, y+66, 70, 30, CREAM)
    p.frame(x+104, y+66, 70, 30, INK, 2)
    for i in range(9):
        p.line([(x+110+i*7, y+90), (x+110+i*7, y+(78 if i % 2 else 84))], INK, 1)
    p.line([(x+142, y+68), (x+142, y+94)], RED, 2)
    p.disc(x+122, y+116, 11, INK)
    p.disc(x+122, y+116, 8, CHROME)
    p.line([(x+122, y+116), (x+127, y+108)], INK, 2)
    p.disc(x+158, y+116, 11, INK)
    p.disc(x+158, y+116, 8, CHROME)
    p.line([(x+158, y+116), (x+151, y+110)], INK, 2)
    p.rect(x+20, y+138, 12, 8, INK)
    p.rect(x+164, y+138, 12, 8, INK)


def sneaker(p, x, y, flip=False):
    """A high-top in profile."""
    q = Scaled(p, x, y, .88)

    def shoe(ox, oy, upper, trim):
        # sole and midsole
        q.poly([(ox + 4, oy + 126), (ox + 4, oy + 108), (ox + 150, oy + 104), (ox + 182, oy + 114), (ox + 184, oy + 126), (ox + 160, oy + 132), (ox + 20, oy + 134)], WHITE)
        q.poly([(ox + 4, oy + 126), (ox + 184, oy + 126), (ox + 160, oy + 132), (ox + 20, oy + 134)], STEEL)
        for k in range(9):                     # sole tread
            q.line([(ox + 14 + k * 18, oy + 112), (ox + 18 + k * 18, oy + 124)], STEEL, 2)
        # upper: heel collar, ankle, tongue slope and toe box
        q.poly([(ox + 8, oy + 108), (ox + 4, oy + 46), (ox + 26, oy + 12), (ox + 72, oy + 6), (ox + 80, oy + 44),
                (ox + 108, oy + 66), (ox + 150, oy + 78), (ox + 180, oy + 98), (ox + 182, oy + 112), (ox + 150, oy + 106)], upper)
        q.poly([(ox + 108, oy + 66), (ox + 150, oy + 78), (ox + 180, oy + 98), (ox + 182, oy + 112), (ox + 126, oy + 108)], trim)
        # heel tab and stripes
        q.poly([(ox + 4, oy + 46), (ox + 26, oy + 12), (ox + 44, oy + 14), (ox + 24, oy + 52)], INK)
        q.line([(ox + 30, oy + 100), (ox + 54, oy + 72), (ox + 92, oy + 66), (ox + 128, oy + 88)], YELLOW, 4)
        # eyelets and laces
        for i in range(5):
            lx, ly = ox + 72 + i * 15, oy + 34 + i * 7
            q.line([(lx - 8, ly + 8), (lx + 8, ly - 4)], WHITE, 3)
            q.disc(lx, ly, 2, INK)
        q.poly([(ox + 60, oy + 6), (ox + 86, oy - 6), (ox + 96, oy + 18), (ox + 76, oy + 36)], trim)
    shoe(x + 6, y + 10, BLUE, RED)


def panel(p, index, painter, name, blurb, price, was):
    x = 12 + index * 210
    p.box(x, 56, 196, 324, PANEL, CHROME, 3)
    p.rect(x+6, 62, 184, 152, [CREAM, SKY, YELLOW][index])
    if index == 0:
        pattern_rect(p, x+6, 62, 184, 152, PINK, 4, 20)       # kitchen tiles
    elif index == 1:
        p.fillrect(x+6, 62, 184, 152, BLUE, 1, 6)             # wallpaper stripes
    else:
        p.fillrect(x+6, 62, 184, 152, ORANGE, 2, 6)           # running-track lanes
    p.rect(x+6, 200, 184, 14, [ORANGE, BLUE, GREEN][index])
    painter(p, x+2, 66)
    if index == 1:
        p.burst(x+34, 92, 30, 22, 10, BLINKER, 9)
        p.say(x+34, 99, 'NEW', BODY, INK, 'c')
    p.say(x+98, 240, name, BODY, WHITE, 'c')
    p.say(x+98, 262, blurb, SMALL, CHROME, 'c')
    p.burst(x+52, 308, 38, 30, 12, RED, 8)
    p.say(x+52, 318, price, LARGE, WHITE, 'c')
    p.ring(x+146, 308, 25, BLINKER, 3)
    p.keycap(x+146, 308, str(index + 1), YELLOW, INK, LARGE, 20)
    p.say(x+98, 360, was, SMALL, SKY, 'c')


def build():
    p = Screen('101a3c ffffff ffd21f e8312a ff8a1f 3fa7e0 1f4fa8 fff1c8 d6dde6 7d8794 2ea84a 1a1a1a ff6fa0 8a4b1e 24407a ffd21f')
    define_texture(p, 0x41, 20, [[(0, 0), (.5, 0), (.5, .5), (0, .5)], [(.5, .5), (1, .5), (1, 1), (.5, 1)]])
    chrome(p, '', '187', RED, WHITE, RED, YELLOW, 'PRESS 1-3 TO ORDER   0 FOR INDEX', 44, LARGE)
    # the store's mark: an F and an L interlocked inside a ring
    p.disc(26, 22, 19, YELLOW)
    p.disc(26, 22, 16, NAVY)
    p.rect(14, 10, 5, 24, WHITE)
    p.rect(14, 10, 15, 5, WHITE)
    p.rect(14, 19, 11, 4, WHITE)
    p.rect(26, 14, 5, 20, YELLOW)
    p.rect(26, 30, 12, 4, YELLOW)
    p.say(56, 32, 'FAIRFIELD & LOWE TELESHOP', LARGE, WHITE)
    p.wait(8)
    panel(p, 0, toaster, 'TWO SLICE TOASTER', 'SLOT LEVER AND DIAL', '$19', 'CATALOGUE PAGE 14')
    p.wait(12)
    panel(p, 1, radio, 'POCKET RADIO', 'AM FM WITH SPEAKER', '$24', 'CATALOGUE PAGE 31')
    p.wait(12)
    panel(p, 2, sneaker, 'RUNNING SHOES', 'SIZES 6 TO 12', '$29', 'CATALOGUE PAGE 52')
    p.wait(10)
    p.rect(0, 392, 640, 54, NAVY)
    p.rect(0, 392, 640, 2, CHROME)
    p.say(14, 418, 'CHARGE IT TO ACCOUNT 4471', BODY, WHITE)
    p.say(14, 440, 'DELIVERED IN 3 DAYS', BODY, SKY)
    # the viewer's own keypad: keys 1 to 3 are the ones to press
    p.box(404, 396, 222, 46, STEEL, CHROME, 2)
    for i, label in enumerate('123456'):
        kx, ky = 414 + (i % 3) * 68 + (0 if i % 3 == 0 else 0), 400 + (i // 3) * 20
        lit = i < 3
        p.rect(kx, ky, 60, 17, YELLOW if lit else CHROME)
        p.say(kx + 30, ky + 14, label, SMALL, INK, 'c')
    p.blink(BLINKER, RED, 6, 6)
    p.wait(25)
    # the viewer presses 2: the radio panel is picked out and the order confirmed
    p.frame(224, 58, 192, 320, YELLOW, 4)
    p.rect(0, 395, 400, 50, NAVY)
    p.say(14, 418, 'YOU PRESSED 2: POCKET RADIO $24', BODY, YELLOW)
    p.say(14, 440, 'CHARGED TO ACCOUNT 4471', BODY, WHITE)
    p.rect(482, 400, 60, 17, ORANGE)
    p.say(512, 414, '2', SMALL, INK, 'c')
    return p


if __name__ == '__main__':
    save(__file__, build)
