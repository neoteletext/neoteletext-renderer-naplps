//! The receiver's reading of a stream without drawing it (renderer parity PAR-15, REQ-6765), for
//! a server that checks every NAPLPS stream a program sends with the reader the receiver uses.

use alloc::vec::Vec;

use super::{CODES, Diagnostics, Event, Terminal};
use crate::limits::{MAX_CANVAS_SIDE, MAX_PROCESSED_BYTES, RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_WIDTH};
use crate::surface::{DISPLAY_HEIGHT_DENOMINATOR, DISPLAY_HEIGHT_NUMERATOR, Surface};
use crate::{BitmapSet, Error, StrokeFont};

/// The colour map a validator's terminal keeps: 16 entries, as the sample pages use. Nothing a
/// validator reports depends on the colour map's size; it only bounds the map's own memory.
const PALETTE_BITS: u32 = 4;

/// A surface of a canvas's size that keeps nothing: what a validator draws on. Every drawing
/// still runs and pays for every pixel it would visit on a canvas of this size, so that the
/// reading, and where the work allowance stops it (TODO-6844), is exactly the terminal's; but
/// the drawing routines pass over the pixels themselves (`keeps_pixels`), so a figure costs
/// its outline's arithmetic and its rows, not its area.
struct Discard {
    width: u32,
    height: u32,
}

impl Surface for Discard {
    fn width(&self) -> i32 {
        i32::try_from(self.width).unwrap_or(i32::MAX)
    }
    fn height(&self) -> i32 {
        i32::try_from(self.height).unwrap_or(i32::MAX)
    }
    fn scale_x(&self) -> (i64, i64) {
        (i64::from(self.width), 1)
    }
    fn scale_y(&self) -> (i64, i64) {
        // As a canvas of this height: the display shows 25/32 of the unit screen's height.
        (i64::from(self.height).saturating_mul(DISPLAY_HEIGHT_DENOMINATOR), DISPLAY_HEIGHT_NUMERATOR)
    }
    fn put(&mut self, _x: i32, _y: i32, _entry: u8) {}
    fn get(&self, _x: i32, _y: i32) -> Option<u8> {
        None
    }
    fn fill_all(&mut self, _entry: u8) {}
    fn keeps_pixels(&self) -> bool {
        false
    }
}

/// Reads a NAPLPS stream exactly as [`Terminal::feed`] reads it, with no canvas (PAR-15): the
/// same parser and the same handling of definitions (a validator holds a [`Terminal`] and runs
/// its own reading of the bytes, drawing onto a surface that keeps nothing), so the same macros,
/// DRCS characters and textures are defined, the same bytes are processed under the same
/// [`MAX_PROCESSED_BYTES`], and the same [`Diagnostics`] and [`Event`]s result, whatever the
/// stream. A server checks many streams with it at a memory cost that does not depend on the
/// picture's size.
///
/// **Work.** A validator counts the pixel work a receiver's terminal spends drawing the stream
/// and stops where it stops (TODO-6844): made with [`Validator::new`] it counts on the
/// receiver's canvas, [`RECEIVER_CANVAS_WIDTH`] by [`RECEIVER_CANVAS_HEIGHT`], and given the
/// receiver's stroke font ([`Validator::set_font`]) and joined character sets
/// ([`Validator::set_teletext_set`]) its count is the receiver's after every call. It visits a
/// figure's rows and steps but not its pixels: the two costliest streams of 1 MiB the work
/// tests know take a validator about 8 milliseconds in a release build, against about 350 for a
/// terminal.
///
/// **Memory.** No canvas is held, and no font or character set unless one is given. What a
/// validator holds is a fixed state and what the stream defines, each within its limit (the
/// macros, the copies of one while they nest, the DRCS characters and textures, a PDI's
/// operands), and [`Validator::held_bytes`] reports it after every call, from the allocations'
/// real sizes; it is never more than [`crate::limits::MAX_HELD_BYTES`] (1,971,344 bytes on a
/// 64-bit target) besides the font and sets given. Measured on 19 November 2026 on `x86_64`
/// Linux (`tests/held.rs`, `tests/validator_memory.rs`): a validator is 1,040 bytes itself and a
/// new one reports 12,360; so does the median page of the NAPLPS corpus, of the repository's
/// samples and of the naplpsdemo channel's pictures, which define nothing; the heaviest stream
/// the tests know (the macros filled, a macro nested 16 deep, all 96 DRCS characters and 4
/// textures at the largest mask with every element drawn, and a polygon of the most operand
/// bytes left open) reports 1,753,352, and 32 validators reading it grew the process's resident
/// size by 56,139,776 bytes against 56,107,264 reported. For comparison, a terminal's canvas of
/// the NeoTeletext raster, 480 by 500, is 240,000 bytes whatever the stream.
pub struct Validator {
    terminal: Terminal,
    surface: Discard,
}

impl Default for Validator {
    fn default() -> Self {
        Self::new()
    }
}

impl Validator {
    /// A validator in the state a terminal powers up in, reading as a receiver's terminal
    /// drawing on its canvas of [`RECEIVER_CANVAS_WIDTH`] by [`RECEIVER_CANVAS_HEIGHT`] does.
    #[must_use]
    pub fn new() -> Self {
        Self {
            terminal: Terminal::new(PALETTE_BITS),
            surface: Discard { width: RECEIVER_CANVAS_WIDTH, height: RECEIVER_CANVAS_HEIGHT },
        }
    }

