from math import cos, pi, sin
from random import Random
from _canvas import Canvas, write_page

META = dict(title='Kiln Opening', purpose='The first glimpse of newly fired clay vessels',
            style='Brick-red tessellation around a molten orange chamber',
            techniques=['native filled arches', 'profile-following glaze arcs', 'WAIT and palette reveal'],
            animated=True)


def build():
    p = Canvas('211c25 392632 542e3b 73363c 9b4944 532d37 4c2a35'
               ' 412832 4a2934 3a2935 392932 ffc3a0 392932 452931 34252c 2f2228')
    rng = Random(151)
    for row in range(10):
        for column in range(9):
            x = 76 * column - 38 * (row % 2)
            left, right = max(0, x + 2), min(639.6, x + 74)
            if right > left:
                top = 46*row+3
                ink = 1+(column*11+row*7+column*row)%3
                p.poly([(left, top+2), (left+(right-left)*.42, top),
                        (right, top+2), (right, top+39),
                        (left+(right-left)*.61, top+41), (left, top+39)], ink)
                if right-left > 20:
                    p.line([(left+4, top+6), (right-4, top+5)], max(1, ink-1), 2)
                    for _ in range(5):
                        x0 = rng.uniform(left+3, right-9)
                        y0 = rng.uniform(top+9, top+36)
                        p.line([(x0, y0), (x0+rng.uniform(2, 7), y0-1)], 2, 1)
    p.rect(104, 215, 432, 200, 4)
    p.arc((104, 216), (320, 31), (536, 216), 4, True)
    for spoke in range(1, 12):
        angle = spoke*pi/12
        p.line([(320+210*cos(angle), 216-181*sin(angle)),
                (320+184*cos(angle), 216-148*sin(angle))], 2, 3)
    for y in (254, 293, 332, 371):
        p.line([(104, y), (136, y)], 2, 3)
        p.line([(504, y), (536, y)], 2, 3)
    p.rect(135, 215, 370, 182, 5)
    p.arc((135, 216), (320, 67), (505, 216), 5, True)
    p.rect(164, 216, 312, 165, 6)
    p.arc((164, 217), (320, 101), (476, 217), 6, True)
    # Receding bands of refractory brick pick up heat near the floor.
    courses = [(175, 465, 122, 350, 7),
                                           (193, 451, 143, 346, 13),
                                           (206, 438, 164, 343, 14),
                                           (225, 422, 187, 342, 13)]
    for left, right, crown, bottom, ink in courses:
        p.arc((left, 236), (320, crown), (right, 236), ink, True)
        p.rect(left, 235, right-left, bottom-235, ink)
    rims = [(164, 476, 101), *((l, r, c) for l, r, c, _, _ in courses)]
    for layer, (outer, inner) in enumerate(zip(rims, rims[1:])):
        for spoke in range(1, 10):
            angle = (spoke + (layer%2)*.42)*pi/10
            normal = cos(angle)
            points = [((left+right)/2 + (right-left)/2*normal,
                       236-(236-crown)*sin(angle))
                      for left, right, crown in (outer, inner)]
            p.line(points, 5 if layer < 2 else 7, 2)
    for y, left, right in [(241, 207, 437), (270, 197, 446), (299, 186, 456)]:
        p.line([(left, y-4), (320, y), (right, y-4)], 7, 2)
        for x in range(226 + y%2*33, 437, 52):
            p.line([(x, y), (x-2, y+22)], 7, 2)
    for _ in range(83):
        x, y = rng.uniform(184, 454), rng.uniform(183, 324)
        if ((x-320)/135)**2 + ((y-252)/97)**2 < .92:
            p.line([(x, y), (x+rng.uniform(1, 5), y)], rng.choice((13, 14, 15)), 1)
    p.pel(4).arc((141, 222), (320, 76), (499, 222), 7)
    p.line([(142, 225), (142, 386), (496, 386)], 7, 3)
    p.poly([(180, 326), (452, 326), (479, 371), (162, 371)], 8)
    p.line([(163, 371), (477, 371)], 5, 4)
    p.line([(166, 365), (474, 365)], 13, 2)
    for x in range(186, 469, 34):
        p.line([(320+(x-320)*.64, 329), (x, 365)], 5, 2)
    # The left jamb catches the hearth light while the right falls into shade.
    p.poly([(165, 239), (184, 238), (201, 326), (166, 362)], 13)
    p.poly([(454, 226), (475, 217), (476, 360), (450, 329)], 7)
    for y in (257, 282, 307, 333):
        p.line([(167, y+5), (186+(y-257)*.24, y)], 7, 2)
        p.line([(458, y-5), (475, y+1)], 5, 2)
    for x, y, w in [(223, 352, 45), (405, 343, 58), (320, 364, 55)]:
        p.ellipse(x, y, w, 8, 9, n=16)

    def vessel(x, y, w, h, ink, profile, glaze, marks, finish):
        left = [(x-w*r, y+h*t) for r, t in profile]
        right = [(x+w*r, y+h*t) for r, t in profile]
        p.poly(left + right[::-1], ink)
        p.poly(left + [(x+w*r*(.17-.68*t), y+h*t) for r, t in profile[::-1]], 8)
        p.poly([(x-w*r*(.94-.18*t), y+h*t) for r, t in profile]
               + [(x-w*r*(.74-.12*t), y+h*t) for r, t in profile[::-1]], 10)
        for t in marks:
            for (a, v), (b, z) in zip(profile, profile[1:]):
                if v <= t < z:
                    radius = w*(a+(b-a)*(t-v)/(z-v))
                    yy = y+h*t
                    p.pel(2).arc((x-radius+3, yy), (x, yy+4), (x+radius-3, yy), glaze)
                    break
        if finish == 'speckled':
            for _ in range(68):
                t = rng.uniform(.29, .94)
                for (a, v), (b, z) in zip(profile, profile[1:]):
                    if v <= t < z:
                        r = w*(a+(b-a)*(t-v)/(z-v))
                        xx = x+r*rng.uniform(-.86, .86)
                        p.circle(xx, y+h*t, rng.uniform(.6, 1.5), glaze)
                        break
        elif finish == 'dripped':
            for u, length in [(-.67, .27), (-.39, .46), (-.05, .37), (.40, .22), (.64, .31)]:
                p.line([(x+w*u, y+6), (x+w*(u-.025), y+h*length*.72),
                        (x+w*u*.82, y+h*length)], 15, 2)
                p.circle(x+w*u*.82, y+h*length, 1.55, 15)
        elif finish == 'burnished':
            sheen = [(x-w*r*(.78-.10*t), y+h*t) for r, t in profile[2:]]
            sheen += [(x-w*r*(.50+.44*t), y+h*t) for r, t in profile[:1:-1]]
            p.poly(sheen, 10)
            p.line([(x-8, y+8), (x-9, y+h*.24), (x-15, y+h*.43),
                    (x-31, y+h*.56), (x-32, y+h*.68)], 15, 2)
            p.pel(3).arc((x-22, y+h*.49), (x-29, y+h*.60), (x-30, y+h*.73), 13)
            p.pel(2).arc((x-31, y+h*.78), (x-28, y+h*.90), (x-23, y+h*.96), 10)
        rim = w*profile[0][0]
        p.ellipse(x, y+1, rim, 4, 5, n=16)
        p.ellipse(x, y, rim*.78, 2.5, 9, n=24)
        p.pel(2).arc((x-rim, y+1), (x, y+5), (x+rim, y+1), 15)

    vessel(219, 252, 37, 96, 10,
           [(.66, 0), (.58, .13), (.82, .35), (1, .61), (.81, .86), (.56, 1)], 13, (.21, .84), "speckled")
    vessel(405, 280, 52, 61, 12,
           [(1, 0), (.98, .21), (.81, .52), (.57, .81), (.49, 1)], 15, (.18, .22, .68, .79), "dripped")
    vessel(319, 171, 45, 189, 9,
           [(.36, 0), (.30, .20), (.38, .35), (.81, .48), (1, .61),
            (.97, .80), (.73, .96), (.50, 1)], 12, (.23, .72, .84), "burnished")

    p.rect(0, 409, 639.7, 71, 0)
    p.text(37, 460, 'KILN OPENING', 36, 45, 11)
    p.wait(11)
    for i, colour in [(5, 'bb5634'), (6, 'ffac47'), (7, 'd46445'),
                      (8, '9b4439'), (9, '54303e'), (10, 'd86a49'), (12, 'b54d46'),
                      (13, 'ef874c'), (14, 'ca613c'), (15, 'ffb46c')]:
        p.set_palette(i, colour)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
