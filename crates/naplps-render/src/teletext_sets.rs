//! NeoTeletext's character sets, read from the engine's checkout (REQ-6668, DEC-6677): the
//! code of every character of every set from the engine's generated list
//! `crates/neoteletext-core/src/glyphs/required.txt` (written by `cargo xtask glyphs` from its
//! code tables), and each character's 12 by 20 glyph from the Noto Teletext BDF files in
//! `third_party/noto/`. The glyphs are the project's own font and nothing else (DEC-6669).
//!
//! The plain Arabic-script sets 44 to 51 (group 1001) are given their joining data as well
//! (renderer parity PAR-14, REQ-6765): each letter's joining type from the engine's
//! `JOINING_TYPES` table (`crates/neoteletext-core/src/charset/arabic_script.rs`), and the glyph
//! of each of its joined forms from the code point the engine's generated list
//! `crates/neoteletext-core/src/glyphs/forms.txt` gives it, so that the renderer joins them as
//! the teletext renderer does. Nothing of either table is copied here.

use std::collections::HashMap;
use std::fs;
use std::path::Path;

use naplps::{BitmapSet, JoinForm, JoiningType, TELETEXT_SET_COUNT, TELETEXT_SETS};

/// The engine's list of every character a set must draw, under its checkout.
pub(crate) const REQUIRED_LIST: &str = "crates/neoteletext-core/src/glyphs/required.txt";
/// The engine's list of every joined form a font draws: `U+FORM U+LETTER form`.
pub(crate) const FORMS_LIST: &str = "crates/neoteletext-core/src/glyphs/forms.txt";
/// The engine's source holding each group 1001 letter's joining type, in its `JOINING_TYPES`.
pub(crate) const JOINING_SOURCE: &str = "crates/neoteletext-core/src/charset/arabic_script.rs";
/// The plain Arabic-script sets, group 1001: `G0-Arabic-Persian` to `G0-Arabic-Plain`, set
/// numbers 44 to 51 (the engine's `FONT_SETS`; PAR-14).
pub(crate) const JOINED_SETS: core::ops::RangeInclusive<usize> = 44..=51;
/// The Noto Teletext font, four files of one font (the engine's `third_party/noto/PROVENANCE.md`).
pub(crate) const NOTO_FILES: [&str; 4] = [
    "third_party/noto/noto-teletext.bdf",
    "third_party/noto/noto-teletext-composed.bdf",
    "third_party/noto/noto-teletext-arabic.bdf",
    "third_party/noto/noto-teletext-japanese.bdf",
];
/// The engine's cell: 12 pixels by 20 lines (its `CELL_WIDTH` and `CELL_HEIGHT`).
pub(crate) const CELL_WIDTH: u8 = 12;
/// See [`CELL_WIDTH`].
pub(crate) const CELL_HEIGHT: u8 = 20;
/// The largest list or font file read: four megabytes, far beyond the engine's (the list is
/// 127 kilobytes, the largest font 157).
const MAX_FILE_BYTES: u64 = 4 * 1024 * 1024;
/// Characters one BDF file may hold: the engine's REQ-FNT-002 allows 1,024.
const MAX_BDF_CHARACTERS: usize = 1024;
/// The bits of a BDF row of a 12-pixel glyph: two bytes, the leftmost pixel the top bit.
const BDF_ROW_BITS: u32 = 16;

/// Each set's name in the engine's list, in the order of [`TELETEXT_SETS`].
const LIST_NAMES: [&str; TELETEXT_SET_COUNT] = [
    "G0 Latin",
    "G0 Latin English",
    "G0 Latin German",
    "G0 Latin SwedishFinnishHungarian",
    "G0 Latin Italian",
    "G0 Latin French",
    "G0 Latin PortugueseSpanish",
    "G0 Latin CzechSlovak",
    "G0 Latin Polish",
    "G0 Latin Turkish",
    "G0 Latin SerbianCroatianSlovenian",
    "G0 Latin Rumanian",
    "G0 Latin Estonian",
    "G0 Latin LettishLithuanian",
    "G0 Cyrillic1",
    "G0 Cyrillic2",
    "G0 Cyrillic3",
    "G0 Greek",
    "G0 Arabic",
    "G0 Hebrew",
    "G2 Latin",
    "G2 Cyrillic",
    "G2 Greek",
    "G2 Arabic",
    "G0 Latin HausaFula",
    "G0 Latin WestAfrican",
    "G0 Latin Ewe",
    "G0 Latin KabyleTamazight",
    "G0 Latin Azerbaijani",
    "G0 Latin KanuriMossi",
    "G0 Vietnamese",
    "G0 Igbo",
    "G0 Ukrainian",
    "G0 Belarusian",
    "G0 Macedonian",
    "G0 Serbian",
    "G0 KyrgyzMongolian",
    "G0 Tatar",
    "G0 Tajik",
    "G0 Georgian",
    "G0 Armenian",
    "G0 Tifinagh",
    "G2 Vietnamese",
    "G2 Armenian",
    "G0 Persian",
    "G0 Urdu",
    "G0 Pashto",
    "G0 Sindhi",
    "G0 Sorani",
    "G0 Uyghur",
    "G0 Balochi",
    "G0 ArabicPlain",
    "G0 Latin JapaneseRomaji",
    "G0 Hiragana",
    "G0 Katakana",
];

