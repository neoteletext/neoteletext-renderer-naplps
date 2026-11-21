"""212: a scene.  A class crowds round the terminal on its cart; the screen shows the world."""
from _kit import LARGE, SMALL, Screen, save

META = dict(title='The Classroom Terminal',
            purpose='A scene of the school that was promised: a class gathered at one terminal, the world on its screen.',
            style='Flat-colour classroom with bright sweaters and a glowing map',
            techniques=['filled polygons', 'native circles', 'arcs', 'dotted line texture', 'proportional text',
                        'WAIT-drawn map', 'BLINK'],
            animated=True)

DARK, WHITE, WALL, BOARD, FLOOR, WOOD, SEA, LAND = range(8)
SAND, RUST, SKIN, SKY, HAIR, RED, MARK, PLUM = range(8, 16)
GROUND = 344


def room(p):
    p.box(0, 0, 640, GROUND, WALL)
    p.box(0, GROUND, 640, 480 - GROUND, FLOOR)
    p.box(0, GROUND - 8, 640, 8, WOOD)
    for x in range(-40, 700, 90):
        p.stroke([(x, 480), (320 + (x - 320) * .55, GROUND)], WOOD, 1)
    # Blackboard with the day's subject, and its ledge.
    p.box(26, 44, 250, 150, WOOD)
    p.box(34, 52, 234, 134, BOARD)
    p.say(48, 100, 'TODAY:', LARGE, WHITE)
    p.say(48, 140, 'THE WORLD', LARGE, SAND, fit=216)
    p.stroke([(48, 150), (120, 153), (200, 149), (250, 152)], WHITE, 2)
    # A chalk compass in the corner of the board.
    p.stroke([(236, 84), (236, 124)], WHITE, 2)
    p.stroke([(216, 104), (256, 104)], WHITE, 2)
    p.poly([(236, 76), (230, 90), (242, 90)], SAND)
    p.box(26, 194, 250, 6, DARK)
    p.box(60, 188, 26, 6, WHITE)
    # A low bookcase under the board, and the globe that used to be the only world in the room.
    p.box(30, 262, 180, 82, WOOD)
    p.box(36, 268, 168, 32, DARK)
    p.box(36, 306, 168, 32, DARK)
    x = 40
    for wide, ink in [(12, RED), (9, SAND), (14, SEA), (10, PLUM), (12, LAND), (9, RUST), (14, WHITE), (10, RED),
                      (12, SEA), (9, SAND), (13, PLUM)]:
        p.box(x, 272, wide, 28, ink)
        p.box(x + 2, 310 + wide % 3, wide, 28 - wide % 3, (PLUM, LAND, RUST, SAND)[wide % 4])
        x += wide + 3
    p.box(64, 254, 28, 8, HAIR)
    p.box(76, 244, 4, 12, HAIR)
    p.disc(78, 222, 24, SEA)
    p.poly([(62, 212), (76, 204), (86, 214), (78, 226), (68, 224)], LAND)
    p.poly([(82, 228), (94, 224), (92, 238), (84, 240)], SAND)
    p.bow((58, 236), (50, 216), (64, 200), HAIR, width=3)
    # An apple for the teacher, left on the bookcase.
    p.disc(150, 252, 10, RED)
    p.stroke([(150, 242), (154, 234)], HAIR, 2)
    p.poly([(154, 236), (164, 232), (160, 240)], LAND)
    # Window with a tree in the yard.
    p.box(470, 40, 150, 170, WHITE)
    p.box(480, 50, 130, 150, SKY)
    p.box(480, 164, 130, 36, LAND)
    for x, y, r in [(500, 78, 9), (512, 72, 12), (526, 80, 9)]:
        p.disc(x, y, r, WHITE)
    p.box(560, 110, 8, 60, WOOD)
    p.disc(564, 100, 26, LAND)
    p.disc(546, 116, 18, LAND)
    p.disc(584, 114, 18, LAND)
    p.box(542, 50, 6, 150, WHITE)
    p.box(480, 120, 130, 6, WHITE)
    # The alphabet runs along the top of the wall on cards.
    places = [30, 80, 130, 180, 230, 280, 404, 454, 504, 554]
    for index, (x, pair) in enumerate(zip(places, ('Aa', 'Bb', 'Cc', 'Dd', 'Ee', 'Ff', 'Gg', 'Hh', 'Ii', 'Jj'))):
        p.box(x, 4, 44, 30, WHITE)
        p.say(x + 22, 30, pair, SMALL, (RED, SEA, PLUM, LAND, RUST)[index % 5], 'c', fit=44)
    # The telephone jack the terminal's lead runs to, by the bookcase.
    p.box(214, 286, 14, 18, WHITE)
    p.box(218, 292, 6, 6, DARK)
    p.stroke([(222, 300), (224, 330), (238, 338)], DARK, 2)
    # A plant on the sill, and the coat pegs under the window.
    p.poly([(492, 200), (496, 184), (514, 184), (518, 200)], RUST)
    for dx, dy in ((-10, -14), (0, -22), (10, -14)):
        p.poly([(505, 184), (505 + dx - 4, 184 + dy), (505 + dx + 5, 184 + dy - 4)], BOARD)
    p.box(470, 228, 150, 6, WOOD)
    for x, ink in ((484, RED), (520, SEA)):
        p.disc(x + 10, 232, 4, DARK)
        p.poly([(x, 240), (x + 20, 240), (x + 26, 300), (x - 6, 300)], ink)
        p.box(x + 8, 234, 4, 8, ink)
    # The clock: ten past ten.
    p.disc(372, 62, 24, WHITE)
    p.disc(372, 62, 24, DARK, fill=False, width=2)
    p.stroke([(372, 62), (364, 50)], DARK, 2)
    p.stroke([(372, 62), (386, 54)], DARK, 2)


