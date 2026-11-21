"""Central transit and its geometric light curve for a uniform stellar disc."""
from math import acos, sqrt
from _drawing import Page, save

META = dict(title='A Star Winks', purpose='Relate an exoplanet crossing a stellar disc to a drop in measured light',
            style='Amber stellar disc paired with an icy photometry trace',
            techniques=['native circles', 'indexed overpainting', 'computed light curve'], animated=False)


def obscured(distance, planet):
    if distance >= 1+planet:
        return 0
    if distance <= 1-planet:
        return planet**2
    a = (distance**2 + 1 - planet**2)/(2*distance)
    b = (distance**2 + planet**2 - 1)/(2*distance*planet)
    return (acos(a) + planet**2*acos(b) - distance*sqrt(1-a*a))/acos(-1)


def build():
    p = Page('152034 fff1d5 283747 e98443 f6b956 ffe081 8be6e4 567c97 e2a74c f8c969 416178 a4bccb')
    p.label(32, 69, 'A STAR WINKS', 58)
    p.label(35, 109, 'EXOPLANET TRANSIT', 29, 6)
    centre, radius, scale = 382, .16, 94
    star_y = 213
    p.disc(centre, star_y, scale, 3).disc(centre, star_y, scale-3, 4)
    p.disc(centre, star_y, scale-7, 9)
    contacts = (-1-radius, -1+radius, 1-radius, 1+radius)
    p.texture(line=2).line([(253,star_y),(511,star_y)], 5, 2).texture()
    p.label(36, 159, 'UNIFORM STAR', 24)
    p.label(36, 191, 'ONE PLANET', 24, 6)
    p.label(36, 220, 'FOUR CONTACTS', 24, 6)
    p.label(36, 269, 'CENTRAL PATH', 23, 11)
    p.arrow((37,237),(184,237),6,2,10)
    for number, distance in enumerate(contacts, start=1):
        x = centre+scale*distance
        p.texture(line=2).line([(x, star_y+16), (x, 412)], 7, 2).texture()
        if number in (2, 3):
            p.disc(x, star_y, scale*radius, 0)
        p.disc(x, star_y, scale*radius, 11 if number in (1,4) else 6, fill=False)
        label_y = star_y-31 if number in (1, 4) else star_y+8
        if number in (1, 4):
            p.line([(x, star_y-17),(x, star_y-26)], 11, 2)
        p.label(x-7, label_y, str(number), 23)

    p.label(36, 296, 'RELATIVE LIGHT', 25)
    p.line([(127,335),(127,411)], 11, 2)
    for y, tick in [(347, '100%'), (374.5, '98.72%'), (402, '97.44%')]:
        p.label(35, y+7, tick, 23)
        p.line([(120,y),(606,y)], 10 if y == 374.5 else 7, 2)
    points = []
    for x in range(139, 607):
        distance = abs(x-centre)/scale
        points.append((x, 347+55*obscured(distance, radius)/radius**2))
    p.line(points, 6, 4)
    for distance, y in zip(contacts, (347,402,402,347)):
        p.disc(centre+scale*distance, y, 5, 1)
    for start, end, label, label_x in [(contacts[0],contacts[1],'INGRESS',203),
                                        (contacts[2],contacts[3],'EGRESS',469)]:
        left, right = centre+scale*start, centre+scale*end
        p.line([(left,415),(left,427),(right,427),(right,415)], 6, 2)
        p.line([((left+right)/2,427), (label_x+24,438)], 6, 2)
        p.label(label_x, 464, label, 23, 6)
    p.arrow((533, 420), (606, 420), 7, 2, 10)
    p.label(551, 448, 'TIME', 24)
    p.line([(127,347),(127,411)], 11, 2)
    p.label(34, 464, '2.56% DIP', 26, 6)
    return p


if __name__ == '__main__':
    save(__file__, build())
