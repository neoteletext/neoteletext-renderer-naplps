"""The Wired Living Room: a family on the sofa, the set-top terminal and a cat on the rug."""
from math import cos, pi, sin
from _drawing import Plate, save

META = dict(
    title='The Wired Living Room',
    purpose='A scene of a family in 1983 with the television as its window on the new services',
    style='Flat-colour poster of a sitting room, wood cabinet, bright television menu and a sleeping cat',
    techniques=['16-entry colour map', 'filled polygons', 'discs for heads',
                'proportional text on the television', 'WAIT between scene layers'],
    animated=True,
)

PALETTE = (
    '2b2d42 f4e1c1 8d5524 c68642 3a5a40 588157 1d1d1d 90e0ef '
    '0077b6 ffd60a e76f51 f5cb5c 7d5ba6 264653 e9b98f 6d4c41'
)
NIGHT, WALL, WALNUT, PINE, SOFA_DARK, SOFA_LIGHT, BEZEL, SKY = range(8)
MENU_BLUE, MUSTARD, ORANGE, RUG, VIOLET, NAVY, SKIN, HAIR = range(8, 16)

TABLE_TOP = 372
SEAT_BOTTOM = 380
SOFA_SEAT_TOP = 318
FIGURES = (
    # centre x, head y, head radius, top colour, hair colour
    (112, 226, 22, VIOLET, HAIR),
    (196, 226, 22, ORANGE, HAIR),
    (262, 252, 15, MUSTARD, WALNUT),
    (316, 250, 14, SKY, MUSTARD),
)


def window(p):
    """A window onto the afternoon, with curtains and a frame of wood."""
    p.rect(30, 50, 170, 180, WALNUT)
    p.rect(42, 62, 146, 156, SKY)
    p.rect(114, 62, 6, 156, WALNUT)
    p.rect(42, 130, 146, 6, WALNUT)
    p.poly([(14, 40), (60, 40), (56, 240), (18, 240)], ORANGE)
    p.poly([(216, 40), (170, 40), (174, 240), (212, 240)], ORANGE)
    p.poly([(12, 40), (216, 40), (214, 50), (14, 50)], WALNUT)
    # Each curtain is held back by a tie in mustard.
    p.rect(44, 136, 20, 10, MUSTARD)
    p.rect(170, 136, 20, 10, MUSTARD)


def television(p):
    """A wooden cabinet with a screen that shows a bright menu of the household's services."""
    p.rect(330, 170, 270, 146, WALNUT)
    p.rect(344, 184, 190, 118, BEZEL)
    p.rect(354, 194, 170, 98, MENU_BLUE)
    p.rect(354, 194, 170, 18, SKY)
    p.text(362, 209, 'MENU', 9, 13, NAVY)
    for index, item in enumerate(('1 NEWS', '2 WEATHER', '3 MAIL', '4 GAMES')):
        p.text(362, 232 + 18 * index, item, 10, 14, SKY)
    for x in range(548, 596, 12):
        p.rect(x, 200, 6, 80, WALNUT)
    # A rabbit-ear aerial stands on the cabinet.
    p.line([(462, 170), (432, 118)], BEZEL, 3)
    p.line([(462, 170), (492, 118)], BEZEL, 3)
    p.rect(330, 316, 270, 14, PINE)
    p.rect(344, 330, 12, 46, WALNUT)
    p.rect(582, 330, 12, 46, WALNUT)


def sofa(p):
    """A green sofa with its back, its seat and two arms, behind the four people."""
    # The sofa stops short of the television, so the menu on its screen stays whole.
    p.rect(88, 262, 250, 70, SOFA_DARK)
    p.rect(68, 296, 36, 84, SOFA_DARK)
    p.rect(302, 296, 36, 84, SOFA_DARK)
    p.rect(104, 318, 224, 62, SOFA_LIGHT)
    p.line([(136, 318), (136, 380)], SOFA_DARK, 2)
    p.line([(210, 318), (210, 380)], SOFA_DARK, 2)
    p.line([(272, 318), (272, 380)], SOFA_DARK, 2)


def people(p):
    """Four people: two adults and two children, each with a head and a torso."""
    for centre_x, head_y, radius, top, hair in FIGURES:
        torso_top = head_y + radius + 4
        # Each torso runs down to the seat, and the head is drawn over its top so no body covers a face.
        p.poly([(centre_x - radius - 6, torso_top), (centre_x + radius + 6, torso_top),
                (centre_x + radius + 10, SEAT_BOTTOM), (centre_x - radius - 10, SEAT_BOTTOM)], top)
        # Each arm rests from the shoulder onto the arm of the sofa.
        p.line([(centre_x - radius - 4, torso_top + 8), (centre_x - radius - 22, 330)], top, 8)
        p.line([(centre_x + radius + 4, torso_top + 8), (centre_x + radius + 22, 330)], top, 8)
        p.disc(centre_x, head_y - 2, radius + 3, hair)
        p.disc(centre_x, head_y, radius, SKIN)
    p.wait(6, 'people')


