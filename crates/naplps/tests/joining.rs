//! Renderer parity PAR-14 (REQ-6765): the letters of a joined teletext set, the plain
//! Arabic-script sets 44 to 51, are drawn in the forms their neighbours give them, by the
//! engine's rule (REQ-CHR-015), and a run ends at a control code, a change of the set in use
//! and any other set's character.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::unwrap_used,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::JoinForm::{Final, Initial, Isolated, Medial};
use naplps::teletext::designation_of;
use naplps::{BitmapSet, Canvas, JoinForm, JoiningType, Terminal};

const ESC: u8 = 0x1B;
const LF: u8 = 0x0A;
/// LS2 (ANSI X3.110-1983 section 4.3.2, Table 2): G2 into the in-use table, locking.
const LS2: [u8; 2] = [ESC, 0x6E];
/// The intermediate designating a 96-character set into G2 (Table 1).
const INTO_G2_96: u8 = 0x2E;
/// SDC (1/10): a C0 control with no effect (section 6.1.6.4), which ends a run.
const SDC: u8 = 0x1A;
/// WORD WRAP ON (C1 9/5) in its 7-bit form, ESC 5/5 (section 6.2.7.11).
const WORD_WRAP_ON: [u8; 2] = [ESC, 0x55];
/// A canvas on which the default character field is the engine's 12 by 20 cell: 480 wide, and
/// 400 high, 25/32 of a unit screen of 512 lines whose 5/128 field is 20 lines.
const WIDTH: u32 = 480;
const HEIGHT: u32 = 400;
const CELL_WIDTH: u8 = 12;
const CELL_HEIGHT: u8 = 20;
/// After two line feeds the field's top is the third row of cells.
const TOP: u32 = 2 * CELL_HEIGHT as u32;
/// The set number of `G0-Arabic-Persian` (`naplps::TELETEXT_SETS`; the engine's `FONT_SETS`).
const PERSIAN: u8 = 44;

/// The engine's tables for the letters these tests write, a fixture taken from the engine at
/// `livedevelopment` 3e5ddb03: each letter's position in `G0 Persian` from
/// `crates/neoteletext-core/src/glyphs/required.txt`, and its joining type from
/// `crates/neoteletext-core/src/charset/arabic_script.rs`'s `JOINING_TYPES`.
const SIN: (u8, JoiningType) = (0x54, JoiningType::Dual); // U+0633, 5/4
const LAM: (u8, JoiningType) = (0x60, JoiningType::Dual); // U+0644, 6/0
const ALEF: (u8, JoiningType) = (0x46, JoiningType::Right); // U+0627, 4/6
const MEEM: (u8, JoiningType) = (0x61, JoiningType::Dual); // U+0645, 6/1
const BEH: (u8, JoiningType) = (0x47, JoiningType::Dual); // U+0628, 4/7
const HAMZA: (u8, JoiningType) = (0x40, JoiningType::None); // U+0621, 4/0
/// The tatweel, join-causing in the engine, which joins as a dual-joining letter does.
const TATWEEL: (u8, JoiningType) = (0x69, JoiningType::Dual); // U+0640, 6/9
/// A code this fixture makes a combining mark, to test transparent codes: Persian 7/0 is a
/// SPACE in the engine's table, so no letter is lost.
const MARK: (u8, JoiningType) = (0x70, JoiningType::Transparent);
const LETTERS: [(u8, JoiningType); 8] = [SIN, LAM, ALEF, MEEM, BEH, HAMZA, TATWEEL, MARK];

const FORMS: [JoinForm; 4] = [Isolated, Final, Initial, Medial];

/// The row of a cell a form's glyph lights, whole: each form its own, so that a cell says
/// which form was drawn.
fn form_row(form: JoinForm) -> u32 {
    2 + 4 * u32::try_from(FORMS.iter().position(|each| *each == form).unwrap()).unwrap()
}

/// Set 44 with the fixture's letters, each form's glyph lighting its own row.
fn persian() -> BitmapSet {
    let mut set = BitmapSet::new(CELL_WIDTH, CELL_HEIGHT).unwrap();
    let full = (1u16 << CELL_WIDTH) - 1;
    for (code, joining) in LETTERS {
        set.set_joining(code, joining).unwrap();
        for form in FORMS {
            let mut rows = vec![0u16; usize::from(CELL_HEIGHT)];
            rows[form_row(form) as usize] = full;
            set.set_form_glyph(code, form, &rows).unwrap();
        }
    }
    set
}

/// The bytes that designate set 44 into G2 as a 96-character set and invoke it, two lines down.
fn preamble() -> Vec<u8> {
    let (supplement, final_byte) = designation_of(PERSIAN).unwrap();
    let mut bytes = vec![LF, LF, ESC, INTO_G2_96];
    bytes.extend(supplement);
    bytes.push(final_byte);
    bytes.extend(LS2);
    bytes
}

fn terminal() -> Terminal {
    let mut terminal = Terminal::new(4);
    terminal.set_teletext_set(PERSIAN, persian()).unwrap();
    terminal
}

/// Draws `text` after the preamble, fed whole, and returns the canvas.
fn draw(text: &[u8]) -> Canvas {
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = terminal();
    let mut bytes = preamble();
    bytes.extend_from_slice(text);
    terminal.feed(&mut canvas, &bytes);
    terminal.finish(&mut canvas);
    canvas
}

