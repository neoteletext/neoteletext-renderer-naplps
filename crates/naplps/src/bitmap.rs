//! Bitmap character sets, supplied as data (REQ-6668, DEC-5768): the glyphs of a NeoTeletext
//! character set, one for each of the 96 codes 2/0 to 7/15, drawn scaled into the character
//! field as a DRCS character's bitmap is (ANSI X3.110-1983 section 5.6). The library contains
//! none; the caller makes them from the project's own Noto Teletext fonts (DEC-6669).

use alloc::vec;
use alloc::vec::Vec;

use crate::Error;
use crate::limits::{MAX_BITMAP_HEIGHT, MAX_BITMAP_WIDTH};

/// The first code of a set: 2/0.
const FIRST_CODE: u8 = 0x20;
/// The last code of a set: 7/15.
const LAST_CODE: u8 = 0x7F;
/// Codes in a set: 2/0 to 7/15, as every teletext set has (the engine's `SET_POSITIONS`).
pub const BITMAP_SET_CODES: usize = (LAST_CODE - FIRST_CODE + 1) as usize;

/// One character set's glyphs, each `width` pixels wide and `height` high. A glyph is its rows
/// from the top, each a bit field whose most significant of `width` bits is the leftmost pixel,
/// as the engine's glyph table and BDF files hold them. A code never given a glyph is blank.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BitmapSet {
    width: u8,
    height: u8,
    /// `height` rows for each code in turn.
    rows: Vec<u16>,
}

impl BitmapSet {
    /// A set of blank glyphs.
    ///
    /// # Errors
    ///
    /// [`Error::Bitmap`] when `width` is not 1 to [`MAX_BITMAP_WIDTH`] or `height` not 1 to
    /// [`MAX_BITMAP_HEIGHT`].
    pub fn new(width: u8, height: u8) -> Result<Self, Error> {
        if !(1..=MAX_BITMAP_WIDTH).contains(&width) || !(1..=MAX_BITMAP_HEIGHT).contains(&height) {
            return Err(Error::Bitmap);
        }
        Ok(Self { width, height, rows: vec![0; BITMAP_SET_CODES.saturating_mul(usize::from(height))] })
    }

    /// Gives `code` (2/0 to 7/15) its glyph: `height` rows from the top.
    ///
    /// # Errors
    ///
    /// [`Error::Bitmap`] when the code is outside the set, the rows are not `height`, or a row
    /// has a bit set beyond the glyph's width; the set is unchanged then.
    pub fn set_glyph(&mut self, code: u8, rows: &[u16]) -> Result<(), Error> {
        let start = self.start(code).ok_or(Error::Bitmap)?;
        let outside = u16::MAX.checked_shl(u32::from(self.width)).unwrap_or(0);
        if rows.len() != usize::from(self.height) || rows.iter().any(|row| row & outside != 0) {
            return Err(Error::Bitmap);
        }
        let end = start.checked_add(rows.len()).ok_or(Error::Bitmap)?;
        self.rows.get_mut(start..end).ok_or(Error::Bitmap)?.copy_from_slice(rows);
        Ok(())
    }

    /// The glyph of `code`, its rows from the top; `None` outside 2/0 to 7/15.
    #[must_use]
    pub fn glyph(&self, code: u8) -> Option<&[u16]> {
        let start = self.start(code)?;
        self.rows.get(start..start.checked_add(usize::from(self.height))?)
    }

    /// The glyphs' width in pixels.
    #[must_use]
    pub fn width(&self) -> u8 {
        self.width
    }

    /// The glyphs' height in pixels.
    #[must_use]
    pub fn height(&self) -> u8 {
        self.height
    }

    fn start(&self, code: u8) -> Option<usize> {
        if !(FIRST_CODE..=LAST_CODE).contains(&code) {
            return None;
        }
        usize::from(code.checked_sub(FIRST_CODE)?).checked_mul(usize::from(self.height))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn glyphs_are_bounded() {
        assert_eq!(BitmapSet::new(0, 20), Err(Error::Bitmap));
        assert_eq!(BitmapSet::new(MAX_BITMAP_WIDTH + 1, 20), Err(Error::Bitmap));
        assert_eq!(BitmapSet::new(12, MAX_BITMAP_HEIGHT + 1), Err(Error::Bitmap));
        let mut set = BitmapSet::new(12, 2).unwrap();
        assert_eq!(set.set_glyph(0x1F, &[0, 0]), Err(Error::Bitmap));
        assert_eq!(set.set_glyph(0x80, &[0, 0]), Err(Error::Bitmap));
        assert_eq!(set.set_glyph(0x41, &[0]), Err(Error::Bitmap));
        assert_eq!(set.set_glyph(0x41, &[0x1000, 0]), Err(Error::Bitmap), "a bit beyond 12 columns");
        set.set_glyph(0x7F, &[0x800, 0x001]).unwrap();
        assert_eq!(set.glyph(0x7F), Some(&[0x800, 0x001][..]));
        assert_eq!(set.glyph(0x20), Some(&[0, 0][..]));
    }
}