    /// A validator reading as a terminal drawing on a canvas of `width` by `height` does: the
    /// pixel work a drawing costs, and so where the work allowance stops a stream, depends on
    /// the canvas's size (TODO-6844).
    ///
    /// # Errors
    ///
    /// [`Error::CanvasSize`] when a side is zero or above [`MAX_CANVAS_SIDE`], as
    /// [`crate::Canvas::new`] refuses it.
    pub fn with_canvas(width: u32, height: u32) -> Result<Self, Error> {
        if !(1..=MAX_CANVAS_SIDE).contains(&width) || !(1..=MAX_CANVAS_SIDE).contains(&height) {
            return Err(Error::CanvasSize);
        }
        // On a whole multiple of the receiver's canvas a terminal draws on the raster's dots
        // and writes each as k by k pixels (`dot_scale`), so it pays for the dots.
        let dot = crate::dot_scale(width, height);
        let (width, height) = (width.checked_div(dot).unwrap_or(width), height.checked_div(dot).unwrap_or(height));
        Ok(Self { terminal: Terminal::new(PALETTE_BITS), surface: Discard { width, height } })
    }

    /// Uses `font` for the primary and supplementary sets, as [`Terminal::set_font`] does. A
    /// stroke character's pixel work depends on its strokes, and where a proportionally spaced
    /// character lands on its font's widths, so a validator counts the receiver's work exactly
    /// only with the receiver's font: NeoTeletext's is `naplps-fonts`' `NEOTELETEXT`
    /// (TODO-6844). Nothing else a validator reports depends on it.
    pub fn set_font(&mut self, font: StrokeFont) {
        self.terminal.set_font(font);
    }

    /// Uses `set` for NeoTeletext character set `number`, as [`Terminal::set_teletext_set`]
    /// does. Only a set's joining data matters to a validator: letters of a joined set are held
    /// back until the letter after them (PAR-14), so where a stream divided into calls has
    /// spent its pixel work, and where the work allowance stops it, depends on them. A
    /// validator given the receiver's joined sets (44 to 51, the plain Arabic-script sets)
    /// counts the receiver's work after every call; without them it counts it at the stream's
    /// end, and may stop a stream that reaches the allowance a few letters from where the
    /// receiver stops it (TODO-6844).
    ///
    /// # Errors
    ///
    /// [`Error::Bitmap`] when `number` is not below [`crate::TELETEXT_SET_COUNT`].
    pub fn set_teletext_set(&mut self, number: u8, set: BitmapSet) -> Result<(), Error> {
        self.terminal.set_teletext_set(number, set)
    }

    /// Reads `bytes` as [`Terminal::feed`] reads them, drawing nothing, and returns the same
    /// events: WAIT, BEL and the processing limit.
    pub fn feed(&mut self, bytes: &[u8]) -> Vec<Event> {
        self.terminal.run(&mut self.surface, bytes, MAX_PROCESSED_BYTES, false);
        core::mem::take(&mut self.terminal.events)
    }

    /// Ends the stream as [`Terminal::finish`] does: runs a PDI still collecting its operands,
    /// whose refusals are then counted, and returns the events.
    pub fn finish(&mut self) -> Vec<Event> {
        self.terminal.end(&mut self.surface);
        core::mem::take(&mut self.terminal.events)
    }

    /// What the stream's bytes did that its author may not have meant: the bytes passed over and
    /// the work refused at a bound, as [`Terminal::diagnostics`] gives them for the same bytes.
    #[must_use]
    pub fn diagnostics(&self) -> &Diagnostics {
        &self.terminal.diagnostics
    }

    /// The pixel work the stream's drawing has spent, as [`Terminal::work_spent`] counts it on
    /// a canvas of this validator's size: what a server counts a drawing's cost by.
    #[must_use]
    pub fn work_spent(&self) -> u64 {
        self.terminal.work_spent()
    }

    /// The memory this validator holds between calls, in bytes, at most, as
    /// [`Terminal::held_bytes`] counts it, with its own structure: never more than
    /// [`crate::limits::MAX_HELD_BYTES`] without the stroke font and the provided sets given to
    /// it. A new validator holds 12,360 bytes on a 64-bit target (`tests/held.rs` prints it); a
    /// server keeping a validator for each picture or stream counts it at this figure after
    /// every call (TODO-6854).
    #[must_use]
    pub fn held_bytes(&self) -> usize {
        // The surface keeps no pixels; only its structure is the validator's own.
        size_of::<Self>().saturating_sub(size_of::<Terminal>()).saturating_add(self.terminal.held_bytes())
    }

    /// For each macro name 2/0 to 7/15 in turn, whether the stream has defined it (by DEF MACRO
    /// or DEFP MACRO, and not deleted it since): what a program's later stream may call. A
    /// transmit macro is not counted, since calling one does nothing (section 6.2.2.3). It is
    /// [`Terminal::defined_macros`] of the terminal the validator holds.
    #[must_use]
    pub fn defined_macros(&self) -> [bool; CODES] {
        self.terminal.defined_macros()
    }
}
