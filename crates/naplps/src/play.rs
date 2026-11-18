//! Playing a stream's WAIT and BLINK on the presentation clock (neoteletext-common
//! `docs/animation.md`, ANIM-1 and ANIM-20).
//!
//! The library has no clock. [`Player`] is told how many ticks of one sixtieth of a second have
//! passed and does what is due: it holds a stream's bytes back while a WAIT (ANSI X3.110-1983
//! section 5.3.2.8) is played, under the limits of [`crate::limits`], and gives the colour map
//! BLINK (section 5.3.2.7) shows at the tick reached. The intervals of both are tenths of a
//! second, [`TENTH_TICKS`] ticks each.

use alloc::vec::Vec;

use crate::limits::{MAX_WAIT_HELD_BYTES, TENTH_TICKS, WAIT_BUDGET_TICKS};
use crate::palette::Rgb;
use crate::surface::Canvas;
use crate::terminal::{Event, Terminal};

/// Plays one generation of one stream into one [`Terminal`]; a new generation takes a new
/// player, and with it a new budget of waiting.
#[derive(Clone, Debug)]
pub struct Player {
    /// Bytes not yet given to the terminal, from `fed` on.
    held: Vec<u8>,
    /// How many of `held` the terminal has taken.
    fed: usize,
    /// Ticks left of the WAIT being played.
    waiting: u32,
    /// Ticks of waiting played so far, at most [`WAIT_BUDGET_TICKS`].
    played: u32,
    /// Ticks passed.
    tick: u64,
    /// The tick at which the first of the blink processes now running was defined.
    blink_origin: Option<u64>,
    /// Whether a WAIT delays anything (the viewer's setting, ANIM-15 and ANIM-20).
    delays: bool,
    /// The caller has said the stream is complete.
    ended: bool,
    /// [`Terminal::finish`] has run.
    finished: bool,
}

impl Default for Player {
    fn default() -> Self {
        Self::new()
    }
}

impl Player {
    /// A player at tick 0 with nothing held and its whole budget of waiting.
    #[must_use]
    pub fn new() -> Self {
        Self {
            held: Vec::new(),
            fed: 0,
            waiting: 0,
            played: 0,
            tick: 0,
            blink_origin: None,
            delays: true,
            ended: false,
            finished: false,
        }
    }

    /// Whether a WAIT delays what follows it. Off, every WAIT passes at once: the viewer's
    /// setting "Paint drawings gradually" turned off (ANIM-20). A WAIT being played ends.
    pub fn set_delays(&mut self, delays: bool) {
        self.delays = delays;
        if !delays {
            self.waiting = 0;
        }
    }

    /// Takes more of the stream. It is drawn at once unless a WAIT is being played, in which
    /// case it is held; when more than [`MAX_WAIT_HELD_BYTES`] would be held the wait ends at
    /// once (ANIM-20). Returns the events of what was drawn, each WAIT among them.
    pub fn push(&mut self, terminal: &mut Terminal, canvas: &mut Canvas, bytes: &[u8]) -> Vec<Event> {
        self.held.extend_from_slice(bytes);
        let mut events = Vec::new();
        self.pump(terminal, canvas, &mut events);
        events
    }

    /// Says the stream is complete: once everything held has been drawn, the terminal's
    /// [`Terminal::finish`] runs, which draws a command still waiting for its operands.
    pub fn end(&mut self, terminal: &mut Terminal, canvas: &mut Canvas) -> Vec<Event> {
        self.ended = true;
        let mut events = Vec::new();
        self.pump(terminal, canvas, &mut events);
        events
    }

    /// Lets `ticks` ticks pass: a WAIT being played runs down, and when it ends what was held
    /// is drawn, up to the next WAIT, and so on within the ticks given.
    pub fn advance(&mut self, terminal: &mut Terminal, canvas: &mut Canvas, ticks: u32) -> Vec<Event> {
        let mut events = Vec::new();
        let mut left = ticks;
        loop {
            let step = self.waiting.min(left);
            self.waiting = self.waiting.saturating_sub(step);
            left = left.saturating_sub(step);
            self.tick = self.tick.saturating_add(u64::from(step));
            if self.waiting > 0 {
                break;
            }
            self.pump(terminal, canvas, &mut events);
            if self.waiting == 0 || left == 0 {
                break;
            }
        }
        self.tick = self.tick.saturating_add(u64::from(left));
        events
    }

