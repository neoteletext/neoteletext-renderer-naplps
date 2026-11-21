from _page import Plate, save, arc_points

META = dict(title='Market Close',
            purpose='A stockbroker\'s quotation page at the close: the day\'s index climbing hour by hour, '
                    'then ten invented shares with their moves.',
            style='Green-screen trading terminal: amber headings, phosphor-green chart over a dark grid',
            techniques=['WAIT reveal of the index hour by hour', 'headline figure repainted at each hour', 'DRCS up and down arrows',
                        'native vertical hatching under the line', 'BLINK closing marker and ringing bell', 'BLINK pulsing the most active row',
                        'fixed-pitch figures', 'hatching over a solid fill for two-tone shading', 'dotted reference line'],
            animated=True)

PALETTE = ('000000 ffffff ffb000 3cff6a ff4a4a 0e3a1c 1d7a3a 9aa4a0 '
           '102030 58d8ff 0a1410 7a5400 1a2a24 b8ffc8 ff8a1a 1a2a24').split()
BLACK, WHITE, AMBER, GREEN, RED, GRID, FILL, GREY, BAND, CYAN, STRIPE, DIM, DEEP, PALE, ORANGE, PANEL = range(16)
UP, DOWN = 0x21, 0x22
ARROW = 20

# Index by half hour from 10:00 to 4:00, invented.
INDEX = [1236.3, 1234.9, 1238.6, 1237.2, 1240.8, 1243.5, 1241.1, 1239.9, 1242.7, 1245.0, 1244.1, 1246.9, 1248.37]
STOCKS = [('Orrin Mills', '24.75', '+0.50'), ('Bay Tel', '41.25', '+1.13'),
          ('Tasker Steel', '18.38', '-0.25'), ('Kestrel Air', '9.63', '+0.38'),
          ('Ninefield Oil', '33.50', '+2.25'), ('Harrow Foods', '15.13', '-0.63'),
          ('Sedge Paper', '12.88', '+0.13'), ('Calder Hydro', '56.00', '+0.75'),
          ('Pellham Mines', '7.25', '-0.38'), ('Lark Freight', '21.63', '+0.88')]


PREVIOUS_CLOSE = 1236.31


def index_value(p, value):
    """Paint over the index figure and write the new one: the headline ticks as the chart draws."""
    change = value - PREVIOUS_CLOSE
    colour = GREEN if change >= 0 else RED
    p.rect(250, 48, 390, 44, BLACK)
    p.text(262, 82, f'{value:,.2f}', 20, 32, colour, prop=False)
    p.chars(446, 78, [UP if change >= 0 else DOWN], 26, 26 * 0.96, colour)
    p.text(476, 82, f'{abs(change):.2f}', 20, 32, colour, prop=False)


