"""211: a programmed-learning lesson on a blackboard: a pie in eighths and four answers."""
import math

from _kit import BODY, HEAD, LARGE, SMALL, Screen, measure, save

META = dict(title='Lesson Four: Fractions',
            purpose='A programmed-learning lesson asks what fraction of a pie is orange and marks the answer.',
            style='Chalk on a green blackboard in a wooden frame',
            techniques=['pie wedges', 'native circles', 'outlined arcs', 'proportional text', 'WAIT',
                        'colour-map answer reveal', 'counted reveal', 'BLINK'],
            animated=True)

BOARD, CHALK, WOOD, GRAIN, ORANGE, CREAM, CRUST, YELLOW = range(8)
PINK, BLUE, KEY, GREEN, NOW, FELT, SLICE, ANSWER = range(8, 16)
PIE_X, PIE_Y, PIE_R = 168, 262, 112

ANSWERS = [('1', '1', '2'), ('2', '3', '8'), ('3', '5', '8'), ('4', '3', '5')]


def board(p):
    p.box(0, 0, 640, 480, WOOD)
    p.box(0, 0, 640, 5, GRAIN)
    for y, x, w in [(6, 40, 150), (8, 300, 220), (466, 90, 260), (472, 420, 150), (460, 10, 70)]:
        p.box(x, y, w, 2, GRAIN)
    p.box(14, 14, 612, 420, BOARD)
    p.frame(14, 14, 612, 420, GRAIN, 3)
    # Brass screws at the frame's corners.
    for x, y in [(8, 8), (632, 8)]:
        p.disc(x, y, 4, YELLOW)
        p.stroke([(x - 3, y), (x + 2, y)], GRAIN, 1)
    # The chalk ledge, three sticks and the felt eraser.
    p.box(0, 440, 640, 12, GRAIN)
    p.box(0, 452, 640, 28, WOOD)
    for x, ink in [(70, CHALK), (118, YELLOW), (160, PINK)]:
        p.box(x, 431, 34, 8, ink)
    p.box(520, 424, 70, 8, GRAIN)
    p.box(520, 432, 70, 8, FELT)
    for x in (60, 108, 200, 232, 470, 604):
        p.box(x, 437, 6, 2, CHALK)


def pie(p):
    # The tin's shadow, a crimped crust of small rounds, then the filling.
    p.oval(PIE_X + 8, PIE_Y + 10, PIE_R + 2, PIE_R - 2, KEY, 36)
    for crimp in range(30):
        angle = math.radians(crimp * 12)
        p.disc(PIE_X + (PIE_R - 5) * math.sin(angle), PIE_Y - (PIE_R - 5) * math.cos(angle), 10, CRUST)
    p.disc(PIE_X, PIE_Y, PIE_R - 6, CRUST)
    p.disc(PIE_X, PIE_Y, PIE_R - 14, CREAM)
    p.wedge(PIE_X, PIE_Y, PIE_R - 14, 0, 135, SLICE, steps=68)
    for cut in range(8):
        angle = math.radians(cut * 45)
        p.stroke([(PIE_X, PIE_Y), (PIE_X + (PIE_R - 2) * math.sin(angle), PIE_Y - (PIE_R - 2) * math.cos(angle))],
                 GRAIN, 3)
    p.disc(PIE_X, PIE_Y, 6, GRAIN)


def answer_key(p, column, row, key, top, bottom, ink):
    x, y = 316 + column * 152, 210 + row * 100
    p.box(x, y, 138, 88, ink)
    p.frame(x, y, 138, 88, CHALK, 2)
    p.box(x + 10, y + 26, 36, 38, CHALK)
    p.say(x + 28, y + 58, key, LARGE, BOARD, 'c', bold=1)
    p.say(x + 82, y + 42, top, HEAD, CHALK, 'c', bold=1)
    p.box(x + 60, y + 43, 44, 4, CHALK)
    p.say(x + 82, y + 84, bottom, HEAD, CHALK, 'c', bold=1)
    return x, y


def star(p, x, y, radius, ink):
    points = []
    for step in range(10):
        angle = math.radians(step * 36)
        reach = radius if step % 2 == 0 else radius * .42
        points.append((x + reach * math.sin(angle), y - reach * math.cos(angle)))
    p.poly(points, ink)


