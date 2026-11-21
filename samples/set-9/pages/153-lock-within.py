from math import cos, pi, sin
from _canvas import Canvas, write_page

META = dict(title='Lock Within', purpose='An exploded view of an imagined four-pin lock',
            style='Cadmium-orange cutaway with charcoal and ivory hardware',
            techniques=['layered cutaway', 'elliptical spring coils', 'dotted assembly axes'],
            animated=False)


def build():
    p = Canvas('ed713a c64f32 fa9c58 3d3437 251e2a 68535a bdaa90 ffecc4'
               ' da6d5f a34848 9a8679 19151e d6c19f 784d44 c75a41')
    p.rect(0, 0, 638.9, 100, 4)
    p.text(38, 73, 'LOCK WITHIN', 40, 56, 7)

    columns = (190, 278, 366, 454)
    p.poly([(105, 333), (520, 333), (568, 305), (153, 305)], 6)
    p.poly([(520, 333), (568, 305), (568, 363), (520, 393)], 5)
    p.rect(105, 333, 415, 60, 3)
    p.rect(156, 337, 351, 50, 11)
    p.poly([(156, 337), (507, 337), (494, 346), (163, 346)], 5)
    p.poly([(156, 337), (163, 346), (163, 379), (156, 387)], 6)
    p.ellipse(485, 365, 20, 18, 10, n=48)
    p.rect(164, 347, 321, 36, 10)
    p.rect(164, 350, 321, 9, 6)
    p.rect(164, 372, 321, 11, 5)
    p.pel(3).arc((489, 350), (503, 365), (489, 380), 6)
    p.line([(164, 355), (490, 355)], 2, 2)
    p.line([(164, 370), (490, 370)], 3, 2)
    p.line([(163, 382), (488, 382)], 12, 1)
    p.ellipse(130, 358, 19, 19, 10, n=40)
    p.ellipse(130, 358, 15, 15, 6, n=36)

    def cylinder(x, y, height, front, shade, top):
        p.rect(x-15, y, 30, height, front)
        p.ellipse(x, y+height, 15, 6, front, n=16)
        p.rect(x+6, y, 9, height, shade)
        p.line([(x-8, y+4), (x-8, y+height-2)], top, 2)
        p.ellipse(x, y, 15, 6, top, n=32)
        p.pel(2).arc((x-13, y+height-3), (x, y+height+2), (x+13, y+height-3), shade)

    for i, x in enumerate(columns):
        p.ellipse(x, 320, 21, 8, 4, n=18)
        p.rect(x-12, 334, 24, 20, 5)
        p.rect(x-9, 337, 18, 16, 11)
        p.rect(x-8, 344, 16, 9, 6)
        p.rect(x-8, 356, 16, 12, 8)
        p.ellipse(x, 368, 8, 3, 9, n=24)
        p.line([(x-5, 345), (x-5, 351)], 7, 2)
        p.line([(x-5, 357), (x-5, 366)], 2, 2)
        p.line([(x-12, 354), (x+12, 354)], 7, 2)
        p.line([(x-19, 395), (x+20, 395)], 13, 2)
        p.texture(line=1)
        p.line([(x, 311), (x, 122)], 3, 2)
        p.texture()
        helix = [(x+14*cos(j*pi/20), 134+10*j/40+4.2*sin(j*pi/20))
                 for j in range(241)]
        p.line(helix, 4, 4)
        for turn in range(6):
            start = turn*40
            p.line(helix[start+2:start+20], 7, 2.5)
            p.line(helix[start+21:start+40], 10, 2)
            p.line(helix[start+23:start+35], 6, 1)
        p.circle(*helix[0], 2, 7)
        p.circle(*helix[-1], 2, 12)
        cylinder(x, 213, 19+4*i, 6, 5, 7)
        cylinder(x, 287-6*i, 12+6*i, 8, 9, 7)
    p.poly([(123, 346), (137, 346), (137, 352), (132, 352),
            (132, 359), (137, 359), (137, 368), (125, 368),
            (125, 358), (123, 358)], 4)
    p.text(39, 456, 'FOUR PIN STUDY', 28, 36, 4)
    return p


if __name__ == '__main__':
    write_page(__file__, build())
