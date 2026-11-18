//! What the tests of `naplps-render` share: the bytes of a small page and the reading of a
//! picture.
#![allow(
    dead_code,
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test's helpers: each test file uses its own part, with fixed inputs within range"
)]

/// The width of the pictures played, in pixels.
pub const WIDTH: usize = 640;
/// The height of the pictures played, in pixels.
pub const HEIGHT: usize = 480;
/// The bytes before a 640 by 480 picture's pixels: `P6\n640 480\n255\n`.
pub const HEADER: usize = 15;

/// SO: the PDI set into the in-use table (ANSI X3.110-1983 section 4.2).
pub const SO: u8 = 0x0E;
/// DEF MACRO (section 5.3.3.1, C1 set).
pub const DEF_MACRO: u8 = 0x80;
/// END, which closes a definition (C1 set).
pub const END: u8 = 0x85;

/// A three-byte coordinate pair, (`x`/256, `y`/256) of the unit screen (ANSI X3.110-1983
/// section 5.3.2.2.3).
pub fn pair(x: u16, y: u16) -> [u8; 3] {
    let byte = |shift: u16| 0x40 | u8::try_from(((x >> shift) & 7) << 3 | ((y >> shift) & 7)).unwrap();
    [byte(6), byte(3), byte(0)]
}

/// SELECT COLOR `entry`, POINT SET to (`x`, `y`), RECT FILLED of (`width`, `height`).
pub fn rectangle(entry: u8, x: u16, y: u16, width: u16, height: u16) -> Vec<u8> {
    let mut bytes = vec![SO, 0x3E, 0x40 | (entry << 2), 0x24];
    bytes.extend(pair(x, y));
    bytes.push(0x31);
    bytes.extend(pair(width, height));
    bytes
}

/// DEF MACRO `code` as a filled rectangle of `entry`, (`width`, `height`) at the origin.
pub fn macro_rectangle(code: u8, entry: u8, width: u16, height: u16) -> Vec<u8> {
    let mut bytes = vec![DEF_MACRO, code];
    bytes.extend(rectangle(entry, 0, 0, width, height));
    bytes.push(END);
    bytes
}

/// WAIT of `tenths` tenths of a second, 0 to 63 (section 5.3.2.8: the control command with
/// operand 5/12, then the interval).
pub fn wait(tenths: u8) -> [u8; 3] {
    [0x3D, 0x5C, 0x40 | tenths]
}

/// The colour at (`x`, `y`) of a picture.
pub fn colour(picture: &[u8], x: usize, y: usize) -> [u8; 3] {
    let at = HEADER + (y * WIDTH + x) * 3;
    [picture[at], picture[at + 1], picture[at + 2]]
}
