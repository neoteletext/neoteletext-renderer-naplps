//! Bitmap character sets, supplied as data (REQ-6668, DEC-5768): the glyphs of a NeoTeletext
//! character set, one for each of the 96 codes 2/0 to 7/15, drawn scaled into the character
//! field as a DRCS character's bitmap is (ANSI X3.110-1983 section 5.6). The library contains
//! none; the caller makes them from the project's own Noto Teletext fonts (DEC-6669).
//!
//! A set may also carry joining data (renderer parity PAR-14, REQ-6765; the engine's REQ-CHR-015):
//! for each code a [`JoiningType`] and the glyphs of its final, initial and medial forms, which
//! the caller gives for the plain Arabic-script sets 44 to 51 (group 1001) from the engine's
//! joining table. The renderer then draws each letter of a run of the set in the form its
//! neighbours give it; a set without joining data draws every code as its own glyph.

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

/// How a letter joins its neighbours: Unicode's joining types (`ArabicShaping.txt`) as the
/// engine's REQ-CHR-015 uses them. The engine's join-causing type (the tatweel) joins exactly as
/// a dual-joining letter does under that rule, so a caller gives it as [`JoiningType::Dual`].
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum JoiningType {
    /// Joins neither neighbour: every code of a set without joining data.
    #[default]
    None,
    /// Joins only the letter before it in reading order.
    Right,
    /// Joins the letters on both sides.
    Dual,
    /// Takes no part in joining and keeps its own glyph (a combining mark): the letters on either
    /// side of it join as if it were not there.
    Transparent,
}

impl JoiningType {
    /// Whether a letter of this type can join the letter before it in reading order.
    #[must_use]
    pub const fn joins_previous(self) -> bool {
        matches!(self, Self::Right | Self::Dual)
    }

    /// Whether a letter of this type can join the letter after it in reading order.
    #[must_use]
    pub const fn joins_next(self) -> bool {
        matches!(self, Self::Dual)
    }
}

/// The form a joined letter is drawn in (REQ-CHR-015).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum JoinForm {
    /// Joining neither neighbour: the set's own glyph.
    #[default]
    Isolated,
    /// Joining only the letter before it in reading order.
    Final,
    /// Joining only the letter after it in reading order.
    Initial,
    /// Joining both.
    Medial,
}

impl JoinForm {
    /// The form of a letter that joins the letter before it in reading order or not, and the
    /// letter after it or not.
    #[must_use]
    pub const fn of(joins_previous: bool, joins_next: bool) -> Self {
        match (joins_previous, joins_next) {
            (false, false) => Self::Isolated,
            (true, false) => Self::Final,
            (false, true) => Self::Initial,
            (true, true) => Self::Medial,
        }
    }

    /// Where the form's glyphs are kept among the further forms: `None` for the isolated form,
    /// which is the set's own glyph.
    const fn further_index(self) -> Option<usize> {
        match self {
            Self::Isolated => None,
            Self::Final => Some(0),
            Self::Initial => Some(1),
            Self::Medial => Some(2),
        }
    }
}

/// The forms a letter has besides its isolated one: final, initial and medial.
const FURTHER_FORMS: usize = 3;

