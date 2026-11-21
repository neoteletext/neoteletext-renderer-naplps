from _kit import *

META = dict(title='Going Once, Going Twice',
            purpose='A live electronic auction counts a rising bid on seven-segment digits while the lot, an antique clock, waits.',
            style='Burgundy salesroom, brass clock in arcs, amber seven-segment bid counter',
            techniques=['colour-map digits', 'native circles', 'native arcs', 'filled polygons', 'DRCS', 'hatch fill', 'WAIT', 'BLINK', 'proportional text'],
            animated=True)

BG, WHITE, BRASS, BRONZE, DKBRASS, WOOD, INK, DIM, LIVE = range(9)
FACE = WHITE
SIGNATURE_ENTRIES = [9, 10, 11, 12, 13, 14, 15]
LED_ON = 'ffb020'
LED_OFF = '4a1a1a'

SEGMENTS = {0: 'abcdef', 1: 'bc', 2: 'abdeg', 3: 'abcdg', 4: 'bcfg', 5: 'acdfg', 6: 'acdefg',
            7: 'abc', 8: 'abcdefg', 9: 'abcdfg'}
BIDS = [98, 105, 112]


def segment_polygon(name, x, y, w, h, t):
    mid = y + h / 2
    cx = x + w / 2
    horizontal = {'a': y + t / 2, 'g': mid, 'd': y + h - t / 2}
    vertical = {'f': (x + t / 2, y + h / 4), 'b': (x + w - t / 2, y + h / 4),
                'e': (x + t / 2, y + 3 * h / 4), 'c': (x + w - t / 2, y + 3 * h / 4)}
    if name in horizontal:
        cy, half = horizontal[name], (w - t) / 2 - 1
        return [(cx - half, cy), (cx - half + t / 2, cy - t / 2), (cx + half - t / 2, cy - t / 2),
                (cx + half, cy), (cx + half - t / 2, cy + t / 2), (cx - half + t / 2, cy + t / 2)]
    sx, cy = vertical[name]
    half = (h - t) / 4 - 1
    return [(sx, cy - half), (sx + t / 2, cy - half + t / 2), (sx + t / 2, cy + half - t / 2),
            (sx, cy + half), (sx - t / 2, cy + half - t / 2), (sx - t / 2, cy - half + t / 2)]


def digit_state(position, state):
    text = f'{BIDS[state]:3d}'
    char = text[position]
    return set() if char == ' ' else set(SEGMENTS[int(char)])


def led_counter(p, x, y):
    """All three bid states share one set of segments; each segment's palette
    entry is lit exactly in the states in which its digit shows it."""
    signatures = {}
    plan = []
    for position in range(3):
        for name in 'abcdefg':
            sig = tuple(name in digit_state(position, s) for s in range(len(BIDS)))
            plan.append((position, name, sig))
            if any(sig):
                signatures.setdefault(sig, None)
    for sig in (tuple(s == k for s in range(3)) for k in range(3)):
        signatures.setdefault(sig, None)
    if len(signatures) > len(SIGNATURE_ENTRIES):
        raise ValueError(f'{len(signatures)} signatures')
    entries = dict(zip(signatures, SIGNATURE_ENTRIES))
    p.rect(x - 14, y - 12, 3 * 62 + 94, 118, INK)
    p.frame(x - 14, y - 12, 3 * 62 + 94, 118, DKBRASS, 4)
    p.say(x + 6, y + 80, '$', HEAD, BRASS)
    for position, name, sig in plan:
        p.poly(segment_polygon(name, x + 48 + position * 62, y, 46, 94, 11), DIM)
    for position, name, sig in plan:
        if any(sig):
            p.poly(segment_polygon(name, x + 48 + position * 62, y, 46, 94, 11), entries[sig])
    return entries


def lamp(p, x, y, label, entry):
    p.disc(x, y, 17, INK)
    p.disc(x, y, 13, entry)
    p.say(x, y + 35, label, SMALL, WHITE, 'c')


HANDS = [(-92, -60), (16, -54), (128, -48)]   # minute and hour hand angles, degrees, one pair per bid
SWING = [12, -12, 12]


def face(p, cx, top, minute, hour):
    cy = top + 130
    p.disc(cx, cy, 68, FACE)
    for i in range(12):
        a = i * math.pi / 6
        inner = 52 if i % 3 else 46
        p.line([(cx + inner * math.cos(a), cy + inner * math.sin(a)),
                (cx + 62 * math.cos(a), cy + 62 * math.sin(a))], INK, 4 if i % 3 == 0 else 2)
    p.arc((cx - 52, top + 106), (cx - 30, top + 84), (cx - 6, top + 76), WHITE)
    for angle, length, width in ((minute, 52, 4), (hour, 34, 6)):
        a = math.radians(angle)
        p.line([(cx, cy), (cx + length * math.cos(a), cy + length * math.sin(a))], INK, width)
    p.disc(cx, cy, 6, BRONZE)


def pendulum(p, cx, top, dx):
    p.rect(cx - 62, top + 226, 124, 74, INK)
    p.frame(cx - 62, top + 226, 124, 74, BRASS, 3)
    p.line([(cx, top + 226), (cx + dx, top + 280)], BRASS, 3)
    p.disc(cx + dx + 1, top + 284, 14, BRASS)
    p.disc(cx + dx + 1, top + 284, 8, BRASS)
    p.disc(cx + dx - 2, top + 280, 4, FACE)


