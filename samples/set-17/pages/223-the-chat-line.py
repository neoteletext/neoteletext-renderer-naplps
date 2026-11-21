"""The Chat Line: a late-night room of the service's chat, where people talked more than they read the news."""
from _screen import Plate, oval, save

META = dict(
    title='The Chat Line',
    purpose='Subscribers talk in a late-night chat room; the service listens and the screen scrolls',
    style='Night-blue room with a colour-coded member list, programmable-character badges and a blinking heart',
    techniques=['DRCS badges for each member, in the list and before each line', 'speech-balloon mark', 'DRCS heart with BLINK', 'a private message panel', 'DRCS musical notes blinking', 'night window with curtains in the member column', 'proportional text in colour per speaker', 'a time on every line',
                'BLINK cursor', 'WAIT between arriving lines'],
    animated=True,
)

PALETTE = ('101a33 3b1f6b f4f1ff 8f9ac2 ffd54a 5fe08a ff7ab8 ff9a3c '
           '5fd3ff c8a2ff ff3b5c 1b2850 0a1022 0a1022 ffd0dc 3a4a80')
(NIGHT, BAND, WHITE, GREY, YELLOW, GREEN, PINK, ORANGE,
 CYAN, LILAC, HEART, PANEL, CURSOR, DEEP, BLUSH, RULE) = range(16)

BADGES = {
    'M': [oval(50, 50, 40, 40), ('clear', oval(68, 38, 34, 34))],                       # moon
    'T': [[(50, 6), (86, 70), (58, 70), (58, 94), (42, 94), (42, 70), (14, 70)]],      # cedar
    'C': [oval(50, 62, 34, 30), [(18, 46), (24, 8), (44, 34)], [(82, 46), (76, 8), (56, 34)],
          ('clear', oval(38, 56, 6, 6, 8)), ('clear', oval(62, 56, 6, 6, 8))],         # cat
    'O': [oval(50, 56, 34, 38), [(16, 30), (24, 6), (40, 22)], [(84, 30), (76, 6), (60, 22)],
          ('clear', oval(36, 46, 11, 11, 12)), ('clear', oval(64, 46, 11, 11, 12)),
          oval(36, 46, 5, 5, 8), oval(64, 46, 5, 5, 8)],                                 # owl
    'P': [[(14, 30), (60, 30), (60, 44), (30, 44), (30, 82), (14, 82)], oval(70, 34, 18, 20)],   # pipe
    'S': [[(50, 4), (62, 38), (96, 40), (68, 60), (80, 94), (50, 72), (20, 94), (32, 60), (4, 40), (38, 38)]],
    'H': [oval(30, 34, 24, 24), oval(70, 34, 24, 24), [(8, 44), (92, 44), (50, 94)]],    # heart
    'N': [oval(36, 78, 22, 15), [(50, 78), (50, 8), (60, 8), (60, 78)],
          [(60, 8), (88, 30), (84, 44), (60, 26)]],                                        # note
}
MEMBERS = (('M', 'MOONPIE', YELLOW), ('T', 'CEDARBOY', GREEN), ('C', 'KAT-7', PINK),
           ('O', 'NIGHTOWL', ORANGE), ('P', 'GRANDPA J', CYAN), ('S', 'SKYE', LILAC))
BADGE_OF = {name: code for code, name, _ in MEMBERS}
LINES = (('MOONPIE', YELLOW, 'anyone else still up?', '11:36'),
         ('NIGHTOWL', ORANGE, 'always :)', '11:37'),
         ('KAT-7', PINK, 'mum says 10 more minutes', '11:39'),
         ('GRANDPA J', CYAN, 'snow coming tomorrow, kids', '11:40'),
         ('MOONPIE', YELLOW, 'cocoa time, back soon', '11:41'))


