"""Download Tonight's Program: telesoftware, a program sent down the line frame by frame to the home computer."""
import math

from _screen import Plate, save

META = dict(
    title="Download Tonight's Program",
    purpose='The service sends a program to the home computer, frame by frame, while the family waits',
    style='Navy night with a broadcast mast, a stream of digits, a beige home computer, a floppy and a cassette',
    techniques=['mosaic progress bar filled frame by frame with WAIT', 'digits set along an arc one WAIT apart', 'a town of aerials under the signal',
                'BLINK receiving lamp', 'outlined and filled rectangles', 'filled arcs', 'a desk and a mug for the room', 'a transmitter hut', 'the program listing on the screen'],
    animated=True,
)

PALETTE = ('0d1b2a f25c05 fff3d6 48cae4 ffffff d9c9a3 a89670 122b18 '
           '6bff8a 2b2d42 ffd166 c0c6cf ef233c 06d6a0 1b3a5a 5a1010')
(NAVY, ORANGE, PAPER, CYAN, WHITE, BEIGE, TAN, SCREEN,
 PHOSPHOR, DISK, LABEL, METAL, RED, GREEN, PANEL, LAMP) = range(16)

FRAMES, RECEIVED = 30, 14
FULL_BLOCK = 0x7f


def build():
    p = Plate(PALETTE, NAVY)
    p.rect(0, 0, 640, 56, ORANGE)
    p.text(18, 40, 'HOMEBYTE', 22, 32, PAPER, prop=False)
    p.text(214, 38, 'TELESOFTWARE', 13, 20, NAVY, prop=False)
    p.text(572, 40, '225', 14, 22, PAPER, prop=False)

    # The mast and its signal.
    p.pel(2)
    p.line([(40, 236), (70, 80), (100, 236)], METAL, 3)
    for y in range(100, 236, 26):
        t = (y - 80) / 156
        p.line([(70 - 30 * t, y), (70 + 30 * t, y + 22)], METAL, 1)
        p.line([(70 + 30 * t, y), (70 - 30 * t, y + 22)], METAL, 1)
    p.disc(70, 78, 6, RED)
    # The transmitter hut at the mast's foot, on a line of ground.
    p.rect(14, 236, 106, 4, PANEL)
    p.rect(82, 210, 40, 26, METAL)
    p.poly([(78, 212), (102, 198), (126, 212)], PANEL)
    p.rect(90, 218, 10, 8, LABEL)
    p.disc(112, 222, 3, RED)
    for radius in (18, 30, 42):
        p.arc((70 + radius * 0.6, 78 - radius * 0.8), (70 + radius, 78), (70 + radius * 0.6, 78 + radius * 0.8), CYAN)

    # The desk the computer stands on, and a mug of cocoa beside the keyboard.
    p.rect(340, 264, 300, 10, TAN)
    p.rect(340, 274, 300, 4, BEIGE)
    p.rect(346, 240, 18, 24, RED)
    p.arc((364, 246), (372, 252), (364, 258), RED)
    p.rect(348, 240, 14, 4, PAPER)
    # The home computer: monitor, screen, keyboard.
    p.rect(404, 70, 216, 150, BEIGE)
    p.rect(420, 84, 184, 120, SCREEN)
    p.rect(470, 220, 116, 10, TAN)
    p.poly([(388, 236), (628, 236), (640, 266), (376, 266)], BEIGE)
    for row in range(3):
        for key in range(12):
            p.rect(396 + key * 19 + row * 4, 240 + row * 8, 14, 5, TAN)
    # The screen shows the program's listing as it arrives, with a block cursor at its end.
    for index, line in enumerate(('LOADING 14/30', '10 REM MOONSKIP', '20 FOR S=1 TO 9', '30 GOSUB 400', '40 NEXT S')):
        p.text(426, 104 + index * 22, line, 12, 18, PHOSPHOR, prop=False)
    p.rect(538, 178, 10, 16, PHOSPHOR)
    p.wait(6, 'scene')

    # The program crosses from the mast to the computer as a stream of digits on an arc.
    # The town the signal crosses: houses with rooftop aerials.
    for hx, width, height in ((128, 40, 26), (176, 34, 34), (218, 46, 22), (272, 38, 30), (318, 44, 26)):
        base = 250
        p.rect(hx, base - height, width, height, PANEL)
        p.poly([(hx - 4, base - height), (hx + width / 2, base - height - 14), (hx + width + 4, base - height)], PANEL)
        p.rect(hx + 8, base - height + 8, 8, 8, LABEL)
        # A rooftop aerial: a mast, a boom pointing at the transmitter, and three elements.
        mx, top = hx + width / 2, base - height - 30
        p.line([(mx, base - height - 14), (mx, top)], METAL, 1)
        p.line([(mx - 16, top), (mx + 2, top)], METAL, 1)
        for k in range(3):
            p.line([(mx - 14 + k * 6, top - 5 + k), (mx - 14 + k * 6, top + 5 - k)], METAL, 1)
    p.rect(110, 250, 280, 3, PANEL)

    bits = '10110011101'
    for index, bit in enumerate(bits):
        t = index / (len(bits) - 1)
        x = 124 + 256 * t
        y = 150 - 56 * math.sin(math.pi * t) + 16 * t
        p.text(x, y, bit, 14, 22, CYAN if index % 3 else WHITE, prop=False)
        p.wait(1)

    # A floppy disk and a cassette.
    p.rect(24, 262, 124, 124, DISK)
    p.rect(54, 262, 64, 40, METAL)
    p.rect(92, 268, 14, 28, DISK)
    p.rect(40, 324, 92, 54, LABEL)
    p.text(48, 348, 'MOON-', 12, 18, NAVY, prop=False)
    p.text(48, 370, 'SKIP', 12, 18, NAVY, prop=False)
    p.rect(166, 296, 170, 92, METAL)
    p.rect(176, 304, 150, 36, LABEL)
    p.text(184, 330, 'SIDE A', 12, 18, NAVY, prop=False)
    p.rect(200, 348, 102, 30, NAVY)
    p.disc(222, 363, 14, TAN)
    p.disc(280, 363, 11, TAN)
    p.rect(222, 372, 58, 5, TAN)
    p.disc(222, 363, 8, WHITE)
    p.disc(280, 363, 8, WHITE)
    p.disc(222, 363, 4, NAVY)
    p.disc(280, 363, 4, NAVY)

    # Tonight's program.
    p.rect(352, 280, 268, 108, PANEL)
    p.text(364, 308, "TONIGHT'S PROGRAM", 12, 18, LABEL, prop=False)
    p.text(364, 340, 'MOONSKIP', 18, 26, WHITE, prop=False)
    p.text(364, 370, 'GAME  32K  FREE', 13, 20, CYAN, prop=False)
    p.wait(6, 'program')

    # The progress bar fills frame by frame: one mosaic block each.
    p.rect(20, 398, 600, 30, PANEL)
    p.rect(526, 406, 14, 14, LAMP)
    for frame in range(RECEIVED):
        p.mosaics(28 + frame * 16, 424, [FULL_BLOCK], 14, 22, GREEN)
        p.wait(3)
    p.text(548, 420, '14/30', 12, 18, WHITE, prop=False)

    p.rect(0, 436, 640, 44, ORANGE)
    p.text(18, 466, 'RECEIVING   ABOUT 4 MIN TO GO', 14, 22, PAPER, prop=False)
    p.blink(LAMP, RED, on=4, off=4)
    return p


if __name__ == '__main__':
    save(__file__, build)
