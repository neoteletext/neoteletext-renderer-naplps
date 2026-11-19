//! The measurement ANIM-4 asks for (neoteletext-common `docs/animation.md`: "Measured before
//! and after: ... one moved sprite, against a whole page"; REQ-6531). It prints its numbers and
//! holds the pixels repainted, which are the same on every machine, to a budget.
//!
//! Before damage, a moved object meant drawing the stream again and composing the whole
//! picture. After, the stream's picture is kept and only the rectangle the object left and
//! the one it reaches are repainted from it (ANIM-4, ANIM-12).
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use std::time::{Duration, Instant};

use naplps::limits::{DISPLAY_FIRST_LINE, DISPLAY_LINES, RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_WIDTH};
use naplps::{Animation, Canvas, Object, ObjectKind, StrokeFont, Terminal};

/// The receiver's canvas, which shows raster lines 20 to 479 (DEC-6857).
const WIDTH: u32 = RECEIVER_CANVAS_WIDTH;
/// See [`WIDTH`].
const HEIGHT: u32 = RECEIVER_CANVAS_HEIGHT;
/// The colour map's bits: the sample pages use 16 entries.
const PALETTE_BITS: u32 = 4;
/// The moving object's width in dots: 16/256 of the unit screen is 30 dots of the 480 across,
/// and one more for the rectangle's far edge.
const SIDE_ACROSS: u16 = 31;
/// Its height in lines: 16/256 of the unit screen is 36.8 lines of the display area's 460 shown
/// as 25/32 of it, rounded at both edges to 38.
const SIDE_DOWN: u16 = 38;
/// The moves measured, each of [`STEP`] pixels to the right: a second of animation at one move
/// a tick.
const MOVES: i16 = 60;
/// The dots of one move: the object overlaps where it was.
const STEP: i16 = 4;
/// Where the object starts.
const START: (i16, i16) = (100, 200);
/// The most pixels one move may repaint: the rectangle that holds the object before and
/// after, 35 by 38, which is 1,330. The whole picture is 220,800.
const MOVE_PIXELS_BUDGET: u64 = (SIDE_ACROSS as u64 + STEP as u64) * SIDE_DOWN as u64;

/// A page of the repository's own samples with a good deal of drawing in it.
fn page() -> Vec<u8> {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../samples/set-4/out/108-festival-poster.nap");
    std::fs::read(path).unwrap()
}

/// DEF MACRO 2/0: SO, SELECT COLOR entry 7, a filled rectangle of 16/256 each way at the
/// origin; END (ANSI X3.110-1983 sections 5.3.2.6, 5.3.3.4 and 6.2.2).
const SPRITE_MACRO: [u8; 10] = [0x80, 0x20, 0x0E, 0x3E, 0x5C, 0x31, 0x40, 0x52, 0x40, 0x85];

/// The moving object: one frame, macro 2/0, whose drawing is the picture's lower left corner.
fn sprite() -> Object {
    Object {
        number: 1,
        kind: ObjectKind::Macro,
        shown: true,
        detectable: false,
        layer: 2,
        order: 0,
        x: START.0,
        y: START.1,
        width: SIDE_ACROSS,
        height: SIDE_DOWN,
        origin_x: 0,
        origin_y: i16::try_from(DISPLAY_FIRST_LINE + DISPLAY_LINES).unwrap() - i16::try_from(SIDE_DOWN).unwrap(),
        cover: 0,
        hover: 0,
        pressed: 0,
        alternative: 0,
        frames: vec![0x20],
        label: String::new(),
    }
}

/// A terminal with the page drawn on `canvas` and the sprite set; the time drawing took.
fn drawn(canvas: &mut Canvas) -> (Terminal, Duration) {
    let mut terminal = Terminal::new(PALETTE_BITS);
    terminal.set_font(StrokeFont::parse(include_str!("../../../fonts/neoteletext.strokes")).unwrap());
    let started = Instant::now();
    let _ = terminal.feed(canvas, &page());
    let taken = started.elapsed();
    // After the page, whose full RESET at its start would delete the macro.
    let _ = terminal.feed(canvas, &SPRITE_MACRO);
    let _ = terminal.finish(canvas);
    terminal.set_objects(&[sprite()]).unwrap();
    (terminal, taken)
}

fn moved(step: i16) -> Animation {
    Animation { position: Some((START.0 + step * STEP, START.1)), ..Animation::default() }
}

/// The middle of some times: the figure least moved by a busy machine.
fn median(mut times: Vec<Duration>) -> Duration {
    times.sort_unstable();
    times[times.len() / 2]
}

#[test]
fn moving_an_object_repaints_its_own_rectangles_and_not_the_page() {
    // Before: each move draws the stream again and composes the whole picture.
    let mut before_times = Vec::new();
    let mut last_before = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut draw_times = Vec::new();
    for step in 1..=MOVES {
        let started = Instant::now();
        let mut background = Canvas::new(WIDTH, HEIGHT).unwrap();
        let (mut terminal, draw) = drawn(&mut background);
        assert!(terminal.set_animation(1, moved(step)));
        let mut presented = Canvas::new(WIDTH, HEIGHT).unwrap();
        terminal.compose(&background, &mut presented).unwrap();
        before_times.push(started.elapsed());
        draw_times.push(draw);
        last_before = presented;
    }

    // After: the stream's picture is kept, and a move repaints what it damaged.
    let mut background = Canvas::new(WIDTH, HEIGHT).unwrap();
    let (mut terminal, _) = drawn(&mut background);
    let mut presented = Canvas::new(WIDTH, HEIGHT).unwrap();
    let started = Instant::now();
    terminal.compose(&background, &mut presented).unwrap();
    let whole_compose = started.elapsed();
    let _ = terminal.take_damage();
    let mut after_times = Vec::new();
    let mut repainted = Vec::new();
    for step in 1..=MOVES {
        let started = Instant::now();
        assert!(terminal.set_animation(1, moved(step)));
        let changed = terminal.compose(&background, &mut presented).unwrap().unwrap();
        after_times.push(started.elapsed());
        repainted.push(u64::from(changed.width) * u64::from(changed.height));
        let _ = terminal.take_damage();
    }

    let whole = u64::from(WIDTH) * u64::from(HEIGHT);
    let most = repainted.iter().copied().max().unwrap();
    let (before, after) = (median(before_times), median(after_times));
    println!("moving a {SIDE_ACROSS} by {SIDE_DOWN} object {STEP} dots over the sample page 108, {WIDTH} by {HEIGHT}:");
    println!("  drawing the stream: {:?} (median of {MOVES})", median(draw_times));
    println!("  composing the whole picture once: {whole_compose:?}, {whole} pixels");
    println!("  before, the stream drawn again and the whole picture composed: {before:?} a move");
    println!("  after, repainted where it changed: {after:?} a move, {most} pixels at most");
    println!(
        "  a move repaints 1/{} of the picture and takes 1/{} of the time",
        whole / most,
        before.as_nanos() / after.as_nanos().max(1)
    );
    // The two ways make the same picture.
    assert!(presented == last_before, "the picture repainted where it changed is not the picture made whole");
    // The pixels are the same on every machine, so they are held exactly.
    assert!(most <= MOVE_PIXELS_BUDGET, "a move repainted {most} pixels");
    // Time depends on the machine and its load, so only the order is held.
    assert!(after < before, "{after:?} against {before:?}");
}
