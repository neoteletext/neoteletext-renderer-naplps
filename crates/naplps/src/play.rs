//! Playing a stream's WAIT and BLINK on the presentation clock (neoteletext-common
//! `docs/animation.md`, ANIM-1 and ANIM-20).
//!
//! The library has no clock. [`Player`] is told how many ticks of one sixtieth of a second have
//! passed and does what is due: it holds a stream's bytes back while a WAIT (ANSI X3.110-1983
//! section 5.3.2.8) is played, under the limits of [`crate::limits`], and gives the colour map
//! BLINK (section 5.3.2.7) shows at the tick reached. The intervals of both are tenths of a
//! second, [`TENTH_TICKS`] ticks each.
//!
//! A player may also be given a [`Pace`] (DEC-7031 item 3, REQ-7024): the stream is then given
//! to the terminal at so many bytes in so many ticks, as a serial line of a stated speed would
//! deliver it, so that the picture paints as it was seen in its day. The caller turns a line
//! speed into a pace; the library knows only bytes and ticks.

use alloc::vec::Vec;

use crate::limits::{MAX_WAIT_HELD_BYTES, TENTH_TICKS, WAIT_BUDGET_TICKS};
use crate::palette::Rgb;
use crate::surface::Canvas;
use crate::terminal::{Event, Terminal};

/// The rate at which a [`Player`] gives a stream's bytes to its terminal: `bytes` bytes in every
/// `ticks` ticks of the presentation clock (DEC-7031 item 3). After `n` paced ticks of a run the
/// terminal has been given `n` x `bytes` / `ticks` bytes of it, rounded down, so a pace states
/// a serial line's speed exactly: 1,200 bits a second at ten bits a byte and 60 ticks a second
/// is 1,200 bytes in 600 ticks. A `ticks` or a `bytes` of 0 is taken as 1, so that no pace
/// divides by nothing or holds a stream for ever.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Pace {
    /// Bytes given in every `ticks` ticks; 0 is taken as 1.
    pub bytes: u32,
    /// The ticks in which `bytes` bytes are given; 0 is taken as 1.
    pub ticks: u32,
}

impl Pace {
    /// The bytes of the pace, 0 taken as 1.
    fn bytes(self) -> u64 {
        u64::from(self.bytes.max(1))
    }