def owl(p):
    """The lesson's teacher, drawn in chalk outline: an owl in a mortarboard."""
    p.oval(92, 112, 24, 30, CHALK, 20, fill=False)
    p.disc(82, 100, 8, CHALK, fill=False, width=2)
    p.disc(102, 100, 8, CHALK, fill=False, width=2)
    p.disc(83, 101, 3, CHALK)
    p.disc(101, 101, 3, CHALK)
    p.poly([(88, 108), (96, 108), (92, 116)], YELLOW)
    p.stroke([(72, 118), (64, 132), (74, 138)], CHALK, 2)
    p.stroke([(112, 118), (122, 108), (138, 100)], CHALK, 2)
    for x in (84, 100):
        p.stroke([(x - 4, 146), (x, 140), (x + 4, 146)], YELLOW, 2)
    p.poly([(64, 82), (92, 72), (120, 82), (92, 90)], CHALK)
    p.stroke([(118, 82), (122, 94)], YELLOW, 2)
    for y in (120, 128):
        p.bow((84, y), (92, y + 4), (100, y), CHALK, width=1)


def build():
    # ANSWER starts as the colour of the other keys; the map turns it green.
    p = Screen('14442e f4f4e4 9a5a2a 5a3214 ff8a1e fff0c0 c88a3a ffe060 '
               'ff9ac0 7ad0ff 0c2c1e 34c860 ff5a8a 8a8a9a ff8a1e 0c2c1e')
    board(p)
    p.say(30, 44, 'CHALKWIRE', SMALL, BLUE)
    p.say(610, 44, 'LESSON 4', SMALL, BLUE, 'r')
    p.say(320, 92, 'FRACTIONS', HEAD, YELLOW, 'c', bold=2)
    p.stroke([(206, 98), (260, 101), (330, 97), (390, 101), (436, 98)], YELLOW, 2)
    pie(p)
    owl(p)
    p.say(316, 148, 'What fraction of the', BODY, CHALK)
    p.say(316, 180, 'pie is', BODY, CHALK)
    # The colour asked about is written in that colour.
    x = 316 + measure('pie is ', BODY[0])
    p.say(x, 180, 'orange', BODY, ORANGE, bold=1)
    p.say(x + measure('orange', BODY[0]) + 3, 180, '?', BODY, CHALK)
    # Where the pupil is in the lesson: two questions done, this one, two to come.
    for pip in range(5):
        x = 272 + pip * 24
        p.disc(x, 36, 8, GREEN if pip < 2 else NOW if pip == 2 else CHALK)
        if pip > 2:
            p.disc(x, 36, 5, BOARD)
    for index, (key, top, bottom) in enumerate(ANSWERS):
        corner = answer_key(p, index % 2, index // 2, key, top, bottom, ANSWER if key == '2' else KEY)
        if key == '2':
            right = corner
    p.say(168, 418, 'PRESS 1 TO 4', SMALL, PINK, 'c')
    # A chalk arrow from the question to the pie.
    p.bow((308, 176), (286, 192), (272, 214), PINK, width=3)
    p.poly([(262, 208), (282, 212), (268, 226)], PINK)
    # The pupil thinks; then the lesson marks the answer.
    p.pause(40)
    p.recolour(ANSWER, '1c8a44')
    # It counts the orange slices aloud, one at a time.
    for count in range(3):
        angle = math.radians(22.5 + count * 45)
        p.say(PIE_X + 66 * math.sin(angle), PIE_Y - 66 * math.cos(angle) + 14, str(count + 1), LARGE, BOARD,
              'c', bold=1)
        p.pause(7)
    # The same fraction as a bar: eight parts, three of them orange.
    p.box(52, 392, 232, 34, BOARD)
    for part in range(8):
        p.box(65 + part * 26, 385, 21, 14, SLICE if part < 3 else CREAM)
        p.pause(2)
    p.frame(62, 382, 210, 20, CHALK, 2)
    p.say(168, 428, 'YES!  3 OF 8', BODY, YELLOW, 'c', bold=1)
    # The owl's wing, which pointed at nothing, now has a star on the end of it.
    star(p, 146, 94, 10, YELLOW)
    p.stroke([(right[0] + 106, right[1] + 48), (right[0] + 114, right[1] + 62), (right[0] + 130, right[1] + 30)],
             YELLOW, 4)
    # The score so far: a star for each right answer, rings for the questions to come.
    p.say(316, 424, 'SCORE', SMALL, BLUE)
    for index in range(5):
        x = 420 + index * 38
        if index < 3:
            star(p, x, 412, 14, YELLOW)
        else:
            p.disc(x, 412, 9, CHALK, fill=False, width=2)
    p.flash(SLICE, YELLOW, 3, 9)
    p.flash(NOW, BOARD, 5, 5)
    return p


if __name__ == '__main__':
    save(__file__, build)
