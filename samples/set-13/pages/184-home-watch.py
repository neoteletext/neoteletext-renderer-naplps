"""Home Watch: a bungalow's floor plan with its rooms, heat, lights and smoke detector."""
from math import cos, radians, sin
from _drawing import Plate, save

META = dict(
    title='Home Watch',
    purpose='A home-control page for a bungalow: heat, lights, the porch lamp and the smoke detector',
    style='Floor plan with each room in its own flat fill, and a status panel beside it',
    techniques=['16-entry colour map', 'filled rectangles as rooms', 'concentric discs for the detector',
                'proportional text', 'BLINK to switch the porch lamp'],
    animated=True,
)

PALETTE = (
    '14213d fca311 e5e5e5 8ecae6 ffb4a2 ffe8a3 cdb4db 2a9d8f '
    '6c757d fefae0 d62828 06d6a0 ffd166 3d405b f4f1de 0b132b'
)
NAVY, AMBER, WALL, LIVING, BEDROOM, KITCHEN, BATH, PORCH = range(8)
GREY, CREAM, ALERT, OK, LAMP_ON, INK, PAPER, DEEP = range(8, 16)

WALL_THICKNESS = 10
DIAL_LOW = 50
DIAL_HIGH = 80
DIAL_TICKS = 6
ROOMS = (
    # name, left, top, width, height, fill
    ('LIVING', 70, 120, 200, 150, LIVING),
    ('KITCHEN', 276, 120, 164, 150, KITCHEN),
    ('BEDROOM', 70, 276, 150, 124, BEDROOM),
    ('BATH', 226, 276, 54, 124, BATH),
    ('STUDY', 286, 276, 154, 124, PAPER),
)


def floor_plan(p):
    """The bungalow's walls, its rooms and the porch, each room a flat fill with its name."""
    p.rect(60, 110, 380, 300, GREY)
    for name, left, top, width, height, fill in ROOMS:
        p.rect(left, top, width, height, fill)
        p.text(left + 8, top + 22, name, 10, 15, INK)
    # Windows are blue strips set in the outer walls; the bedroom door opens off the living room.
    p.rect(120, 110, 60, 6, LIVING)
    p.rect(330, 110, 60, 6, LIVING)
    p.rect(60, 330, 6, 50, LIVING)
    p.rect(440, 300, 6, 50, LIVING)
    p.rect(96, 406, 40, 6, LIVING)
    p.rect(170, 268, 28, 8, PAPER)
    p.poly(door_swing(170, 268, 28), INK)
    # Three kitchen ceiling lamps share the porch lamp's entry, so they switch with it.
    for x in (320, 360, 400):
        p.disc(x, 240, 6, LAMP_ON)
        p.disc(x, 240, 12, LAMP_ON, fill=False)
    # A study lamp: a small disc with a glow ring, in the amber that the dial uses.
    p.disc(372, 330, 10, AMBER)
    p.disc(372, 330, 18, AMBER, fill=False)
    p.rect(170, 410, 70, 14, PORCH)
    p.text(108, 424, 'PORCH', 9, 13, PAPER)
    # The porch lamp is a disc whose entry blinks between on and off, with a glow ring round it.
    p.disc(205, 404, 12, LAMP_ON)
    p.disc(205, 404, 20, LAMP_ON, fill=False)
    p.blink(LAMP_ON, DEEP, on=7, off=7)
    p.wait(6, 'plan')


def door_swing(hinge_x, hinge_y, radius, steps=8):
    """A door leaf and its quarter-circle swing, drawn as a thin wedge from the hinge."""
    arc = [(hinge_x + radius * cos(radians(90 * step / steps)), hinge_y + radius * sin(radians(90 * step / steps)))
           for step in range(steps + 1)]
    return [(hinge_x, hinge_y)] + arc


def devices(p):
    """The thermostat in the living room and the smoke detector in the bedroom."""
    thermostat(p, (150, 206), 34, 68)
    p.disc(300, 178, 8, INK)
    p.disc(300, 178, 16, INK, fill=False)
    p.disc(300, 178, 24, OK, fill=False)
    p.disc(132, 336, 10, CREAM)
    p.disc(132, 336, 20, CREAM, fill=False)
    p.text(108, 378, 'SMOKE OK', 9, 13, CREAM)
    p.wait(4, 'devices')


def thermostat(p, centre, radius, reading):
    """A dial from 50 F to 80 F over a half circle: ticks, a needle at the reading, and the figure below."""
    centre_x, centre_y = centre
    p.disc(centre_x, centre_y, radius + 4, PAPER)
    p.disc(centre_x, centre_y, radius - 4, NAVY)
    for tick in range(DIAL_TICKS + 1):
        angle = radians(180 + 180 * tick / DIAL_TICKS)
        p.line([(centre_x + (radius - 8) * cos(angle), centre_y + (radius - 8) * sin(angle)),
                (centre_x + (radius - 2) * cos(angle), centre_y + (radius - 2) * sin(angle))], PAPER, 2)
    needle = radians(180 + 180 * (reading - DIAL_LOW) / (DIAL_HIGH - DIAL_LOW))
    p.line([(centre_x, centre_y), (centre_x + (radius - 10) * cos(needle), centre_y + (radius - 10) * sin(needle))],
           AMBER, 6)
    p.disc(centre_x, centre_y, 4, AMBER)
    p.text(centre_x - 26, centre_y + 56, f'{reading} F', 13, 18, INK)


def status_panel(p):
    """The panel of readings: a green dot for each device that is well, and yellow for a light on."""
    p.rect(452, 96, 180, 296, PAPER)
    p.rect(452, 96, 180, 36, INK)
    p.text(466, 120, 'HOME', 14, 22, PAPER)
    p.text(466, 152, 'CHECKED 7:40 PM', 9, 13, INK)
    rows = (
        ('HEAT 68 F', OK),
        ('KITCHEN ON', AMBER),
        ('PORCH LAMP', LAMP_ON),
        ('SMOKE OK', OK),
        ('DOOR LOCKED', OK),
    )
    for index, (text, dot) in enumerate(rows):
        baseline = 172 + 46 * index
        p.disc(470, baseline - 6, 7, dot)
        p.text(486, baseline, text, 10, 15, INK)
    p.rect(452, 344, 180, 48, INK)
    p.text(462, 364, 'PRESS 3 FOR', 9, 13, PAPER)
    p.text(462, 382, 'PORCH LIGHT', 9, 13, PAPER)


def build():
    p = Plate(PALETTE)
    p.rect(0, 0, 640, 480, NAVY)
    p.rect(0, 0, 640, 60, INK)
    p.title(24, 42, 'WARDWELL HOME WATCH', AMBER, 20, 30)
    floor_plan(p)
    devices(p)
    status_panel(p)
    p.rect(0, 440, 640, 40, INK)
    p.text(24, 466, 'THERMOSTAT 68 F    ALARM ARMED AT NIGHT', 11, 16, AMBER)
    return p


if __name__ == '__main__':
    save(__file__, build)
