//! REQ-6668 in `naplps-render`: `--teletext` draws every code of every one of NeoTeletext's
//! character sets as the engine's Noto Teletext glyph of the character the engine's code tables
//! give it, and the set names are the engine's in its order.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use std::collections::HashMap;
use std::fmt::Write as _;
use std::fs;
use std::path::PathBuf;
use std::process::Command;

use naplps::teletext::designation_of;
use naplps::{TELETEXT_SET_COUNT, TELETEXT_SETS};

const ESC: u8 = 0x1B;
const CR: u8 = 0x0D;
const LF: u8 = 0x0A;
/// SDC (1/10), a control with no effect on the display (ANSI X3.110-1983 section 6.1.6.4),
/// which ends a run of joined letters (PAR-14).
const SDC: u8 = 0x1A;
/// The plain Arabic-script sets, group 1001, whose letters join (PAR-14).
const JOINED_SETS: std::ops::RangeInclusive<u8> = 44..=51;
/// LS2 (ANSI X3.110-1983 Table 2) and the designation of a 96-character set into G2.
const LS2: [u8; 2] = [ESC, 0x6E];
const INTO_G2_96: u8 = 0x2E;
/// A canvas on which the default field is the 12 by 20 cell: 480 wide, 25/32 of 512 high.
const WIDTH: usize = 480;
const HEIGHT: usize = 400;
const CELL_WIDTH: usize = 12;
const CELL_HEIGHT: usize = 20;
const PER_LINE: usize = 16;
/// The bytes before a picture's pixels: `P6\n480 400\n255\n`, and the same for 480 by 500.
const HEADER: usize = 15;

/// The engine's checkout: `NEOTELETEXT_ENGINE`, or the sibling of this repository's checkout.
fn engine() -> PathBuf {
    std::env::var_os("NEOTELETEXT_ENGINE").map_or_else(
        || PathBuf::from(std::env::var_os("HOME").expect("HOME")).join("devel/neoteletext-renderer-teletext"),
        PathBuf::from,
    )
}

fn engine_file(path: &str) -> String {
    let path = engine().join(path);
    fs::read_to_string(&path)
        .unwrap_or_else(|error| panic!("{}: {error}: this test needs the engine's checkout", path.display()))
}

/// Renders `bytes` with `options` and returns the picture's bytes.
fn render(name: &str, bytes: &[u8], options: &[&str]) -> Vec<u8> {
    let base = PathBuf::from(env!("CARGO_TARGET_TMPDIR")).join(format!("teletext-{name}"));
    fs::create_dir_all(&base).unwrap();
    let page = base.join("page.nap");
    let out = base.join("page.ppm");
    fs::write(&page, bytes).unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_naplps-render")).args(options).arg(&page).arg(&out).output().unwrap();
    assert!(output.status.success(), "{}", String::from_utf8_lossy(&output.stderr));
    fs::read(out).unwrap()
}

#[test]
#[ignore = "needs the engine's checkout at ~/devel/neoteletext-renderer-teletext (or NEOTELETEXT_ENGINE); scripts/check.sh full runs it"]
fn the_sets_are_the_engines_font_sets_in_the_engines_order() {
    let source = engine_file("crates/neoteletext-core/src/glyphs/conformance.rs");
    let block = source.split("pub const FONT_SETS").nth(1).unwrap().split("];").next().unwrap();
    let names: Vec<&str> = block.split("(\"").skip(1).map(|rest| rest.split('"').next().unwrap()).collect();
    assert_eq!(names, TELETEXT_SETS, "naplps::TELETEXT_SETS must be the engine's FONT_SETS, in order");
}

/// The engine's glyph of each character, independently of the program: Unicode scalar to rows.
fn noto_glyphs() -> HashMap<u32, Vec<u16>> {
    let mut glyphs = HashMap::new();
    for file in
        ["noto-teletext.bdf", "noto-teletext-composed.bdf", "noto-teletext-arabic.bdf", "noto-teletext-japanese.bdf"]
    {
        let text = engine_file(&format!("third_party/noto/{file}"));
        for character in text.split("STARTCHAR").skip(1) {
            let encoding = character.lines().find_map(|line| line.strip_prefix("ENCODING ")).unwrap().parse().unwrap();
            let bitmap = character.split("BITMAP\n").nth(1).unwrap();
            let rows = bitmap
                .lines()
                .take_while(|line| *line != "ENDCHAR")
                .map(|row| u16::from_str_radix(row, 16).unwrap() >> 4)
                .collect();
            glyphs.insert(encoding, rows);
        }
    }
    glyphs
}