    /// The ticks of the pace, 0 taken as 1.
    fn ticks(self) -> u64 {
        u64::from(self.ticks.max(1))
    }
}

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
    /// The pace at which held bytes are given to the terminal; `None` gives them at once
    /// (DEC-7031 item 3).
    pace: Option<Pace>,
    /// The current run's credit, in bytes times the pace's ticks: each paced tick adds the
    /// pace's bytes and each byte given takes the pace's ticks, so no fraction of a byte is
    /// lost between ticks and the line's speed is kept exactly. Always 0 with no pace.
    credit: u64,
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
            pace: None,
            credit: 0,
            ended: false,
            finished: false,
        }
    }

    /// Whether a WAIT delays what follows it. Off, every WAIT passes at once: the viewer's
    /// setting "Paint drawings gradually" turned off (ANIM-20). A WAIT being played ends, and
    /// so does a pace (DEC-7023 item 5: the viewer keeps the last word), which is forgotten and
    /// not taken again while delays are off; what is held is drawn whole by the next
    /// [`Player::push`], [`Player::end`] or [`Player::advance`] (of 0 ticks, if none are to pass).
    /// Turning delays on again brings no pace back: the caller sets it.
    pub fn set_delays(&mut self, delays: bool) {
        self.delays = delays;
        if !delays {
            self.waiting = 0;
            self.pace = None;
            self.credit = 0;
        }
    }

    /// Sets, changes or (with `None`) removes the pace at which the stream is given to the
    /// terminal (DEC-7031 item 3, REQ-7024). With a pace, bytes pushed are held and given as
    /// ticks pass in [`Player::advance`]:
    ///
    /// - a run begins when bytes arrive while nothing is held, and its first byte is due only
    ///   after ticks have passed, as on a line;
    /// - only ticks that pass while bytes are held and no WAIT is being played count, so a
    ///   WAIT's time is added to the line's time and never hidden inside it;
    /// - when everything held has been given the run is over and its credit forgotten, so a
    ///   stream that arrives late is not then drawn in a burst;
    /// - when more than [`MAX_WAIT_HELD_BYTES`] would be held the pace ends, as a WAIT does,
    ///   and everything is drawn at once.
    ///
    /// The picture at the end is the picture drawn at once: a pace changes when bytes are
    /// drawn, never which. Setting a pace forgets the credit of the run in hand. With `None`,
    /// what is held is drawn by the next [`Player::push`], [`Player::end`] or
    /// [`Player::advance`]. While delays are off ([`Player::set_delays`]) no pace is taken.
    pub fn set_pace(&mut self, pace: Option<Pace>) {
        self.pace = pace.filter(|_| self.delays);
        self.credit = 0;
    }

    /// Takes more of the stream. It is drawn at once unless a WAIT is being played or a pace is
    /// set ([`Player::set_pace`]), in which case it is held; when more than
    /// [`MAX_WAIT_HELD_BYTES`] would be held the wait and the pace end at once (ANIM-20,
    /// DEC-7031 item 3). Returns the events of what was drawn, each WAIT among them.
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
    /// is drawn, up to the next WAIT, and so on within the ticks given. With a pace
    /// ([`Player::set_pace`]) what is held is drawn as its bytes fall due, each on its own
    /// tick. Letting ticks pass in one call or one at a time draws the same at every tick.
    pub fn advance(&mut self, terminal: &mut Terminal, canvas: &mut Canvas, ticks: u32) -> Vec<Event> {
        let mut events = Vec::new();
        let mut left = ticks;
        loop {
            if self.waiting > 0 {
                let step = self.waiting.min(left);
                self.waiting = self.waiting.saturating_sub(step);
                left = left.saturating_sub(step);
                self.tick = self.tick.saturating_add(u64::from(step));
                if self.waiting > 0 {
                    break;
                }
            }
            self.pump(terminal, canvas, &mut events);
            if left == 0 {
                break;
            }
            if self.waiting > 0 {
                continue;
            }
            // DEC-7031 item 3: only here, with bytes held and no WAIT playing, do ticks earn
            // credit, so a WAIT's ticks are added to the line's time. The ticks up to the next
            // byte's are passed in one step: nothing is due on them, so the picture at every
            // tick is the one a caller passing them singly sees.
            let (Some(pace), Some(due)) = (self.pace, self.ticks_to_byte()) else {
                break;
            };
            let step = due.min(left);
            self.credit = self.credit.saturating_add(u64::from(step).saturating_mul(pace.bytes()));
            left = left.saturating_sub(step);
            self.tick = self.tick.saturating_add(u64::from(step));
        }
        self.tick = self.tick.saturating_add(u64::from(left));
        events
    }

    /// Paced ticks until the next held byte is due, at least 1; `None` with no pace or nothing
    /// held.
    fn ticks_to_byte(&self) -> Option<u32> {
        let pace = self.pace?;
        if self.held_bytes() == 0 {
            return None;
        }
        let short = pace.ticks().saturating_sub(self.credit);
        Some(u32::try_from(short.div_ceil(pace.bytes())).unwrap_or(u32::MAX).max(1))
    }

    /// Draws what is held until a WAIT is being played, the pace allows no more, or nothing is
    /// left.
    fn pump(&mut self, terminal: &mut Terminal, canvas: &mut Canvas, events: &mut Vec<Event>) {
        loop {
            let mut rest = self.held.get(self.fed..).unwrap_or(&[]);
            if rest.len() > MAX_WAIT_HELD_BYTES {
                // ANIM-20: when more arrive than may be held, the wait ends at once; and so
                // does the pace, for good, so that the hold has one bound (DEC-7031 item 3).
                self.waiting = 0;
                self.pace = None;
                self.credit = 0;
            }
            if self.waiting > 0 {
                return;
            }
            if rest.is_empty() {
                self.held.clear();
                self.fed = 0;
                // DEC-7031 item 3: a run's credit is forgotten when the hold empties.
                self.credit = 0;
                if self.ended && !self.finished {
                    self.finished = true;
                    events.extend(terminal.finish(canvas));
                    self.note_blinks(terminal);
                }
                return;
            }
            if let Some(pace) = self.pace {
                let allowed = usize::try_from(self.credit.checked_div(pace.ticks()).unwrap_or(0)).unwrap_or(usize::MAX);
                if allowed == 0 {
                    return;
                }
                rest = rest.get(..allowed).unwrap_or(rest);
            }
            let (taken, more) = terminal.feed_until_wait(canvas, rest);
            self.fed = self.fed.saturating_add(taken);
            if let Some(pace) = self.pace {
                let spent = u64::try_from(taken).unwrap_or(u64::MAX).saturating_mul(pace.ticks());
                // A run ends with its last byte even when that byte is a WAIT's and the hold is
                // only cleared after the wait: bytes arriving meanwhile begin a new run.
                self.credit = if self.fed >= self.held.len() { 0 } else { self.credit.saturating_sub(spent) };
            }
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

    /// Ticks until something is due, a WAIT's end, a blink's change or, under a pace, the next
    /// held byte (DEC-7031 item 3), or `None` when nothing is: a caller with a clock sleeps
    /// until then (ANIM-1). During a WAIT the next byte is not counted: it is due only after
    /// the wait, whose end is.
    #[must_use]
    pub fn ticks_to_next(&self, terminal: &Terminal) -> Option<u32> {
        let wait = if self.waiting > 0 { Some(self.waiting) } else { self.ticks_to_byte() };
        match (wait, self.ticks_to_blink(terminal)) {
            (Some(wait), Some(blink)) => Some(wait.min(blink)),
            (wait, blink) => wait.or(blink),
        }
    }

    /// Whether the player has nothing left to draw as ticks pass: nothing is held and no WAIT
    /// is being played. A caller uses it to tell that a paced picture is painted whole
    /// (DEC-7031 items 3 and 5); blinking goes on regardless ([`Player::ticks_to_blink`]).
    #[must_use]
    pub fn idle(&self) -> bool {
        self.held_bytes() == 0 && self.waiting == 0
    }

    /// The pace in force, as it was set; `None` when bytes are drawn as they arrive.
    #[must_use]
    pub fn pace(&self) -> Option<Pace> {
        self.pace
    }

    /// Bytes held, waiting for a WAIT to end or for the pace.
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
