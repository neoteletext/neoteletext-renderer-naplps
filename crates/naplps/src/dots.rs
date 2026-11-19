//! Raster dots and the unit screen (`docs/naplps-raster.md` RAS-2, DEC-6853, DEC-6857): the one
//! mapping every NeoTeletext writer of NAPLPS calls, so that a place named in dots of the 480 by
//! 500 teletext raster is written as the operand the receiver's canvas draws on that dot.
//!
//! The display area, raster lines [`DISPLAY_FIRST_LINE`] to [`DISPLAY_FIRST_LINE`] +
//! [`DISPLAY_LINES`] − 1, shows the unit screen's width and the displayed 25/32 of its height
//! (DEC-5766). The centre of dot (X, Y) is the point across X / 480, up (F + D − 1 − Y) × 25 /
//! (32 D) of the unit screen, which for F 20 and D 460 is (479 − Y) × 25 / 14,720.

use alloc::vec::Vec;

use crate::fixed::{Point, Unit};
use crate::limits::{DISPLAY_FIRST_LINE, DISPLAY_LINES, RASTER_WIDTH};
use crate::surface::{DISPLAY_HEIGHT_DENOMINATOR, DISPLAY_HEIGHT_NUMERATOR, Surface, pixel_of};

/// How a place between two operand values is rounded to one of them.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Rounding {
    /// To the nearest value, a tie up (towards plus infinity): a coordinate written at a dot
    /// (RAS-2, RAS-6).
    Nearest,
    /// Down (towards minus infinity): the text field and its origin, which must lie at or just
    /// short of the cell they are written for (RAS-8).
    Down,
}

/// The most bytes a multi-value operand has (ANSI X3.110-1983 section 5.3.2.2.3, Table 5:
/// b5 b4 b3 of DOMAIN's fixed-format byte give 1 to 8).
const MAX_OPERAND_BYTES: u8 = 8;
/// The bits of each axis a byte of a two-dimensional multi-value operand carries (section
/// 5.3.2.2.3, Figure 11: three of x in b6 b5 b4, three of y in b3 b2 b1).
const AXIS_BITS_PER_BYTE: u32 = 3;
/// The bits of one axis within a byte.
const AXIS_BYTE_MASK: i128 = 0b111;
/// Every operand byte has b7 set, the bit that puts it in columns 4 to 7 (section 5.3.1).
const DATA_BIT: u8 = 0x40;

/// The axis value of the whole unit screen for operands of `bytes` bytes, 2^(3 `bytes` − 1):
/// each axis is 3 `bytes` bits of two's complement, the first the sign. `None` for a length
/// the standard does not have.
fn full_scale(bytes: u8) -> Option<i128> {
    if !(1..=MAX_OPERAND_BYTES).contains(&bytes) {
        return None;
    }
    let fraction_bits = AXIS_BITS_PER_BYTE.saturating_mul(u32::from(bytes)).saturating_sub(1);
    1i128.checked_shl(fraction_bits)
}

/// `numerator / denominator`, for a positive denominator, rounded as `rounding` says.
fn rounded(numerator: i128, denominator: i128, rounding: Rounding) -> i128 {
    let numerator = match rounding {
        // floor(n / d + 1/2) = floor((2n + d) / 2d).
        Rounding::Nearest => {
            return numerator
                .saturating_mul(2)
                .saturating_add(denominator)
                .checked_div_euclid(denominator.saturating_mul(2))
                .unwrap_or(0);
        }
        Rounding::Down => numerator,
    };
    numerator.checked_div_euclid(denominator).unwrap_or(0)
}

/// `value` held to the operand's range, −`full` to `full` − 1.
fn held(value: i128, full: i128) -> i64 {
    let value = value.clamp(full.saturating_neg(), full.saturating_sub(1));
    i64::try_from(value).unwrap_or(0)
}

