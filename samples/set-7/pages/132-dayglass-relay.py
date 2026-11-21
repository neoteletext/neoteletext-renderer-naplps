"""A tabletop logic game about routing sunlight into a sleeping lens."""
import _local
from encoder.screen import Screen, save

META = dict(title='Dayglass Relay', purpose='Optics puzzle with a misdirected beam and a dormant lens',
            style='Sea-glass board, deep green channels and bright yellow light',
            techniques=['connected line beams', 'native rings', 'filled direction markers', 'logical pels'],
            animated=False)


def build():
    p = Screen('bcdcc9 163e39 8cb7a9 77a89b 246459 ffe27a fffff0 b84537 a6cbb7 4b8376')
    p.text(28, 54, 'DAYGLASS RELAY', 35, 45, 1)
    p.rect(27, 72, 586, 324, 1)
    p.rect(34, 79, 572, 310, 9)
    for row in range(4):
        for col in range(7):
            x, y = 49 + col*80, 91 + row*73
            p.rect(x, y, 62, 61, 2)
            p.rect(x+3, y+3, 56, 55, 8)
            p.line([(x+3, y+57), (x+58, y+57), (x+58, y+3)], 3, 2)

    # A dashed channel leads from the selected mirror to the dormant lens.
    p.rect(395, 139, 10, 201, 4)
    p.rect(400, 335, 150, 10, 4)
    for y in range(151, 321, 18):
        p.rect(398, y, 4, 8, 8)
    for x in range(429, 539, 18):
        p.rect(x, 338, 8, 4, 8)
    for x, y, width, height in [(42, 267, 198, 0), (240, 121, 0, 146),
                                (240, 121, 160, 0), (400, 91, 0, 30)]:
        p.rect(x-5, y-5, width+10, height+10, 4)
        p.rect(x-2, y-2, width+4, height+4, 5)
    # The beam is currently lost in the vent at the top of the board.
    p.poly([(376, 79), (382, 61), (418, 61), (424, 79)], 1)
    p.line([(400, 91), (400, 68), (426, 49)], 5, 4)
    for ray in [[(432, 43), (440, 34)], [(430, 53), (447, 50)],
                [(425, 40), (428, 29)]]:
        p.line(ray, 7, 2)
    for x, y, slope in [(240, 267, 1), (240, 121, 1), (400, 121, 1),
                        (400, 340, -1), (160, 194, -1), (480, 194, 1)]:
        p.disk(x, y, 22, 1)
        p.disk(x, y, 17, 4)
        p.line([(x-13, y+slope*13), (x+13, y-slope*13)], 6, 4)
    for x, y, dx, dy in [(371, 93, 1, 1), (429, 93, -1, 1),
                         (371, 149, 1, -1), (429, 149, -1, -1)]:
        p.line([(x, y+dy*9), (x, y), (x+dx*9, y)], 7, 3)
    p.poly([(29, 248), (49, 248), (63, 261), (63, 273),
            (49, 286), (29, 286)], 1)
    p.poly([(37, 253), (50, 258), (57, 267), (50, 276), (37, 281)], 5)
    p.rect(531, 334, 19, 12, 4)
    p.rect(534, 338, 10, 4, 8)
    p.disk(560, 340, 26, 1).disk(560, 340, 21, 4).disk(560, 340, 16, 9)
    for dx, dy in [(0, -13), (12, -4), (7, 11), (-7, 11), (-12, -4)]:
        p.line([(560+dx, 340+dy), (560-dy*.4, 340+dx*.4)], 3, 3)
    p.disk(560, 340, 7, 0)
    p.rect(27, 414, 38, 42, 7)
    p.text(35, 451, 'A', 25, 33, 6, False)
    p.text(78, 451, 'TURN MIRROR', 25, 33, 1)
    p.line([(382, 112), (378, 122), (382, 131)], 7, 3)
    p.poly([(377, 132), (387, 135), (385, 125)], 7)
    p.poly([(396, 166), (404, 166), (400, 173)], 5)
    p.poly([(480, 335), (480, 345), (487, 340)], 5)
    p.text(440, 451, 'MOVES  07', 23, 33, 1)
    return p


if __name__ == '__main__':
    save(__file__, build())
