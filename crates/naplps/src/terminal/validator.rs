//! The receiver's reading of a stream without drawing it (renderer parity PAR-15, REQ-6765), for
//! a server that checks every NAPLPS stream a program sends with the reader the receiver uses.

use alloc::vec::Vec;

use super::{CODES, Diagnostics, Event, Terminal};
use crate::limits::MAX_PROCESSED_BYTES;
use crate::surface::{DISPLAY_HEIGHT_DENOMINATOR, DISPLAY_HEIGHT_NUMERATOR, Surface};

/// The colour map a validator's terminal keeps: 16 entries, as the sample pages use. Nothing a
/// validator reports depends on the colour map's size; it only bounds the map's own memory.
const PALETTE_BITS: u32 = 4;

/// A surface of one pixel that keeps nothing: what a validator draws on. Every drawing still
/// runs, so that the reading is exactly the terminal's, but on one pixel a figure costs no more
/// than its outline's arithmetic, and nothing is kept.
struct Discard;

impl Surface for Discard {
    fn width(&self) -> i32 {
        1
    }
    fn height(&self) -> i32 {
        1
    }
    fn scale_x(&self) -> (i64, i64) {
        (1, 1)
    }
    fn scale_y(&self) -> (i64, i64) {
        // As a canvas one pixel high: the display shows 25/32 of the unit screen's height.
        (DISPLAY_HEIGHT_DENOMINATOR, DISPLAY_HEIGHT_NUMERATOR)
    }
    fn put(&mut self, _x: i32, _y: i32, _entry: u8) {}
    fn get(&self, _x: i32, _y: i32) -> Option<u8> {
        None
    }
    fn fill_all(&mut self, _entry: u8) {}
}

/// Reads a NAPLPS stream exactly as [`Terminal::feed`] reads it, with no canvas (PAR-15): the
/// same parser and the same handling of definitions (a validator holds a [`Terminal`] and runs
/// its own reading of the bytes, drawing onto a surface that keeps nothing), so the same macros,
/// DRCS characters and textures are defined, the same bytes are processed under the same
/// [`MAX_PROCESSED_BYTES`], and the same [`Diagnostics`] and [`Event`]s result, whatever the
/// stream. A server checks many streams with it at a memory cost that does not depend on the
/// picture's size.
///
/// **Memory.** No canvas, no font and no character set is held. What a validator holds is a
/// fixed state and what the stream defines, each within its limit: the macros at most
/// [`crate::limits::MAX_ALL_MACRO_BYTES`] (65,536) bytes, and while macros expand at most
/// [`crate::limits::MAX_MACRO_DEPTH`] (16) copies of a definition of at most
/// [`crate::limits::MAX_MACRO_BYTES`] (4,096); the 96 DRCS characters and 4 texture masks, and
/// one being defined, each a bitmap of at most [`crate::limits::MASK_SIDE`] squared (16,384)
/// one-byte elements, at most 1,654,784 bytes together; a PDI's operands at most
/// [`crate::limits::MAX_PDI_BYTES`] (32,768) bytes, with at most
/// [`crate::limits::MAX_VERTICES`] (4,096) points of 8 bytes while it runs: 1,851,392 bytes
/// at most for what a stream defines and sends, besides the fixed state. Measured on 19
/// November 2026 by `tests/validator_memory.rs` on `x86_64` Linux: a validator is 936 bytes
/// itself, and a new one reading the heaviest stream the test knows (the macros filled, a macro
/// nested 16 deep, all 96 DRCS characters and 4 textures at the largest mask with every
/// element drawn, and a polygon of the most operand bytes) grew the process's peak resident
/// size by 1,761,280 bytes in a release build and 1,822,720 in a debug build. For comparison, a
/// terminal's canvas of the NeoTeletext raster, 480 by 500, is 240,000 bytes whatever the
/// stream; a validator's memory beyond its fixed state grows only with what the stream defines.
pub struct Validator {
    terminal: Terminal,
}

impl Default for Validator {
    fn default() -> Self {
        Self::new()
    }
}

impl Validator {
    /// A validator in the state a terminal powers up in.
    #[must_use]
    pub fn new() -> Self {
        Self { terminal: Terminal::new(PALETTE_BITS) }
    }

    /// Reads `bytes` as [`Terminal::feed`] reads them, drawing nothing, and returns the same
    /// events: WAIT, BEL and the processing limit.
    pub fn feed(&mut self, bytes: &[u8]) -> Vec<Event> {
        self.terminal.run(&mut Discard, bytes, MAX_PROCESSED_BYTES, false);
        core::mem::take(&mut self.terminal.events)
    }

    /// Ends the stream as [`Terminal::finish`] does: runs a PDI still collecting its operands,
    /// whose refusals are then counted, and returns the events.
    pub fn finish(&mut self) -> Vec<Event> {
        self.terminal.settle(&mut Discard);
        self.terminal.flush(&mut Discard);
        core::mem::take(&mut self.terminal.events)
    }

    /// What the stream's bytes did that its author may not have meant: the bytes passed over and
    /// the work refused at a bound, as [`Terminal::diagnostics`] gives them for the same bytes.
    #[must_use]
    pub fn diagnostics(&self) -> &Diagnostics {
        &self.terminal.diagnostics
    }

    /// For each macro name 2/0 to 7/15 in turn, whether the stream has defined it (by DEF MACRO
    /// or DEFP MACRO, and not deleted it since): what a program's later stream may call. A
    /// transmit macro is not counted, since calling one does nothing (section 6.2.2.3).
    #[must_use]
    pub fn defined_macros(&self) -> [bool; CODES] {
        core::array::from_fn(|index| self.terminal.macros.get(index).is_some_and(Option::is_some))
    }
}
