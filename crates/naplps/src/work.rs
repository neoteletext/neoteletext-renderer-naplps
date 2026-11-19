//! The pixel work allowance that bounds what a stream can cost to draw (TODO-6844, DEC-6851;
//! renderer parity section 19, threats 2 and 6).
//!
//! Eight bytes of NAPLPS can fill the whole screen, and a macro can repeat that up to
//! [`crate::limits::MAX_PROCESSED_BYTES`] times. Every pixel a drawing routine visits is
//! therefore paid for, before it is visited, from an allowance that grows with the stream's
//! bytes ([`WORK_PER_BYTE`]) up to [`WORK_CAP`], so the work of drawing a stream is at most
//! linear in its length. Once a payment is refused the allowance stops for good: drawing ends
//! there, and the terminal passes over the rest of the stream, in this call and every later
//! one, so that what is drawn never depends on how the stream was divided into calls.

use crate::limits::{WORK_CAP, WORK_PER_BYTE};
use crate::surface::Surface;

/// A token bucket of work units (pixels visited): filled by the stream's bytes, drained by
/// drawing.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct Work {
    left: u64,
    /// Every unit paid since the start, for the caller that counts a drawing's cost.
    spent: u64,
    /// A payment was refused: every later one is refused too, so that what is drawn is exactly
    /// what comes before the first thing that could not be afforded.
    stopped: bool,
}

impl Default for Work {
    fn default() -> Self {
        Self::new()
    }
}

impl Work {
    /// The allowance of a new stream: [`WORK_CAP`].
    pub(crate) const fn new() -> Self {
        Self::with(WORK_CAP)
    }

    /// An allowance of exactly `units`, earning nothing: what one composing of objects may
    /// spend.
    pub(crate) const fn with(units: u64) -> Self {
        Self { left: units, spent: 0, stopped: false }
    }

    /// Credits the allowance for `bytes` of the stream, up to [`WORK_CAP`].
    pub(crate) fn earn(&mut self, bytes: usize) {
        let bytes = u64::try_from(bytes).unwrap_or(u64::MAX);
        self.left = self.left.saturating_add(bytes.saturating_mul(WORK_PER_BYTE)).min(WORK_CAP.max(self.left));
    }

    /// Pays for `units`; false, and nothing paid, if they cannot be afforded or a payment was
    /// already refused.
    pub(crate) fn spend(&mut self, units: u64) -> bool {
        if self.stopped {
            return false;
        }
        if let Some(left) = self.left.checked_sub(units) {
            self.left = left;
            self.spent = self.spent.saturating_add(units);
            true
        } else {
            self.stopped = true;
            false
        }
    }

    /// Whether a payment was refused.
    pub(crate) const fn stopped(&self) -> bool {
        self.stopped
    }

    /// The units paid since the start.
    pub(crate) const fn spent(&self) -> u64 {
        self.spent
    }
}

/// A surface whose drawing is paid for from a [`Work`]: what a terminal draws through.
pub(crate) struct Metered<'a> {
    pub(crate) surface: &'a mut dyn Surface,
    pub(crate) work: &'a mut Work,
}

impl Surface for Metered<'_> {
    fn width(&self) -> i32 {
        self.surface.width()
    }
    fn height(&self) -> i32 {
        self.surface.height()
    }
    fn scale_x(&self) -> (i64, i64) {
        self.surface.scale_x()
    }
    fn scale_y(&self) -> (i64, i64) {
        self.surface.scale_y()
    }
    fn subpixel_shift(&self) -> (i64, i64) {
        self.surface.subpixel_shift()
    }
    fn put(&mut self, x: i32, y: i32, entry: u8) {
        self.surface.put(x, y, entry);
    }
    fn get(&self, x: i32, y: i32) -> Option<u8> {
        self.surface.get(x, y)
    }
    fn fill_all(&mut self, entry: u8) {
        if self.spend(area(&*self.surface)) {
            self.surface.fill_all(entry);
        }
    }
    fn spend(&mut self, units: u64) -> bool {
        self.work.spend(units)
    }
    fn keeps_pixels(&self) -> bool {
        self.surface.keeps_pixels()
    }
}

/// A definition's bitmap drawn on while a stream is drawn: its pixels are paid for by the
/// stream's surface, `payer`, since a DEF DRCS or DEF TEXTURE inside a macro can be repeated as
/// often as a fill on the screen.
pub(crate) struct PaidBy<'a> {
    pub(crate) surface: &'a mut dyn Surface,
    pub(crate) payer: &'a mut dyn Surface,
}

impl Surface for PaidBy<'_> {
    fn width(&self) -> i32 {
        self.surface.width()
    }
    fn height(&self) -> i32 {
        self.surface.height()
    }
    fn scale_x(&self) -> (i64, i64) {
        self.surface.scale_x()
    }
    fn scale_y(&self) -> (i64, i64) {
        self.surface.scale_y()
    }
    fn subpixel_shift(&self) -> (i64, i64) {
        self.surface.subpixel_shift()
    }
    fn put(&mut self, x: i32, y: i32, entry: u8) {
        self.surface.put(x, y, entry);
    }
    fn get(&self, x: i32, y: i32) -> Option<u8> {
        self.surface.get(x, y)
    }
    fn fill_all(&mut self, entry: u8) {
        if self.spend(area(&*self.surface)) {
            self.surface.fill_all(entry);
        }
    }
    fn spend(&mut self, units: u64) -> bool {
        self.payer.spend(units)
    }
    // A definition's bitmap is always drawn, by a validator too: what it holds is what the
    // stream defined, whatever reads it.
}

/// The pixels of a surface: what clearing it visits.
pub(crate) fn area(surface: &dyn Surface) -> u64 {
    let side = |pixels: i32| u64::try_from(pixels).unwrap_or(0);
    side(surface.width()).saturating_mul(side(surface.height()))
}

/// The pixels from `low` to `high` inclusive, or none when `high` is below `low`.
pub(crate) fn span(low: i64, high: i64) -> u64 {
    u64::try_from(high.saturating_sub(low).saturating_add(1)).unwrap_or(0)
}
