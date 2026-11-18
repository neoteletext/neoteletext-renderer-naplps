//! Stroke fonts, supplied as data (decision D5): ANSI X3.110-1983 section 5.3.2.3.9 leaves the
//! font to the implementation, and the library contains none.
//!
//! A glyph is a list of line segments on a grid 7 wide and 10 high (x 0 to 6, y 0 to 9, y
//! upward), the layout of the Microstar fonts recovered from PP3 and MGE, plus two metric bytes
//! kept as found. The text form, one glyph per line:
//!
//! ```text
//! # comment
//! [primary]            or [supplementary]
//! 21 1 3 3,2,3,2 3,4,3,8
//! ```
//!
//! that is: the code in hexadecimal (21 to 7e), the two metric bytes, then each segment as
//! `x1,y1,x2,y2`.

use alloc::vec;
use alloc::vec::Vec;

use crate::Error;
use crate::limits::MAX_STROKE_FONT_BYTES;

/// Grid columns: x runs 0 to 6.
pub const GRID_WIDTH: u8 = 7;
/// Grid rows: y runs 0 to 9.
pub const GRID_HEIGHT: u8 = 10;
/// Segments one glyph may have.
pub const MAX_SEGMENTS: usize = 64;
/// Positions in a 94-character set: 2/1 to 7/14.
const POSITIONS: usize = 94;
/// The first position's code.
const FIRST_CODE: u8 = 0x21;

/// One glyph.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Glyph {
    /// Line segments, `[x1, y1, x2, y2]`; equal ends make a dot.
    pub segments: Vec<[u8; 4]>,
    /// The first metric byte, as found in the source font.
    pub left: u8,
    /// The second metric byte, as found in the source font.
    pub width: u8,
}

/// Which character set a glyph belongs to.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FontSet {
    /// The primary set (ASCII positions).
    Primary,
    /// The supplementary set.
    Supplementary,
}

/// A stroke font for the primary and supplementary sets.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct StrokeFont {
    primary: Vec<Option<Glyph>>,
    supplementary: Vec<Option<Glyph>>,
}

impl Default for StrokeFont {
    fn default() -> Self {
        Self { primary: vec![None; POSITIONS], supplementary: vec![None; POSITIONS] }
    }
}

impl StrokeFont {
    /// The glyph for a code of a set, if the font has one.
    #[must_use]
    pub fn glyph(&self, set: FontSet, code: u8) -> Option<&Glyph> {
        let index = usize::from(code.checked_sub(FIRST_CODE)?);
        let table = match set {
            FontSet::Primary => &self.primary,
            FontSet::Supplementary => &self.supplementary,
        };
        table.get(index)?.as_ref()
    }

    /// Reads the text form.
    ///
    /// # Errors
    ///
    /// [`Error::Font`] naming the line of the first fault, or line 0 when the text is longer than
    /// [`MAX_STROKE_FONT_BYTES`].
    pub fn parse(text: &str) -> Result<Self, Error> {
        if text.len() > MAX_STROKE_FONT_BYTES {
            return Err(Error::Font(0));
        }
        let mut font = Self::default();
        let mut set = None;
        for (number, line) in text.lines().enumerate() {
            let fault = Error::Font(number.saturating_add(1));
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            match line {
                "[primary]" => set = Some(FontSet::Primary),
                "[supplementary]" => set = Some(FontSet::Supplementary),
                _ => {
                    let set = set.ok_or(fault)?;
                    let mut fields = line.split_ascii_whitespace();
                    let code = fields.next().and_then(|field| u8::from_str_radix(field, 16).ok()).ok_or(fault)?;
                    let index = usize::from(code.checked_sub(FIRST_CODE).ok_or(fault)?);
                    let left = fields.next().and_then(|field| field.parse().ok()).ok_or(fault)?;
                    let width = fields.next().and_then(|field| field.parse().ok()).ok_or(fault)?;
                    let mut segments = Vec::new();
                    for field in fields {
                        if segments.len() >= MAX_SEGMENTS {
                            return Err(fault);
                        }
                        let mut values = field.split(',').map(str::parse::<u8>);
                        let mut segment = [0u8; 4];
                        for (slot, limit) in segment.iter_mut().zip([GRID_WIDTH, GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT])
                        {
                            let value = values.next().and_then(Result::ok).ok_or(fault)?;
                            if value >= limit {
                                return Err(fault);
                            }
                            *slot = value;
                        }
                        if values.next().is_some() {
                            return Err(fault);
                        }
                        segments.push(segment);
                    }
                    let table = match set {
                        FontSet::Primary => &mut font.primary,
                        FontSet::Supplementary => &mut font.supplementary,
                    };
                    let slot = table.get_mut(index).ok_or(fault)?;
                    *slot = Some(Glyph { segments, left, width });
                }
            }
        }
        Ok(font)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_and_refuses() {
        let font = StrokeFont::parse("# test\n[primary]\n21 1 3 3,2,3,2 3,4,3,8\n[supplementary]\n7e 0 6\n").unwrap();
        assert_eq!(font.glyph(FontSet::Primary, 0x21).unwrap().segments, vec![[3, 2, 3, 2], [3, 4, 3, 8]]);
        assert_eq!(font.glyph(FontSet::Supplementary, 0x7E).unwrap().segments.len(), 0);
        assert!(font.glyph(FontSet::Primary, 0x22).is_none());
        assert_eq!(StrokeFont::parse("21 1 3 3,2,3,2"), Err(Error::Font(1)));
        assert_eq!(StrokeFont::parse("[primary]\n21 1 3 7,2,3,2"), Err(Error::Font(2)));
        assert_eq!(StrokeFont::parse("[primary]\n80 1 3"), Err(Error::Font(2)));
        assert_eq!(StrokeFont::parse("[primary]\n21 1 3 1,2,3"), Err(Error::Font(2)));
    }

    #[test]
    fn a_font_longer_than_the_bound_is_refused() {
        let at_bound = "#".repeat(MAX_STROKE_FONT_BYTES);
        assert!(StrokeFont::parse(&at_bound).is_ok(), "a comment as long as the bound is read");
        let past = "#".repeat(MAX_STROKE_FONT_BYTES + 1);
        assert_eq!(StrokeFont::parse(&past), Err(Error::Font(0)));
    }
}
