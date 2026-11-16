//! REQ-6408 item 1: NeoTeletext's own stroke font, `fonts/neoteletext.strokes`,
//! parses whole and has a glyph for every position of the primary set and
//! none for the supplementary set.

use naplps::{FontSet, StrokeFont};

/// The font, as `scripts/make_font.py` writes it.
const FONT: &str = include_str!("../../../fonts/neoteletext.strokes");
/// The primary set's positions: 2/1 to 7/14 (ANSI X3.110-1983 section 4.2).
const FIRST: u8 = 0x21;
const LAST: u8 = 0x7e;

#[test]
fn the_font_has_a_glyph_for_every_primary_position() {
    let font = StrokeFont::parse(FONT).expect("the font parses");
    for code in FIRST..=LAST {
        let glyph = font.glyph(FontSet::Primary, code).unwrap_or_else(|| panic!("no glyph for {code:#04x}"));
        assert!(!glyph.segments.is_empty(), "{code:#04x} draws nothing");
        assert!(
            font.glyph(FontSet::Supplementary, code).is_none(),
            "{code:#04x}: the supplementary set has no glyphs yet"
        );
    }
}
