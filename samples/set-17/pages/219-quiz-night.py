"""Quiz Night: a question, four coloured answers, a draining clock, then the answer revealed by the colour map."""
from _screen import Plate, save

META = dict(
    title='Quiz Night',
    purpose='A household plays the evening quiz against the clock and the rest of the city',
    style='Game-show panels in four saturated answer colours on deep violet',
    techniques=['WAIT countdown dial overdrawn slice by slice', 'drawn globe', 'question badge', 'progress pips', 'drop-shadowed answer buttons', 'colour-map reveal dimming the wrong answers',
                'BLINK on the right answer', 'star sparks after the reveal', 'filled arcs', 'fixed and proportional text'],
    animated=True,
)

PALETTE = ('1a0b3b 2b1366 ffd93d 1a1033 ffffff 4de1ff ff4fb4 4a4566 '
           'e63946 3a7bff 21b35b ff8c1a 7cff6b 8cff9e 120830 b9b3d9')
(VIOLET, BAND, YELLOW, INK, WHITE, CYAN, PINK, DIM,
 RED, BLUE, GREEN, ORANGE, CLOCK, BRIGHT, SLOT, LAVENDER) = range(16)

ANSWERS = (('A', 'ATLANTIC', RED), ('B', 'INDIAN', BLUE), ('C', 'PACIFIC', GREEN), ('D', 'ARCTIC', ORANGE))
CORRECT = 2
CLOCK_BLOCKS = 10
WRONG = 3  # the one question of the six answered that the household got wrong


def bulb(p, x, y):
    """The quiz's mark: a lit bulb with waves of thought either side."""
    p.disc(x, y, 18, YELLOW)
    p.rect(x - 8, y + 14, 16, 12, LAVENDER)
    p.line([(x - 8, y + 19), (x + 8, y + 19)], INK, 1)
    for radius in (26, 34):
        p.arc((x - radius * 0.7, y - radius * 0.7), (x - radius, y), (x - radius * 0.7, y + radius * 0.7), PINK)
        p.arc((x + radius * 0.7, y - radius * 0.7), (x + radius, y), (x + radius * 0.7, y + radius * 0.7), PINK)


def build():
    p = Plate(PALETTE, VIOLET)
    p.rect(0, 0, 640, 64, BAND)
    p.pel(2)
    bulb(p, 56, 30)
    p.text(108, 46, 'BRAINWAVE', 22, 32, YELLOW, prop=False)
    p.text(318, 44, 'QUIZ', 18, 26, PINK, prop=False)
    p.text(564, 44, '219', 16, 24, CYAN, prop=False)

    # Ten pips for the round's questions: right in lime, wrong crossed, this one pink, the rest to come.
    p.text(24, 96, 'ROUND 3', 13, 20, LAVENDER, prop=False)
    for question in range(10):
        x, y, r = 136 + question * 24, 89, 8
        if question < 6:
            if question == WRONG:
                p.disc(x, y, r, DIM)
                p.line([(x - 4, y - 4), (x + 4, y + 4)], INK, 2)
                p.line([(x - 4, y + 4), (x + 4, y - 4)], INK, 2)
            else:
                p.disc(x, y, r, CLOCK)
        elif question == 6:
            p.disc(x, y, r + 2, PINK)
        else:
            p.ring(x, y, r - 1, LAVENDER, 1)
    p.rect(470, 76, 150, 28, SLOT)
    p.text(482, 96, 'SCORE  50', 13, 20, WHITE, prop=False)

    # The question on a bright card.
    p.rect(24, 112, 592, 92, YELLOW)
    p.rect(24, 204, 592, 6, ORANGE)
    # The question's number on a round badge at the card's edge.
    p.disc(46, 158, 30, PINK)
    p.text(26, 170, 'Q7', 20, 30, WHITE, prop=False)
    p.text(90, 150, 'Which is the largest', 18, 28, INK)
    p.text(90, 188, 'ocean on Earth?', 18, 28, INK)
    # A small globe gives the question a picture: ocean, two continents, a shine.
    p.disc(552, 158, 38, INK)
    p.disc(552, 158, 34, CYAN)
    p.poly([(530, 132), (548, 128), (556, 140), (546, 156), (550, 172), (540, 184), (532, 166), (524, 148)], CLOCK)
    p.poly([(566, 136), (580, 144), (584, 162), (574, 176), (566, 160)], CLOCK)
    p.disc(540, 140, 5, WHITE)

    # Four answers, each in its own colour-map entry so that the reveal can dim it.
    for index, (letter, word, ink) in enumerate(ANSWERS):
        x, y = 24 + (index % 2) * 300, 226 + (index // 2) * 76
        p.rect(x + 5, y + 5, 292, 64, SLOT)
        p.rect(x, y, 292, 64, ink)
        p.disc(x + 34, y + 32, 22, WHITE)
        p.text(x + 25, y + 42, letter, 18, 26, ink, prop=False)
        p.text(x + 70, y + 44, word, 17, 26, WHITE, prop=False)
    p.wait(6, 'question')

    # The clock: a dial of ten slices, overdrawn one a second as time runs out.
    dial_x, dial_y, dial_r = 60, 404, 28
    p.disc(dial_x, dial_y, dial_r + 4, LAVENDER)
    p.disc(dial_x, dial_y, dial_r + 1, SLOT)
    for block in range(CLOCK_BLOCKS):
        p.sector(dial_x, dial_y, dial_r, -90 + block * 36, -90 + (block + 1) * 36, CLOCK)
    p.text(104, 412, 'TIME', 14, 22, LAVENDER, prop=False)
    for block in reversed(range(CLOCK_BLOCKS)):
        p.wait(6)
        p.sector(dial_x, dial_y, dial_r, -90 + block * 36, -90 + (block + 1) * 36, SLOT)
    p.ring(dial_x, dial_y, dial_r - 4, PINK, 2)
    p.text(dial_x - 8, dial_y + 11, '0', 16, 22, PINK, prop=False)
    p.wait(4, 'time up')

    # The reveal: the wrong answers fade, the right one blinks, the score is redrawn.
    for index, (_, _, ink) in enumerate(ANSWERS):
        if index != CORRECT:
            p.recolour(ink, '4a4566')
    p.blink(GREEN, PINK, on=4, off=4)
    p.rect(176, 380, 440, 46, PINK)
    p.text(192, 412, 'RIGHT ANSWER: C', 17, 26, WHITE, prop=False)
    p.rect(470, 76, 150, 28, SLOT)
    p.text(482, 96, 'SCORE  60', 13, 20, BRIGHT, prop=False)
    p.text(408, 98, '+10', 15, 22, BRIGHT, prop=False)
    # Sparks burst round the right answer.
    left, top, right, bottom = 24, 302, 316, 366
    sparks = ((left - 2, top + 6), (left + 60, top - 8), (left + 150, top - 10), (left + 240, top - 8),
              (right + 2, top + 10), (right + 4, bottom - 8), (left + 200, bottom + 6), (left + 100, bottom + 6))
    for index, (x, y) in enumerate(sparks):
        size = 9 if index % 2 else 12
        p.poly([(x, y - size), (x + 3, y - 3), (x + size, y), (x + 3, y + 3), (x, y + size), (x - 3, y + 3),
                (x - size, y), (x - 3, y - 3)], (YELLOW, CYAN, WHITE)[index % 3])

    p.rect(0, 436, 640, 44, BAND)
    p.text(24, 466, '1,204 HOMES PLAYING   # NEXT', 14, 22, WHITE, prop=False)
    return p


if __name__ == '__main__':
    save(__file__, build)