def terminal(p):
    # The cart, its shelf with the keyboard, and the set.
    for x in (236, 420):
        p.box(x, 300, 8, 132, DARK)
        p.disc(x + 4, 438, 8, DARK)
    p.box(228, 300, 208, 10, DARK)
    p.box(228, 384, 208, 8, DARK)
    p.box(262, 312, 140, 18, WALL)
    p.box(262, 326, 140, 5, HAIR)
    for x in range(270, 394, 12):
        p.box(x, 315, 8, 8, DARK)
    p.box(240, 130, 184, 170, WOOD)
    p.box(240, 130, 184, 6, HAIR)
    p.box(252, 144, 160, 128, DARK)
    p.box(258, 150, 148, 116, SEA)
    p.box(258, 256, 148, 10, WHITE)
    for index, ink in enumerate((LAND, SAND, RUST)):
        p.box(264 + index * 18, 258, 12, 6, ink)
    p.box(330, 259, 60, 4, SEA)
    p.box(252, 280, 60, 8, HAIR)
    p.disc(400, 284, 5, RED)


def world(p):
    """The map draws itself while the class watches: one land at a time, then the equator."""
    lands = [
        ([(266, 170), (276, 160), (296, 158), (310, 164), (304, 176), (296, 182), (292, 194), (284, 198),
          (282, 208), (274, 196), (266, 184)], LAND),
        ([(312, 154), (326, 154), (320, 166)], WHITE),
        ([(286, 210), (298, 208), (308, 220), (302, 240), (294, 254), (290, 236)], SAND),
        ([(328, 166), (346, 160), (350, 172), (340, 180), (330, 176)], RUST),
        ([(326, 186), (348, 184), (358, 200), (350, 226), (342, 242), (336, 222), (326, 202)], SAND),
        ([(350, 160), (396, 156), (402, 176), (392, 194), (380, 188), (372, 198), (362, 190), (354, 178)], LAND),
        ([(366, 194), (376, 196), (372, 212)], RUST),
        ([(378, 228), (398, 224), (402, 240), (386, 246)], RUST),
    ]
    for outline, ink in lands:
        p.poly(outline, ink)
        p.pause(5)
    p.pattern(line=1)
    p.stroke([(258, 212), (404, 212)], WHITE, 2)
    p.pattern()


