"""A finish-board for timed sail-sled runs across a salt pan."""
import _local
from encoder.screen import Screen, save

META = dict(title='Brine Dash', purpose='Race results showing four sail-sled times',
            style='Cobalt and persimmon sports graphics on chalk white',
            techniques=['slanted polygon lanes', 'diagonal pel strokes', 'fixed-pitch race times'],
            animated=False)


def build():
    p = Screen('f5edda 183761 2047a3 ff784d ffd078 e0d2b2 fff8e9 6a654e')
    p.poly([(0, 0), (639, 0), (639, 123), (0, 99)], 2)
    for row in range(3):
        for col in range(6):
            if (row+col)%2 == 0:
                x, y = 518 + col*16 - row*4, 23 + row*17
                p.poly([(x, y), (x+15, y), (x+11, y+16), (x-4, y+16)], 4)
    p.text(25, 81, 'BRINE DASH', 61, 77, 6)
    p.text(25, 146, 'SALT FLAT FINAL', 28, 35, 1)
    # Shallow evaporating pans and salt ridges mark the course.
    for x, y, span in [(416, 128, 84), (480, 138, 112), (427, 147, 57)]:
        p.poly([(x, y+4), (x+span*.30, y), (x+span, y+2),
                (x+span*.67, y+7)], 5)
    p.line([(471, 149), (498, 145), (531, 151), (585, 146), (608, 149)], 7, 2)
    for row, name, time, gap in [(0, 'PELL', '0:41.8', 0), (1, 'VOSK', '0:42.2', 4),
                                 (2, 'EMRU', '0:43.6', 18), (3, 'NALV', '0:45.1', 33)]:
        y = 162 + row*69
        p.poly([(22, y), (606, y), (619, y+59), (35, y+59)], 3 if row == 0 else 5)
        p.poly([(22, y), (101, y), (117, y+59), (35, y+59)], 1)
        p.text(48, y+49, str(row+1), 34, 45, 6)
        p.text(130, y+49, name, 32, 42, 1)
        p.text(407, y+49, time, 29, 42, 1, False)
        if gap:
            p.text(237, y+42, f'+{gap/10:.1f}', 20, 29, 1, False)
        else:
            p.line([(248, y+31), (281, y+31)], 1, 3)
        p.poly([(322, y+40), (377, y+40), (367, y+45), (326, y+45)], 1)
        for x in (333, 361):
            p.line([(x, y+44), (x-3, y+51)], 1, 3)
        p.line([(319, y+51), (369, y+51), (378, y+47)], 1, 2)
        p.line([(349, y+43), (339, y+9)], 1, 2)
        rigs = (
            [(339, 9), (369, 17), (381, 36), (350, 39)],
            [(339, 9), (370, 35), (350, 39)],
            [(337, 9), (347, 38), (319, 33)],
            [(339, 10), (362, 13), (369, 33), (349, 37)],
        )
        p.poly([(x, y+dy) for x, dy in rigs[row]], 6)
        accents = [((345, 17), (370, 34)), ((345, 20), (356, 34)),
                   ((330, 23), (342, 29)), ((344, 22), (364, 22))]
        p.line([(x, y+dy) for x, dy in accents[row]], 3 if row == 0 else 2, 3)
        if row == 0:
            p.poly([(338, y+9), (321, y+32), (344, y+37)], 4)
    p.poly([(22, 439), (275, 439), (284, 473), (30, 473)], 2)
    for x, y in [(237, 446), (251, 453), (233, 460)]:
        p.poly([(x, y), (x+10, y), (x+8, y+7), (x-2, y+7)], 4)
    p.text(39, 469, 'NEW RECORD', 24, 29, 6)
    p.text(312, 469, 'GAPS IN SECONDS', 24, 31, 1)
    return p


if __name__ == '__main__':
    save(__file__, build())
