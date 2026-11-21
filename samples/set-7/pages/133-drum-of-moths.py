"""Timing screen where percussion cues arrive as mosaic wings."""
import _local
from encoder.screen import Screen, save

META = dict(title='Drum of Moths', purpose='Rhythm playfield with a five-lane percussion pattern',
            style='Charcoal stage, hot coloured beat lanes and chunky teletext wing glyphs',
            techniques=['native six-cell mosaics', 'palette BLINK', 'segmented strike pads'],
            animated=True)

# Left and right mosaic glyphs for level and raised wings.
WINGS = ([0x6d, 0x3e], [0x65, 0x3a])


def build():
    p = Screen('211529 fff3d4 31243d 493050 e16ba5 f89368 f4cf6a'
               ' 96d592 73d0d1 765876 ffffff')
    p.text(24, 48, 'DRUM OF MOTHS', 39, 47, 1)
    lanes = [28 + index*119 for index in range(5)]
    for index, x in enumerate(lanes):
        p.rect(x, 74, 108, 302, 2)
        p.rect(x, 74, 108, 5, 4+index)
        for y in (114, 179, 244, 309):
            p.rect(x, y, 108, 2, 3)
    p.text(472, 44, 'COMBO 12', 24, 32, 6)
    # One timing gate spans all five lanes.
    p.line([(16, 310), (623, 310)], 9, 6)
    p.line([(16, 310), (623, 310)], 1, 2)
    for x in lanes:
        p.poly([(x+48, 305), (x+60, 305), (x+54, 314)], 1)
    for index, x in enumerate(lanes):
        p.rect(x, 319, 108, 55, 6 if index == 2 else 9)
        p.rect(x+3, 322, 102, 49, 3)
        # Sidewall and lugs give the drum a body beneath its head.
        p.poly([(x+10, 345), (x+98, 345), (x+90, 368),
                (x+73, 377), (x+35, 377), (x+18, 368)], 9)
        for dx in (23, 38, 70, 85):
            p.line([(x+dx, 350), (x+dx, 368)], 4+index, 3)
        p.ellipse(x+54, 346, 44, 17, 4+index)
        p.ellipse(x+54, 345, 38, 12, 0 if index == 2 else 2)
        p.line([(x+5, 344), (x+15, 344)], 4+index, 2)
        p.line([(x+93, 344), (x+103, 344)], 4+index, 2)
        if index == 2:
            for dx in (8, 96):
                p.line([(x+dx, 329), (x+dx+4, 324)], 6, 2)
                p.line([(x+dx, 363), (x+dx+4, 368)], 6, 2)
    for index, rows in enumerate([(120, 238), (153, 267), (94, 200, 284),
                                 (151, 233), (112, 266)]):
        x = lanes[index]
        for beat, y in enumerate(rows):
            ink = 10 if y == 284 else 4+index
            raised = (index + beat) % 2
            p.mosaic(x+18, y+33, WINGS[raised], 36, 30, ink)
            if raised:
                for side in (-1, 1):
                    p.poly([(x+54, y+26), (x+54+side*18, y+12),
                            (x+54+side*36, y+2), (x+54+side*29, y+20)], ink)
            p.poly([(x+46, y+22), (x+54, y+9), (x+62, y+22),
                    (x+54, y+39)], ink)
            for side in (-1, 1):
                p.line([(x+54, y+16), (x+54+side*8, y+6),
                        (x+54+side*13, y+3)], ink, 2)
                p.disk(x+54+side*24, y+(15 if raised else 19), 4, 0)
        if index == 2:
            p.ellipse(x+54, 345, 28, 9, 10, False, n=24)
            p.ellipse(x+54, 345, 13, 4, 10, False, n=16)
            for dx in (5, 103):
                direction = -1 if dx == 5 else 1
                for y, dy in [(333, -5), (342, 0), (351, 5)]:
                    p.line([(x+dx, y), (x+dx+direction*7, y+dy)], 10, 2)
        p.rect(x+14, 394, 80, 49, 4+index)
        p.text(x+45, 432, 'ASDFG'[index], 27, 38, 0, False)
    p.blink(10, 5, 2, 3)
    return p


if __name__ == '__main__':
    save(__file__, build())