def build():
    p = Plate('200', PALETTE)
    p.define_drcs(UP, ARROW, ARROW * 0.96, [[(0.10, 0.12), (0.50, 0.86), (0.90, 0.12)]])
    p.define_drcs(DOWN, ARROW, ARROW * 0.96, [[(0.10, 0.86), (0.90, 0.86), (0.50, 0.12)]])
    p.rect(0, 0, 640, 40, BAND)
    # The broker's device: a Q drawn as a ring with a tail.
    p.disc(30, 20, 15, AMBER)
    p.disc(30, 20, 10, BAND)
    p.line([(34, 25), (46, 36)], AMBER, 4)
    p.text(56, 31, 'QUILLON & MARSH QUOTES', 17, 26, AMBER)
    p.rtext(624, 30, 'p 400', 14, 22, GREY, prop=False)
    # The closing bell; its sound lines are in the entry that blinks with the closing marker, so it rings.
    bx = 486
    p.poly(arc_points(bx, 16, 10, 9, 0, 180, 10) + [(bx + 12, 30), (bx - 12, 30)], AMBER)
    p.disc(bx, 33, 3, AMBER)
    for side in (-1, 1):
        p.line([(bx + side * 16, 12), (bx + side * 22, 8)], PALE, 2)
        p.line([(bx + side * 17, 20), (bx + side * 25, 20)], PALE, 2)
        p.line([(bx + side * 16, 28), (bx + side * 22, 32)], PALE, 2)
    p.text(16, 82, 'CALDER 300', 20, 32, WHITE, prop=False)
    index_value(p, INDEX[0])

    left, right, top, bottom = 72, 620, 100, 250
    low, high = 1230, 1252
    p.rect(left, top, right - left, bottom - top, STRIPE)
    for v in range(1230, 1253, 5):
        y = bottom - (v - low) / (high - low) * (bottom - top)
        p.line([(left, y), (right, y)], GRID, 1)
        if v % 10 == 0:
            p.rtext(left - 6, y + 8, str(v), 13, 20, CYAN, prop=False)
    hours = ['10', '11', '12', '1', '2', '3', '4']
    step = (right - left) / 12
    for i, h in enumerate(hours):
        x = left + 2 * i * step
        p.line([(x, top), (x, bottom)], GRID, 1)
        p.ctext(x, bottom + 22, h, 13, 20, GREY, prop=False)
    pts = [(left + i * step, bottom - (v - low) / (high - low) * (bottom - top)) for i, v in enumerate(INDEX)]
    for i in range(12):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if i and i % 2 == 0:
            index_value(p, INDEX[i])
            p.wait(4)
        p.poly([(x0, bottom), (x0, y0), (x1, y1), (x1, bottom)], GRID)
        p.hatch(1)
        p.poly([(x0, bottom), (x0, y0), (x1, y1), (x1, bottom)], FILL)
        p.solid()
        p.line([(x0, y0), (x1, y1)], GREEN, 3)
    index_value(p, INDEX[-1])
    # Yesterday's close as a dotted reference across the chart.
    prev_y = bottom - (PREVIOUS_CLOSE - low) / (high - low) * (bottom - top)
    p.pel(2).cmd(0x23, b'\x41')
    p.line([(left, prev_y), (right, prev_y)], CYAN, 2)
    p.cmd(0x23, b'\x40')
    p.rect(right - 66, prev_y + 4, 62, 24, BLACK)
    p.text(right - 60, prev_y + 23, 'PREV', 12, 19, CYAN, prop=False)
    cx, cy = pts[-1]
    p.disc(cx, cy, 6, PALE)
    # The day's low and high, flagged on the line.
    lx, ly = pts[1]
    p.line([(lx, ly - 4), (lx, ly - 40)], ORANGE, 2)
    p.rect(lx - 4, ly - 64, 132, 26, ORANGE)
    p.text(lx + 3, ly - 44, 'LOW 1234.9', 12, 19, BLACK, prop=False)
    p.line([(cx - 4, cy + 4), (cx - 30, cy + 40)], GREEN, 2)
    p.rect(cx - 150, cy + 36, 132, 26, GREEN)
    p.text(cx - 143, cy + 56, 'HIGH CLOSE', 12, 19, BLACK, prop=False)
    p.wait(6)

    for i, (name, price, change) in enumerate(STOCKS):
        col, row = i % 2, i // 2
        x, y = 16 + col * 312, 300 + row * 34
        if name == 'Ninefield Oil':
            # The most active share: its row's panel has an entry of its own that pulses amber.
            p.rect(x - 6, y - 26, 302, 32, DEEP)
        elif row % 2 == 0:
            p.rect(x - 6, y - 26, 302, 32, PANEL)
        p.text(x, y, name, 13, 21, WHITE)
        p.rtext(x + 196, y, price, 12, 20, AMBER, prop=False)
        up = change.startswith('+')
        p.chars(x + 204, y - 2, [UP if up else DOWN], ARROW, ARROW * 0.96, GREEN if up else RED)
        p.rtext(x + 292, y, change[1:], 12, 20, GREEN if up else RED, prop=False)
    p.rect(0, 446, 640, 34, BAND)
    p.text(16, 472, 'Vol 14.2M   7 up  3 down', 14, 22, CYAN)
    p.rtext(624, 472, 'NEXT  p 401', 14, 22, AMBER, prop=False)
    p.blink(PALE, BLACK, 5, 5)
    p.blink(DEEP, DIM, 7, 7)
    return p


if __name__ == '__main__':
    save(__file__, build)