/// The character at `position` (`C/R`) of the set named `list_name` in the engine's list.
fn listed_character(list: &str, list_name: &str, position: &str) -> u32 {
    let wanted = format!("{list_name} {position}");
    let line = list
        .lines()
        .find(|line| {
            line.starts_with("U+")
                && line.split("; ").any(|usage| usage == wanted || usage.ends_with(&format!(" {wanted}")))
        })
        .unwrap_or_else(|| panic!("the list has no {wanted}"));
    u32::from_str_radix(&line[2..line.find(' ').unwrap()], 16).unwrap()
}

#[test]
#[ignore = "needs the engine's checkout at ~/devel/neoteletext-renderer-teletext (or NEOTELETEXT_ENGINE); scripts/check.sh full runs it"]
fn every_code_of_every_set_draws_the_engines_glyph_for_its_character() {
    let list = engine_file("crates/neoteletext-core/src/glyphs/required.txt");
    let glyphs = noto_glyphs();
    let engine = engine();
    for number in 0..u8::try_from(TELETEXT_SET_COUNT).unwrap() {
        // The list names a set with spaces where the engine's name has hyphens, and writes the
        // sets of its own beside their script without the script's name.
        let list_name = list_name(TELETEXT_SETS[usize::from(number)]);
        let (supplement, final_byte) = designation_of(number).unwrap();
        let mut bytes = vec![LF, LF, ESC, INTO_G2_96];
        bytes.extend(supplement);
        bytes.push(final_byte);
        bytes.extend(LS2);
        for (index, code) in (0x20u8..=0x7F).enumerate() {
            if index > 0 && index % PER_LINE == 0 {
                bytes.extend([CR, LF]);
            }
            // PAR-14: the plain Arabic-script sets join adjacent letters; a control between
            // each code (SDC, which does nothing else) draws every code as its own glyph.
            if JOINED_SETS.contains(&number) {
                bytes.push(SDC);
            }
            bytes.push(code);
        }
        let picture = render(
            &format!("set-{number}"),
            &bytes,
            &["--width", "480", "--height", "400", "--teletext", engine.to_str().unwrap()],
        );
        let is_lit = |x: usize, y: usize| picture[HEADER + (y * WIDTH + x) * 3..][..3] != [0, 0, 0];
        // Two lines down from the top of the display: the first line's field is lines 40 to 59.
        let top = 2 * CELL_HEIGHT;
        for (index, code) in (0x20u8..=0x7F).enumerate() {
            let position = format!("{:X}/{:X}", code >> 4, code & 0xF);
            let character = listed_character(&list, &list_name, &position);
            let rows = &glyphs[&character];
            for (row, bits) in rows.iter().enumerate() {
                for column in 0..CELL_WIDTH {
                    let want = bits >> (CELL_WIDTH - 1 - column) & 1 != 0;
                    let (x, y) = (index % PER_LINE * CELL_WIDTH + column, top + index / PER_LINE * CELL_HEIGHT + row);
                    assert_eq!(
                        is_lit(x, y),
                        want,
                        "{} {position} (U+{character:04X}) row {row} column {column}",
                        TELETEXT_SETS[usize::from(number)]
                    );
                }
            }
        }
        assert!(HEIGHT > top + 6 * CELL_HEIGHT);
    }
}

/// The engine's list's name for a set of [`TELETEXT_SETS`].
fn list_name(name: &str) -> String {
    let spaced = name.replace('-', " ");
    for (prefix, script) in [("G0 Cyrillic ", "Cyrillic"), ("G0 Arabic ", "Arabic")] {
        if let Some(rest) = spaced.strip_prefix(prefix) {
            return match rest {
                "1" | "2" | "3" => format!("G0 {script}{rest}"),
                "Plain" => "G0 ArabicPlain".to_owned(),
                _ => format!("G0 {rest}"),
            };
        }
    }
    spaced
}

/// The code point the engine's `forms.txt` gives `letter` in `form`.
fn engine_form(forms: &str, letter: u32, form: &str) -> u32 {
    let wanted = format!("U+{letter:04X} {form}");
    let line =
        forms.lines().find(|line| line.ends_with(&wanted)).unwrap_or_else(|| panic!("forms.txt has no {wanted}"));
    u32::from_str_radix(&line[2..line.find(' ').unwrap()], 16).unwrap()
}

