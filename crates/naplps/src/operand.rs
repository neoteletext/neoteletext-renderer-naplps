//! PDI operands: fixed-format bytes, single-value operands, multi-value coordinates and colours
//! (ANSI X3.110-1983 sections 5.3.1 and 5.3.2.2).
//!
//! Every operand byte carries six data bits, b6 to b1 (the byte's bit 7 marks it as data). A
//! multi-value operand of n bytes in two dimensions gives each coordinate 3n bits, sign first,
//! three per byte (b6 to b4 for x, b3 to b1 for y); in three dimensions 2n bits each (b6 b5 x,
//! b4 b3 y, b2 b1 z). Bytes the sender omitted count as zero (section 5.3.2.2.5).

use crate::fixed::{FRACTION_BITS, Point, Unit};

/// Data bits in one operand byte.
pub const DATA_BITS: u32 = 6;
/// The data bits of an operand byte.
pub const DATA_MASK: u8 = 0x3F;

/// How operands are currently encoded (section 5.3.2.2): set by DOMAIN.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Domain {
    /// Bytes in a single-value operand, 1 to 4.
    pub single_bytes: usize,
    /// Bytes in a multi-value operand, 1 to 8.
    pub multi_bytes: usize,
    /// Whether coordinates have a Z component (which is read and ignored).
    pub three_d: bool,
}

impl Default for Domain {
    /// Section 5.3.2.2: one-byte single values, three-byte multi values, two dimensions.
    fn default() -> Self {
        Self { single_bytes: 1, multi_bytes: 3, three_d: false }
    }
}

impl Domain {
    /// The DOMAIN command's fixed-format byte (section 5.3.2.2.2 to 5.3.2.2.4).
    #[must_use]
    pub fn from_byte(byte: u8) -> Self {
        let bits = byte & DATA_MASK;
        Self {
            single_bytes: usize::from(bits & 0b11).saturating_add(1),
            multi_bytes: usize::from((bits >> 2) & 0b111).saturating_add(1),
            three_d: bits & 0b10_0000 != 0,
        }
    }
}

/// Reads operands from a PDI's data bytes, front to back.
pub struct Reader<'a> {
    bytes: &'a [u8],
    position: usize,
}

impl<'a> Reader<'a> {
    /// A reader over a PDI's data bytes.
    #[must_use]
    pub fn new(bytes: &'a [u8]) -> Self {
        Self { bytes, position: 0 }
    }

    /// Whether every byte has been read.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.position >= self.bytes.len()
    }

    /// Bytes not yet read.
    #[must_use]
    pub fn remaining(&self) -> usize {
        self.bytes.len().saturating_sub(self.position)
    }

    /// The next byte's six data bits, if any.
    pub fn byte(&mut self) -> Option<u8> {
        let byte = self.bytes.get(self.position).copied()?;
        self.position = self.position.saturating_add(1);
        Some(byte & DATA_MASK)
    }

    /// Up to `count` bytes, the missing ones as zero; `None` when no byte at all remains.
    fn take(&mut self, count: usize) -> Option<([u8; 8], usize)> {
        if self.is_empty() {
            return None;
        }
        let mut out = [0u8; 8];
        let mut present: usize = 0;
        for slot in out.iter_mut().take(count) {
            if let Some(byte) = self.byte() {
                *slot = byte;
                present = present.saturating_add(1);
            }
        }
        Some((out, present))
    }

    /// A single-value operand: its value and its width in bits (6 per byte).
    pub fn single(&mut self, domain: Domain) -> Option<(u32, u32)> {
        let count = domain.single_bytes.clamp(1, 4);
        let (bytes, _) = self.take(count)?;
        let mut value: u32 = 0;
        for byte in bytes.iter().take(count) {
            value = (value << DATA_BITS) | u32::from(*byte);
        }
        Some((value, DATA_BITS.saturating_mul(u32::try_from(count).unwrap_or(4))))
    }

    /// A multi-value coordinate operand as a unit-screen point (Z ignored).
    pub fn point(&mut self, domain: Domain) -> Option<Point> {
        let count = domain.multi_bytes.clamp(1, 8);
        let (bytes, _) = self.take(count)?;
        let per_byte: u32 = if domain.three_d { 2 } else { 3 };
        let mut x: i64 = 0;
        let mut y: i64 = 0;
        for byte in bytes.iter().take(count) {
            let byte = u32::from(*byte);
            let (bx, by) = if domain.three_d {
                ((byte >> 4) & 0b11, (byte >> 2) & 0b11)
            } else {
                ((byte >> 3) & 0b111, byte & 0b111)
            };
            x = (x << per_byte) | i64::from(bx);
            y = (y << per_byte) | i64::from(by);
        }
        let bits = per_byte.saturating_mul(u32::try_from(count).unwrap_or(8));
        Some(Point::new(signed_fraction(x, bits), signed_fraction(y, bits)))
    }

    /// A multi-value colour operand: green, red and blue as 8-bit intensities (each primary
    /// gets two bits per byte, G R B G R B from b6 to b1; section 5.3.2.5.1).
    pub fn colour(&mut self, domain: Domain) -> Option<[u8; 3]> {
        let count = domain.multi_bytes.clamp(1, 8);
        let (bytes, _) = self.take(count)?;
        let mut green: u32 = 0;
        let mut red: u32 = 0;
        let mut blue: u32 = 0;
        for byte in bytes.iter().take(count) {
            let byte = u32::from(*byte);
            green = (green << 2) | (((byte >> 5) & 1) << 1) | ((byte >> 2) & 1);
            red = (red << 2) | (((byte >> 4) & 1) << 1) | ((byte >> 1) & 1);
            blue = (blue << 2) | (((byte >> 3) & 1) << 1) | (byte & 1);
        }
        let bits = 2u32.saturating_mul(u32::try_from(count).unwrap_or(8));
        Some([to_eight_bits(red, bits), to_eight_bits(green, bits), to_eight_bits(blue, bits)])
    }
}

