//! Renderer parity PAR-15 (REQ-6765): `naplps::Validator` reads a stream as `Terminal::feed`
//! reads it, keeping no canvas: the same diagnostics and events, the same processing limit, and
//! the macros the stream defined. Its memory is measured in `tests/validator_memory.rs`.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::unwrap_used,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::limits::{MAX_ALL_MACRO_BYTES, MAX_MACRO_BYTES, MAX_PDI_BYTES};
use naplps::{Canvas, Event, Refusal, StrokeFont, Terminal, Validator};

const ESC: u8 = 0x1B;
const SO: u8 = 0x0E;
const SS2: u8 = 0x19;
const DEF_MACRO: u8 = 0x80;
const END: u8 = 0x85;
/// The macro set into G2 as a 96-character set (ANSI X3.110-1983 Table 1), with the further
/// intermediate 2/0 this renderer accepts.
const MACROS_INTO_G2: [u8; 4] = [ESC, 0x2E, 0x20, 0x7A];

/// A terminal as the receiver has it, with the repository's stroke font, on the canvas the
/// browser draws on.
fn terminal_reading(bytes: &[u8]) -> (Terminal, Vec<Event>) {
    let mut terminal = Terminal::new(4);
    terminal.set_font(StrokeFont::parse(include_str!("../../../fonts/neoteletext.strokes")).unwrap());
    let mut canvas = Canvas::new(480, 462).unwrap();
    let events = terminal.feed(&mut canvas, bytes);
    (terminal, events)
}

/// The stream of `exponential_macros_stop_at_the_processing_budget`: sixteen macros, each
/// calling the next sixty times, far past `MAX_PROCESSED_BYTES`.
fn exponential_macros() -> Vec<u8> {
    let mut bytes = MACROS_INTO_G2.to_vec();
    for number in 0x21..0x31u8 {
        bytes.extend_from_slice(&[DEF_MACRO, number]);
        for _ in 0..60 {
            bytes.extend_from_slice(&[SS2, number + 1]);
        }
    }
    bytes.extend_from_slice(&[DEF_MACRO, 0x31, b'x', END, SS2, 0x21, b'a']);
    bytes
}

#[test]
fn a_stream_past_the_processing_limit_is_refused_by_both() {
    let bytes = exponential_macros();
    let (terminal, terminal_events) = terminal_reading(&bytes);
    let mut validator = Validator::new();
    let events = validator.feed(&bytes);
    assert!(events.contains(&Event::LimitReached));
    assert_eq!(events, terminal_events);
    assert!(validator.diagnostics().count(Refusal::ProcessingLimit) > 0);
    assert_eq!(*validator.diagnostics(), terminal.diagnostics());
}

#[test]
fn defined_macros_names_exactly_the_macros_defined() {
    // Macros 2/0 and 7/15 defined, 2/1 defined then deleted by an empty definition, 2/2 a
    // transmit macro (DEFT MACRO, C1 8/2), which calling does nothing.
    let bytes =
        [DEF_MACRO, 0x20, b'a', DEF_MACRO, 0x7F, b'b', DEF_MACRO, 0x21, b'c', DEF_MACRO, 0x21, 0x82, 0x22, b'd', END];
    let mut validator = Validator::new();
    validator.feed(&bytes);
    let defined: Vec<usize> =
        validator.defined_macros().iter().enumerate().filter(|(_, on)| **on).map(|(at, _)| at).collect();
    assert_eq!(defined, [0, 0x7F - 0x20]);
}