/// Renderer parity PAR-14 (REQ-6765): with `--teletext`, the plain Arabic-script sets join. سلام
/// in `G0-Arabic-Persian` (set 44), in visual order م ا ل س, draws meem isolated, alef final,
/// lam medial and sin initial, the forms the engine's joining test `a_word_joins_right_to_left`
/// gives the same codes, each as the engine's Noto Teletext glyph of the code point its
/// `forms.txt` names for that form.
#[test]
#[ignore = "needs the engine's checkout at ~/devel/neoteletext-renderer-teletext (or NEOTELETEXT_ENGINE); scripts/check.sh full runs it"]
fn a_persian_word_joins_as_the_engine_joins_it() {
    const PERSIAN: u8 = 44;
    let list = engine_file("crates/neoteletext-core/src/glyphs/required.txt");
    let forms = engine_file("crates/neoteletext-core/src/glyphs/forms.txt");
    let glyphs = noto_glyphs();
    let (supplement, final_byte) = designation_of(PERSIAN).unwrap();
    let mut bytes = vec![LF, LF, ESC, INTO_G2_96];
    bytes.extend(supplement);
    bytes.push(final_byte);
    bytes.extend(LS2);
    // Meem 6/1, alef 4/6, lam 6/0, sin 5/4, and the form each takes.
    let word = [(0x61u8, None), (0x46, Some("final")), (0x60, Some("medial")), (0x54, Some("initial"))];
    bytes.extend(word.iter().map(|(code, _)| *code));
    let picture = render(
        "persian-joining",
        &bytes,
        &["--width", "480", "--height", "400", "--teletext", engine().to_str().unwrap()],
    );
    let is_lit = |x: usize, y: usize| picture[HEADER + (y * WIDTH + x) * 3..][..3] != [0, 0, 0];
    let top = 2 * CELL_HEIGHT;
    for (index, (code, form)) in word.iter().enumerate() {
        let position = format!("{:X}/{:X}", code >> 4, code & 0xF);
        let letter = listed_character(&list, "G0 Persian", &position);
        let drawn = form.map_or(letter, |form| engine_form(&forms, letter, form));
        let rows = &glyphs[&drawn];
        for (row, bits) in rows.iter().enumerate() {
            for column in 0..CELL_WIDTH {
                let want = bits >> (CELL_WIDTH - 1 - column) & 1 != 0;
                assert_eq!(
                    is_lit(index * CELL_WIDTH + column, top + row),
                    want,
                    "{position} (U+{letter:04X}) as U+{drawn:04X}, row {row} column {column}"
                );
            }
        }
        assert_ne!(form.map(|_| drawn), Some(letter), "a joined form is not the letter's own glyph");
    }
}

/// RAS-8's full page: 23 rows of 40 characters, row r column c the G0 Latin English code
/// 0x21 + ((r + c) mod 94).
const TEXT_ROWS: std::ops::RangeInclusive<u32> = 1..=23;
const TEXT_COLUMNS: u32 = 40;
/// The printable codes of a 94-character set, 2/1 to 7/14.
const FIRST_PRINTABLE: u32 = 0x21;
const PRINTABLE_CODES: u32 = 94;
/// NeoTeletext's set of the Latin English G0 table (`naplps::TELETEXT_SETS`).
const LATIN_ENGLISH: &str = "G0-Latin-English";
/// The operand bytes every NeoTeletext writer selects (RAS-6).
const OPERAND_BYTES: u8 = 6;
const SO: u8 = 0x0E;
const SI: u8 = 0x0F;
/// The first intermediate that designates a 94-character set into G0 (ANSI X3.110-1983
/// section 4.3.1.2).
const INTO_G0: u8 = 0x28;
/// RESET (section 5.3.2.9) clearing the display to nominal black (Table 15: b6 b5 b4 = 001).
const RESET_TO_BLACK: [u8; 3] = [0x20, 0x48, 0x40];
/// DOMAIN (section 5.3.2.2): its fixed-format byte 5/4 (one-byte single values, six-byte
/// multi-value operands, two dimensions; Figure 14) and the logical pel (0, 0).
const DOMAIN_SIX: [u8; 2] = [0x21, 0x54];
/// TEXT (section 5.3.2.3) and its two fixed-format bytes: no spacing change, path right, no
/// rotation; the cursor and the drawing point move together.
const TEXT: [u8; 3] = [0x22, 0x40, 0x40];
/// SELECT COLOR (section 5.3.2.6) with two single values: colour mode 2, drawing in entry 7
/// (white) on entry 8 (blue) in the default colour map of 16.
const MODE_TWO: [u8; 3] = [0x3E, 0x40 | (7 << 2), 0x40 | (8 << 2)];
/// POINT SET ABSOLUTE (section 5.3.3.1).
const POINT_SET: u8 = 0x24;
const WHITE: [u8; 3] = [255, 255, 255];
const BLUE: [u8; 3] = [0, 0, 255];
const BLACK: [u8; 3] = [0, 0, 0];
/// The raster, which `naplps-render` draws by default (RAS-11).
const RASTER_WIDTH: usize = 480;
const RASTER_HEIGHT: usize = 500;

/// The code of row `row`, column `column` of the page.
fn page_code(row: u32, column: u32) -> u8 {
    u8::try_from(FIRST_PRINTABLE + (row + column) % PRINTABLE_CODES).unwrap()
}

