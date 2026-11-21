"""Third harmonic of an ideal string fixed at both ends."""
from math import pi, sin
from _drawing import Page, save

META = dict(title='The Still Points', purpose='Show the third harmonic and its stationary nodes',
            style='Violet oscilloscope envelopes over black plum',
            techniques=['sampled polylines', 'native circle nodes', 'alternating palette BLINK'], animated=True)


def build():
    p = Page('21182f f9ecff 49325c cc79df b16ebe f8baff b16ebe d2ff99 a58bb5 664873 826594')
    p.label(32, 70, 'THE STILL POINTS', 52)
    p.label(34, 112, 'THIRD HARMONIC', 29, 5)
    p.label(358, 110, '3 HALF WAVES FIT', 23, 7)
    for y in (174, 218, 304, 348):
        p.line([(50, y), (590, y)], 2)
    for x in (50, 590):
        p.rect(x-12, 239, 24, 44, 2)
        p.texture(fill=2).rect(x-12, 239, 24, 44, 10).texture()
        p.rect(x-12, 239, 24, 44, 8, fill=False)
    for scale in (-.68, -.34, .34, .68):
        points = [(50+540*i/144, 261+87*scale*sin(3*pi*i/144))
                  for i in range(145)]
        p.line(points, 9, 2)
    for x in (140, 320, 500):
        p.line([(x, 189), (x, 333)], 8, 2)
        for y in (189, 333):
            p.line([(x-5, y), (x+5, y)], 8, 2)
    for scale, colour, width in [(0, 8, 3), (1, 3, 5), (-1, 4, 5)]:
        points = [(50 + 540*i/72, 261 + 87*scale*sin(3*pi*i/72)) for i in range(73)]
        p.line(points, colour, width)
    for x in (140, 320, 500):
        for y in (174, 348):
            p.disc(x, y, 4, 1)
    p.label(259, 146, 'ANTINODES', 25)
    for x in (140, 320, 500):
        p.line([(x,151),(x,167)], 1, 2)
    p.line([(140,151),(500,151)], 1, 2)
    p.line([(50,363),(50,370),(410,370),(410,363)], 5, 2)
    p.rect(103, 378, 251, 25, 0)
    p.label(125, 399, 'ONE WAVELENGTH', 25, 5)
    for x in (50, 230, 410, 590):
        if x in (50, 590):
            p.disc(x, 261, 7, 1).disc(x, 261, 3, 0)
        else:
            p.disc(x, 261, 8, 7)
    for x in (230, 410):
        p.line([(x, 278), (x, 360)], 7, 2)
        p.label(x-31, 425, 'NODE', 25, 7)
    for x, label_x in ((50, 25), (590, 554)):
        p.line([(x, 291), (x, 360)], 7, 2)
        p.label(label_x, 425, 'FIXED', 24, 1)
    p.line([(35,443), (60,443)], 3, 4)
    p.line([(35,453), (60,453)], 4, 4)
    p.label(72, 459, 'EXTREMES', 25, 5)
    p.line([(202,450),(225,450)], 9, 3)
    p.label(237, 459, 'BETWEEN', 23, 8)
    p.line([(354,450), (377,450)], 8, 4)
    p.label(389, 459, 'REST POSITION', 25)
    p.blink(3, 6, 6, 6).blink(4, 5, 6, 6)
    return p


if __name__ == '__main__':
    save(__file__, build())
