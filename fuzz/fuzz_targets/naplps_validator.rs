//! The fuzz target `naplps_validator` (renderer parity PAR-15, REQ-6765): any bytes, in any
//! pieces, read by a `Validator` and drawn by a `Terminal` give the same events and the same
//! `Diagnostics` after every piece and after the stream ends. The terminal draws as the
//! receiver does, with the repository's stroke font and a joined teletext set, and the
//! validator holds none of them, so that what the check reports never depends on what drawing
//! needs.
//!
//! This file holds the target's body, `naplps_validator`, which takes the fuzzer's bytes: the
//! first says how the rest is divided, and the rest is the stream. `crates/naplps-fuzz` runs it.

use naplps::{BitmapSet, Canvas, JoinForm, JoiningType, StrokeFont, Terminal, Validator};

/// The picture drawn on: small, so that an input is quick.
const WIDTH: u32 = 160;
/// See [`WIDTH`].
const HEIGHT: u32 = 120;
/// The colour map's bits: 16 entries, as the sample pages use.
const PALETTE_BITS: u32 = 4;
/// The most bytes of one piece, less one: pieces of 1 to 64 bytes.
const PIECE_SPAN: u8 = 64;
/// The set given joining data: `G0-Arabic-Persian`, the first of the plain Arabic-script sets.
const JOINED_SET: u8 = 44;

/// A set of 12 by 20 glyphs whose codes take every joining type in turn, each form lit
/// differently, so that joining changes what is drawn.
fn joined_set() -> Option<BitmapSet> {
    let mut set = BitmapSet::new(12, 20).ok()?;
    let types = [JoiningType::Dual, JoiningType::Right, JoiningType::None, JoiningType::Transparent];
    for (code, joining) in (0x20u8..=0x7F).zip(types.iter().cycle()) {
        let mut rows = [0u16; 20];
        *rows.get_mut(usize::from(code % 20))? = 0x0FFF;
        set.set_glyph(code, &rows).ok()?;
        set.set_joining(code, *joining).ok()?;
        for (form, row) in [(JoinForm::Final, 1u16), (JoinForm::Initial, 2), (JoinForm::Medial, 3)] {
            let mut rows = [0u16; 20];
            *rows.get_mut(usize::from(row))? = 0x0FFF;
            set.set_form_glyph(code, form, &rows).ok()?;
        }
    }
    Some(set)
}

/// Runs one input. Panics when a property fails, as a fuzzing engine expects.
///
/// # Panics
///
/// When the validator's events or diagnostics differ from the terminal's after any piece or at
/// the end.
pub fn naplps_validator(data: &[u8]) {
    let Some((seed, stream)) = data.split_first() else { return };
    let Ok(mut canvas) = Canvas::new(WIDTH, HEIGHT) else { return };
    let mut terminal = Terminal::new(PALETTE_BITS);
    if let Ok(font) = StrokeFont::parse(naplps_fonts::NEOTELETEXT) {
        terminal.set_font(font);
    }
    if let Some(set) = joined_set() {
        let _ = terminal.set_teletext_set(JOINED_SET, set);
    }
    let mut validator = Validator::new();
    let mut rest = stream;
    let mut chooser = *seed;
    while !rest.is_empty() {
        let length = usize::from(chooser % PIECE_SPAN).saturating_add(1).min(rest.len());
        let (piece, more) = rest.split_at(length);
        rest = more;
        chooser = chooser.wrapping_mul(31).wrapping_add(piece.last().copied().unwrap_or(0));
        let drawn = terminal.feed(&mut canvas, piece);
        let read = validator.feed(piece);
        assert_eq!(read, drawn, "the validator's events differ from the terminal's");
        assert_eq!(
            *validator.diagnostics(),
            terminal.diagnostics(),
            "the validator's diagnostics differ from the terminal's"
        );
    }
    assert_eq!(validator.finish(), terminal.finish(&mut canvas), "the events at the end differ");
    assert_eq!(*validator.diagnostics(), terminal.diagnostics(), "the diagnostics at the end differ");
}