def child(p, x, y, sweater, hair, skin, style, *detail):
    """A child from behind: shoulders, neck, the back of the head."""
    p.poly([(x - 46, 480), (x - 44, y + 62), (x - 24, y + 40), (x + 24, y + 40), (x + 44, y + 62),
            (x + 46, 480)], sweater)
    p.box(x - 10, y + 22, 20, 22, skin)
    p.disc(x, y, 30, hair)
    p.disc(x - 30, y + 6, 6, skin)
    p.disc(x + 30, y + 6, 6, skin)
    for trim in detail:
        if trim == 'stripes':
            for band in (74, 96, 118):
                p.box(x - 44, y + band, 88, 7, WHITE)
        elif trim == 'braces':
            p.stroke([(x - 18, y + 42), (x - 22, 480)], RUST, 6)
            p.stroke([(x + 18, y + 42), (x + 22, 480)], RUST, 6)
        elif trim == 'pack':
            p.box(x - 26, y + 62, 52, 60, PLUM)
            p.box(x - 26, y + 62, 52, 8, DARK)
            p.box(x - 14, y + 86, 28, 20, SAND)
        elif trim == 'collar':
            p.poly([(x - 24, y + 40), (x, y + 60), (x + 24, y + 40), (x + 30, y + 52), (x, y + 74), (x - 30, y + 52)],
                   WHITE)
        elif trim == 'hood':
            p.poly([(x - 26, y + 42), (x + 26, y + 42), (x + 16, y + 66), (x - 16, y + 66)], DARK)
    if style == 'tails':
        p.disc(x - 36, y + 22, 12, hair)
        p.disc(x + 36, y + 22, 12, hair)
        p.box(x - 40, y + 8, 8, 6, RED)
        p.box(x + 32, y + 8, 8, 6, RED)
    elif style == 'cap':
        p.bow((x - 30, y - 2), (x, y - 32), (x + 30, y - 2), RED, fill=True)
        p.poly([(x + 16, y - 10), (x + 50, y - 6), (x + 48, y + 2), (x + 20, y)], RED)
    elif style == 'bob':
        p.box(x - 30, y, 60, 30, hair)


def teacher(p):
    """In profile, facing the screen: skirt, cardigan, collar, face, glasses, hair in a bun."""
    p.box(566, 416, 14, 50, SKIN)
    p.box(596, 416, 14, 50, SKIN)
    p.poly([(556, 462), (582, 462), (582, 474), (548, 474)], DARK)
    p.poly([(588, 462), (612, 462), (612, 474), (580, 474)], DARK)
    p.poly([(544, 420), (552, 318), (620, 318), (630, 420)], DARK)
    p.poly([(548, 330), (552, 246), (568, 218), (606, 218), (624, 246), (626, 330)], PLUM)
    p.poly([(572, 218), (586, 240), (600, 218)], WHITE)
    p.box(576, 204, 22, 30, SKIN)
    p.disc(584, 180, 30, SKIN)
    p.poly([(556, 176), (544, 190), (558, 192)], SKIN)
    p.bow((558, 164), (588, 146), (614, 178), HAIR, fill=True)
    p.poly([(590, 150), (616, 170), (612, 200), (598, 180)], HAIR)
    p.disc(618, 172, 15, HAIR)
    p.disc(566, 176, 7, DARK, fill=False, width=2)
    p.stroke([(573, 176), (598, 174)], DARK, 2)
    p.stroke([(558, 198), (568, 198)], DARK, 2)
    # Her near arm reaches toward the screen; the other holds the lesson book.
    p.poly([(560, 246), (480, 222), (476, 236), (556, 276)], PLUM)
    p.disc(474, 228, 9, SKIN)
    p.box(584, 268, 34, 44, WHITE)
    p.box(584, 268, 6, 44, RED)
    p.poly([(616, 250), (630, 292), (606, 306), (598, 294), (612, 284), (606, 256)], PLUM)
    p.disc(600, 300, 8, SKIN)


def build():
    p = Screen('1c1820 f8f4e8 ecdc9c 2a5a44 c09868 8a5628 1a50c8 40c850 '
               'ffd040 f06030 f0c098 a8dcf8 3a2414 d83848 ffffff 8048b8')
    room(p)
    terminal(p)
    teacher(p)
    child(p, 96, 356, LAND, HAIR, WOOD, 'short', 'hood')
    child(p, 196, 330, RED, SAND, SKIN, 'tails', 'stripes')
    child(p, 330, 396, SAND, RUST, SKIN, 'bob', 'braces')
    child(p, 452, 344, RUST, HAIR, SKIN, 'cap', 'pack')
    child(p, 562, 410, SEA, HAIR, WOOD, 'bob', 'collar')
    # One arm goes up: she knows where that is.
    p.poly([(222, 372), (250, 300), (264, 304), (240, 384)], RED)
    p.disc(259, 298, 9, SKIN)
    # The class is settled; now the map arrives, and the pointer comes up to it.
    p.pause(10)
    world(p)
    p.stroke([(472, 226), (392, 196)], WOOD, 3)
    # Where the pointer rests, a marker on the map blinks.
    p.disc(386, 192, 5, MARK)
    p.flash(MARK, DARK, 4, 4)
    return p


if __name__ == '__main__':
    save(__file__, build)