/// The place (`x` / `denominator`, `y` / `denominator`) of the raster, in dots from its top
/// left, as the axis values of a two-dimensional multi-value operand of `bytes` bytes (RAS-2;
/// ANSI X3.110-1983 section 5.3.2.2.3, Table 5): across × 2^(3 `bytes` − 1) and up ×
/// 2^(3 `bytes` − 1), each rounded as `rounding` says, then held to the operand's range,
/// −2^(3 `bytes` − 1) to 2^(3 `bytes` − 1) − 1. A place of rows 0 and 24, outside the display
/// area, is written as any other and lands off the canvas. `bytes` outside 1 to 8, or a
/// `denominator` that is not positive, gives (0, 0).
#[must_use]
pub fn dot_steps(x: i64, y: i64, denominator: i64, bytes: u8, rounding: Rounding) -> (i64, i64) {
    let Some(full) = full_scale(bytes) else { return (0, 0) };
    if denominator <= 0 {
        return (0, 0);
    }
    let denominator = i128::from(denominator);
    // Across: x / (denominator 480) of the unit screen.
    let across =
        rounded(i128::from(x).saturating_mul(full), denominator.saturating_mul(i128::from(RASTER_WIDTH)), rounding);
    // Up: (F + D − 1 − y / denominator) × 25 / (32 D), the last line of the display area being
    // the unit screen's foot, 0.
    let last_line = i128::from(DISPLAY_FIRST_LINE).saturating_add(i128::from(DISPLAY_LINES)).saturating_sub(1);
    let lines_up = last_line.saturating_mul(denominator).saturating_sub(i128::from(y));
    let up = rounded(
        lines_up.saturating_mul(i128::from(DISPLAY_HEIGHT_NUMERATOR)).saturating_mul(full),
        i128::from(DISPLAY_HEIGHT_DENOMINATOR).saturating_mul(i128::from(DISPLAY_LINES)).saturating_mul(denominator),
        rounding,
    );
    (held(across, full), held(up, full))
}

/// The unit-screen fraction `numerator` / `denominator` as one axis's value for operands of
/// `bytes` bytes, rounded and held as [`dot_steps`] does (RAS-2): for sizes, such as the text
/// field of RAS-8, `unit_steps(1, 40, 6, Rounding::Down)`, 3,276. `bytes` outside 1 to 8, or a
/// zero `denominator`, gives 0.
#[must_use]
pub fn unit_steps(numerator: i64, denominator: i64, bytes: u8, rounding: Rounding) -> i64 {
    let Some(full) = full_scale(bytes) else { return 0 };
    let (numerator, denominator) = match denominator {
        0 => return 0,
        negative if negative < 0 => (i128::from(numerator).saturating_neg(), i128::from(denominator).saturating_neg()),
        _ => (i128::from(numerator), i128::from(denominator)),
    };
    held(rounded(numerator.saturating_mul(full), denominator, rounding), full)
}

/// The axis values `across` and `up` as the bytes of a two-dimensional multi-value operand of
/// `bytes` bytes, appended to `out` (ANSI X3.110-1983 section 5.3.2.2.3, Figure 11): each held
/// to the operand's range and written in two's complement, three bits of x and three of y to a
/// byte, most significant first, each byte with b7 set. `bytes` outside 1 to 8 writes nothing.
pub fn multi_value_operand(across: i64, up: i64, bytes: u8, out: &mut Vec<u8>) {
    let Some(full) = full_scale(bytes) else { return };
    let (across, up) = (i128::from(held(i128::from(across), full)), i128::from(held(i128::from(up), full)));
    for index in (0..u32::from(bytes)).rev() {
        let shift = AXIS_BITS_PER_BYTE.saturating_mul(index);
        let bits = |value: i128| value.checked_shr(shift).unwrap_or(0) & AXIS_BYTE_MASK;
        let pair = bits(across).checked_shl(AXIS_BITS_PER_BYTE).unwrap_or(0) | bits(up);
        out.push(DATA_BIT | u8::try_from(pair).unwrap_or(0));
    }
}