/// The form drawn in each of the first `cells` cells of the line, `None` for an empty cell.
fn forms(canvas: &Canvas, cells: u32) -> Vec<Option<JoinForm>> {
    (0..cells)
        .map(|cell| {
            let x = cell * u32::from(CELL_WIDTH) + u32::from(CELL_WIDTH) / 2;
            let lit: Vec<JoinForm> =
                FORMS.into_iter().filter(|form| canvas.pixel(x, TOP + form_row(*form)) != Some(0)).collect();
            assert!(lit.len() <= 1, "cell {cell} holds more than one form: {lit:?}");
            lit.first().copied()
        })
        .collect()
}

fn codes(letters: &[(u8, JoiningType)]) -> Vec<u8> {
    letters.iter().map(|(code, _)| *code).collect()
}

/// سلام, in visual order م ا ل س, read right to left: sin initial, lam medial, alef final,
/// meem isolated, since alef does not join what follows. The engine's joining test
/// `a_word_joins_right_to_left` (`crates/neoteletext-core/src/joining/tests.rs`) gives these
/// forms for the same codes in visual order: isolated, final, medial, initial.
#[test]
fn a_persian_word_draws_the_forms_the_teletext_renderer_draws() {
    let canvas = draw(&codes(&[MEEM, ALEF, LAM, SIN]));
    assert_eq!(forms(&canvas, 4), [Some(Isolated), Some(Final), Some(Medial), Some(Initial)]);
}

/// The engine's `breaks_ligature_and_private_forms` and `a_letter_beside_a_tatweel_joins_it`:
/// three behs join; hamza joins nothing; a tatweel joins both sides.
#[test]
fn the_engines_other_joining_cases() {
    let canvas = draw(&codes(&[BEH, BEH, BEH]));
    assert_eq!(forms(&canvas, 3), [Some(Final), Some(Medial), Some(Initial)]);
    let canvas = draw(&codes(&[BEH, HAMZA, BEH]));
    assert_eq!(forms(&canvas, 3), [Some(Isolated); 3]);
    let canvas = draw(&codes(&[BEH, TATWEEL, BEH]));
    assert_eq!(forms(&canvas, 3), [Some(Final), Some(Medial), Some(Initial)]);
}

#[test]
fn a_run_ends_at_a_control_code_and_at_a_change_of_the_set_in_use() {
    let mut text = codes(&[BEH, BEH]);
    text.push(SDC);
    text.push(BEH.0);
    let canvas = draw(&text);
    assert_eq!(forms(&canvas, 3), [Some(Final), Some(Initial), Some(Isolated)], "SDC ends the run");
    // LS2 again between the letters: the set in use is reinvoked, an escape sequence ends it.
    let mut text = codes(&[BEH, BEH]);
    text.extend(LS2);
    text.push(BEH.0);
    let canvas = draw(&text);
    assert_eq!(forms(&canvas, 3), [Some(Final), Some(Initial), Some(Isolated)], "an escape sequence ends the run");
    // A space is the primary set's SPACE (section 4.3.1.2) and ends the run.
    let canvas = draw(&[BEH.0, BEH.0, 0x20, BEH.0]);
    assert_eq!(forms(&canvas, 4), [Some(Final), Some(Initial), None, Some(Isolated)]);
}

/// A transparent code takes no part: the letters on either side join across it, and it keeps
/// its own glyph in its own cell.
#[test]
fn a_transparent_code_keeps_its_glyph_and_the_letters_join_across_it() {
    let canvas = draw(&codes(&[BEH, MARK, BEH]));
    assert_eq!(forms(&canvas, 3), [Some(Final), Some(Isolated), Some(Initial)]);
    let canvas = draw(&codes(&[MARK, BEH, BEH, MARK]));
    assert_eq!(forms(&canvas, 4), [Some(Isolated), Some(Final), Some(Initial), Some(Isolated)]);
}

/// A set without joining data draws every code as its own glyph.
#[test]
fn a_set_without_joining_data_is_not_joined() {
    let mut set = BitmapSet::new(CELL_WIDTH, CELL_HEIGHT).unwrap();
    let mut rows = vec![0u16; usize::from(CELL_HEIGHT)];
    rows[form_row(Isolated) as usize] = (1 << CELL_WIDTH) - 1;
    set.set_glyph(BEH.0, &rows).unwrap();
    let mut terminal = Terminal::new(4);
    terminal.set_teletext_set(PERSIAN, set).unwrap();
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut bytes = preamble();
    bytes.extend([BEH.0; 3]);
    terminal.feed(&mut canvas, &bytes);
    terminal.finish(&mut canvas);
    assert_eq!(forms(&canvas, 3), [Some(Isolated); 3]);
}

/// The picture does not depend on how the stream was divided: a letter held back at the end of
/// one call takes its form from the next call's first byte.
#[test]
fn joining_holds_across_calls() {
    let mut bytes = preamble();
    bytes.extend(codes(&[MEEM, ALEF, LAM, SIN]));
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = terminal();
    for byte in &bytes {
        terminal.feed(&mut canvas, core::slice::from_ref(byte));
    }
    terminal.finish(&mut canvas);
    assert_eq!(canvas, draw(&codes(&[MEEM, ALEF, LAM, SIN])));
}

/// In word wrap mode the word is buffered with each letter's form (section 6.2.7.11).
#[test]
fn joined_forms_survive_word_wrap() {
    let mut text = WORD_WRAP_ON.to_vec();
    text.extend(codes(&[BEH, BEH, BEH]));
    text.push(0x20);
    let canvas = draw(&text);
    assert_eq!(forms(&canvas, 3), [Some(Final), Some(Medial), Some(Initial)]);
}
