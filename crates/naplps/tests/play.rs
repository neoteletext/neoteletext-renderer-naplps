//! WAIT and BLINK played on the presentation clock's ticks (neoteletext-common
//! `docs/animation.md`, ANIM-20; REQ-6531). Each test names what it verifies.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::cast_possible_truncation,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::limits::{
    MAX_WAIT_HELD_BYTES, OBJECT_PICTURE_HEIGHT, OBJECT_PICTURE_WIDTH, TENTH_TICKS, WAIT_BUDGET_TICKS,
};
use naplps::{Canvas, Event, Player, Terminal};

const SO: u8 = 0x0E;
const ESC: u8 = 0x1B;
const SS2: u8 = 0x19;
const DEF_MACRO: u8 = 0x80;
const END: u8 = 0x85;
/// SELECT COLOR (section 5.3.2.6).
const SELECT_COLOUR: u8 = 0x3E;
/// RECTANGLE, filled, from the drawing point (section 5.3.3.4).
const RECT_FILLED: u8 = 0x31;
/// POINT SET, absolute (section 5.3.3.1).
const POINT_SET: u8 = 0x24;
/// WAIT and its fixed-format byte (section 5.3.2.8).
const WAIT: [u8; 2] = [0x3D, 0x5C];
const WIDTH: u32 = OBJECT_PICTURE_WIDTH;
const HEIGHT: u32 = OBJECT_PICTURE_HEIGHT;

/// A three-byte coordinate pair in the default domain: (`x`/256, `y`/256) of the unit screen
/// (section 5.3.2.2.3: three bits of x and three of y a byte, the sign first).
fn pair(x: u8, y: u8) -> [u8; 3] {
    let (x, y) = (u16::from(x), u16::from(y));
    let byte = |shift: u16| 0x40 | ((((x >> shift) & 7) as u8) << 3) | (((y >> shift) & 7) as u8);
    [byte(6), byte(3), byte(0)]
}

/// SELECT COLOR of colour-map entry `entry` of 16.
fn select(entry: u8) -> [u8; 2] {
    [SELECT_COLOUR, 0x40 | (entry << 2)]
}

/// PDI bytes drawing a filled rectangle of `entry` from (`x`, `y`) of size (`width`, `height`),
/// all in 256ths of the unit screen.
fn rectangle(entry: u8, x: u8, y: u8, width: u8, height: u8) -> Vec<u8> {
    let mut bytes = vec![SO];
    bytes.extend(select(entry));
    bytes.push(POINT_SET);
    bytes.extend(pair(x, y));
    bytes.push(RECT_FILLED);
    bytes.extend(pair(width, height));
    bytes
}

/// DEF MACRO `code` holding `body`.
fn define(code: u8, body: &[u8]) -> Vec<u8> {
    let mut bytes = vec![DEF_MACRO, code];
    bytes.extend_from_slice(body);
    bytes.push(END);
    bytes
}

/// Whether two pictures are the same; a failure then prints its message and not 307,200 pixels.
fn same(a: &Canvas, b: &Canvas) -> bool {
    a == b
}

fn count(canvas: &Canvas, entry: u8) -> usize {
    canvas.pixels().iter().fold(0, |count, &pixel| count + usize::from(pixel == entry))
}

/// Two rectangles with a WAIT of `tenths` between them.
fn two_scenes(tenths: u8) -> Vec<u8> {
    let mut stream = rectangle(3, 0, 0, 32, 16);
    stream.extend(WAIT);
    stream.push(0x40 | tenths);
    stream.extend(rectangle(6, 128, 100, 32, 16));
    stream
}

#[test]
fn a_wait_of_five_tenths_shows_the_earlier_picture_for_thirty_ticks() {
    // ANIM-20: on a WAIT of w tenths the stream stops for 6 x w ticks.
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    let mut player = Player::new();
    let mut events = player.push(&mut terminal, &mut canvas, &two_scenes(5));
    events.extend(player.end(&mut terminal, &mut canvas));
    assert_eq!(events, vec![Event::Wait(5)]);
    assert_eq!(player.waiting_ticks(), 5 * TENTH_TICKS);
    assert_eq!(player.ticks_to_next(&terminal), Some(30));
    assert!(player.held_bytes() > 0);
    let _ = player.advance(&mut terminal, &mut canvas, 29);
    assert_eq!((count(&canvas, 3) > 0, count(&canvas, 6)), (true, 0), "tick 29: still the earlier picture");
    let _ = player.advance(&mut terminal, &mut canvas, 1);
    assert!(count(&canvas, 6) > 0, "tick 30: what follows the WAIT is drawn");
    assert_eq!((player.tick(), player.waiting_ticks(), player.held_bytes()), (30, 0, 0));
    // The picture is the picture drawn without waiting.
    let mut at_once = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut plain = Terminal::new(4);
    let _ = plain.feed(&mut at_once, &two_scenes(5));
    let _ = plain.finish(&mut at_once);
    assert!(same(&canvas, &at_once));
}