/// One character set's glyphs, each `width` pixels wide and `height` high. A glyph is its rows
/// from the top, each a bit field whose most significant of `width` bits is the leftmost pixel,
/// as the engine's glyph table and BDF files hold them. A code never given a glyph is blank.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BitmapSet {
    width: u8,
    height: u8,
    /// `height` rows for each code in turn.
    rows: Vec<u16>,
    /// Each code's joining type; empty until the caller gives one, so that a set without
    /// joining data holds nothing for it.
    joining: Vec<JoiningType>,
    /// The final, initial and medial forms' rows, `height` rows for each form of each code in
    /// turn; empty until the caller gives one.
    forms: Vec<u16>,
    /// Which of `forms` the caller gave: a form not given draws the code's own glyph.
    forms_given: Vec<bool>,
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
        Ok(Self {
            width,
            height,
            rows: vec![0; BITMAP_SET_CODES.saturating_mul(usize::from(height))],
            joining: Vec::new(),
            forms: Vec::new(),
            forms_given: Vec::new(),
        })
    }

    /// Gives `code` (2/0 to 7/15) its glyph: `height` rows from the top.
    ///
    /// # Errors
    ///
    /// [`Error::Bitmap`] when the code is outside the set, the rows are not `height`, or a row
    /// has a bit set beyond the glyph's width; the set is unchanged then.
    pub fn set_glyph(&mut self, code: u8, rows: &[u16]) -> Result<(), Error> {
        let start = self.start(code).ok_or(Error::Bitmap)?;
        self.check_rows(rows)?;
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

    /// Gives `code` (2/0 to 7/15) its joining type (PAR-14). A set given any type other than
    /// [`JoiningType::None`] is joined: the renderer draws its letters in their joined forms.
    ///
    /// # Errors
    ///
    /// [`Error::Bitmap`] when the code is outside the set; the set is unchanged then.
    pub fn set_joining(&mut self, code: u8, joining: JoiningType) -> Result<(), Error> {
        let index = code_index(code).ok_or(Error::Bitmap)?;
        if self.joining.is_empty() {
            if joining == JoiningType::None {
                return Ok(());
            }
            self.joining = vec![JoiningType::None; BITMAP_SET_CODES];
        }
        *self.joining.get_mut(index).ok_or(Error::Bitmap)? = joining;
        Ok(())
    }

    /// The joining type of `code`: [`JoiningType::None`] for a code never given one and outside
    /// 2/0 to 7/15.
    #[must_use]
    pub fn joining(&self, code: u8) -> JoiningType {
        code_index(code).and_then(|index| self.joining.get(index).copied()).unwrap_or_default()
    }

    /// Whether any code of the set joins: whether the renderer joins its letters (PAR-14).
    #[must_use]
    pub fn is_joined(&self) -> bool {
        self.joining.iter().any(|joining| *joining != JoiningType::None)
    }

    /// Gives `code` (2/0 to 7/15) the glyph of one of its forms, `height` rows from the top;
    /// the isolated form is the code's own glyph, as [`BitmapSet::set_glyph`] gives.
    ///
    /// # Errors
    ///
    /// [`Error::Bitmap`] as for [`BitmapSet::set_glyph`]; the set is unchanged then.
    pub fn set_form_glyph(&mut self, code: u8, form: JoinForm, rows: &[u16]) -> Result<(), Error> {
        let Some(further) = form.further_index() else { return self.set_glyph(code, rows) };
        let index = code_index(code).ok_or(Error::Bitmap)?;
        self.check_rows(rows)?;
        let slot = index.checked_mul(FURTHER_FORMS).and_then(|base| base.checked_add(further)).ok_or(Error::Bitmap)?;
        let height = usize::from(self.height);
        if self.forms.is_empty() {
            self.forms = vec![0; BITMAP_SET_CODES.saturating_mul(FURTHER_FORMS).saturating_mul(height)];
            self.forms_given = vec![false; BITMAP_SET_CODES.saturating_mul(FURTHER_FORMS)];
        }
        let start = slot.checked_mul(height).ok_or(Error::Bitmap)?;
        let end = start.checked_add(height).ok_or(Error::Bitmap)?;
        self.forms.get_mut(start..end).ok_or(Error::Bitmap)?.copy_from_slice(rows);
        *self.forms_given.get_mut(slot).ok_or(Error::Bitmap)? = true;
        Ok(())
    }

    /// The glyph of `code` in `form`, its rows from the top: the form's own glyph when the
    /// caller gave one, otherwise the code's glyph (a letter with no such form, such as the
    /// tatweel, looks the same in every form); `None` outside 2/0 to 7/15.
    #[must_use]
    pub fn form_glyph(&self, code: u8, form: JoinForm) -> Option<&[u16]> {
        let given = form.further_index().and_then(|further| {
            let slot = code_index(code)?.checked_mul(FURTHER_FORMS)?.checked_add(further)?;
            if !self.forms_given.get(slot).copied().unwrap_or(false) {
                return None;
            }
            let start = slot.checked_mul(usize::from(self.height))?;
            self.forms.get(start..start.checked_add(usize::from(self.height))?)
        });
        given.or_else(|| self.glyph(code))
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
        code_index(code)?.checked_mul(usize::from(self.height))
    }

    /// Whether `rows` are one glyph of this set: `height` rows with no bit beyond `width`.
    fn check_rows(&self, rows: &[u16]) -> Result<(), Error> {
        let outside = u16::MAX.checked_shl(u32::from(self.width)).unwrap_or(0);
        if rows.len() != usize::from(self.height) || rows.iter().any(|row| row & outside != 0) {
            return Err(Error::Bitmap);
        }
        Ok(())
    }
}

