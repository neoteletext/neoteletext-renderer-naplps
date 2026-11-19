//! The diagnostics an authoring check reports (DEC-6638 item 7, row 9.3): bytes the renderer
//! passed over and work it refused at a bound, with the offset of the first of each.
#![allow(clippy::arithmetic_side_effects, reason = "a test: fixed inputs within range, and failure is a panic")]

use naplps::limits::{MAX_MACRO_BYTES, MAX_PDI_BYTES};
use naplps::{Canvas, Refusal, Terminal};

const SO: u8 = 0x0E;
const ESC: u8 = 0x1B;
const DEF_MACRO: u8 = 0x80;
const END: u8 = 0x85;
/// RECTANGLE, filled, from the drawing point (section 5.3.3.4).
const RECT_FILLED: u8 = 0x31;
/// PP3's VGA screen: these tests draw a stream alone and place nothing NeoTeletext defines, so
/// the size is the oracle's (`docs/naplps-raster.md` section 1, out of scope of DEC-6853).
const WIDTH: u32 = 640;
/// See [`WIDTH`].
const HEIGHT: u32 = 480;

/// A terminal that has drawn `bytes` as a whole page.
fn drawn(bytes: &[u8]) -> Terminal {
    let mut terminal = Terminal::new(4);
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    terminal.feed(&mut canvas, bytes);
    terminal.finish(&mut canvas);
    terminal
}

#[test]
fn a_clean_stream_has_nothing_to_report() {
    // DEF MACRO 2/0 holding a filled rectangle, then text.
    let terminal = drawn(&[DEF_MACRO, 0x20, SO, RECT_FILLED, 0x48, 0x40, 0x40, END, b'H', b'i']);
    assert_eq!(terminal.diagnostics().passed_over, 0);
    assert_eq!(terminal.diagnostics().refused(), 0);
    assert_eq!(terminal.diagnostics().first_refused, None);
}

#[test]
fn bytes_passed_over_are_counted_from_their_first_offset() {
    let mut terminal = Terminal::new(4);
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    // 0/1 belongs to another layer (section 6.1); in the PDI set, 4/1 is an operand byte with no
    // command before it; ESC 2/8 7/14 designates an unknown set into G0, a null set (section
    // 4.3.2), whose next byte is passed over too.
    let bytes = [b'A', 0x01, SO, 0x41, ESC, 0x28, 0x7E, 0x0F, b'B'];
    terminal.feed(&mut canvas, &bytes);
    terminal.finish(&mut canvas);
    let diagnostics = terminal.diagnostics();
    assert_eq!(diagnostics.passed_over, 3);
    assert_eq!(diagnostics.first_passed_over, Some(1));
    assert_eq!(diagnostics.refused(), 0);
}

#[test]
fn work_refused_at_a_bound_is_counted_by_kind() {
    let mut terminal = Terminal::new(4);
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    // A macro definition one byte longer than the limit, of data bytes that do nothing.
    let mut bytes = vec![DEF_MACRO, 0x22];
    bytes.extend(std::iter::repeat_n(0x41, MAX_MACRO_BYTES + 1));
    bytes.push(END);
    let offset = bytes.len();
    // A PDI with three bytes more than the limit of operands.
    bytes.extend([SO, RECT_FILLED]);
    bytes.extend(std::iter::repeat_n(0x40, MAX_PDI_BYTES + 3));
    bytes.push(0x0F);
    terminal.feed(&mut canvas, &bytes);
    terminal.finish(&mut canvas);
    let diagnostics = terminal.diagnostics();
    assert_eq!(diagnostics.count(Refusal::MacroTooLong), 1);
    assert_eq!(diagnostics.count(Refusal::PdiTooLong), 3);
    assert_eq!(diagnostics.refused(), 4);
    assert!(diagnostics.first_refused.is_some_and(|first| first < offset), "{:?}", diagnostics.first_refused);
}

#[test]
fn a_macro_calling_itself_is_refused_at_the_depth_limit() {
    let mut terminal = Terminal::new(4);
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    // DEF MACRO 2/1 holding a call of itself, then a call (ESC 2/8 7/10 puts the macro set in
    // G0, section 6.2.2).
    let bytes = [DEF_MACRO, 0x21, 0x21, END, ESC, 0x28, 0x7A, 0x21];
    terminal.feed(&mut canvas, &bytes);
    assert_eq!(terminal.diagnostics().count(Refusal::MacroTooDeep), 1);
}
