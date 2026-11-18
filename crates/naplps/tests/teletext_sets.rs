//! REQ-6668 and DEC-6677: every NeoTeletext character set, designated by its private
//! designation in either form and invoked, draws every code as exactly the glyph given for it;
//! a private designation that is no set designates the null set (ANSI X3.110-1983 section
//! 4.3.2); and a designation takes effect at the next character.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::cast_possible_truncation,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::teletext::designation_of;
use naplps::{BitmapSet, Canvas, TELETEXT_SET_COUNT, Terminal};

/// A canvas on which the default character field (1/40 by 5/128 of the unit screen, section
/// 5.3.2.3) is 12 by 20 pixels, the teletext cell: 480 wide, and 25/32 of a unit 512 high.
const WIDTH: u32 = 480;
const HEIGHT: u32 = 400;
const CELL_WIDTH: u32 = 12;
const CELL_HEIGHT: u32 = 20;
/// Characters drawn on one line of the chart.
const PER_LINE: u32 = 16;
/// The codes of a set, 2/0 to 7/15, and the chart's lines.
const CODES: std::ops::RangeInclusive<u8> = 0x20..=0x7F;
const LINES: u32 = 6;
const ESC: u8 = 0x1B;
const SI: u8 = 0x0F;
const SO: u8 = 0x0E;
const SS2: u8 = 0x19;
const CR: u8 = 0x0D;
const LF: u8 = 0x0A;
/// LS2 and LS3 (Table 2).
const LS2: [u8; 2] = [ESC, 0x6E];
const LS3: [u8; 2] = [ESC, 0x6F];
const SPACE: u8 = 0x20;
const DELETE: u8 = 0x7F;
/// The 12 columns of a row.
const ROW_MASK: u16 = 0x0FFF;

/// A glyph unlike every other set's and code's, blank at 2/0 as every teletext set's is.
fn glyph(number: u8, code: u8) -> Vec<u16> {
    (0..CELL_HEIGHT)
        .map(|row| {
            if code == SPACE {
                return 0;
            }
            let seed = u32::from(number) * 7919 + u32::from(code) * 104_729 + row * 13;
            u16::try_from(seed.wrapping_mul(2_654_435_761) >> 13 & u32::from(ROW_MASK)).unwrap()
        })
        .collect()
}

fn set(number: u8) -> BitmapSet {
    let mut set = BitmapSet::new(12, 20).unwrap();
    for code in CODES {
        set.set_glyph(code, &glyph(number, code)).unwrap();
    }
    set
}

fn terminal() -> Terminal {
    let mut terminal = Terminal::new(4);
    for number in 0..TELETEXT_SET_COUNT as u8 {
        terminal.set_teletext_set(number, set(number)).unwrap();
    }
    terminal
}

/// The private designation of set `number` with first intermediate `slot`.
fn designate(slot: u8, number: u8) -> Vec<u8> {
    let (supplement, final_byte) = designation_of(number).unwrap();
    let mut bytes = vec![ESC, slot];
    bytes.extend(supplement);
    bytes.push(final_byte);
    bytes
}

/// The codes in chart order: 16 a line, each line ended by CR LF.
fn chart(codes: impl Iterator<Item = u8>) -> Vec<u8> {
    let mut bytes = Vec::new();
    for (index, code) in codes.enumerate() {
        if index > 0 && (index as u32).is_multiple_of(PER_LINE) {
            bytes.extend([CR, LF]);
        }
        bytes.push(code);
    }
    bytes
}

fn draw(bytes: &[u8]) -> Canvas {
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = terminal();
    // Two lines down, so that the first line's field lies wholly on the canvas.
    terminal.feed(&mut canvas, &[LF, LF]);
    terminal.feed(&mut canvas, bytes);
    terminal.finish(&mut canvas);
    canvas
}

fn lit(canvas: &Canvas, x: u32, y: u32) -> bool {
    canvas.pixel(x, y).is_some_and(|entry| entry != 0)
}