const _: () = assert!(TELETEXT_SETS.len() == LIST_NAMES.len());
const _: () = assert!(*JOINED_SETS.end() < TELETEXT_SET_COUNT);

/// Each letter's joining type and the code points of its joined forms.
#[derive(Default)]
pub(crate) struct Joining {
    /// Unicode scalar of a letter to its joining type.
    pub(crate) types: HashMap<u32, JoiningType>,
    /// Unicode scalar of a letter to the code point drawn for each of its joined forms.
    pub(crate) forms: HashMap<u32, Vec<(JoinForm, u32)>>,
}

/// The joining types of the engine's `JOINING_TYPES` table: lines
/// `('\u{XXXX}', JoiningType::Kind), // NAME` between its opening and the `];` that closes it.
/// The engine's join-causing type (the tatweel) is given as dual-joining, which it joins as
/// under REQ-CHR-015's rule (`naplps::JoiningType`).
pub(crate) fn joining_types(source: &str) -> Result<HashMap<u32, JoiningType>, String> {
    let table = source
        .split("const JOINING_TYPES")
        .nth(1)
        .and_then(|rest| rest.split("];").next())
        .ok_or("no JOINING_TYPES table")?;
    let mut types = HashMap::new();
    for line in table.lines().map(str::trim).filter(|line| line.starts_with("('")) {
        let scalar = line
            .split("\\u{")
            .nth(1)
            .and_then(|rest| rest.split('}').next())
            .and_then(|hex| u32::from_str_radix(hex, 16).ok())
            .ok_or_else(|| format!("a JOINING_TYPES line without a letter: {line}"))?;
        let kind = line
            .split("JoiningType::")
            .nth(1)
            .and_then(|rest| rest.split(')').next())
            .ok_or_else(|| format!("a JOINING_TYPES line without a type: {line}"))?;
        let kind = match kind {
            "None" => JoiningType::None,
            "Right" => JoiningType::Right,
            "Dual" | "Causing" => JoiningType::Dual,
            other => return Err(format!("an unknown joining type {other} in JOINING_TYPES")),
        };
        types.insert(scalar, kind);
    }
    if types.is_empty() {
        return Err("JOINING_TYPES is empty".to_owned());
    }
    Ok(types)
}

/// The joined forms of the engine's list: lines `U+FORM U+LETTER final|initial|medial`.
pub(crate) fn joined_forms(list: &str) -> Result<HashMap<u32, Vec<(JoinForm, u32)>>, String> {
    let scalar = |field: Option<&str>, line_number: usize| {
        field
            .and_then(|field| field.strip_prefix("U+"))
            .and_then(|hex| u32::from_str_radix(hex, 16).ok())
            .ok_or_else(|| format!("line {line_number}: no code point"))
    };
    let mut forms: HashMap<u32, Vec<(JoinForm, u32)>> = HashMap::new();
    for (index, line) in list.lines().enumerate() {
        let line_number = index.saturating_add(1);
        if line.starts_with(';') || line.trim().is_empty() {
            continue;
        }
        let mut fields = line.split_whitespace();
        let point = scalar(fields.next(), line_number)?;
        let letter = scalar(fields.next(), line_number)?;
        let form = match fields.next() {
            Some("final") => JoinForm::Final,
            Some("initial") => JoinForm::Initial,
            Some("medial") => JoinForm::Medial,
            other => return Err(format!("line {line_number}: the form {other:?}")),
        };
        forms.entry(letter).or_default().push((form, point));
    }
    Ok(forms)
}

/// Every set's code table: for each set, (code, Unicode scalar) of each position listed.
pub(crate) type CodeTables = Vec<Vec<(u8, u32)>>;

/// Reads a file of at most [`MAX_FILE_BYTES`].
fn read(path: &Path) -> Result<String, String> {
    let length = fs::metadata(path).map_err(|error| format!("{}: {error}", path.display()))?.len();
    if length > MAX_FILE_BYTES {
        return Err(format!("{} is {length} bytes, more than {MAX_FILE_BYTES}", path.display()));
    }
    fs::read_to_string(path).map_err(|error| format!("{}: {error}", path.display()))
}

