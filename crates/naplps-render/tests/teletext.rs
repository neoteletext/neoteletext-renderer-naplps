//! REQ-6668 in `naplps-render`: `--teletext` draws every code of every one of NeoTeletext's
//! character sets as the engine's Noto Teletext glyph of the character the engine's code tables
//! give it, and the set names are the engine's in its order.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::process::Command;

use naplps::teletext::designation_of;
use naplps::{TELETEXT_SET_COUNT, TELETEXT_SETS};

const ESC: u8 = 0x1B;
const CR: u8 = 0x0D;
const LF: u8 = 0x0A;
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
