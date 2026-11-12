"""A small NAPLPS page builder for the examples in docs/guide.md and docs/reference.md.

Python 3 standard library only. Every function returns bytes in NAPLPS's 7-bit form, so a page
is these pieces concatenated. docs/reference.md describes each encoding; the section numbers
below are those of ANSI X3.110-1983 / CSA T500-1983.
"""

# C0 controls (section 6.1).
BS, HT, LF, VT, CS, CR = b"\x08", b"\x09", b"\x0a", b"\x0b", b"\x0c", b"\x0d"
SO = b"\x0e"  # the PDI set into the 7-bit code table: opcodes and operands follow
SI = b"\x0f"  # the primary (ASCII) set back: text follows
SS2 = b"\x19"  # the next byte comes from G2 (the supplementary set by default)
SS3 = b"\x1d"  # the next byte comes from G3 (the mosaic set by default)
ESC = b"\x1b"

# C1 controls, in their 7-bit form ESC Fe (section 6.2).
DEF_MACRO, DEFP_MACRO, DEFT_MACRO = ESC + b"\x40", ESC + b"\x41", ESC + b"\x42"
DEF_DRCS, DEF_TEXTURE, END = ESC + b"\x43", ESC + b"\x44", ESC + b"\x45"
REPEAT, REPEAT_TO_EOL = ESC + b"\x46", ESC + b"\x47"
REVERSE_VIDEO, NORMAL_VIDEO = ESC + b"\x48", ESC + b"\x49"
SMALL_TEXT, MEDIUM_TEXT, NORMAL_TEXT = ESC + b"\x4a", ESC + b"\x4b", ESC + b"\x4c"
DOUBLE_HEIGHT, DOUBLE_SIZE = ESC + b"\x4d", ESC + b"\x4f"
BLINK_START, BLINK_STOP = ESC + b"\x4e", ESC + b"\x5e"
UNDERLINE_START, UNDERLINE_STOP = ESC + b"\x59", ESC + b"\x5a"

# Designations (section 4.3): which set G2 or G3 holds.
MACROS_INTO_G3 = ESC + b"\x2f\x7a"
DRCS_INTO_G3 = ESC + b"\x2f\x7b"
MOSAICS_INTO_G3 = ESC + b"\x2f\x7d"
SUPPLEMENTARY_INTO_G2 = ESC + b"\x2a\x7c"

# PDI opcodes (section 5.3). In each group of four: +1 is the second form (relative or filled),
# +2 the "set" form that takes its starting point as its first operand.
RESET, DOMAIN, TEXT, TEXTURE = 0x20, 0x21, 0x22, 0x23
POINT_SET_ABS, POINT_SET_REL, POINT_ABS, POINT_REL = 0x24, 0x25, 0x26, 0x27
LINE_ABS, LINE_REL, SET_LINE_ABS, SET_LINE_REL = 0x28, 0x29, 0x2A, 0x2B
ARC_OUTLINED, ARC_FILLED, SET_ARC_OUTLINED, SET_ARC_FILLED = 0x2C, 0x2D, 0x2E, 0x2F
RECT_OUTLINED, RECT_FILLED, SET_RECT_OUTLINED, SET_RECT_FILLED = 0x30, 0x31, 0x32, 0x33
POLY_OUTLINED, POLY_FILLED, SET_POLY_OUTLINED, SET_POLY_FILLED = 0x34, 0x35, 0x36, 0x37
FIELD, INCREMENTAL_POINT, INCREMENTAL_LINE, INCREMENTAL_POLY_FILLED = 0x38, 0x39, 0x3A, 0x3B
SET_COLOR, WAIT, SELECT_COLOR, BLINK = 0x3C, 0x3D, 0x3E, 0x3F

OPERAND = 0x40  # bit 7 marks an operand byte; its six low bits are data


def fixed(*values):
    """Fixed-format operand bytes: six data bits each."""
    return bytes(OPERAND | (value & 0x3F) for value in values)


def xy(x, y, length=3):
    """A coordinate pair as a multi-value operand of `length` bytes (section 5.3.2.2.5).

    x and y are fractions of the unit screen, -1 <= value < 1. Each gets 3 x length bits: a sign
    bit, then the fraction, most significant bits first, three bits of x and three of y per byte.
    """
    bits = 3 * length
    scale = 1 << (bits - 1)

    def field(value):
        whole = max(-scale, min(scale - 1, round(value * scale)))
        return whole & ((1 << bits) - 1)  # two's complement

    fx, fy = field(x), field(y)
    out = bytearray()
    for index in range(length):
        shift = 3 * (length - 1 - index)
        out.append(OPERAND | ((fx >> shift) & 7) << 3 | ((fy >> shift) & 7))
    return bytes(out)


def rgb(red, green, blue, length=3):
    """A colour as a multi-value operand (section 5.3.2.5.1): 0 to 255 per primary.

    Each byte carries two bits of each primary in the order G R B G R B, most significant first.
    """
    bits = 2 * length
    g, r, b = (value >> (8 - bits) if bits <= 8 else value << (bits - 8) for value in (green, red, blue))
    out = bytearray()
    for index in range(length):
        high = bits - 1 - 2 * index
        byte = 0
        for shift in (high, high - 1):
            for primary in (g, r, b):
                byte = byte << 1 | ((primary >> shift) & 1)
        out.append(OPERAND | byte)
    return bytes(out)


def pdi(opcode, *operands):
    """One PDI: its opcode byte followed by its operand bytes."""
    return bytes([opcode]) + b"".join(operands)


def reset_all():
    """RESET with every bit set: default DOMAIN, colour mode 1 with the default colour map,
    screen cleared to black, text, blink, texture, macros and DRCS to their defaults."""
    return pdi(RESET, fixed(0x3F, 0x3F))


def select(entry, background=None, map_bits=4):
    """SELECT COLOR: draw with colour-map `entry` (mode 1), or with `background` too (mode 2)."""
    operands = [fixed(entry << (6 - map_bits))]
    if background is not None:
        operands.append(fixed(background << (6 - map_bits)))
    return pdi(SELECT_COLOR, *operands)


def define(entry, red, green, blue, map_bits=4):
    """Select colour-map `entry` and give it a colour."""
    return select(entry, map_bits=map_bits) + pdi(SET_COLOR, rgb(red, green, blue))


def wait(tenths):
    """WAIT: pause `tenths` tenths of a second (up to 63 per interval byte)."""
    intervals = []
    while tenths > 0:
        intervals.append(min(tenths, 63))
        tenths -= intervals[-1]
    return pdi(WAIT, fixed(0x1C, *intervals))


def text_at(x, y, characters):
    """Text with its first character field's lower left corner at (x, y), then back to PDIs."""
    return pdi(POINT_SET_ABS, xy(x, y)) + SI + characters.encode("ascii") + SO


def polygon(points, filled=True):
    """A polygon through absolute points: SET & POLY takes the first point, then steps."""
    # Snap to the 1/256 grid of three-byte operands first, so the rounded steps add up exactly.
    points = [(round(x * 256) / 256, round(y * 256) / 256) for x, y in points]
    operands = [xy(*points[0])]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        operands.append(xy(x1 - x0, y1 - y0))
    return pdi(SET_POLY_FILLED if filled else SET_POLY_OUTLINED, *operands)


def circle(cx, cy, radius, filled=True):
    """A circle: an arc given its start point and the diametrically opposite point."""
    return pdi(SET_ARC_FILLED if filled else SET_ARC_OUTLINED, xy(cx - radius, cy), xy(2 * radius, 0))