def build():
    p = Plate(PALETTE, NIGHT)
    for code, contours in BADGES.items():
        p.glyph(code, *contours)

    p.rect(0, 0, 640, 56, BAND)
    # The service's mark: a speech balloon with three dots.
    p.poly(oval(34, 26, 22, 16, 24), PINK)
    p.poly([(22, 36), (16, 50), (34, 40)], PINK)
    for k in range(3):
        p.disc(24 + k * 10, 26, 3, BAND)
    p.text(66, 40, 'PARLOUR', 22, 32, PINK, prop=False)
    p.text(240, 38, 'NIGHT OWLS', 14, 22, WHITE, prop=False)
    p.text(450, 38, '11:42 PM', 13, 20, YELLOW, prop=False)
    p.text(580, 38, '223', 13, 20, CYAN, prop=False)

    # Who is in the room, each with a badge, and the night outside.
    p.rect(0, 56, 176, 330, PANEL)
    p.text(14, 84, '6 IN THE ROOM', 12, 18, GREY, prop=False)
    for index, (code, name, ink) in enumerate(MEMBERS):
        y = 116 + index * 32
        p.programmable(12, y + 4, code, 24, 24, ink)
        p.text(44, y, name, 12, 18, ink, prop=False)
    p.programmable(150, 116 + 5 * 32 + 2, 'H', 18, 18, HEART)
    p.rect(22, 300, 132, 76, DEEP)
    p.disc(112, 326, 14, YELLOW)
    p.disc(120, 320, 12, DEEP)
    for sx, sy in ((40, 316), (66, 334), (52, 360), (90, 360), (138, 356)):
        p.disc(sx, sy, 2, WHITE)
    p.rect(20, 298, 136, 80, RULE, fill=False)
    p.line([(88, 298), (88, 378)], RULE, 3)
    p.line([(20, 338), (156, 338)], RULE, 3)
    # Curtains drawn back to either side and a sill under the window.
    p.poly([(14, 292), (40, 292), (24, 336), (30, 380), (14, 380)], PINK)
    p.poly([(162, 292), (136, 292), (152, 336), (146, 380), (162, 380)], PINK)
    p.rect(10, 292, 156, 6, RULE)
    p.rect(12, 378, 152, 7, GREY)
    p.line([(176, 56), (176, 386)], RULE, 2)
    p.wait(6, 'members')

    # The conversation arrives a line at a time.
    for index, (name, ink, words, time) in enumerate(LINES):
        y = 88 + index * 40
        p.programmable(192, y + 1, BADGE_OF[name], 18, 18, ink)
        p.text(216, y, name + ':', 12, 18, ink, prop=False)
        p.text(562, y, time, 12, 18, GREY, prop=False)
        p.text(206, y + 19, words, 13, 20, WHITE)
        p.wait(5)

    # A private message for this household, apart from the room.
    p.rect(190, 300, 438, 78, LILAC)
    p.rect(194, 304, 430, 70, DEEP)
    p.text(206, 328, 'PRIVATE FROM SKYE', 12, 18, LILAC, prop=False)
    p.programmable(424, 330, 'H', 20, 20, HEART)
    p.text(206, 358, 'did u get my card? it plays a tune', 13, 20, WHITE)
    # The card's tune: three notes rising out of the panel.
    for index, (nx, ny, size) in enumerate(((470, 334, 18), (512, 322, 22), (558, 308, 26))):
        p.programmable(nx, ny, 'N', size, size, BLUSH)

    # The line being typed, with a blinking cursor, and the commands.
    p.rect(0, 386, 640, 44, DEEP)
    p.text(14, 416, 'CEDARBOY>', 13, 20, GREEN, prop=False)
    p.text(140, 416, 'yes! see u in the quiz room', 14, 22, WHITE)
    p.rect(468, 398, 12, 22, CURSOR)
    p.rect(0, 430, 640, 50, BAND)
    p.text(14, 462, '# SEND   1 ROOMS   2 PRIVATE', 13, 20, WHITE, prop=False)
    # The cursor's own colour is the input line's; BLINK lends it white for half of each second.
    p.blink(CURSOR, WHITE, on=5, off=5)
    p.blink(HEART, BLUSH, on=4, off=8)
    p.blink(BLUSH, LILAC, on=3, off=5, delay=2)
    return p


if __name__ == '__main__':
    save(__file__, build)
