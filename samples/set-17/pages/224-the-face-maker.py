"""The Face Maker: a face kit played on the keypad, each part chosen by number and drawn in turn."""
import math

from _screen import Plate, oval, polar, save

META = dict(
    title='The Face Maker',
    purpose='A family builds a cartoon face from numbered parts and sends it on as a card',
    style='Big flat-colour cartoon face in a photo-booth frame beside a numbered parts menu',
    techniques=['WAIT between face parts', 'BLINK on the part being changed', 'filled arcs for smile and cheeks', 'a rounded nose and inner ears',
                'many small discs for curls', 'pleated curtains with a scalloped valance', 'an envelope for the card', 'DEF TEXTURE polka-dot wallpaper', 'a speech balloon', 'thumbnail choices in boxes', 'DRCS part icons in the menu', 'fixed-pitch menu text'],
    animated=True,
)

PALETTE = ('2a1650 e8505b ffe29a f2b88a d98a5c c0452a ffffff 2f7fd8 '
           '1d1a2a b0203a ff8a8a 3fbf7f ffd23f 3a2470 fff5e0 e8505b')
(VIOLET, RED_BAND, BACKDROP, SKIN, SHADE, HAIR, EYE_WHITE, IRIS,
 INK, MOUTH, CHEEK, HAT, STRIPE, PANEL, PAPER, CHOSEN) = range(16)

FX, FY = 190, 262
PARTS = (('1', 'HEAD', '2'), ('2', 'HAIR', '4'), ('3', 'EYES', '3'), ('4', 'NOSE', '1'),
         ('5', 'MOUTH', '5'), ('6', 'HAT', '2'))
SELECTED = 4
# One programmable icon per part, on the 100 by 100 glyph grid, in the order of PARTS.
ICONS = (
    ('h', [oval(50, 54, 34, 40)]),
    ('w', [oval(26, 52, 22, 22), oval(50, 38, 24, 24), oval(74, 52, 22, 22), [(6, 52), (94, 52), (94, 74), (6, 74)]]),
    ('e', [[(4, 50), (30, 26), (70, 26), (96, 50), (70, 74), (30, 74)], ('clear', oval(50, 50, 17, 17)),
           oval(50, 50, 9, 9)]),
    ('n', [[(52, 8), (82, 88), (22, 88)]]),
    ('m', [[(50 + 42 * math.cos(math.radians(t)), 34 + 46 * math.sin(math.radians(t))) for t in range(0, 181, 15)]]),
    ('t', [[(50, 12), (88, 90), (12, 90)], oval(50, 10, 10, 10)]),
)