#[test]
fn with_delays_off_no_wait_delays_anything() {
    // ANIM-20: the viewer's setting "Paint drawings gradually" off.
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    let mut player = Player::new();
    player.set_delays(false);
    let _ = player.push(&mut terminal, &mut canvas, &two_scenes(63));
    let _ = player.end(&mut terminal, &mut canvas);
    assert!(count(&canvas, 6) > 0);
    assert_eq!((player.waiting_ticks(), player.waited_ticks()), (0, 0));
}

#[test]
fn waits_are_played_for_at_most_the_budget() {
    // ANIM-20: WAIT_BUDGET_TICKS in a generation; after that each WAIT passes without delay.
    let mut stream = Vec::new();
    for _ in 0..12 {
        stream.extend(two_scenes(63)); // 63 tenths: 378 ticks each, 4,536 in all
    }
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    let mut player = Player::new();
    let _ = player.push(&mut terminal, &mut canvas, &stream);
    let mut ticks = 0u32;
    while player.waiting_ticks() > 0 {
        let _ = player.advance(&mut terminal, &mut canvas, 1);
        ticks += 1;
        assert!(ticks <= WAIT_BUDGET_TICKS, "more waiting than the budget");
    }
    assert_eq!((ticks, player.waited_ticks(), player.held_bytes()), (WAIT_BUDGET_TICKS, WAIT_BUDGET_TICKS, 0));
}

#[test]
fn a_wait_ends_at_once_when_more_arrives_than_may_be_held() {
    // ANIM-20: at most MAX_WAIT_HELD_BYTES are held.
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    let mut player = Player::new();
    let _ = player.push(&mut terminal, &mut canvas, &two_scenes(63));
    assert!(player.waiting_ticks() > 0);
    let held = player.held_bytes();
    let _ = player.push(&mut terminal, &mut canvas, &vec![0u8; MAX_WAIT_HELD_BYTES - held]);
    assert!(player.waiting_ticks() > 0, "exactly the limit is still held");
    assert_eq!(player.held_bytes(), MAX_WAIT_HELD_BYTES);
    let _ = player.push(&mut terminal, &mut canvas, &[0u8]);
    let _ = player.end(&mut terminal, &mut canvas);
    assert_eq!((player.waiting_ticks(), player.held_bytes()), (0, 0));
    assert!(count(&canvas, 6) > 0);
}

#[test]
fn a_wait_inside_a_macro_stops_the_macro_and_it_goes_on_afterwards() {
    // ANIM-20, for a WAIT a macro holds (section 6.2.2: a macro may hold any presentation code).
    let mut stream = define(0x20, &two_scenes(5));
    stream.extend([ESC, 0x2E, 0x20, 0x7A, SS2, 0x20]);
    stream.extend(rectangle(9, 64, 150, 16, 16));
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    let (taken, events) = terminal.feed_until_wait(&mut canvas, &stream);
    assert_eq!(events, vec![Event::Wait(5)]);
    assert!(taken < stream.len());
    assert_eq!((count(&canvas, 3) > 0, count(&canvas, 6), count(&canvas, 9)), (true, 0, 0));
    let (rest, events) = terminal.feed_until_wait(&mut canvas, &stream[taken..]);
    assert_eq!((rest, events), (stream.len() - taken, Vec::new()));
    let _ = terminal.finish(&mut canvas);
    assert!(count(&canvas, 6) > 0 && count(&canvas, 9) > 0, "the rest of the macro, then the stream");
    let mut at_once = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut plain = Terminal::new(4);
    let _ = plain.feed(&mut at_once, &stream);
    let _ = plain.finish(&mut at_once);
    assert!(same(&canvas, &at_once));
}

#[test]
fn a_blink_of_five_on_and_five_off_changes_the_palette_every_thirty_ticks() {
    // ANIM-20: BLINK is played by the colour map alone; no pixel is repainted.
    let mut stream = rectangle(1, 0, 0, 32, 16);
    stream.extend([0x3F, 0x40 | (7 << 2), 0x45, 0x45, 0x40]); // BLINK to entry 7: on 5, off 5, no delay
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    let mut player = Player::new();
    let _ = player.push(&mut terminal, &mut canvas, &stream);
    let _ = player.end(&mut terminal, &mut canvas);
    assert_eq!(terminal.palette().blinks().len(), 1);
    let _ = terminal.take_damage();
    let (own, other) = (terminal.palette().colour(1), terminal.palette().colour(7));
    let mut seen = Vec::new();
    for tick in 0..120u32 {
        let colour = player.colours(&terminal)[1];
        assert_eq!(colour, if (tick / 30) % 2 == 0 { other } else { own }, "tick {tick}");
        assert_eq!(player.ticks_to_blink(&terminal), Some(30 - tick % 30), "tick {tick}");
        if seen.last() != Some(&colour) {
            seen.push(colour);
        }
        let _ = player.advance(&mut terminal, &mut canvas, 1);
    }
    assert_eq!(seen, vec![other, own, other, own]);
    assert_eq!(terminal.take_damage(), None, "blinking repaints no pixel");
}
