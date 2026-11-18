//! REQ-6408 item 1 and the supplementary set's glyphs (DEC-6638 item 5, TODO-5791): NeoTeletext's
//! own stroke font, `fonts/neoteletext.strokes`, parses whole and has a glyph for every position
//! of the primary set and of the supplementary set, and an accent sent before a letter is drawn
//! over (or, for the cedilla, under) that letter.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::{Canvas, FontSet, StrokeFont, Terminal};

/// The font, as `scripts/make_font.py` writes it.
const FONT: &str = include_str!("../../../fonts/neoteletext.strokes");
/// The positions of a 94-character set: 2/1 to 7/14 (ANSI X3.110-1983 section 4.2).
const FIRST: u8 = 0x21;
const LAST: u8 = 0x7e;
/// The non-spacing accents of the supplementary set, 4/0 to 4/15 (section 5.2: column 4 is nonspacing).
const ACCENTS: core::ops::RangeInclusive<u8> = 0x40..=0x4F;
/// SS2: the next byte comes from G2, the supplementary set at power-up (section 4.3.2).
const SS2: u8 = 0x19;
/// Supplementary 4/2, the acute accent, and 4/11, the cedilla (section 5.2, Figure 8).
const ACUTE: u8 = 0x42;
const CEDILLA: u8 = 0x4B;
/// The canvas the pages are drawn on: PP3's VGA screen.
const WIDTH: u32 = 640;
const HEIGHT: u32 = 480;

#[test]
fn the_font_has_a_glyph_for_every_position_of_both_sets() {
    let font = StrokeFont::parse(FONT).expect("the font parses");
    for set in [FontSet::Primary, FontSet::Supplementary] {
        for code in FIRST..=LAST {
            let glyph = font.glyph(set, code).unwrap_or_else(|| panic!("{set:?} has no glyph for {code:#04x}"));
            assert!(!glyph.segments.is_empty(), "{set:?} {code:#04x} draws nothing");
        }
    }
}

/// The page drawn with the font: the pixels lit (not the background entry 0) as (x, y) pairs.
fn lit(bytes: &[u8]) -> Vec<(u32, u32)> {
    let mut canvas = Canvas::new(WIDTH, HEIGHT).expect("a canvas");
    let mut terminal = Terminal::new(4);
    terminal.set_font(StrokeFont::parse(FONT).expect("the font parses"));
    terminal.feed(&mut canvas, bytes);
    terminal.finish(&mut canvas);
    let mut pixels = Vec::new();
    for y in 0..canvas.height() {
        for x in 0..canvas.width() {
            if canvas.pixel(x, y) != Some(0) {
                pixels.push((x, y));
            }
        }
    }
    pixels
}

#[test]
fn an_acute_accent_is_drawn_above_its_letter_and_the_letter_is_unchanged() {
    let plain = lit(b"e");
    let accented = lit(&[SS2, ACUTE, b'e']);
    assert!(!plain.is_empty(), "e draws");
    assert!(plain.iter().all(|pixel| accented.contains(pixel)), "the letter is drawn whole under its accent");
    let added: Vec<_> = accented.iter().filter(|pixel| !plain.contains(pixel)).collect();
    assert!(!added.is_empty(), "the accent draws");
    // Screen y grows downward: the accent lies wholly above the letter's top.
    let letter_top = plain.iter().map(|&(_, y)| y).min().expect("e draws");
    assert!(added.iter().all(|&&(_, y)| y < letter_top), "the acute accent lies above the letter: {added:?}");
}

#[test]
fn a_cedilla_is_drawn_below_its_letter() {
    let plain = lit(b"c");
    let accented = lit(&[SS2, CEDILLA, b'c']);
    let added: Vec<_> = accented.iter().filter(|pixel| !plain.contains(pixel)).collect();
    assert!(!added.is_empty(), "the cedilla draws");
    let letter_bottom = plain.iter().map(|&(_, y)| y).max().expect("c draws");
    assert!(added.iter().any(|&&(_, y)| y > letter_bottom), "the cedilla reaches below the letter: {added:?}");
}

#[test]
fn every_supplementary_spacing_character_draws_and_advances() {
    for code in (FIRST..=LAST).filter(|code| !ACCENTS.contains(code)) {
        let one = lit(&[SS2, code]);
        assert!(!one.is_empty(), "supplementary {code:#04x} draws");
        // A spacing character moves the cursor on, so a second copy lands beside the first.
        let two = lit(&[SS2, code, SS2, code]);
        assert!(two.len() > one.len(), "supplementary {code:#04x} advances the cursor");
    }
}
