"""216: the clinic's page: where it is, when it is open, when a baby's shots are due, whom to call."""
from _kit import BODY, LARGE, SMALL, TITLE, Screen, save

META = dict(title='The Community Health Page',
            purpose='A community clinic gives its hours, a timeline of a child\'s vaccinations and a nurse\'s telephone line.',
            style='Friendly public-service page in teal with a coloured dose timeline',
            techniques=['filled polygons', 'native circles', 'arcs', 'repeated rectangles', 'proportional text',
                        'keypad key tops', 'WAIT reveal and booking', 'BLINK'],
            animated=True)

NAVY, WHITE, SKY, WALL, SHADE, TEAL, DEEP, GRASS = range(8)
GLASS, PINK, YELLOW, ORANGE, VIOLET, RED, PANEL, LAMP = range(8, 16)

AGES = ['2 MO', '4 MO', '6 MO', '12 MO', '18 MO', '5 YR']
# vaccine, colour, which of the ages it is given at
DUE = 2
DOSES = [('DPT', PINK, (0, 1, 2, 4, 5)), ('POLIO', YELLOW, (0, 1, 4, 5)), ('MMR', ORANGE, (3,))]


def clinic(p):
    p.box(0, 44, 640, 126, SKY)
    p.box(0, 164, 640, 14, GRASS)
    p.box(0, 176, 640, 16, SHADE)
    for x in range(10, 640, 60):
        p.box(x, 183, 30, 2, WHITE)
    # A low building with a deep fascia, a glazed entrance and a sign on a post.
    p.disc(30, 66, 13, YELLOW)
    for x, y, r in [(100, 62, 8), (112, 58, 11), (126, 64, 8)]:
        p.disc(x, y, r, WHITE)
    p.box(40, 96, 340, 72, WALL)
    p.box(32, 74, 356, 26, TEAL)
    p.box(32, 98, 356, 3, DEEP)
    p.say(244, 98, 'CLINIC', SMALL, WHITE, 'c')
    for x in (56, 104, 152, 300, 340):
        p.box(x, 114, 30, 30, GLASS)
        p.box(x, 127, 30, 2, WALL)
    p.box(206, 104, 76, 64, SHADE)
    p.box(214, 112, 28, 56, GLASS)
    p.box(246, 112, 28, 56, GLASS)
    p.box(196, 100, 96, 8, DEEP)
    # The sign on its post by the road, and shrubs.
    p.box(408, 110, 5, 60, DEEP)
    p.disc(410, 98, 19, DEEP)
    p.disc(410, 98, 16, WHITE)
    p.box(406, 87, 9, 23, TEAL)
    p.box(399, 94, 23, 9, TEAL)
    for x, r in [(18, 16), (392, 10), (428, 13)]:
        p.disc(x, 160, r, DEEP)
    # The town bus stops at the door.
    p.box(456, 163, 92, 22, ORANGE)
    p.box(456, 163, 92, 3, WHITE)
    for x in range(462, 536, 18):
        p.box(x, 168, 13, 8, GLASS)
    p.box(536, 168, 9, 12, GLASS)
    p.disc(474, 185, 5, NAVY)
    p.disc(530, 185, 5, NAVY)
    p.box(436, 150, 3, 26, DEEP)
    p.box(430, 142, 15, 10, YELLOW)
    # A tree at the corner, a nurse at the door, a child with a balloon.
    p.box(8, 120, 6, 48, DEEP)
    p.disc(12, 110, 20, GRASS)
    p.disc(24, 126, 14, GRASS)
    p.disc(292, 140, 6, WALL)
    p.poly([(286, 147), (298, 147), (301, 170), (283, 170)], WHITE)
    p.box(287, 133, 10, 3, TEAL)
    p.disc(116, 148, 5, WALL)
    p.poly([(111, 153), (121, 153), (123, 170), (109, 170)], ORANGE)
    p.stroke([(122, 156), (130, 128)], NAVY, 1)
    p.disc(131, 120, 8, RED)
    # A parent arriving with a pram.
    p.box(150, 150, 4, 22, NAVY)
    p.disc(152, 138, 7, WALL)
    p.poly([(144, 146), (160, 146), (164, 168), (140, 168)], PINK)
    p.bow((164, 160), (178, 146), (192, 160), YELLOW, fill=True)
    p.box(164, 160, 28, 8, YELLOW)
    p.disc(170, 172, 4, NAVY)
    p.disc(188, 172, 4, NAVY)


def hours(p):
    p.box(444, 56, 184, 104, WHITE)
    p.box(444, 56, 184, 26, TEAL)
    # The page knows the time: a lamp says the doors are open now.
    p.disc(462, 69, 8, WHITE)
    p.disc(462, 69, 6, LAMP)
    p.say(546, 78, 'OPEN NOW', SMALL, WHITE, 'c')
    p.say(536, 116, 'MON-FRI 8-6', BODY, NAVY, 'c', fit=180)
    p.box(456, 120, 160, 3, TEAL)
    p.say(536, 148, 'SAT 9-1', BODY, NAVY, 'c')