/// The place of `code` among the set's codes; `None` outside 2/0 to 7/15.
fn code_index(code: u8) -> Option<usize> {
    if !(FIRST_CODE..=LAST_CODE).contains(&code) {
        return None;
    }
    Some(usize::from(code.checked_sub(FIRST_CODE)?))
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

    #[test]
    fn joining_data_is_kept_per_code_and_a_missing_form_is_the_own_glyph() {
        let mut set = BitmapSet::new(12, 2).unwrap();
        assert!(!set.is_joined());
        set.set_joining(0x41, JoiningType::None).unwrap();
        assert!(!set.is_joined(), "a type of none makes no set joined");
        set.set_glyph(0x41, &[1, 1]).unwrap();
        set.set_joining(0x41, JoiningType::Dual).unwrap();
        set.set_form_glyph(0x41, JoinForm::Medial, &[2, 2]).unwrap();
        assert!(set.is_joined());
        assert_eq!(set.joining(0x41), JoiningType::Dual);
        assert_eq!(set.joining(0x42), JoiningType::None);
        assert_eq!(set.form_glyph(0x41, JoinForm::Medial), Some(&[2, 2][..]));
        assert_eq!(set.form_glyph(0x41, JoinForm::Final), Some(&[1, 1][..]), "no final form given");
        assert_eq!(set.form_glyph(0x41, JoinForm::Isolated), Some(&[1, 1][..]));
        set.set_form_glyph(0x41, JoinForm::Isolated, &[3, 3]).unwrap();
        assert_eq!(set.glyph(0x41), Some(&[3, 3][..]), "the isolated form is the set's own glyph");
        assert_eq!(set.set_joining(0x80, JoiningType::Dual), Err(Error::Bitmap));
        assert_eq!(set.set_form_glyph(0x1F, JoinForm::Final, &[0, 0]), Err(Error::Bitmap));
        assert_eq!(set.set_form_glyph(0x41, JoinForm::Final, &[0x1000, 0]), Err(Error::Bitmap));
        assert_eq!(set.form_glyph(0x80, JoinForm::Final), None);
    }

    #[test]
    fn forms_follow_the_rule_of_req_chr_015() {
        assert_eq!(JoinForm::of(false, false), JoinForm::Isolated);
        assert_eq!(JoinForm::of(true, false), JoinForm::Final);
        assert_eq!(JoinForm::of(false, true), JoinForm::Initial);
        assert_eq!(JoinForm::of(true, true), JoinForm::Medial);
        assert!(JoiningType::Right.joins_previous() && !JoiningType::Right.joins_next());
        assert!(JoiningType::Dual.joins_previous() && JoiningType::Dual.joins_next());
        assert!(!JoiningType::None.joins_previous() && !JoiningType::Transparent.joins_next());
    }
}