/// The geometry of the receiver's canvas, which [`dot_of_point`] rounds a point on: drawing
/// nothing, only its size and scales.
struct ReceiverGeometry;

impl Surface for ReceiverGeometry {
    fn width(&self) -> i32 {
        i32::try_from(RASTER_WIDTH).unwrap_or(i32::MAX)
    }
    fn height(&self) -> i32 {
        i32::try_from(DISPLAY_LINES).unwrap_or(i32::MAX)
    }
    fn scale_x(&self) -> (i64, i64) {
        (i64::from(RASTER_WIDTH), 1)
    }
    fn scale_y(&self) -> (i64, i64) {
        (i64::from(DISPLAY_LINES).saturating_mul(DISPLAY_HEIGHT_DENOMINATOR), DISPLAY_HEIGHT_NUMERATOR)
    }
    fn put(&mut self, _x: i32, _y: i32, _entry: u8) {}
    fn get(&self, _x: i32, _y: i32) -> Option<u8> {
        None
    }
}

/// The raster dot a unit-screen point lands on (RAS-2): the pixel of the receiver's canvas of
/// 480 by 460 the renderer rounds the point to, as every drawing routine does, moved down to the
/// display area's first line. A point above the unit screen's displayed height or below its
/// foot lands on a line of rows 0 or 24, or past the raster, where the canvas has no pixel.
#[must_use]
pub fn dot_of_point(across: Unit, up: Unit) -> (i32, i32) {
    let (x, y) = pixel_of(&ReceiverGeometry, Point::new(across, up));
    (x, y.saturating_add(i32::try_from(DISPLAY_FIRST_LINE).unwrap_or(0)))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_text_field_is_a_hair_under_one_cell() {
        // RAS-8 item 1: 3,276 by 4,452 steps of 1/131072.
        assert_eq!(unit_steps(1, 40, 6, Rounding::Down), 3_276);
        assert_eq!(unit_steps(20 * 25, 32 * 460, 6, Rounding::Down), 4_452);
        assert_eq!(unit_steps(1, 40, 6, Rounding::Nearest), 3_277);
        assert_eq!(unit_steps(-1, -40, 6, Rounding::Down), 3_276);
        assert_eq!(unit_steps(1, 0, 6, Rounding::Down), 0);
        assert_eq!(unit_steps(1, 40, 9, Rounding::Down), 0);
    }

    #[test]
    fn values_are_held_to_the_operands_range() {
        // Three bytes: nine bits an axis, −256 to 255.
        assert_eq!(dot_steps(480, 0, 1, 3, Rounding::Nearest).0, 255);
        assert_eq!(unit_steps(-2, 1, 3, Rounding::Nearest), -256);
        assert_eq!(dot_steps(1, 1, 0, 6, Rounding::Nearest), (0, 0));
        assert_eq!(dot_steps(1, 1, 1, 0, Rounding::Nearest), (0, 0));
    }

    #[test]
    fn an_operand_is_three_bits_of_each_axis_a_byte_most_significant_first() {
        let mut out = Vec::new();
        // Across 0b000_001 010, up the nine bits of −1: all ones.
        multi_value_operand(0b1010, -1, 3, &mut out);
        assert_eq!(out, [0x40 | 0b000_111, 0x40 | 0b001_111, 0x40 | 0b010_111]);
        out.clear();
        multi_value_operand(1, 1, 0, &mut out);
        assert_eq!(out, Vec::<u8>::new());
    }

    #[test]
    fn the_corners_of_the_display_area() {
        // Dot (0, 479), the display area's bottom left, is the unit screen's origin.
        assert_eq!(dot_steps(0, 479, 1, 6, Rounding::Nearest), (0, 0));
        assert_eq!(dot_of_point(0, 0), (0, 479));
    }
}
