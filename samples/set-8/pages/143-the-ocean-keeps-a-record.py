"""An idealised spreading ridge with mirrored magnetic polarity bands."""
from _drawing import Page, save

META = dict(title='The Ocean Keeps a Record', purpose='Show how polarity reversals are recorded symmetrically as ocean floor spreads',
            style='Rust and marine-blue seafloor block diagram',
            techniques=['oblique polygons', 'spaced polarity marks', 'directional arrows'], animated=False)


def build():
    p = Page('e7e4d7 182f3a 28576e 99482d d77b50 8db4b3 502c29 c8dbcb 67544e d6b897 ae6540 f7d1a3 f1a16d bfe0d8 6d453c 804232')
    p.label(27, 52, 'THE OCEAN KEEPS', 45)
    p.label(27, 94, 'A RECORD', 45)
    p.label(30, 132, 'MIRRORED MAGNETIC STRIPES', 25, 2)

    def face(distance):
        return 279+distance, 250 + min(abs(distance),65)*.51 + max(0, 1-abs(distance)/19)*12

    def rear(distance):
        x, y = face(distance)
        return x+83, y-112

    def drop(point, depth):
        return point[0], point[1]+depth

    depths = [0,19,46,63,99,121,155,183,229]
    f, g = face(229), rear(229)
    p.poly([f,g,drop(g,126),(f[0],401)], 8)
    p.poly([f,g,drop(g,30),drop(f,30)], 2)
    for side in (-1, 1):
        for i, (d1,d2) in enumerate(zip(depths,depths[1:])):
            a,b = side*d1,side*d2
            f,g = face(a),face(b)
            p.poly([drop(f,29),drop(g,29),(g[0],401),(f[0],401)], 9)
            p.poly([f,g,drop(g,30),drop(f,30)], 3 if i%2==0 else 2)
            h,j = rear(a),rear(b)
            p.poly([f,g,j,h], 4 if i%2==0 else 5)
            if i%2:
                for t in (.18, .38, .58, .78):
                    p.line([(f[0]+(g[0]-f[0])*u+83*t,
                             f[1]+(g[1]-f[1])*u-112*t)
                            for u in (.14, .86)], 2, 2)
    p.poly([(50,371),(138,361),(222,366),(338,366),(419,358),(508,368),
            (508,401),(50,401)], 10)
    p.poly([(212,401),(246,379),(264,350),(274,305),(285,305),
            (294,350),(313,379),(346,401)], 3)
    p.poly([(244,401),(265,375),(275,342),(278,301),(282,301),
            (286,342),(296,375),(317,401)], 12)
    p.arrow((280,392),(280,327),6,3,12)
    p.line([face(0), rear(0)], 6, 3)
    p.arrow((218,323),(88,323),1,3)
    p.arrow((344,323),(476,323),1,3)
    p.label(87, 355, 'OLDER', 24)
    p.label(415, 355, 'OLDER', 24)
    p.label(387, 398, 'RIDGE AXIS', 24)
    x, y = face(0)
    p.line([(382,389),(337,389),(311,335),(x,y+7)],6,2)
    p.disc(x,y+7,4,6)
    p.label(475, 424, 'RISING MELT', 24)
    p.line([(463,415),(332,415),(296,376)], 6, 2)
    p.label(176, 160, 'SAME AGE', 23)
    band_distance = (depths[5]+depths[6])/2
    for side, start, elbow in [(-1, 169, 150), (1, 289, 321)]:
        x,y = face(side*band_distance)
        point = (x+83*.67, y-112*.67)
        p.line([(start,153),(elbow,153),point], 1, 2)
        p.disc(*point, 9, 1).disc(*point, 5, 11)
    p.rect(36, 433, 26, 23, 4)
    p.label(74, 455, 'NORMAL', 27)
    p.rect(287,433,26,23,5)
    for y in (438, 445, 452):
        p.line([(291,y),(309,y)], 2, 2)
    p.label(324, 455, 'REVERSED', 27)
    return p


if __name__ == '__main__':
    save(__file__, build())
