//! Fixed-point positions on the unit screen.
//!
//! ANSI X3.110-1983 section 5.3.2.2: coordinates are signed binary fractions of the unit
//! screen. Multi-value operands carry at most 23 magnitude bits per coordinate (8 bytes of 2 + 7
//! x 3 bits, section 5.3.2.2.3), so a fraction with 24 fractional bits holds every value exactly;
//! no floating point is used anywhere (the engine's REQ-GEN-006).

/// Fractional bits of a [`Unit`].
pub const FRACTION_BITS: u32 = 24;
/// One whole unit screen.
pub const ONE: Unit = 1 << FRACTION_BITS;

/// A signed fraction of the unit screen with [`FRACTION_BITS`] fractional bits.
pub type Unit = i32;

/// A position or displacement on the unit screen.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Point {
    /// Rightward.
    pub x: Unit,
    /// Upward.
    pub y: Unit,
}

impl Point {
    /// A point from its coordinates.
    #[must_use]
    pub const fn new(x: Unit, y: Unit) -> Self {
        Self { x, y }
    }

    /// The sum, saturating at the limits of [`Unit`].
    #[must_use]
    pub const fn plus(self, other: Self) -> Self {
        Self { x: self.x.saturating_add(other.x), y: self.y.saturating_add(other.y) }
    }
}

/// `value * numerator / denominator`, rounded toward negative infinity, saturating; a zero
/// denominator gives zero.
#[must_use]
pub fn scale(value: i64, numerator: i64, denominator: i64) -> i64 {
    if denominator == 0 {
        return 0;
    }
    let product = i128::from(value).saturating_mul(i128::from(numerator));
    let quotient = product.div_euclid(i128::from(denominator));
    // A negative denominator makes div_euclid round the other way; normalise.
    let quotient = if denominator < 0 && product.rem_euclid(i128::from(denominator)) != 0 {
        quotient.saturating_sub(1)
    } else {
        quotient
    };
    i64::try_from(quotient).unwrap_or(if quotient < 0 { i64::MIN } else { i64::MAX })
}

/// A unit-screen fraction as a whole number of pixels on a screen `pixels_per_unit` wide,
/// rounded down.
#[must_use]
pub fn to_pixels(value: Unit, pixels_per_unit: u32) -> i32 {
    let pixels = scale(i64::from(value), i64::from(pixels_per_unit), i64::from(ONE));
    i32::try_from(pixels).unwrap_or(if pixels < 0 { i32::MIN } else { i32::MAX })
}

/// A unit-screen fraction as pixels at `numerator / denominator` pixels per unit, rounded down.
#[must_use]
pub fn to_pixels_at(value: Unit, numerator: i64, denominator: i64) -> i32 {
    let pixels = scale(i64::from(value), numerator, denominator.saturating_mul(i64::from(ONE)));
    i32::try_from(pixels).unwrap_or(if pixels < 0 { i32::MIN } else { i32::MAX })
}

/// A unit-screen length as whole pixels at `numerator / denominator` pixels per unit, rounded
/// up.
#[must_use]
#[allow(
    clippy::arithmetic_side_effects,
    reason = "a 32-bit unit length times a pixel scale of at most 2^24 stays within i64"
)]
pub fn to_pixels_up_at(length: Unit, numerator: i64, denominator: i64) -> i32 {
    let magnitude = i64::from(length).saturating_abs();
    let whole = denominator.saturating_mul(i64::from(ONE)).max(1);
    let pixels = magnitude.saturating_mul(numerator).saturating_add(whole - 1) / whole;
    i32::try_from(pixels).unwrap_or(i32::MAX)
}

/// A unit-screen length as a whole number of pixels, rounded up (section 5.3.2.2.6: the logical
/// pel is rounded up to whole pixels).
#[must_use]
#[allow(
    clippy::arithmetic_side_effects,
    reason = "a 32-bit unit length times a pixel scale of at most 2^24 stays within i64"
)]
pub fn to_pixels_up(length: Unit, pixels_per_unit: u32) -> i32 {
    let magnitude = i64::from(length).saturating_abs();
    let numerator = magnitude.saturating_mul(i64::from(pixels_per_unit));
    let pixels = numerator.saturating_add(i64::from(ONE).saturating_sub(1)) / i64::from(ONE);
    i32::try_from(pixels).unwrap_or(i32::MAX)
}

/// A fraction `numerator / denominator` of the unit screen.
#[must_use]
pub fn fraction(numerator: i64, denominator: i64) -> Unit {
    let value = scale(i64::from(ONE), numerator, denominator);
    i32::try_from(value).unwrap_or(if value < 0 { i32::MIN } else { i32::MAX })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fractions_and_pixels() {
        assert_eq!(fraction(1, 2), ONE / 2);
        assert_eq!(to_pixels(fraction(1, 2), 640), 320);
        assert_eq!(to_pixels(-fraction(1, 4), 640), -160);
        assert_eq!(to_pixels_up(fraction(13, 10_000), 640), 1);
        assert_eq!(to_pixels_up(fraction(1, 40), 640), 16);
        assert_eq!(to_pixels_up(0, 640), 0);
    }

    #[test]
    fn scale_rounds_down() {
        assert_eq!(scale(7, 1, 2), 3);
        assert_eq!(scale(-7, 1, 2), -4);
        assert_eq!(scale(7, -1, 2), -4);
        assert_eq!(scale(5, 3, 0), 0);
    }
}