/// The top left pixel of the first character: where a solid glyph's pixels begin.
fn origin() -> (u32, u32) {
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    let mut solid = BitmapSet::new(12, 20).unwrap();
    solid.set_glyph(0x41, &[ROW_MASK; CELL_HEIGHT as usize]).unwrap();
    terminal.set_teletext_set(0, solid).unwrap();
    let mut bytes = vec![LF, LF];
    bytes.extend(designate(0x28, 0));
    bytes.push(0x41);
    terminal.feed(&mut canvas, &bytes);
    terminal.finish(&mut canvas);
    let pixels: Vec<(u32, u32)> =
        (0..HEIGHT).flat_map(|y| (0..WIDTH).map(move |x| (x, y))).filter(|&(x, y)| lit(&canvas, x, y)).collect();
    let left = pixels.iter().map(|p| p.0).min().unwrap();
    let top = pixels.iter().map(|p| p.1).min().unwrap();
    assert_eq!(pixels.len() as u32, CELL_WIDTH * CELL_HEIGHT, "the field is the 12 by 20 cell");
    assert!(pixels.iter().all(|&(x, y)| x - left < CELL_WIDTH && y - top < CELL_HEIGHT));
    (left, top)
}

/// Checks the chart's cell `index` holds the glyph `expected` (`None`: nothing drawn).
fn assert_cell(canvas: &Canvas, (left, top): (u32, u32), index: u32, expected: &[u16], what: &str) {
    let cell_x = left + index % PER_LINE * CELL_WIDTH;
    let cell_y = top + index / PER_LINE * CELL_HEIGHT;
    for row in 0..CELL_HEIGHT {
        for column in 0..CELL_WIDTH {
            let want = expected[row as usize] >> (CELL_WIDTH - 1 - column) & 1 != 0;
            assert_eq!(
                lit(canvas, cell_x + column, cell_y + row),
                want,
                "{what}: cell {index} row {row} column {column}"
            );
        }
    }
}

/// Everything outside the chart's cells is unlit.
fn assert_nothing_else(canvas: &Canvas, (left, top): (u32, u32), what: &str) {
    for y in 0..HEIGHT {
        for x in 0..WIDTH {
            let inside =
                (left..left + PER_LINE * CELL_WIDTH).contains(&x) && (top..top + LINES * CELL_HEIGHT).contains(&y);
            assert!(inside || !lit(canvas, x, y), "{what}: pixel ({x}, {y}) outside the chart is lit");
        }
    }
}

#[test]
fn every_code_of_every_set_in_the_96_character_form_draws_its_glyph() {
    let origin = origin();
    for number in 0..TELETEXT_SET_COUNT as u8 {
        // Into G2 as a 96-character set (2/14), invoked by LS2.
        let mut bytes = designate(0x2E, number);
        bytes.extend(LS2);
        bytes.extend(chart(CODES));
        let canvas = draw(&bytes);
        for (index, code) in CODES.enumerate() {
            assert_cell(&canvas, origin, index as u32, &glyph(number, code), &format!("set {number} code {code:#04x}"));
        }
        assert_nothing_else(&canvas, origin, &format!("set {number}"));
    }
}

#[test]
fn every_code_of_every_set_in_the_94_character_form_draws_its_glyph() {
    let origin = origin();
    let blank = [0; CELL_HEIGHT as usize];
    for number in 0..TELETEXT_SET_COUNT as u8 {
        // Into G0 as a 94-character set (2/8): GL holds G0 at power-up, and SI says so.
        let mut bytes = designate(0x28, number);
        bytes.push(SI);
        bytes.extend(chart(CODES));
        let canvas = draw(&bytes);
        for (index, code) in CODES.enumerate() {
            // Section 4.3.1.2: 2/0 is SPACE and 7/15 DELETE, which draws nothing.
            let expected = if code == SPACE || code == DELETE { blank.to_vec() } else { glyph(number, code) };
            assert_cell(&canvas, origin, index as u32, &expected, &format!("set {number} code {code:#04x}"));
        }
        assert_nothing_else(&canvas, origin, &format!("set {number}"));
    }
}

