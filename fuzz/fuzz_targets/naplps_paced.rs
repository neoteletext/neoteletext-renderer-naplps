//! The fuzz target `naplps_paced` (DEC-7031 item 3, REQ-7024): a [`Player`] driven by any
//! sequence of pushes, advances, paces set, changed and removed, and the viewer's setting turned
//! off and on. It must never panic and always finish; it never holds more than
//! `MAX_WAIT_HELD_BYTES`, never keeps a pace while delays are off, and lets exactly the ticks it
//! is given pass. Once the stream is ended and everything held has been drawn, the picture,
//! colour map and border are those of the same bytes fed at once and finished: a pace changes
//! when bytes are drawn, never which.
//!
//! This file holds the target's body, `naplps_paced`, which takes the fuzzer's bytes as a list
//! of operations (see [`naplps_paced`]); `crates/naplps-fuzz` runs it.

use naplps::limits::MAX_WAIT_HELD_BYTES;
use naplps::{Canvas, Pace, Player, StrokeFont, Terminal};

/// The picture drawn on: small, so that an input is quick, as `naplps_stream`'s.
const WIDTH: u32 = 160;
/// See [`WIDTH`].
const HEIGHT: u32 = 120;
/// The colour map's bits: 16 entries, as the sample pages use.
const PALETTE_BITS: u32 = 4;
/// The operations, each the remainder of its first byte by this.
const OPERATIONS: u8 = 5;
/// A pace's part at or above this is followed by four bytes, big-endian, giving the part
/// whole; below it, it is the part.
const WHOLE_PART: u8 = 0xF0;
/// An advance of this many ticks is of the most, `u32::MAX`.
const MOST_TICKS: u8 = 0xFF;

/// A terminal as each way of feeding starts with: the repository's own font, so that text is
/// drawn.
fn terminal() -> Terminal {
    let mut terminal = Terminal::new(PALETTE_BITS);
    if let Ok(font) = StrokeFont::parse(naplps_fonts::NEOTELETEXT) {
        terminal.set_font(font);
    }
    terminal
}

/// Reads the operations' bytes in turn; past the end every byte is 0.
struct Reader<'a> {
    rest: &'a [u8],
}

impl Reader<'_> {
    fn byte(&mut self) -> u8 {
        let Some((&first, rest)) = self.rest.split_first() else { return 0 };
        self.rest = rest;
        first
    }

    fn bytes(&mut self, count: usize) -> &[u8] {
        let (taken, rest) = self.rest.split_at(count.min(self.rest.len()));
        self.rest = rest;
        taken
    }

    /// A pace's part: one byte, or after [`WHOLE_PART`] four.
    fn part(&mut self) -> u32 {
        let first = self.byte();
        if first < WHOLE_PART {
            return u32::from(first);
        }
        let mut whole = [0u8; 4];
        for (to, &from) in whole.iter_mut().zip(self.bytes(4)) {
            *to = from;
        }
        u32::from_be_bytes(whole)
    }
}

/// Runs one input. Its bytes are operations, each chosen by its first byte's remainder by
/// [`OPERATIONS`]: 0, push the next byte's count of bytes; 1, advance the next byte's count of
/// ticks ([`MOST_TICKS`] the most); 2, set a pace of two parts ([`Reader::part`]); 3, remove the
/// pace; 4, turn delays off when the next byte is odd and on when it is even. Then the stream is
/// ended and the player advanced until nothing is held.
///
/// # Panics
///
/// When the player holds more than its bound, keeps a pace with delays off, lets a different
/// number of ticks pass than it was given, does not drain, or leaves a different picture than
/// the bytes fed at once.
pub fn naplps_paced(data: &[u8]) {
    let Ok(mut canvas) = Canvas::new(WIDTH, HEIGHT) else { return };
    let mut terminal = terminal();
    let mut player = Player::new();
    let mut stream = Vec::new();
    let mut delays = true;
    let mut reader = Reader { rest: data };
    while !reader.rest.is_empty() {
        let before = player.tick();
        let mut ticks = 0u64;
        match reader.byte() % OPERATIONS {
            0 => {
                let count = usize::from(reader.byte());
                let piece = reader.bytes(count);
                stream.extend_from_slice(piece);
                let _ = player.push(&mut terminal, &mut canvas, piece);
            }
            1 => {
                let count = reader.byte();
                let count = if count == MOST_TICKS { u32::MAX } else { u32::from(count) };
                ticks = u64::from(count);
                let _ = player.advance(&mut terminal, &mut canvas, count);
            }
            2 => {
                let pace = Pace { bytes: reader.part(), ticks: reader.part() };
                player.set_pace(Some(pace));
                assert_eq!(player.pace(), delays.then_some(pace), "a pace is taken only while delays are on");
            }
            3 => player.set_pace(None),
            _ => {
                delays = reader.byte().is_multiple_of(2);
                player.set_delays(delays);
            }
        }
        assert!(player.held_bytes() <= MAX_WAIT_HELD_BYTES, "more held than the bound");
        assert!(delays || player.pace().is_none(), "a pace kept with delays off");
        assert_eq!(player.tick(), before.saturating_add(ticks), "the ticks given pass, and only they");
    }
    let _ = player.end(&mut terminal, &mut canvas);
    // Each advance of the most ticks draws at least one byte held, whatever the pace (one byte
    // in the most ticks is the slowest), and plays out any WAIT before it.
    let mut calls = player.held_bytes().saturating_add(2);
    while !player.idle() {
        assert!(calls > 0, "the player does not drain");
        calls = calls.saturating_sub(1);
        let _ = player.advance(&mut terminal, &mut canvas, u32::MAX);
    }
    let Ok(mut whole) = Canvas::new(WIDTH, HEIGHT) else { return };
    let mut at_once = self::terminal();
    let _ = at_once.feed(&mut whole, &stream);
    let _ = at_once.finish(&mut whole);
    assert!(canvas == whole, "the picture paced differs from the picture fed at once");
    assert_eq!(terminal.palette().at(0), at_once.palette().at(0), "the colour map differs");
    assert_eq!(terminal.border(), at_once.border(), "the border differs");
}