#[test]
fn every_refusal_and_pass_is_the_terminals() {
    let mut streams: Vec<Vec<u8>> = Vec::new();
    // A macro longer than MAX_MACRO_BYTES.
    let mut long = vec![DEF_MACRO, 0x21];
    long.extend(std::iter::repeat_n(b'a', MAX_MACRO_BYTES + 10));
    long.push(END);
    streams.push(long);
    // Macros past MAX_ALL_MACRO_BYTES.
    let mut full = Vec::new();
    for number in 0x20..0x40u8 {
        full.extend_from_slice(&[DEF_MACRO, number]);
        full.extend(std::iter::repeat_n(b'a', MAX_ALL_MACRO_BYTES / 16));
    }
    full.push(END);
    streams.push(full);
    // A PDI's operands past MAX_PDI_BYTES, run by the byte after them.
    let mut pdi = vec![SO, 0x37];
    pdi.extend(std::iter::repeat_n(0x40, MAX_PDI_BYTES + 10));
    pdi.push(0x0F);
    streams.push(pdi);
    // A self-calling macro past MAX_MACRO_DEPTH; bytes of other layers passed over; an unknown
    // designation's null set.
    streams.push(vec![0x2E, 0x20, 0x7A, ESC, 0x2E, 0x20, 0x7A, DEF_MACRO, 0x21, SS2, 0x21, END, SS2, 0x21]);
    streams.push(vec![0x00, 0x10, b'a', ESC, 0x28, 0x5E, b'b', b'c']);
    for (index, bytes) in streams.iter().enumerate() {
        let (terminal, terminal_events) = terminal_reading(bytes);
        let mut validator = Validator::new();
        let events = validator.feed(bytes);
        assert_eq!(events, terminal_events, "stream {index}");
        assert_eq!(*validator.diagnostics(), terminal.diagnostics(), "stream {index}");
        assert!(validator.diagnostics().refused() > 0 || validator.diagnostics().passed_over > 0, "stream {index}");
    }
}

/// A PDI still collecting at the end of a stream runs at `finish`, as a terminal's does: a
/// polygon of more points than `MAX_VERTICES` (operands of three bytes a point, every one the
/// PDI may hold) is refused when it runs.
#[test]
fn finish_runs_a_pdi_still_collecting() {
    let mut bytes = vec![SO, 0x37];
    bytes.extend(std::iter::repeat_n(0x40, MAX_PDI_BYTES));
    let mut terminal = Terminal::new(4);
    let mut canvas = Canvas::new(480, 462).unwrap();
    terminal.feed(&mut canvas, &bytes);
    terminal.finish(&mut canvas);
    let mut validator = Validator::new();
    validator.feed(&bytes);
    assert_eq!(validator.diagnostics().count(Refusal::TooManyVertices), 0, "not yet run");
    validator.finish();
    assert_eq!(*validator.diagnostics(), terminal.diagnostics());
    assert_eq!(validator.diagnostics().count(Refusal::TooManyVertices), 1);
    assert_eq!(validator.diagnostics().count(Refusal::PdiTooLong), 0);
}

/// PAR-23 (with PAR-5): a character written back over the one before it by APB while colour
/// mode 2 is in force is counted, as a text part's mark over its letter is written: APB, the
/// supplementary set designated into G2 (ESC 2/10 7/12, Table 1), SS2 and the mark. Not in
/// colour mode 0, and not when something is drawn between.
#[test]
fn a_mark_written_over_its_letter_in_colour_mode_two_is_counted() {
    // SELECT COLOR (3/14) with two operands: colour mode 2 (section 5.3.2.6.3).
    let mode_two = [SO, 0x3E, 0x70, 0x4C, 0x0F];
    let mark = [b'a', 0x08, ESC, 0x2A, 0x7C, SS2, 0x41];
    let mut bytes = mode_two.to_vec();
    bytes.extend_from_slice(&mark);
    let (terminal, _) = terminal_reading(&bytes);
    let mut validator = Validator::new();
    validator.feed(&bytes);
    assert_eq!(validator.diagnostics().overwritten_in_mode_two, 1);
    assert_eq!(validator.diagnostics().first_overwritten_in_mode_two, Some(bytes.len() - 1));
    assert_eq!(*validator.diagnostics(), terminal.diagnostics());
    assert_eq!(validator.diagnostics().refused(), 0, "not a refusal");

    let mut colour_mode_zero = Validator::new();
    colour_mode_zero.feed(&mark);
    assert_eq!(colour_mode_zero.diagnostics().overwritten_in_mode_two, 0, "colour mode 0 keeps the letter");

    let mut moved_on = Validator::new();
    let mut bytes = mode_two.to_vec();
    bytes.extend_from_slice(&[b'a', 0x08, b'b', b'c']);
    moved_on.feed(&bytes);
    assert_eq!(moved_on.diagnostics().overwritten_in_mode_two, 1, "only the character right after APB");
    let mut cut = Validator::new();
    let mut bytes = mode_two.to_vec();
    bytes.extend_from_slice(&[b'a', 0x08, 0x0D, b'b']);
    cut.feed(&bytes);
    assert_eq!(cut.diagnostics().overwritten_in_mode_two, 0, "another control between ends it");
}
