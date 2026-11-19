//! The fuzz target `naplps_validator` (renderer parity PAR-15, REQ-6765): any bytes, divided into
//! any pieces, read by a `Validator` and drawn by a `Terminal` give the same events after every
//! piece and at the end, the same `Diagnostics` (every count and first offset: the bytes passed
//! over, each kind of refusal, and the characters written over in colour mode 2) after every
//! piece and at the end, the same defined macros at the end, the same pixel work spent after
//! every piece, never more than the allowance of the bytes fed (TODO-6844), and the same memory
//! held after every piece and at the end (`held_bytes`, TODO-6854), once each is counted
//! without the font and the sets it was given and the validator without its surface, and never
//! more than `MAX_HELD_BYTES`. The terminal
//! draws as the receiver does: on the receiver's canvas, the display area of 480 by 460
//! (REQ-5819, DEC-6857), and on PP3's 640 by 480, with the repository's stroke font and all 55 provided character
//! sets, the plain Arabic-script ones with joining data (PAR-14). The validator is made for the
//! terminal's canvas and given the stroke font and the joined sets, since a drawing's pixel
//! work depends on them (TODO-6844); it holds no other set, so that what the server's check
//! reports never depends on them.
//!
//! This file holds the target's body, `naplps_validator`, which takes the fuzzer's bytes, and
//! `naplps_validator_in_pieces`, which takes a stream and its division. The bytes are: one byte,
//! the number of pieces given; that many piece lengths of two bytes each, least significant
//! first; and the stream. A length past what is left of the stream takes the rest, a length of
//! zero is an empty feed, and what the lengths leave is fed as one last piece.
//! `crates/naplps-fuzz` runs it.

use std::sync::{Arc, OnceLock};

use naplps::limits::{MAX_HELD_BYTES, RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_WIDTH, WORK_CAP, WORK_PER_BYTE};
use naplps::{BitmapSet, Canvas, JoinForm, JoiningType, StrokeFont, TELETEXT_SET_COUNT, Terminal, Validator};

/// The canvases each stream is drawn on: the receiver's, and PP3's 640 by 480, a canvas of
/// another size showing the same display area (RAS-3).
const CANVASES: [(u32, u32); 2] = [(RECEIVER_CANVAS_WIDTH, RECEIVER_CANVAS_HEIGHT), (640, 480)];
/// The colour map's bits: 16 entries, as the sample pages use and the validator keeps.
const PALETTE_BITS: u32 = 4;
/// The bytes of one piece length in the target's input.
pub const LENGTH_BYTES: usize = 2;
/// The plain Arabic-script sets, group 1001 (`G0-Arabic-Persian` to `G0-Arabic-Plain`), which
/// the receiver gives joining data (PAR-14; `naplps-render`'s `JOINED_SETS`).
const JOINED_SETS: core::ops::RangeInclusive<usize> = 44..=51;
/// The engine's cell: 12 pixels by 20 lines, the size of every provided set's glyphs.
const CELL_WIDTH: u8 = 12;
/// See [`CELL_WIDTH`].
const CELL_HEIGHT: usize = 20;
/// A row of a glyph with all of its 12 pixels lit.
const FULL_ROW: u16 = 0x0FFF;
/// The graphic codes of a set: 2/0 to 7/15.
const GRAPHIC_CODES: core::ops::RangeInclusive<u8> = 0x20..=0x7F;

/// A glyph of one lit row, `row` counted from the top modulo the cell's height.
fn one_row(row: usize) -> [u16; CELL_HEIGHT] {
    let mut rows = [0u16; CELL_HEIGHT];
    if let Some(slot) = rows.get_mut(row % CELL_HEIGHT) {
        *slot = FULL_ROW;
    }
    rows
}

/// Stand-ins for the 55 provided sets, made once: a set of 12 by 20 glyphs for each number, each
/// code lit on its own row; the plain Arabic-script sets also give every code a joining type,
/// in a cycle that starts at a different type in each set, and a glyph for each joined form.
/// The real glyphs come from the engine's checkout, which this crate does not read; what the
/// receiver's reading does with a set depends only on whether it is given and on its joining
/// data, never on its pixels.
/// They are shared, as a receiver's and a server's are (TODO-6895), so that what a terminal or
/// validator counts is its own.
fn provided_sets() -> &'static [Option<Arc<BitmapSet>>] {
    static SETS: OnceLock<Vec<Option<Arc<BitmapSet>>>> = OnceLock::new();
    SETS.get_or_init(|| (0..TELETEXT_SET_COUNT).map(|number| provided_set(number).map(Arc::new)).collect())
}

/// The receiver's stroke font, shared as the sets are.
fn stroke_font() -> Option<Arc<StrokeFont>> {
    static FONT: OnceLock<Option<Arc<StrokeFont>>> = OnceLock::new();
    FONT.get_or_init(|| StrokeFont::parse(naplps_fonts::NEOTELETEXT).ok().map(Arc::new)).clone()
}