def build():
    p = Plate(PALETTE, VIOLET)
    for code, contours in ICONS:
        p.glyph(code, *contours)
    p.rect(0, 0, 640, 56, RED_BAND)
    p.text(18, 42, 'PHIZKIT', 24, 34, STRIPE, prop=False)
    p.text(214, 38, 'MAKE A FACE', 13, 20, PAPER, prop=False)
    p.text(572, 40, '224', 14, 22, PAPER, prop=False)

    # The photo-booth frame.
    p.rect(20, 70, 340, 352, PANEL)
    p.rect(30, 80, 320, 332, BACKDROP)
    for k in range(9):
        p.disc(40 + k * 38, 92, 6, STRIPE)
    # Polka-dot wallpaper behind the sitter: one dot programmed as fill pattern 4 on a 20-unit mask.
    p.pattern('A', (20, 20), oval(30, 30, 16, 16, 10))
    p.fill_with(4)
    p.rect(62, 100, 256, 312, CHEEK)
    p.fill_with(0)
    # Photo-booth curtains, pleated, drawn back to either side.
    for left in (30, 318):
        p.rect(left, 80, 32, 332, RED_BAND)
        for k in range(1, 4):
            p.line([(left + k * 8, 84), (left + k * 8 + (3 if left < 100 else -3), 410)], MOUTH, 2)
    p.rect(30, 80, 320, 14, MOUTH)
    for k in range(10):
        p.disc(46 + k * 32, 94, 16, RED_BAND)
    p.wait(4, 'frame')

    # Shoulders, collar and neck, under the head.
    p.poly([(50, 412), (74, 372), (306, 372), (330, 412)], HAT)
    p.rect(160, 340, 60, 44, SHADE)
    p.poly([(150, 372), (190, 384), (176, 404)], EYE_WHITE)
    p.poly([(230, 372), (190, 384), (204, 404)], EYE_WHITE)

    # Head and ears.
    p.disc(FX - 104, FY + 10, 24, SHADE)
    p.disc(FX + 104, FY + 10, 24, SHADE)
    # The curve inside each ear.
    p.pel(3)
    p.arc((FX - 110, FY - 4), (FX - 118, FY + 10), (FX - 110, FY + 24), SKIN)
    p.arc((FX + 110, FY - 4), (FX + 118, FY + 10), (FX + 110, FY + 24), SKIN)
    p.poly(oval(FX, FY + 10, 106, 126, 40), SKIN)
    p.wait(5, 'head')

    # Hair: a fringe of curls.
    for k in range(12):
        x, y = polar(FX, FY + 10, 114, 196 + k * 13.4)
        p.disc(x, y, 24, HAIR)
    p.poly([(FX - 96, FY - 70), (FX - 60, FY - 98), (FX, FY - 108), (FX + 60, FY - 98), (FX + 96, FY - 70),
            (FX + 60, FY - 80), (FX, FY - 86), (FX - 60, FY - 80)], HAIR)
    p.wait(5, 'hair')

    # Eyes and brows.
    for side in (-1, 1):
        ex = FX + side * 44
        p.poly(oval(ex, FY - 14, 28, 22, 24), EYE_WHITE)
        p.disc(ex + 4, FY - 12, 13, IRIS)
        p.disc(ex + 4, FY - 12, 6, INK)
        p.disc(ex + 8, FY - 16, 3, EYE_WHITE)
        p.line([(ex - 22, FY - 44), (ex - 8, FY - 54), (ex + 8, FY - 54), (ex + 22, FY - 46)], HAIR, 5)
    p.wait(5, 'eyes')

    # Nose, freckles and cheeks.
    # A rounded nose: a soft bridge, a round tip and two nostrils.
    p.poly([(FX - 3, FY - 6), (FX + 3, FY - 6), (FX + 9, FY + 26), (FX - 9, FY + 26)], SHADE)
    p.poly(oval(FX, FY + 30, 17, 13, 20), SHADE)
    p.disc(FX - 7, FY + 36, 3, MOUTH)
    p.disc(FX + 7, FY + 36, 3, MOUTH)
    for dx, dy in ((-60, 22), (-48, 32), (-70, 36), (60, 22), (48, 32), (70, 36)):
        p.disc(FX + dx, FY + dy, 3, SHADE)
    p.disc(FX - 72, FY + 52, 18, CHEEK)
    p.disc(FX + 72, FY + 52, 18, CHEEK)
    p.wait(5, 'nose')

    # The smile: a filled arc, its teeth, its tongue.
    p.arc((FX - 56, FY + 62), (FX, FY + 112), (FX + 56, FY + 62), MOUTH, fill=True)
    p.rect(FX - 40, FY + 62, 80, 12, EYE_WHITE)
    p.arc((FX - 22, FY + 98), (FX, FY + 88), (FX + 22, FY + 98), CHEEK, fill=True)
    p.wait(5, 'mouth')

    # A party hat on top.
    p.poly([(FX - 60, FY - 104), (FX + 10, FY - 168), (FX + 64, FY - 92)], HAT)
    for t in (0.35, 0.65):
        a = (FX - 60 + (70 * t), FY - 104 - 64 * t)
        b = (FX + 64 - (54 * t), FY - 92 - 76 * t)
        p.line([a, b], STRIPE, 6)
    p.disc(FX + 10, FY - 168, 12, STRIPE)
    p.wait(5, 'hat')

    # The face speaks: this is a card in the making.
    p.poly(oval(300, 126, 64, 24, 28), PAPER)
    p.poly([(262, 140), (244, 170), (282, 146)], PAPER)
    p.text(252, 136, 'HI GRAN!', 12, 18, INK, prop=False)

    # The parts menu with the current choice of each.
    p.rect(376, 70, 248, 352, PANEL)
    p.text(392, 100, 'PART      No.', 13, 20, STRIPE, prop=False)
    for index, (key, name, choice) in enumerate(PARTS):
        y = 136 + index * 34
        if index == SELECTED:
            p.rect(384, y - 24, 232, 32, CHOSEN)
        p.text(392, y, f'{key} {name}', 14, 22, PAPER, prop=False)
        p.text(548, y, choice, 14, 22, STRIPE, prop=False)
        p.programmable(580, y, ICONS[index][0], 24, 24, PAPER)
    # Three mouths to choose from, numbered; the chosen one is framed in gold.
    for k in range(3):
        x = 396 + k * 76
        if k == 1:
            p.rect(x - 6, 340, 76, 68, STRIPE)
        p.rect(x, 346, 64, 56, BACKDROP)
        p.text(x + 4, 366, str(k + 4), 12, 18, INK, prop=False)
        if k == 1:
            p.arc((x + 16, 370), (x + 36, 396), (x + 56, 370), MOUTH, fill=True)
        elif k == 0:
            p.poly(oval(x + 38, 380, 13, 12, 12), MOUTH)
        else:
            p.line([(x + 18, 382), (x + 56, 382)], MOUTH, 4)

    p.rect(0, 432, 640, 48, RED_BAND)
    p.text(18, 464, '1-6 CHANGE   7 SEND AS A CARD', 14, 22, PAPER, prop=False)
    p.rect(470, 442, 48, 30, PAPER)
    p.line([(470, 442), (494, 460), (518, 442)], RED_BAND, 2)
    # The part being changed flashes in the menu.
    p.blink(CHOSEN, HAT, on=5, off=5)
    return p


if __name__ == '__main__':
    save(__file__, build)