def clock(p, cx, top):
    # case, arch and plinth
    p.rect(cx - 112, top + 128, 224, 192, WOOD)
    p.rect(cx - 112, top + 300, 224, 38, DKBRASS)
    p.rect(cx - 124, top + 330, 248, 20, WOOD)
    p.poly([(cx - 130, top + 350), (cx + 130, top + 350), (cx + 118, top + 368), (cx - 118, top + 368)], BRONZE)
    p.rect(cx - 112, top + 128, 224, 8, BRASS)
    p.disc(cx, top + 128, 112, WOOD)
    p.arc((cx - 112, top + 128), (cx, top + 16), (cx + 112, top + 128), BRASS)
    p.ring(cx, top + 128, 112, BRASS, 4)
    p.rect(cx - 96, top + 128, 8, 160, BRONZE)
    p.rect(cx + 88, top + 128, 8, 160, BRONZE)
    p.rect(cx - 94, top + 128, 2, 160, BRASS)
    p.rect(cx + 90, top + 128, 2, 160, BRASS)
    for k in range(5):
        p.line([(cx - 100 + k * 50, top + 316), (cx - 84 + k * 50, top + 322), (cx - 68 + k * 50, top + 316)], BRASS, 2)
    p.disc(cx - 92, top + 296, 12, BRASS)
    p.disc(cx + 92, top + 296, 12, BRASS)
    # dial
    p.disc(cx, top + 130, 82, DKBRASS)
    p.disc(cx, top + 130, 76, BRASS)
    face(p, cx, top, *HANDS[0])
    pendulum(p, cx, top, SWING[0])
    # finial
    p.disc(cx, top + 10, 8, BRASS)
    p.rect(cx - 3, top + 14, 6, 14, BRASS)


def gavel(p, x, y):
    q = Scaled(p, x, y, 1.1)
    q.rect(x - 32, y + 46, 84, 12, BRONZE)
    q.rect(x - 28, y + 40, 76, 8, BRASS)
    q.poly([(x - 8, y + 42), (x + 4, y + 38), (x + 50, y + 4), (x + 38, y - 8)], WOOD)
    q.poly([(x + 18, y - 16), (x + 50, y - 40), (x + 66, y - 22), (x + 34, y + 2)], BRASS)
    q.poly([(x + 28, y - 14), (x + 50, y - 34), (x + 58, y - 26), (x + 36, y - 6)], FACE)
    q.poly([(x + 18, y - 16), (x + 22, y - 12), (x + 38, y + 2), (x + 34, y + 2)], BRONZE)
    for dx, dy in ((-18, 30), (-26, 18), (-12, 38)):
        q.line([(x + dx, y + dy), (x + dx - 8, y + dy - 4)], BRASS, 2)


def build():
    p = Screen('2a0f1c fff6dc f3c969 c18a2c 7a4f12 6b3a22 1a1210 4a1a1a ff3a2a 4a1a1a 4a1a1a 4a1a1a 4a1a1a 4a1a1a 4a1a1a 4a1a1a')
    p.rect(0, 0, 640, 480, BG)
    p.rect(0, 0, 640, 44, WOOD)
    p.rect(0, 44, 640, 6, BRASS)
    p.say(14, 32, 'TELEAUCTION', LARGE, BRASS)
    p.say(626, 32, '192', LARGE, BRASS, 'r')
    define_character(p, 0x21, 30, 20, [('poly', [(0, 10), (8, 3), (15, 1), (22, 3), (29, 10), (22, 17), (15, 19), (8, 17)]), ('hole', 15, 10, 6.5), ('disc', 15, 10, 3.5)])
    p.disc(250, 22, 9, LIVE)
    p.say(268, 30, 'LIVE', BODY, WHITE)
    character(p, 0x21, 356, 34, 30, 20, BRASS)
    p.say(394, 30, '212 WATCHING', BODY, WHITE)
    p.rect(0, 446, 640, 34, WOOD)
    p.say(14, 470, '1 BID +$5   2 BID +$10   3 PROXY BID', BODY, BRASS)
    p.fillpoly([(142, 52), (6, 442), (278, 442)], DKBRASS, 2, 5)
    clock(p, 142, 70)
    p.say(142, 456 - 8, '', SMALL, WHITE)
    p.wait(6)
    p.say(296, 96, 'LOT 27', HEAD, WHITE)
    p.say(296, 128, 'WALNUT MANTEL CLOCK', BODY, BRASS)
    p.say(296, 152, 'EIGHT DAY MOVEMENT, MADE 1894', SMALL, FACE)
    p.wait(8)
    entries = led_counter(p, 322, 192)
    p.say(296, 188, 'HIGH BID', BODY, BRASS)
    for i, (bidder, amount) in enumerate([('0212', '$98'), ('0388', '$105'), ('0417', '$112')]):
        ink = WHITE if i == 0 else entries[tuple(k >= i for k in range(3))]
        p.say(296, 336 + i * 25, f'BIDDER {bidder}', BODY, ink)
        p.say(520, 336 + i * 25, amount, BODY, ink, 'r')
    lamp_entries = [entries[(False, True, True)], entries[(False, False, True)], None]
    for i, (label, entry) in enumerate([('ONCE', lamp_entries[0]), ('TWICE', lamp_entries[1]), ('SOLD', DIM)]):
        lamp(p, 322 + i * 84, 408, label, entry)
    gavel(p, 548, 374)
    # State 0 lights its pattern; the colour map then walks through the bids.
    states = []
    for s in range(3):
        states.append({e: (LED_ON if sig[s] else LED_OFF) for sig, e in entries.items()})
    for e, colour in states[0].items():
        p.set_palette(e, colour)
    p.wait(14)
    for s in (1, 2):
        for e, colour in states[s].items():
            p.set_palette(e, colour)
        face(p, 142, 70, *HANDS[s])
        pendulum(p, 142, 70, SWING[s])
        p.wait(14)
    p.blink(LIVE, WHITE, 5, 5)
    return p


if __name__ == '__main__':
    save(__file__, build)