fn provided_set(number: usize) -> Option<BitmapSet> {
    let mut set = BitmapSet::new(CELL_WIDTH, u8::try_from(CELL_HEIGHT).ok()?).ok()?;
    let types = [JoiningType::Dual, JoiningType::Right, JoiningType::None, JoiningType::Transparent];
    let joined = JOINED_SETS.contains(&number);
    for (code, joining) in GRAPHIC_CODES.zip(types.iter().cycle().skip(number % types.len())) {
        set.set_glyph(code, &one_row(usize::from(code))).ok()?;
        if joined {
            set.set_joining(code, *joining).ok()?;
            for (form, row) in [(JoinForm::Final, 1), (JoinForm::Initial, 2), (JoinForm::Medial, 3)] {
                set.set_form_glyph(code, form, &one_row(row)).ok()?;
            }
        }
    }
    Some(set)
}

/// A terminal as the receiver has it: the stroke font and every provided set.
fn receiver() -> Terminal {
    let mut terminal = Terminal::new(PALETTE_BITS);
    if let Some(font) = stroke_font() {
        terminal.set_font(font);
    }
    for (number, set) in provided_sets().iter().enumerate() {
        if let (Ok(number), Some(set)) = (u8::try_from(number), set) {
            let _ = terminal.set_teletext_set(number, Arc::clone(set));
        }
    }
    terminal
}

/// What a terminal and a validator hold of their own, each without what it was given and the
/// validator without its surface's structure, which must be equal (TODO-6854).
fn own_held(terminal: &Terminal, validator: &Validator) -> (usize, usize) {
    // The font and the sets are shared, so neither counts them (TODO-6895); but the terminal is
    // given every set and the validator the joined ones, and both then hold the sets' slots.
    let surface = size_of::<Validator>().saturating_sub(size_of::<Terminal>());
    (terminal.held_bytes(), validator.held_bytes().saturating_sub(surface))
}

/// Runs one input of the fuzzer's bytes. Panics when a property fails, as a fuzzing engine
/// expects.
///
/// # Panics
///
/// As [`naplps_validator_in_pieces`].
pub fn naplps_validator(data: &[u8]) {
    let Some((&count, rest)) = data.split_first() else { return };
    let (lengths, stream) = rest.split_at(usize::from(count).saturating_mul(LENGTH_BYTES).min(rest.len()));
    let lengths: Vec<usize> =
        lengths.as_chunks::<LENGTH_BYTES>().0.iter().map(|pair| usize::from(u16::from_le_bytes(*pair))).collect();
    naplps_validator_in_pieces(stream, &lengths);
}

/// Feeds `stream` divided by `lengths` (see the module's text) to a validator and to a receiver's
/// terminal on each of [`CANVASES`].
///
/// # Panics
///
/// When the validator's events, diagnostics, pixel work or memory held differ from a terminal's
/// after any piece or at the end, the validator holds more than `MAX_HELD_BYTES` besides what
/// it was given, the terminal's work passes the allowance of the bytes fed, or the
/// defined macros differ at the end.
pub fn naplps_validator_in_pieces(stream: &[u8], lengths: &[usize]) {
    let mut pieces = Vec::with_capacity(lengths.len().saturating_add(1));
    let mut rest = stream;
    for &length in lengths {
        let (piece, more) = rest.split_at(length.min(rest.len()));
        pieces.push(piece);
        rest = more;
    }
    if !rest.is_empty() {
        pieces.push(rest);
    }
    for (width, height) in CANVASES {
        let Ok(mut canvas) = Canvas::new(width, height) else { return };
        let mut terminal = receiver();
        let Ok(mut validator) = Validator::with_canvas(width, height) else { return };
        if let Some(font) = stroke_font() {
            validator.set_font(font);
        }
        for number in JOINED_SETS {
            if let (Ok(number), Some(Some(set))) = (u8::try_from(number), provided_sets().get(number)) {
                let _ = validator.set_teletext_set(number, Arc::clone(set));
            }
        }
        let mut fed = 0usize;
        for (index, piece) in pieces.iter().enumerate() {
            fed = fed.saturating_add(piece.len());
            let drawn = terminal.feed(&mut canvas, piece);
            let read = validator.feed(piece);
            assert_eq!(read, drawn, "the events of piece {index} differ on the {width} by {height} canvas");
            assert_eq!(
                *validator.diagnostics(),
                terminal.diagnostics(),
                "the diagnostics after piece {index} differ on the {width} by {height} canvas"
            );
            assert_eq!(
                validator.work_spent(),
                terminal.work_spent(),
                "the work after piece {index} differs on the {width} by {height} canvas"
            );
            let (terminal_held, validator_held) = own_held(&terminal, &validator);
            assert_eq!(
                validator_held, terminal_held,
                "the memory held after piece {index} differs on the {width} by {height} canvas"
            );
            assert!(validator_held <= MAX_HELD_BYTES, "the validator holds {validator_held} after piece {index}");
            let allowance =
                WORK_CAP.saturating_add(WORK_PER_BYTE.saturating_mul(u64::try_from(fed).unwrap_or(u64::MAX)));
            assert!(terminal.work_spent() <= allowance, "the work after piece {index} is past the allowance");
        }
        assert_eq!(validator.finish(), terminal.finish(&mut canvas), "the events at the end differ");
        assert_eq!(*validator.diagnostics(), terminal.diagnostics(), "the diagnostics at the end differ");
        assert_eq!(validator.defined_macros(), terminal.defined_macros(), "the defined macros differ");
        assert_eq!(validator.work_spent(), terminal.work_spent(), "the work at the end differs");
        let (terminal_held, validator_held) = own_held(&terminal, &validator);
        assert_eq!(validator_held, terminal_held, "the memory held at the end differs");
    }
}