/// The page's bytes, written as RAS-8 says a writer writes text: a six-byte DOMAIN, the TEXT
/// field of 3,276 by 4,452 steps (`unit_steps` rounded down), and each row as one run from the
/// point of the dot (12 c, 20 r + 19) with c = 0, rounded down on both axes (`dot_steps`).
fn text_page() -> Vec<u8> {
    use naplps::{Rounding, dot_steps, multi_value_operand, unit_steps};
    let number = TELETEXT_SETS.iter().position(|name| *name == LATIN_ENGLISH).unwrap();
    let (supplement, final_byte) = designation_of(u8::try_from(number).unwrap()).unwrap();
    let mut bytes = vec![SO];
    bytes.extend(RESET_TO_BLACK);
    bytes.extend(DOMAIN_SIX);
    multi_value_operand(0, 0, OPERAND_BYTES, &mut bytes);
    bytes.extend(TEXT);
    let across = unit_steps(1, i64::from(TEXT_COLUMNS), OPERAND_BYTES, Rounding::Down);
    let up = unit_steps(20 * 25, 32 * 460, OPERAND_BYTES, Rounding::Down);
    assert_eq!((across, up), (3_276, 4_452), "RAS-8 item 1");
    multi_value_operand(across, up, OPERAND_BYTES, &mut bytes);
    bytes.extend(MODE_TWO);
    bytes.extend([SI, ESC, INTO_G0]);
    bytes.extend(supplement);
    bytes.push(final_byte);
    for row in TEXT_ROWS {
        let (x, y) = dot_steps(0, i64::from(20 * row + 19), 1, OPERAND_BYTES, Rounding::Down);
        bytes.extend([SO, POINT_SET]);
        multi_value_operand(x, y, OPERAND_BYTES, &mut bytes);
        bytes.push(SI);
        bytes.extend((0..TEXT_COLUMNS).map(|column| page_code(row, column)));
    }
    bytes
}

/// RAS-8's test, which every writer of NAPLPS text passes: the page written at six-byte
/// precision and drawn by `naplps-render` with the engine's Noto Teletext glyphs puts every
/// character exactly on its 12 by 20 cell, glyph column k on dot 12 c + k and glyph row j on
/// line 20 r + j, the glyph's dots in the drawing colour on the field's background (colour mode
/// 2), across a whole 40-cell run from one point; and nothing is written on rows 0 and 24. The
/// page's bytes are the shared example `naplps-text-page` (neoteletext-common
/// `docs/picture-examples.jsonl`), written to `naplps-text-page.hex` beside the picture.
#[test]
#[ignore = "needs the engine's checkout at ~/devel/neoteletext-renderer-teletext (or NEOTELETEXT_ENGINE); scripts/check.sh full runs it"]
fn a_full_page_of_text_puts_every_character_on_its_noto_cell() {
    let list = engine_file("crates/neoteletext-core/src/glyphs/required.txt");
    let glyphs = noto_glyphs();
    let page = text_page();
    let hex = page.iter().fold(String::new(), |mut hex, byte| {
        let _ = write!(hex, "{byte:02x}");
        hex
    });
    let base = PathBuf::from(env!("CARGO_TARGET_TMPDIR"));
    fs::write(base.join("naplps-text-page.hex"), format!("{hex}\n")).unwrap();
    let picture = render("text-page", &page, &["--teletext", engine().to_str().unwrap()]);
    let header = format!("P6\n{RASTER_WIDTH} {RASTER_HEIGHT}\n255\n");
    assert!(picture.starts_with(header.as_bytes()));
    let at = |x: usize, y: usize| -> [u8; 3] {
        picture[header.len() + (y * RASTER_WIDTH + x) * 3..][..3].try_into().unwrap()
    };
    let list_name = list_name(LATIN_ENGLISH);
    let mut wrong_cells = Vec::new();
    for row in TEXT_ROWS {
        for column in 0..TEXT_COLUMNS {
            let code = page_code(row, column);
            let position = format!("{:X}/{:X}", code >> 4, code & 0xF);
            let rows = &glyphs[&listed_character(&list, &list_name, &position)];
            let right = (0..CELL_HEIGHT).all(|line| {
                (0..CELL_WIDTH).all(|dot| {
                    let ink = rows[line] >> (CELL_WIDTH - 1 - dot) & 1 != 0;
                    let (x, y) = (12 * column as usize + dot, 20 * row as usize + line);
                    at(x, y) == if ink { WHITE } else { BLUE }
                })
            });
            if !right {
                wrong_cells.push((row, column));
            }
        }
    }
    assert_eq!(wrong_cells, [], "every one of the 920 cells is exactly its glyph");
    for y in (0..CELL_HEIGHT).chain(RASTER_HEIGHT - CELL_HEIGHT..RASTER_HEIGHT) {
        for x in 0..RASTER_WIDTH {
            assert_eq!(at(x, y), BLACK, "({x}, {y}) of rows 0 and 24 is not written");
        }
    }
}
