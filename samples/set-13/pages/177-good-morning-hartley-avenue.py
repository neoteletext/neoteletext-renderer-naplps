"""Good Morning, Hartley Avenue: a household's morning front page from an invented city service."""
from _drawing import Plate, save

META = dict(
    title='Good Morning, Hartley Avenue',
    purpose='A household reads the morning page of its neighbourhood service: weather, mail and the bus',
    style='Sunrise in banded arcs over a flat-colour street, with a paper menu panel',
    techniques=['16-entry colour map', 'filled discs as sunrise bands', 'filled polygons',
                'proportional text', 'BLINK on a new-mail badge', 'WAIT between reveal steps'],
    animated=True,
)

PALETTE = (
    '0b132b fbf5e6 ffd166 f79d4c ef6f3c d9473b 1f7a7a 2f4858 '
    '9fd8ec f2c79b 7a4b2a 5b9b4a 3a3f58 ff4d6d c9e7f5 1b2a4a'
)
NAVY, PAPER, YELLOW, ORANGE, DEEP_ORANGE, RED, TEAL, SLATE = range(8)
MORNING_BLUE, SAND, BROWN, GRASS, DUSK, ALERT, PALE_SKY, PANEL = range(8, 16)


def build():
    p = Plate(PALETTE)
    # Title band and a two-band sky: pale above, morning blue at the horizon.
    p.rect(0, 0, 640, 70, PANEL)
    p.title(24, 48, 'NEIGHBOURLINE', YELLOW, 24, 34)
    p.text(452, 34, 'MON 14 JUNE', 12, 18, YELLOW)
    p.text(452, 60, 'HARTLEY AVE', 12, 18, PALE_SKY)
    p.rect(0, 70, 640, 130, PALE_SKY)
    p.rect(0, 200, 640, 130, MORNING_BLUE)

    # A cloud and a pair of birds fill the upper sky.
    for x, y, radius in ((96, 118, 16), (120, 106, 22), (146, 116, 16)):
        p.disc(x, y, radius, PAPER)
    p.rect(96, 116, 66, 16, PAPER)
    p.line([(230, 96), (240, 90), (250, 96)], NAVY, 2)
    p.line([(262, 84), (270, 79), (278, 84)], NAVY, 2)

    # The sun is revealed band by band, outer ring first, as the page draws, with a pale halo behind it.
    sun_x, sun_y = 190, 330
    p.disc(sun_x, sun_y, 172, PALE_SKY)
    p.disc(sun_x, sun_y, 150, DEEP_ORANGE)
    p.wait(6, 'sunrise')
    for radius, ink in ((128, ORANGE), (106, YELLOW), (84, ORANGE), (62, SAND)):
        p.disc(sun_x, sun_y, radius, ink)
    p.disc(sun_x, sun_y, 38, YELLOW)
    p.wait(6, 'sun complete')

    # The horizon is grass, with a road in dusk grey and dashes in sun yellow.
    p.rect(0, 330, 640, 150, GRASS)
    p.poly([(0, 398), (640, 386), (640, 424), (0, 438)], DUSK)
    for x in range(20, 640, 90):
        p.rect(x, 411, 40, 3, YELLOW)

    # Lamp posts stand along the grass above the road.
    for x in (150, 230, 300):
        p.rect(x, 350, 6, 42, SLATE)
        p.disc(x + 3, 347, 8, YELLOW)
    # A mailbox stands at the gate, its flag up when there is post; the flag blinks with the badge.
    p.rect(44, 364, 4, 30, SLATE)
    p.rect(32, 346, 28, 18, TEAL)
    p.line([(36, 355), (56, 355)], PANEL, 2)
    p.rect(60, 344, 3, 22, SLATE)
    p.rect(60, 344, 9, 6, ALERT)
    # Stepping stones lead from the mailbox to the door.
    for x in (80, 100, 118):
        p.disc(x, 384, 5, PAPER)
    # The house stands in front of the sun: body, roof, lit window, door and a tree.
    p.rect(92, 300, 120, 72, SAND)
    p.poly([(78, 302), (152, 236), (226, 302)], RED)
    p.rect(176, 248, 16, 30, BROWN)
    p.rect(138, 322, 28, 50, BROWN)
    p.rect(104, 314, 24, 22, YELLOW)
    p.rect(176, 314, 24, 22, YELLOW)
    p.line([(116, 314), (116, 336)], SLATE, 2)
    p.line([(188, 314), (188, 336)], SLATE, 2)
    p.rect(132, 372, 44, 6, PAPER)
    p.rect(236, 320, 8, 52, BROWN)
    p.disc(240, 306, 28, TEAL)
    p.disc(222, 320, 22, GRASS)
    p.wait(6, 'house')

    # The menu of the day is a paper panel under a teal header.
    p.rect(352, 96, 264, 296, PAPER)
    p.rect(352, 96, 264, 36, TEAL)
    p.text(368, 122, 'TODAY', 18, 26, PAPER)
    rows = (
        ('1 WEATHER', 'SUNNY, HIGH 74 F'),
        ('2 MAIL', None),
        ('3 SCHOOL LUNCH', 'PIZZA DAY'),
        ('4 THE BUS', 'ROUTE 14 ON TIME'),
    )
    for index, (label, detail) in enumerate(rows):
        baseline = 168 + 62 * index
        p.text(394, baseline, label, 12, 18, PANEL)
        if detail:
            p.text(394, baseline + 24, detail, 12, 18, SLATE)
        if index < len(rows) - 1:
            p.rect(368, baseline + 40, 232, 1, SAND)
    # Each menu row has its own mark: a sun, an envelope, a lunch box and a bus.
    p.disc(376, 160, 5, DEEP_ORANGE)
    p.rect(368, 220, 16, 11, TEAL)
    p.line([(368, 220), (376, 226), (384, 220)], PANEL, 2)
    p.rect(369, 282, 14, 13, ORANGE)
    p.rect(372, 279, 8, 4, PANEL)
    p.rect(368, 344, 16, 11, DEEP_ORANGE)
    p.disc(372, 358, 2, PANEL)
    p.disc(381, 358, 2, PANEL)
    # The mail badge sits on the MAIL row and blinks between alert red and deep orange.
    p.rect(548, 214, 64, 24, ALERT)
    p.text(556, 231, '2 NEW', 11, 15, PAPER)
    p.blink(ALERT, DEEP_ORANGE, on=5, off=10)
    p.wait(4, 'menu')

    # The bus the menu names is on the road, drawn last.
    p.rect(30, 398, 92, 24, YELLOW)
    for x in (40, 62, 84):
        p.rect(x, 404, 14, 10, PALE_SKY)
    p.disc(50, 424, 6, NAVY)
    p.disc(104, 424, 6, NAVY)
    p.wait(4, 'bus')

    # The prompt band at the foot of the page.
    p.rect(0, 440, 640, 40, PANEL)
    p.text(24, 466, 'PRESS 1-4 TO CHOOSE     0 FOR INDEX', 12, 18, YELLOW)
    return p


if __name__ == '__main__':
    save(__file__, build)
