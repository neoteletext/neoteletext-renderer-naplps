"""214: an electronic referendum: the proposed library, the question, two keys and the running count."""
from _kit import BODY, HEAD, LARGE, SMALL, TITLE, Screen, save

META = dict(title='Vote on the New Library',
            purpose='A township puts a question to its households on the television and shows the count as it comes in.',
            style='Civic notice: a stone facade over ballot keys and a tally bar',
            techniques=['filled polygons', 'DRCS crest character', 'inset street plan', 'repeated rectangles',
                        'native circles', 'proportional text', 'WAIT tally', 'BLINK'],
            animated=True)

NAVY, WHITE, SKY, STONE, SHADE, SLATE, DOOR, GRASS = range(8)
TREE, YES, NO, AMBER, RING, PANEL, BAND, GREY = range(8, 16)
LAWN = 204
YES_SHARE = 61


def library(p):
    p.box(0, 44, 640, LAWN - 44, SKY)
    p.box(0, LAWN, 640, 28, GRASS)
    for x, y, r in [(70, 104, 10), (86, 98, 14), (104, 106, 10), (560, 92, 9), (574, 86, 12), (590, 94, 9)]:
        p.disc(x, y, r, WHITE)
    p.box(62, 106, 50, 9, WHITE)
    p.box(554, 94, 42, 8, WHITE)
    for x, y, r in [(60, 154, 30), (100, 168, 24), (30, 178, 22)]:
        p.disc(x, y, r, TREE)
    for x, y, r in [(50, 142, 16), (90, 158, 12)]:
        p.disc(x, y, r, GRASS)
    p.box(62, 170, 8, 40, DOOR)
    # Wings with tall windows, then the portico: steps, six columns, the name, the pediment.
    p.box(140, 110, 360, 94, STONE)
    p.box(140, 104, 360, 8, SHADE)
    for x in (156, 190, 426, 460):
        p.box(x, 126, 22, 56, SLATE)
        p.box(x, 152, 22, 3, STONE)
        p.box(x + 10, 126, 2, 56, STONE)
        p.box(x - 2, 182, 26, 4, WHITE)
    # A row of dentils under the cornice.
    for x in range(144, 498, 12):
        p.box(x, 112, 6, 4, SHADE)
    p.poly([(214, 84), (320, 50), (426, 84)], STONE)
    p.poly([(236, 82), (320, 56), (404, 82)], SHADE)
    # An open book in the pediment.
    p.poly([(320, 78), (302, 74), (302, 64), (320, 68)], WHITE)
    p.poly([(320, 78), (338, 74), (338, 64), (320, 68)], WHITE)
    p.box(319, 66, 2, 13, SLATE)
    p.box(210, 84, 220, 30, STONE)
    p.box(210, 112, 220, 3, SHADE)
    p.say(320, 110, 'LIBRARY', SMALL, DOOR, 'c')
    p.box(222, 116, 196, 76, SHADE)
    p.box(300, 136, 40, 56, DOOR)
    p.box(318, 136, 3, 56, SHADE)
    for x in range(224, 420, 36):
        p.box(x, 118, 14, 74, STONE)
        p.box(x + 4, 122, 2, 64, SHADE)
        p.box(x + 9, 122, 2, 64, SHADE)
        p.box(x - 3, 116, 20, 5, WHITE)
        p.box(x - 3, 188, 20, 5, WHITE)
    for step in range(3):
        p.box(206 - step * 10, 192 + step * 6, 228 + step * 20, 6, WHITE if step % 2 == 0 else SHADE)
    p.poly([(290, 210), (350, 210), (380, 232), (260, 232)], GREY)
    # Flower beds along the front, and the drawing's label.
    for bed in (150, 440):
        p.box(bed, 206, 50, 6, TREE)
        for x in range(bed + 5, bed + 50, 10):
            p.disc(x, 205, 4, NO if (x // 10) % 2 else AMBER)
    p.box(8, 50, 164, 26, NAVY)
    p.say(90, 72, 'THE PROPOSAL', SMALL, WHITE, 'c', fit=156)
    p.box(412, 50, 220, 26, NAVY)
    p.say(522, 72, 'POLLS CLOSE 9 PM', SMALL, AMBER, 'c', fit=212)
    # Lamps at the foot of the steps, and two townspeople for scale.
    for x in (186, 454):
        p.box(x, 172, 3, 38, SLATE)
        p.disc(x + 1, 168, 6, AMBER)
    for x, coat in ((276, NO), (352, SLATE)):
        p.disc(x, 190, 4, DOOR)
        p.poly([(x - 4, 194), (x + 4, 194), (x + 5, 210), (x - 5, 210)], coat)
    # A parent and child on the path.
    p.disc(312, 212, 4, DOOR)
    p.poly([(308, 216), (316, 216), (317, 230), (307, 230)], SLATE)
    p.disc(324, 220, 3, DOOR)
    p.poly([(321, 223), (327, 223), (328, 231), (320, 231)], AMBER)
    # The township's flag on a pole in the lawn, a bench, and somebody already reading.
    p.box(488, 92, 3, 116, SLATE)
    p.poly([(491, 94), (516, 100), (491, 110)], NO)
    p.box(396, 216, 44, 4, DOOR)
    p.box(400, 220, 3, 8, DOOR)
    p.box(433, 220, 3, 8, DOOR)
    p.disc(416, 200, 5, DOOR)
    p.poly([(410, 205), (422, 205), (424, 217), (410, 217)], SLATE)
    p.box(422, 208, 10, 7, WHITE)


def site_plan(p):
    """Where it would stand: three streets, the creek, and the lot marked."""
    p.box(522, 84, 112, 116, WHITE)
    p.box(525, 87, 106, 110, NAVY)
    p.stroke([(525, 104), (560, 112), (590, 100), (627, 108)], SKY, 3)
    p.box(525, 150, 106, 5, GREY)
    p.box(556, 87, 5, 68, GREY)
    p.box(606, 87, 5, 68, GREY)
    p.box(566, 128, 34, 20, RING)
    p.say(578, 180, 'MILL ST', SMALL, WHITE, 'c', fit=104)


def crest(cell):
    """The township's arms for a DRCS character: a shield with an elder tree cut out of it."""
    cell.poly([(8, 96), (92, 96), (92, 46), (50, 4), (8, 46)])
    cell.cut()
    cell.disc(50, 62, 22)
    cell.box(45, 22, 10, 24)
    cell.ink()
    cell.box(47, 50, 6, 20)


def key(p, x, digit, word, ink):
    p.box(x, 322, 240, 48, ink)
    p.box(x + 8, 328, 40, 36, WHITE)
    p.say(x + 28, 362, digit, LARGE, NAVY, 'c', bold=1)
    p.say(x + 140, 366, word, HEAD, WHITE, 'c', bold=1)


def build():
    p = Screen('101830 ffffff a4d4f4 ece0c4 b8a888 4a5a80 7a3a1a 3aa04a '
               '1e6a34 28b858 e84838 ffb820 ffd040 1a2a5a 6a1a3a c0c4d0')
    p.glyph(0x21, (34, 34), crest)
    library(p)
    site_plan(p)
    p.box(0, 0, 640, 44, BAND)
    p.stamp(8, 40, 0x21, (34, 34), AMBER)
    p.say(50, 38, 'TOWNSHIP OF ELDERWICK', TITLE, AMBER, bold=1)
    p.say(630, 34, 'BALLOT 3', SMALL, WHITE, 'r')
    p.box(0, 232, 640, 214, NAVY)
    p.box(0, 232, 640, 3, AMBER)
    p.say(320, 262, 'Shall the township build a new', BODY, WHITE, 'c')
    p.say(320, 288, 'public library on Mill Street?', BODY, WHITE, 'c')
    p.say(320, 314, 'COST: $1.2 MILLION OVER 10 YEARS', SMALL, GREY, 'c')
    key(p, 60, '1', 'YES', YES)
    key(p, 340, '2', 'NO', NO)
    # The household presses 1: its key is ringed and ticked.
    p.pause(20)
    p.frame(54, 316, 252, 60, RING, 4)
    p.stroke([(262, 346), (272, 358), (290, 332)], WHITE, 5)
    # Then the count so far arrives and grows from the left.
    p.pause(10)
    p.say(60, 398, 'COUNT SO FAR', SMALL, GREY)
    p.say(580, 398, '1,204 HOMES', SMALL, GREY, 'r')
    p.box(60, 402, 520, 20, PANEL)
    for step in range(10):
        p.box(60 + step * 52, 402, 52, 20, YES if step * 10 < YES_SHARE else NO)
        p.pause(2)
    p.box(60 + 520 * YES_SHARE / 100 - 4, 402, 4, 20, YES)
    p.box(60 + 520 * YES_SHARE / 100, 399, 3, 26, WHITE)
    # A tick at every tenth under the bar.
    for tenth in range(11):
        p.box(60 + tenth * 52 - (2 if tenth == 10 else 0), 422, 2, 5, GREY)
    # The half-way mark: a simple majority carries it.
    p.poly([(312, 398), (328, 398), (320, 406)], AMBER)
    p.poly([(312, 426), (328, 426), (320, 418)], AMBER)
    p.say(320, 445, 'HALF CARRIES IT', SMALL, AMBER, 'c')
    p.say(60, 445, f'YES {YES_SHARE}%', SMALL, YES)
    p.say(580, 445, f'NO {100 - YES_SHARE}%', SMALL, NO, 'r')
    p.box(0, 446, 640, 34, BAND)
    p.say(320, 472, 'YOUR VOTE IS IN.  RECEIPT 4471', SMALL, WHITE, 'c')
    # The ring round the key pressed and the lot on the plan flash together.
    p.flash(RING, WHITE, 5, 10)
    return p


if __name__ == '__main__':
    save(__file__, build)