    /// Draws what is held until a WAIT is being played or nothing is left.
    fn pump(&mut self, terminal: &mut Terminal, canvas: &mut Canvas, events: &mut Vec<Event>) {
        loop {
            let rest = self.held.get(self.fed..).unwrap_or(&[]);
            if self.waiting > 0 {
                if rest.len() <= MAX_WAIT_HELD_BYTES {
                    return;
                }
                // ANIM-20: when more arrive than may be held, the wait ends at once.
                self.waiting = 0;
            }
            if rest.is_empty() {
                self.held.clear();
                self.fed = 0;
                if self.ended && !self.finished {
                    self.finished = true;
                    events.extend(terminal.finish(canvas));
                    self.note_blinks(terminal);
                }
                return;
            }
            let (taken, more) = terminal.feed_until_wait(canvas, rest);
            self.fed = self.fed.saturating_add(taken);
            // Bytes already drawn are dropped once they are the larger part, so that a stream of
            // many short WAITs is not copied down once for each.
            if self.fed > self.held.len() / 2 {
                self.held.drain(..self.fed.min(self.held.len()));
                self.fed = 0;
            }
            for event in &more {
                if let Event::Wait(tenths) = event {
                    self.wait(*tenths);
                }
            }
            events.extend(more);
            self.note_blinks(terminal);
        }
    }

    /// Starts playing a WAIT of `tenths` tenths of a second, as far as the budget allows.
    fn wait(&mut self, tenths: u32) {
        if !self.delays {
            return;
        }
        let ticks = tenths.saturating_mul(TENTH_TICKS).min(WAIT_BUDGET_TICKS.saturating_sub(self.played));
        self.played = self.played.saturating_add(ticks);
        self.waiting = ticks;
    }

    /// Notes the tick at which the first blink process was defined, from which the colour map's
    /// time is counted (ANIM-20).
    fn note_blinks(&mut self, terminal: &Terminal) {
        if terminal.palette().blinks().is_empty() {
            self.blink_origin = None;
        } else if self.blink_origin.is_none() {
            self.blink_origin = Some(self.tick);
        }
    }

    /// Tenths of a second since the first blink process was defined.
    fn blink_tenths(&self) -> u32 {
        let ticks = self.blink_origin.map_or(0, |origin| self.tick.saturating_sub(origin));
        u32::try_from(ticks.checked_div(u64::from(TENTH_TICKS)).unwrap_or(0)).unwrap_or(u32::MAX)
    }

    /// The colour map at the tick reached, blinks applied (ANIM-20): the picture's palette, by
    /// which a blink is shown with no pixel repainted.
    #[must_use]
    pub fn colours(&self, terminal: &Terminal) -> Vec<Rgb> {
        terminal.palette().at(self.blink_tenths())
    }

    /// Ticks until the colour map next changes by a blink, or `None` when nothing blinks.
    #[must_use]
    pub fn ticks_to_blink(&self, terminal: &Terminal) -> Option<u32> {
        let origin = self.blink_origin?;
        let next = terminal.palette().next_change(self.blink_tenths())?;
        let due = origin.saturating_add(u64::from(next).saturating_mul(u64::from(TENTH_TICKS)));
        Some(u32::try_from(due.saturating_sub(self.tick)).unwrap_or(u32::MAX))
    }

    /// Ticks left of the WAIT being played; 0 when none is.
    #[must_use]
    pub fn waiting_ticks(&self) -> u32 {
        self.waiting
    }

    /// Ticks until something is due, a WAIT's end or a blink's change, or `None` when nothing
    /// is: a caller with a clock sleeps until then (ANIM-1).
    #[must_use]
    pub fn ticks_to_next(&self, terminal: &Terminal) -> Option<u32> {
        let wait = (self.waiting > 0).then_some(self.waiting);
        match (wait, self.ticks_to_blink(terminal)) {
            (Some(wait), Some(blink)) => Some(wait.min(blink)),
            (wait, blink) => wait.or(blink),
        }
    }

    /// Bytes held, waiting for a WAIT to end.
    #[must_use]
    pub fn held_bytes(&self) -> usize {
        self.held.len().saturating_sub(self.fed)
    }

    /// Ticks of waiting played so far in this generation, at most [`WAIT_BUDGET_TICKS`].
    #[must_use]
    pub fn waited_ticks(&self) -> u32 {
        self.played
    }

    /// Ticks passed since the player was made.
    #[must_use]
    pub fn tick(&self) -> u64 {
        self.tick
    }
}
