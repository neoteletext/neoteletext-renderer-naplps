//! The fuzz target `naplps_stream` (REQ-5788; TODO-5760): any bytes, in any pieces, fed to the
//! renderer. It must never panic and always finish, and the picture must not depend on how the
//! bytes were divided: fed whole, fed in pieces, fed up to each WAIT in turn
//! (`Terminal::feed_until_wait`) and played with its WAITs passing without delay
//! (`Player`), a stream gives the same pixels, colour map and border. Every pixel a feed
//! changes lies inside the damage it reports (neoteletext-common `docs/animation.md`, ANIM-4).
//!
//! This file holds the target's body, `naplps_stream`, which takes the fuzzer's bytes: the
//! first says how the rest is divided, and the rest is the stream. `crates/naplps-fuzz` runs it.

use naplps::{Canvas, Player, StrokeFont, Terminal};

/// The picture drawn on: small, so that an input is quick, and neither side a power of two or
/// equal to the other, so that scaling is exercised.
const WIDTH: u32 = 160;
/// See [`WIDTH`].
const HEIGHT: u32 = 120;
/// The colour map's bits: 16 entries, as the sample pages use.
const PALETTE_BITS: u32 = 4;
/// The most bytes of one piece, less one: pieces of 1 to 64 bytes.
const PIECE_SPAN: u8 = 64;
/// The most calls of `feed_until_wait` a stream can need: a call takes a byte of the stream,
/// or goes on with a macro a WAIT stopped, whose bytes count toward the limit on bytes
/// processed. More calls than this means feeding does not finish.
const fn most_calls(stream: &[u8]) -> usize {
    stream.len().saturating_add(naplps::limits::MAX_PROCESSED_BYTES)
}

/// A terminal as each way of feeding starts with: the repository's own font, so that text is
/// drawn.
fn terminal() -> Terminal {
    let mut terminal = Terminal::new(PALETTE_BITS);
    if let Ok(font) = StrokeFont::parse(naplps_fonts::NEOTELETEXT) {
        terminal.set_font(font);
    }
    terminal
}

/// What a way of feeding left: the pixels, the colour map at rest and the border.
type Left = (Canvas, Vec<[u8; 3]>, u8);

fn left(terminal: &Terminal, canvas: Canvas) -> Left {
    (canvas, terminal.palette().at(0), terminal.border())
}

/// Feeds `stream` in pieces whose lengths the bytes of `stream` themselves choose, checking
/// after each that every pixel changed lies inside the damage reported.
fn in_pieces(stream: &[u8], seed: u8) -> Option<Left> {
    let mut canvas = Canvas::new(WIDTH, HEIGHT).ok()?;
    let mut terminal = terminal();
    let _ = terminal.take_damage();
    let mut rest = stream;
    let mut chooser = seed;
    while !rest.is_empty() {
        let length = usize::from(chooser % PIECE_SPAN).saturating_add(1).min(rest.len());
        let (piece, more) = rest.split_at(length);
        rest = more;
        chooser = chooser.wrapping_mul(31).wrapping_add(piece.last().copied().unwrap_or(0));
        let before = canvas.clone();
        let _ = terminal.feed(&mut canvas, piece);
        let damage = terminal.take_damage();
        for y in 0..HEIGHT {
            for x in 0..WIDTH {
                assert!(
                    before.pixel(x, y) == canvas.pixel(x, y) || damage.is_some_and(|rect| rect.contains(x, y)),
                    "pixel ({x}, {y}) changed outside the damage {damage:?}"
                );
            }
        }
    }
    let _ = terminal.finish(&mut canvas);
    Some(left(&terminal, canvas))
}

/// Runs one input. Panics when a property fails, as a fuzzing engine expects.
///
/// # Panics
///
/// When two ways of feeding the same stream leave different pictures, a pixel changes outside
/// the damage reported, or feeding up to each WAIT does not finish.
pub fn naplps_stream(data: &[u8]) {
    let Some((seed, stream)) = data.split_first() else { return };
    let Ok(blank) = Canvas::new(WIDTH, HEIGHT) else { return };

    // Whole.
    let mut canvas = blank.clone();
    let mut whole = terminal();
    let _ = whole.feed(&mut canvas, stream);
    let _ = whole.finish(&mut canvas);
    let whole = left(&whole, canvas);

    // In pieces.
    let Some(pieces) = in_pieces(stream, *seed) else { return };
    assert!(pieces == whole, "the picture depends on how the stream was divided");

    // Up to each WAIT in turn.
    let mut canvas = blank.clone();
    let mut staged = terminal();
    let mut rest = stream;
    let mut calls = 0usize;
    while !rest.is_empty() {
        let (taken, _) = staged.feed_until_wait(&mut canvas, rest);
        assert!(taken <= rest.len(), "more bytes taken than given");
        rest = rest.get(taken..).unwrap_or(&[]);
        calls = calls.saturating_add(1);
        // A call that takes nothing went on with a macro a WAIT had stopped.
        assert!(calls <= most_calls(stream), "feeding up to each WAIT does not finish");
    }
    let _ = staged.finish(&mut canvas);
    assert!(left(&staged, canvas) == whole, "the picture fed up to each WAIT differs from the picture fed whole");

    // Played, with every WAIT passing without delay.
    let mut canvas = blank;
    let mut on_ticks = terminal();
    let mut player = Player::new();
    player.set_delays(false);
    let _ = player.push(&mut on_ticks, &mut canvas, stream);
    let _ = player.end(&mut on_ticks, &mut canvas);
    assert_eq!(player.held_bytes(), 0, "a player whose WAITs do not delay holds nothing");
    assert!(left(&on_ticks, canvas) == whole, "the picture played differs from the picture fed whole");
}