/// The code tables from the engine's list: lines `U+XXXX CHARACTER USE; USE; ...`, each use a
/// set's name and a position `C/R`, or a note.
pub(crate) fn code_tables(list: &str) -> Result<CodeTables, String> {
    let names: HashMap<&str, usize> = LIST_NAMES.iter().enumerate().map(|(number, name)| (*name, number)).collect();
    let mut tables = vec![Vec::new(); TELETEXT_SET_COUNT];
    for (index, line) in list.lines().enumerate() {
        let line_number = index.saturating_add(1);
        if line.starts_with(';') || line.trim().is_empty() {
            continue;
        }
        let mut fields = line.splitn(3, ' ');
        let scalar = fields
            .next()
            .and_then(|field| field.strip_prefix("U+"))
            .and_then(|hex| u32::from_str_radix(hex, 16).ok())
            .ok_or_else(|| format!("line {line_number}: no code point"))?;
        let _character = fields.next();
        for usage in fields.next().unwrap_or("").split("; ") {
            let Some((name, position)) = usage.rsplit_once(' ') else { continue };
            let Some(&number) = names.get(name) else { continue };
            let code = position_code(position).ok_or_else(|| format!("line {line_number}: position {position:?}"))?;
            if let Some(table) = tables.get_mut(number) {
                table.push((code, scalar));
            }
        }
    }
    Ok(tables)
}

/// The code of a position `C/R` (column 2 to 7, row 0 to F).
fn position_code(position: &str) -> Option<u8> {
    let (column, row) = position.split_once('/')?;
    let column = u8::from_str_radix(column, 16).ok().filter(|column| (2..=7).contains(column))?;
    let row = u8::from_str_radix(row, 16).ok().filter(|row| *row <= 0xF)?;
    column.checked_mul(16)?.checked_add(row)
}

/// The glyphs of a BDF file of 12 by 20 glyphs: Unicode scalar to rows from the top, the
/// leftmost pixel the most significant of 12 bits.
pub(crate) fn bdf_glyphs(text: &str, glyphs: &mut HashMap<u32, Vec<u16>>) -> Result<(), String> {
    let mut lines = text.lines().enumerate();
    let mut count = 0usize;
    while let Some((_, line)) = lines.next() {
        if !line.starts_with("STARTCHAR") {
            continue;
        }
        count = count.saturating_add(1);
        if count > MAX_BDF_CHARACTERS {
            return Err(format!("more than {MAX_BDF_CHARACTERS} characters"));
        }
        let mut encoding = None;
        let mut rows = Vec::new();
        let mut in_bitmap = false;
        for (index, line) in lines.by_ref() {
            let line_number = index.saturating_add(1);
            if line == "ENDCHAR" {
                break;
            }
            if in_bitmap {
                if rows.len() >= usize::from(CELL_HEIGHT) {
                    return Err(format!("line {line_number}: more than {CELL_HEIGHT} rows"));
                }
                let row =
                    u16::from_str_radix(line.trim(), 16).map_err(|_| format!("line {line_number}: bitmap row"))?;
                rows.push(row.checked_shr(BDF_ROW_BITS.saturating_sub(u32::from(CELL_WIDTH))).unwrap_or(0));
            } else if let Some(value) = line.strip_prefix("ENCODING ") {
                encoding = value.trim().parse::<u32>().ok();
            } else if let Some(value) = line.strip_prefix("BBX ") {
                if value.split_whitespace().collect::<Vec<_>>()
                    != [CELL_WIDTH.to_string(), CELL_HEIGHT.to_string(), "0".into(), "0".into()]
                {
                    return Err(format!("line {line_number}: a glyph is not the {CELL_WIDTH} by {CELL_HEIGHT} cell"));
                }
            } else if line == "BITMAP" {
                in_bitmap = true;
            }
        }
        let encoding = encoding.ok_or("a character has no ENCODING")?;
        if rows.len() != usize::from(CELL_HEIGHT) {
            return Err(format!("U+{encoding:04X} has {} rows, not {CELL_HEIGHT}", rows.len()));
        }
        glyphs.insert(encoding, rows);
    }
    Ok(())
}