/// A two's complement number of `bits` bits, read as a fraction with one sign bit, to a [`Unit`].
#[allow(
    clippy::arithmetic_side_effects,
    reason = "bit assembly of at most 8 six-bit bytes: shifts below 64 and values within i64"
)]
fn signed_fraction(raw: i64, bits: u32) -> Unit {
    if bits == 0 {
        return 0;
    }
    let sign_bit = 1i64 << (bits - 1);
    let value = if raw & sign_bit != 0 { raw - (1i64 << bits) } else { raw };
    // The magnitude has bits - 1 fractional bits.
    let fractional = bits - 1;
    let shifted = if fractional <= FRACTION_BITS {
        value << (FRACTION_BITS - fractional)
    } else {
        value >> (fractional - FRACTION_BITS)
    };
    Unit::try_from(shifted).unwrap_or(if shifted < 0 { Unit::MIN } else { Unit::MAX })
}

/// An unsigned fraction of `bits` bits as an 8-bit intensity, the most significant bits kept and
/// short values padded with zero bits (section 5.3.2.5.1); all ones stays all ones.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "bit assembly of at most 8 six-bit bytes: shifts below 64 and values within i64"
)]
fn to_eight_bits(value: u32, bits: u32) -> u8 {
    if bits == 0 {
        return 0;
    }
    let all_ones = (1u32 << bits) - 1;
    if value == all_ones {
        return u8::MAX;
    }
    let scaled = if bits >= 8 { value >> (bits - 8) } else { value << (8 - bits) };
    u8::try_from(scaled & 0xFF).unwrap_or(u8::MAX)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::fixed::{ONE, fraction};

    #[test]
    fn domain_byte() {
        assert_eq!(Domain::from_byte(0x48), Domain { single_bytes: 1, multi_bytes: 3, three_d: false });
        assert_eq!(Domain::from_byte(0x40 | 0b10_0111), Domain { single_bytes: 4, multi_bytes: 2, three_d: true });
    }

    #[test]
    fn two_d_points() {
        // x = 010 000 000 (one half), y = 001 000 000 (one quarter): the first byte carries the
        // top three bits of each.
        let bytes = [0x40 | 0b010_001, 0x40, 0x40];
        let mut reader = Reader::new(&bytes);
        assert_eq!(reader.point(Domain::default()), Some(Point::new(ONE / 2, ONE / 4)));
        assert!(reader.is_empty());
        // Negative: x = 1 1111 1111 = -1/256.
        let bytes = [0x40 | 0b111_000, 0x40 | 0b111_000, 0x40 | 0b111_000];
        assert_eq!(Reader::new(&bytes).point(Domain::default()), Some(Point::new(-fraction(1, 256), 0)));
        // A short operand is padded with zero bits.
        let bytes = [0x40 | 0b001_000];
        assert_eq!(Reader::new(&bytes).point(Domain::default()), Some(Point::new(fraction(1, 4), 0)));
    }

    #[test]
    fn single_values_and_colours() {
        let bytes = [0x40 | 0x07];
        assert_eq!(Reader::new(&bytes).single(Domain::default()), Some((7, 6)));
        // All ones: white.
        let bytes = [0x7F, 0x7F, 0x7F];
        assert_eq!(Reader::new(&bytes).colour(Domain::default()), Some([255, 255, 255]));
        // Only green's top bit: G R B G R B = 1 0 0 0 0 0.
        let bytes = [0x40 | 0b100_000];
        assert_eq!(Reader::new(&bytes).colour(Domain::default()), Some([0, 128, 0]));
    }
}