def coffee_table(p):
    """A low table, with the set-top terminal and its infrared keyboard on top."""
    p.rect(456, TABLE_TOP, 150, 12, PINE)
    p.rect(466, TABLE_TOP + 12, 8, 40, WALNUT)
    p.rect(584, TABLE_TOP + 12, 8, 40, WALNUT)
    p.rect(478, 324, 104, 48, NAVY)
    p.rect(488, 332, 84, 30, MENU_BLUE)
    p.text(494, 352, 'HOME', 11, 16, MUSTARD)
    p.rect(472, 352, 8, 16, RUG)
    for row in range(2):
        for column in range(7):
            p.rect(466 + column * 17, TABLE_TOP - 18 + row * 8, 13, 6, WALL)


def cat(p, centre_x, centre_y):
    """A grey-violet cat asleep on the rug, its tail drawn as a curve."""
    p.poly([(centre_x + 60 * cos(2 * pi * step / 24), centre_y + 14 * sin(2 * pi * step / 24))
            for step in range(24)], VIOLET)
    p.disc(centre_x - 48, centre_y - 4, 16, VIOLET)
    p.poly([(centre_x - 62, centre_y - 16), (centre_x - 56, centre_y - 32), (centre_x - 46, centre_y - 16)], VIOLET)
    p.poly([(centre_x - 40, centre_y - 16), (centre_x - 34, centre_y - 30), (centre_x - 26, centre_y - 14)], VIOLET)
    # Closed eyes, and a tail that curls up from the rug.
    p.line([(centre_x - 56, centre_y - 6), (centre_x - 50, centre_y - 4)], NAVY, 2)
    p.line([(centre_x - 46, centre_y - 6), (centre_x - 40, centre_y - 4)], NAVY, 2)
    p.line([(centre_x + 52, centre_y + 4), (centre_x + 80, centre_y - 6), (centre_x + 92, centre_y - 28)], VIOLET, 8)


def floor_lamp(p):
    """A floor lamp at the front left, its shade lit warm, with a glow ring round it."""
    p.disc(42, 314, 36, MUSTARD, fill=False)
    p.poly([(22, 330), (62, 330), (54, 300), (30, 300)], MUSTARD)
    p.rect(38, 330, 4, 50, WALNUT)
    p.rect(28, 378, 28, 8, WALNUT)


def sunlight(p):
    """Three thin pale stripes of light fall from the window across the floor, as through blinds."""
    for offset in (0, 44, 88):
        p.poly([(60 + offset, 344), (76 + offset, 344), (100 + offset, 392), (84 + offset, 392)], WALL)


def wall_clock(p):
    """A wall clock between the window and the picture, its hands at ten past two."""
    p.disc(262, 96, 28, WALNUT)
    p.disc(262, 96, 22, WALL)
    p.line([(262, 96), (262, 80)], NAVY, 3)
    p.line([(262, 96), (276, 104)], NAVY, 3)
    p.disc(262, 96, 3, NAVY)


def picture(p):
    """A framed view of hills and a lake, hung on the bare right-hand wall."""
    p.rect(490, 80, 104, 76, WALNUT)
    p.rect(498, 88, 88, 60, SKY)
    p.poly([(498, 124), (530, 104), (560, 120), (586, 108), (586, 148), (498, 148)], PINE)
    p.rect(498, 136, 88, 12, MENU_BLUE)


def build():
    p = Plate(PALETTE)
    # Wall and floor, with the floor's boards drawn as lines.
    p.rect(0, 0, 640, 330, WALL)
    p.rect(0, 330, 640, 110, PINE)
    for y in range(344, 440, 16):
        p.line([(0, y), (640, y)], WALNUT, 1)
    p.wait(6, 'room')
    window(p)
    floor_lamp(p)
    wall_clock(p)
    picture(p)
    television(p)
    p.wait(6, 'television')
    sunlight(p)
    sofa(p)
    people(p)
    # A round rug, striped in two bands, with the cat asleep on it.
    p.poly([(190 + 120 * cos(2 * pi * step / 32), 412 + 18 * sin(2 * pi * step / 32)) for step in range(32)], RUG)
    p.poly([(190 + 100 * cos(2 * pi * step / 32), 412 + 13 * sin(2 * pi * step / 32)) for step in range(32)], ORANGE)
    p.poly([(190 + 80 * cos(2 * pi * step / 32), 412 + 9 * sin(2 * pi * step / 32)) for step in range(32)], RUG)
    # A plant in a pot on the far right of the floor.
    p.poly([(596, 380), (628, 380), (622, 412), (602, 412)], ORANGE)
    p.disc(612, 364, 16, SOFA_LIGHT)
    p.disc(598, 372, 11, SOFA_DARK)
    p.disc(626, 372, 11, SOFA_DARK)
    cat(p, 470, 412)
    coffee_table(p)
    p.rect(0, 440, 640, 40, NAVY)
    p.text(24, 466, 'THE WIRED LIVING ROOM', 16, 24, MUSTARD)
    p.text(468, 466, '1983', 12, 18, SKY)
    return p


if __name__ == '__main__':
    save(__file__, build)