/// Every set, from the engine's checkout at `engine`, the plain Arabic-script sets with their
/// joining data.
pub(crate) fn load(engine: &Path) -> Result<Vec<BitmapSet>, String> {
    let list_path = engine.join(REQUIRED_LIST);
    let tables = code_tables(&read(&list_path)?).map_err(|error| format!("{}: {error}", list_path.display()))?;
    let source_path = engine.join(JOINING_SOURCE);
    let forms_path = engine.join(FORMS_LIST);
    let joining = Joining {
        types: joining_types(&read(&source_path)?).map_err(|error| format!("{}: {error}", source_path.display()))?,
        forms: joined_forms(&read(&forms_path)?).map_err(|error| format!("{}: {error}", forms_path.display()))?,
    };
    let mut glyphs = HashMap::new();
    for file in NOTO_FILES {
        let path = engine.join(file);
        bdf_glyphs(&read(&path)?, &mut glyphs).map_err(|error| format!("{}: {error}", path.display()))?;
    }
    tables
        .iter()
        .zip(TELETEXT_SETS)
        .enumerate()
        .map(|(number, (table, name))| {
            let mut set = BitmapSet::new(CELL_WIDTH, CELL_HEIGHT).map_err(|error| error.to_string())?;
            for &(code, scalar) in table {
                let rows = glyphs.get(&scalar).ok_or_else(|| format!("{name}: no glyph for U+{scalar:04X}"))?;
                set.set_glyph(code, rows).map_err(|error| format!("{name} {code:#04x}: {error}"))?;
                if JOINED_SETS.contains(&number) {
                    give_joining(&mut set, code, scalar, &joining, &glyphs)
                        .map_err(|error| format!("{name} {code:#04x}: {error}"))?;
                }
            }
            Ok(set)
        })
        .collect()
}

/// Gives the letter `scalar` at `code` its joining type and its joined forms' glyphs.
fn give_joining(
    set: &mut BitmapSet,
    code: u8,
    scalar: u32,
    joining: &Joining,
    glyphs: &HashMap<u32, Vec<u16>>,
) -> Result<(), String> {
    let Some(&kind) = joining.types.get(&scalar) else { return Ok(()) };
    set.set_joining(code, kind).map_err(|error| error.to_string())?;
    for &(form, point) in joining.forms.get(&scalar).map_or(&[][..], Vec::as_slice) {
        let rows = glyphs.get(&point).ok_or_else(|| format!("no glyph for the form U+{point:04X}"))?;
        set.set_form_glyph(code, form, rows).map_err(|error| error.to_string())?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_list_gives_each_set_its_codes() {
        let list =
            "; a comment\nU+0041 A G0 Latin 4/1; G0 Greek 4/1; spacing mark (decision E.26)\nU+0391 Α G0 Greek 4/1\n";
        let tables = code_tables(list).unwrap();
        assert_eq!(tables[0], [(0x41, 0x41)]);
        assert_eq!(tables[17], [(0x41, 0x41), (0x41, 0x391)]);
        assert!(code_tables("U+0041 A G0 Latin 8/1").is_err(), "a position outside columns 2 to 7");
        assert!(code_tables("0041 A G0 Latin 4/1").is_err(), "no code point");
    }

    fn character(bbx: &str, rows: usize) -> String {
        format!("STARTCHAR x\nENCODING 65\nBBX {bbx}\nBITMAP\n{}ENDCHAR\n", "FFF0\n".repeat(rows))
    }

    #[test]
    fn the_engines_joining_tables_are_read() {
        let source = "const JOINING_TYPES: [(char, JoiningType); 3] = [\n    ('\\u{0621}', JoiningType::None), // HAMZA\n    ('\\u{0627}', JoiningType::Right), // ALEF\n    ('\\u{0640}', JoiningType::Causing), // TATWEEL\n];\nconst OTHER: [(char, JoiningType); 1] = [\n    ('\\u{0628}', JoiningType::Dual),\n];";
        let types = joining_types(source).unwrap();
        assert_eq!(types.len(), 3, "only the JOINING_TYPES table is read");
        assert_eq!(types[&0x627], JoiningType::Right);
        assert_eq!(types[&0x640], JoiningType::Dual, "join-causing joins as dual-joining");
        assert!(
            joining_types(
                "const JOINING_TYPES: [(char, JoiningType); 1] = [\n    ('\\u{0621}', JoiningType::Sideways),\n];"
            )
            .is_err()
        );
        let forms = joined_forms("; a comment\nU+FE90 U+0628 final\nU+FE91 U+0628 initial\n").unwrap();
        assert_eq!(forms[&0x628], [(JoinForm::Final, 0xFE90), (JoinForm::Initial, 0xFE91)]);
        assert!(joined_forms("U+FE90 U+0628 sideways").is_err());
        assert!(joined_forms("FE90 U+0628 final").is_err());
    }

    #[test]
    fn a_bdf_glyph_must_be_the_cell() {
        let mut glyphs = HashMap::new();
        bdf_glyphs(&character("12 20 0 0", 20), &mut glyphs).unwrap();
        assert_eq!(glyphs[&65], vec![0x0FFF; 20]);
        assert!(bdf_glyphs(&character("8 16 0 0", 20), &mut glyphs).is_err());
        assert!(bdf_glyphs(&character("12 20 0 0", 21), &mut glyphs).is_err());
        assert!(bdf_glyphs(&character("12 20 0 0", 19), &mut glyphs).is_err());
        assert!(bdf_glyphs(&character("12 20 0 0", 20).repeat(MAX_BDF_CHARACTERS + 1), &mut glyphs).is_err());
    }
}