#[test]
fn g1_and_g3_and_a_single_shift_take_the_sets_too() {
    let origin = origin();
    // G1 by SO (2/13, 96 characters), G3 by LS3 (2/11, 94 characters), and SS2 from G2.
    let mut bytes = designate(0x2D, 17);
    bytes.extend(designate(0x2B, 40));
    bytes.extend(designate(0x2E, 53));
    bytes.extend([SO, 0x41]);
    bytes.extend(LS3);
    bytes.push(0x42);
    bytes.extend([SS2, 0x43]);
    let canvas = draw(&bytes);
    assert_cell(&canvas, origin, 0, &glyph(17, 0x41), "G1");
    assert_cell(&canvas, origin, 1, &glyph(40, 0x42), "G3");
    assert_cell(&canvas, origin, 2, &glyph(53, 0x43), "SS2");
}

#[test]
fn a_designation_mid_line_takes_effect_at_the_next_character() {
    let origin = origin();
    let mut bytes = designate(0x28, 15);
    bytes.extend(b"AB");
    bytes.extend(designate(0x28, 44));
    bytes.push(b'C');
    let canvas = draw(&bytes);
    assert_cell(&canvas, origin, 0, &glyph(15, b'A'), "before the switch");
    assert_cell(&canvas, origin, 1, &glyph(15, b'B'), "before the switch");
    assert_cell(&canvas, origin, 2, &glyph(44, b'C'), "after the switch");
}

#[test]
fn a_private_designation_that_is_no_set_designates_the_null_set() {
    let origin = origin();
    for unknown in [
        vec![ESC, 0x28, 0x23, 0x37],       // number 55
        vec![ESC, 0x28, 0x23, 0x3F],       // number 63
        vec![ESC, 0x28, 0x20, 0x30],       // the SELECT-DRCS indicator: these sets are not DRCS (DEC-6669)
        vec![ESC, 0x28, 0x21, 0x21, 0x30], // a third intermediate
        vec![ESC, 0x24, 0x28, 0x30],       // a multiple-byte private set into G0
        vec![ESC, 0x24, 0x30],             // the same, in the form without a slot
    ] {
        // The null set's codes are null operations: nothing is drawn and the cursor stays, so
        // the set designated after it draws in the first cell.
        let mut bytes = unknown.clone();
        bytes.extend(b"ABC");
        bytes.extend(designate(0x28, 1));
        bytes.push(b'D');
        let canvas = draw(&bytes);
        assert_cell(&canvas, origin, 0, &glyph(1, b'D'), &format!("{unknown:02x?}"));
        assert_nothing_else(&canvas, origin, &format!("{unknown:02x?}"));
        for index in 1..PER_LINE {
            assert_cell(&canvas, origin, index, &[0; CELL_HEIGHT as usize], &format!("{unknown:02x?}"));
        }
    }
}

#[test]
fn a_set_without_glyphs_advances_the_cursor_and_draws_nothing() {
    let origin = origin();
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    terminal.set_teletext_set(1, set(1)).unwrap();
    let mut bytes = vec![LF, LF];
    bytes.extend(designate(0x28, 2));
    bytes.extend(b"AB");
    bytes.extend(designate(0x28, 1));
    bytes.push(b'C');
    terminal.feed(&mut canvas, &bytes);
    terminal.finish(&mut canvas);
    assert_cell(&canvas, origin, 0, &[0; CELL_HEIGHT as usize], "no glyphs");
    assert_cell(&canvas, origin, 2, &glyph(1, b'C'), "two cells on");
}

#[test]
fn a_set_number_past_the_last_is_refused() {
    let mut terminal = Terminal::new(4);
    assert_eq!(terminal.set_teletext_set(TELETEXT_SET_COUNT as u8, set(0)), Err(naplps::Error::Bitmap));
}

#[test]
fn the_screen_colour_follows_clear_screen() {
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    assert_eq!(terminal.screen_colour(), 0, "nominal black at power-up");
    // RESET with 010 in bits 4 to 6 (Table 15): the display is cleared to the drawing colour.
    terminal.feed(&mut canvas, &[SO, 0x20, 0x50, 0x40]);
    terminal.finish(&mut canvas);
    assert_eq!(terminal.screen_colour(), canvas.pixel(0, 0).unwrap());
    assert_ne!(terminal.screen_colour(), 0);
}