def timeline(p):
    """The page knows whose child it is for: doses given are solid, doses to come are rings."""
    p.box(0, 192, 640, 180, NAVY)
    p.box(0, 192, 640, 3, TEAL)
    p.say(14, 220, "ANNA'S SHOTS", SMALL, WHITE, bold=1)
    p.disc(364, 208, 8, WHITE)
    p.say(378, 220, 'GIVEN', SMALL, WHITE)
    p.disc(480, 208, 8, WHITE)
    p.disc(480, 208, 4, NAVY)
    p.say(494, 220, 'TO COME', SMALL, WHITE)
    for row in range(3):
        p.box(104, 232 + row * 30, 524, 26, PANEL)
    for column, age in enumerate(AGES):
        x = 148 + column * 88
        p.box(x - 1, 232, 2, 90, DEEP)
        p.say(x, 346, age, SMALL, VIOLET if column == DUE else WHITE, 'c')
    p.pause(8)
    for row, (name, ink, given) in enumerate(DOSES):
        y = 245 + row * 30
        p.say(14, y + 11, name, SMALL, ink)
        for column in given:
            p.disc(148 + column * 88, y, 10, ink)
            if column >= DUE:
                p.disc(148 + column * 88, y, 5, PANEL)
        p.pause(6)
    # She is six months old: that column is ringed, and the ring flashes.
    x = 148 + DUE * 88
    p.frame(x - 34, 228, 68, 124, VIOLET, 3)
    p.box(x - 52, 350, 104, 22, VIOLET)
    p.say(x, 371, 'DUE NOW', SMALL, NAVY, 'c', fit=100)


def nurse(p):
    """The nurse at the other end of the line: cap, hair, headset, a smile."""
    p.poly([(516, 446), (524, 420), (548, 408), (592, 408), (616, 420), (624, 446)], WHITE)
    p.poly([(556, 408), (570, 424), (584, 408)], WALL)
    p.box(560, 396, 20, 16, WALL)
    p.disc(570, 384, 24, WALL)
    p.bow((546, 384), (568, 356), (594, 382), DEEP, fill=True)
    p.poly([(550, 366), (590, 366), (586, 354), (554, 354)], WHITE)
    p.box(565, 356, 10, 4, TEAL)
    p.box(568, 353, 4, 10, TEAL)
    p.disc(562, 386, 3, NAVY)
    p.disc(580, 386, 3, NAVY)
    p.bow((562, 396), (571, 401), (580, 396), NAVY, width=2)
    p.bow((546, 386), (548, 404), (562, 406), NAVY, width=3)
    p.disc(546, 386, 6, NAVY)
    p.box(560, 404, 8, 5, NAVY)


def build():
    p = Screen('0c1c34 ffffff c4ecf8 f4ecd8 c8b898 14a098 0a5a5c 58b84a '
               '5a8ac8 f070a0 ffcc30 ff8030 9a70e8 e83a3a 123058 50f070')
    clinic(p)
    hours(p)
    p.box(0, 0, 640, 44, TEAL)
    p.say(14, 38, 'TAMARACK CREEK CLINIC', TITLE, WHITE, bold=1)
    p.say(626, 34, 'P 610', SMALL, WHITE, 'r')
    timeline(p)
    p.box(0, 372, 640, 74, RED)
    # A telephone handset, then the number.
    p.bow((28, 426), (40, 394), (76, 384), WHITE, width=9)
    p.oval(34, 430, 15, 11, WHITE, 16)
    p.oval(82, 390, 11, 15, WHITE, 16)
    p.say(110, 410, 'NURSE LINE 555-0142', LARGE, WHITE, bold=1)
    p.say(110, 438, 'A NURSE ANSWERS, ANY HOUR', SMALL, WHITE)
    nurse(p)
    p.box(0, 446, 640, 34, DEEP)
    p.menu(472, [('1', 'BOOK HER SHOT'), ('2', 'FIRST AID'), ('0', 'INDEX')], YELLOW, WHITE)
    p.flash(VIOLET, WHITE, 5, 5)
    # Key 1 is pressed.  The tab that said the shot was due now says when it is booked for,
    # in the green of the open lamp, and the foot band offers to change it.
    p.pause(30)
    p.box(210, 350, 228, 22, LAMP)
    p.say(324, 371, 'BOOKED: THU 2:30', SMALL, NAVY, 'c', fit=224)
    p.box(0, 446, 640, 34, DEEP)
    p.menu(472, [('1', 'CHANGE TIME'), ('2', 'FIRST AID'), ('0', 'INDEX')], YELLOW, WHITE)
    p.flash(LAMP, GRASS, 6, 6, 3)
    return p


if __name__ == '__main__':
    save(__file__, build)
