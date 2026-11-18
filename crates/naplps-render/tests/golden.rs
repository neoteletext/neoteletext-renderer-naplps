//! Golden image sequences (neoteletext-common `docs/animation.md`, ANIM-18: "the golden
//! sequences named in ... ANIM-14 ... and ANIM-20"; ANIM-12: "golden images of the same
//! objects in each layer and order"; REQ-6531).
//!
//! Each sequence is a page played by `naplps-render --frames`; `tests/golden/sequences.txt`
//! holds a checksum of each picture, a PPM file, so of its size, its pixels and their colours.
//! Beside the checksums each test asserts what its requirement says of the sequence, so that
//! a regenerated file cannot quietly accept a wrong one.
//!
//! The pages here are written for the tests: no period page may be in this repository
//! (`CLAUDE.md`). The sequence of a historical animated page that ANIM-20 names is the last
//! test, which reads its page from `~/devel/teletext-reference` and is ignored without it.
//!
//! The file carries a format version (DEVELOPMENT.md section 8). A deliberate change to what
//! is drawn raises the version and regenerates the file in the same change, with the reason
//! in the commit: run with `NAPLPS_UPDATE_GOLDEN=1` (and `-- --include-ignored` for the
//! historical page), then check that only the expected lines changed.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

mod common;

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use common::{colour, macro_rectangle, rectangle, wait};

/// Raise when what `naplps-render` draws for one of these pages changes on purpose.
const FORMAT_VERSION: u32 = 1;

/// The first line of the golden file.
fn heading() -> String {
    format!("format {FORMAT_VERSION}\n")
}

fn golden_path() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/golden/sequences.txt")
}

/// The 64-bit FNV-1a hash: the offset basis, then for each byte an exclusive-or and a
/// multiplication by the FNV prime (Fowler, Noll and Vo; the constants are the algorithm's).
fn fnv(bytes: &[u8]) -> u64 {
    const OFFSET_BASIS: u64 = 0xCBF2_9CE4_8422_2325;
    const PRIME: u64 = 0x0000_0100_0000_01B3;
    bytes.iter().fold(OFFSET_BASIS, |hash, &byte| (hash ^ u64::from(byte)).wrapping_mul(PRIME))
}

/// One golden sequence: what is played, and for how long.
struct Sequence<'a> {
    name: &'a str,
    page: &'a Path,
    objects: Option<&'a str>,
    script: Option<&'a str>,
    font: Option<&'a Path>,
    frames: u32,
    step: u32,
}

/// Plays a sequence into a new folder and returns its pictures by tick.
fn play(sequence: &Sequence<'_>) -> BTreeMap<u32, Vec<u8>> {
    let folder = Path::new(env!("CARGO_TARGET_TMPDIR")).join(format!("golden-{}", sequence.name));
    let _ = fs::remove_dir_all(&folder);
    fs::create_dir_all(&folder).unwrap();
    let mut command = Command::new(env!("CARGO_BIN_EXE_naplps-render"));
    command.args(["--frames", &sequence.frames.to_string(), "--frame-step", &sequence.step.to_string()]);
    for (option, text) in [("--objects", sequence.objects), ("--script", sequence.script)] {
        if let Some(text) = text {
            let path = folder.join(option.trim_start_matches('-'));
            fs::write(&path, text).unwrap();
            command.arg(option).arg(path);
        }
    }
    if let Some(font) = sequence.font {
        command.arg("--font").arg(font);
    }
    let output = command.arg(sequence.page).arg(folder.join("picture.ppm")).output().unwrap();
    let report = String::from_utf8_lossy(&output.stderr);
    assert!(output.status.success(), "{}: {report}", sequence.name);
    assert!(report.is_empty(), "{}: {report}", sequence.name);
    let mut pictures = BTreeMap::new();
    for tick in 0..sequence.frames {
        if let Ok(bytes) = fs::read(folder.join(format!("picture-{tick:05}.ppm"))) {
            pictures.insert(tick, bytes);
        }
    }
    pictures
}

/// Plays a sequence and holds its pictures to the golden file; with `NAPLPS_UPDATE_GOLDEN`
/// set, writes its lines there instead.
fn held_to_golden(sequence: &Sequence<'_>) -> BTreeMap<u32, Vec<u8>> {
    let pictures = play(sequence);
    let mut actual = String::new();
    for (tick, picture) in &pictures {
        let _ = writeln!(actual, "{} {tick:05} {:016x}", sequence.name, fnv(picture));
    }
    let prefix = format!("{} ", sequence.name);
    let path = golden_path();
    if std::env::var_os("NAPLPS_UPDATE_GOLDEN").is_some() {
        // The other sequences' lines are kept: each test owns its own, and the tests may run
        // at once, so the file is rewritten under a lock.
        let lock = fs::File::create(path.with_extension("lock")).unwrap();
        lock.lock().unwrap();
        let file = fs::read_to_string(&path).unwrap_or_default();
        let kept = file.lines().filter(|line| !line.starts_with(&prefix) && !line.starts_with("format "));
        let mut all: Vec<String> = kept.chain(actual.lines()).map(String::from).collect();
        all.sort();
        fs::write(&path, format!("{}{}\n", heading(), all.join("\n"))).unwrap();
        lock.unlock().unwrap();
        let _ = fs::remove_file(path.with_extension("lock"));
        return pictures;
    }
    let file = fs::read_to_string(&path).unwrap_or_default();
    assert!(
        file.starts_with(&heading()),
        "tests/golden/sequences.txt is not of format {FORMAT_VERSION}; generate with NAPLPS_UPDATE_GOLDEN=1"
    );
    let mut expected = String::new();
    for line in file.lines().filter(|line| line.starts_with(&prefix)) {
        let _ = writeln!(expected, "{line}");
    }
    assert_eq!(actual, expected, "{} changed: if deliberate, raise FORMAT_VERSION and regenerate", sequence.name);
    pictures
}

/// Writes a page built by a test where `naplps-render` can read it.
fn written(name: &str, page: &[u8]) -> PathBuf {
    let path = Path::new(env!("CARGO_TARGET_TMPDIR")).join(format!("golden-page-{name}.nap"));
    fs::write(&path, page).unwrap();
    path
}

/// A macro's rectangle, 16/256 of the unit screen each way, is 41 by 40 pixels of a 640 by
/// 480 picture and lies at the picture's lower left; an object's origin of (0, 440) is its
/// top left corner there.
const FRAME: &str = "41 40 0 440";

/// ANIM-12: three objects that overlap, each drawn by a macro of one colour, played through
/// the layers and orders.
#[test]
fn the_same_objects_in_each_layer_and_order_are_the_golden_images() {
    // Macros 2/0, 2/1 and 2/2 fill the same rectangle with entries 3, 4 and 5; the stream
    // then fills the picture's lower part with entry 1.
    let mut page = Vec::new();
    for (code, entry) in [(0x20, 3), (0x21, 4), (0x22, 5)] {
        page.extend(macro_rectangle(code, entry, 16, 16));
    }
    page.extend(rectangle(1, 0, 0, 255, 128));
    let page = written("layers", &page);
    // Objects 1, 2 and 3, each 41 by 40, stepped 15 pixels apart so that all three cover the
    // pixel (135, 135) and each shows alone at one corner.
    let objects =
        format!("macro 1 1 0 100 100 {FRAME} 20\nmacro 2 1 0 115 115 {FRAME} 21\nmacro 3 1 0 130 130 {FRAME} 22\n");
    // Within a layer the order decides, then the number; a higher layer wins whatever the
    // order; layer 0 of the animation state is still over the stream's picture.
    let script = "1 order 1 keep 5\n\
                  2 order 3 keep -5\n\
                  3 order 2 2 -128\n\
                  4 order 1 3 -128\n\
                  5 order 3 3 127\n\
                  6 order 3 3 -128\n\
                  7 order 2 0 0\n\
                  8 order 1 0 0\n\
                  9 order 3 0 0\n\
                  10 order 3 0 -1\n\
                  11 order 1 1 0\n\
                  12 order 2 1 0\n\
                  13 order 3 2 0\n\
                  14 order 2 3 0\n\
                  15 order 1 2 1\n";
    let sequence = Sequence {
        name: "layers",
        page: &page,
        objects: Some(&objects),
        script: Some(script),
        font: None,
        frames: 16,
        step: 1,
    };
    let pictures = held_to_golden(&sequence);
    assert_eq!(pictures.len(), 16);
    let at = |tick: u32, x: usize, y: usize| colour(&pictures[&tick], x, y);
    let [one, two, three] = [at(0, 102, 102), at(0, 117, 152), at(0, 168, 168)];
    assert!(one != two && two != three && one != three);
    let top: Vec<[u8; 3]> = (0..16).map(|tick| at(tick, 135, 135)).collect();
    let expected = [three, one, one, two, one, three, three, three, three, three, two, one, two, three, two, two];
    assert_eq!(top, expected);
    // At tick 9 all three are in layer 0, over the stream's picture: each still shows.
    assert_eq!([at(9, 102, 102), at(9, 117, 152), at(9, 168, 168)], [one, two, three]);
}

/// ANIM-14: an image sequence of a four-frame cycle, and of one played once.
#[test]
fn a_four_frame_cycle_is_the_golden_sequence() {
    // Macros 2/0 to 2/3: rectangles of entries 3 to 6, each narrower than the one before, so
    // that the frames differ in shape as well as in colour.
    let mut page = Vec::new();
    for frame in 0..4u8 {
        page.extend(macro_rectangle(0x20 + frame, 3 + frame, 16 - u16::from(frame) * 3, 16));
    }
    let page = written("cycle", &page);
    let objects = format!("macro 1 2 0 300 100 {FRAME} 20,21,22,23\n");
    let cycle = Sequence {
        name: "cycle",
        page: &page,
        objects: Some(&objects),
        script: Some("0 cycle 1 0 3 3\n"),
        font: None,
        frames: 15,
        step: 1,
    };
    let pictures = held_to_golden(&cycle);
    // Frame 0 until the cycle starts at tick 1, then three ticks a frame.
    let frame_at = [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 0, 0];
    for (tick, frame) in (0..).zip(frame_at) {
        let first = u32::try_from(frame_at.iter().position(|other| *other == frame).unwrap()).unwrap();
        assert!(pictures[&tick] == pictures[&first], "tick {tick} is not frame {frame}");
    }
    let distinct: std::collections::BTreeSet<&Vec<u8>> = pictures.values().collect();
    assert_eq!(distinct.len(), 4);

    let once = Sequence { name: "cycle-once", script: Some("0 cycle 1 0 3 2 once\n"), frames: 10, ..cycle };
    let once = held_to_golden(&once);
    let frame_at = [0, 0, 0, 1, 1, 2, 2, 3, 3, 3];
    for (tick, frame) in (0..).zip(frame_at) {
        // The frames are the cycle's: 0 at its tick 0, 1 at 4, 2 at 7, 3 at 10.
        let same = [0, 4, 7, 10][frame];
        assert!(once[&tick] == pictures[&same], "tick {tick} of the cycle played once is not frame {frame}");
    }
}

/// ANIM-20: an animated page, written for this test, whose stream draws in four stages with
/// WAITs between and blinks two of its colours.
#[test]
fn an_animated_page_of_waits_and_blinks_is_the_golden_sequence() {
    // Four rectangles of entries 1 to 4 across the picture; a WAIT of 3 tenths (18 ticks)
    // after the first, 2 tenths (12 ticks) after the second and 4 tenths (24 ticks) after
    // the third. Entry 1 blinks to entry 7, 5 tenths on and 5 off, from the start.
    let mut page = rectangle(1, 0, 100, 48, 48);
    page.extend([0x3F, 0x40 | (7 << 2), 0x45, 0x45, 0x40]);
    page.extend(wait(3));
    page.extend(rectangle(2, 64, 100, 48, 48));
    page.extend(wait(2));
    page.extend(rectangle(3, 128, 100, 48, 48));
    page.extend(wait(4));
    page.extend(rectangle(4, 192, 100, 48, 48));
    let page = written("animated", &page);
    let sequence =
        Sequence { name: "animated", page: &page, objects: None, script: None, font: None, frames: 73, step: 6 };
    let pictures = held_to_golden(&sequence);
    assert_eq!(pictures.keys().copied().collect::<Vec<_>>(), [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72]);
    let black = colour(&pictures[&0], 639, 0);
    // A unit of 1/256 is 2.5 pixels of the 640 across, and the same upward from the foot:
    // the rectangles' columns begin at 0, 160, 320 and 480, and row 180 crosses all four
    // (rows 110 to 229).
    let drawn = |tick: u32, rectangle: usize| colour(&pictures[&tick], 20 + rectangle * 160, 180) != black;
    let appears = |rectangle: usize| pictures.keys().copied().find(|tick| drawn(*tick, rectangle)).unwrap();
    // WAITs of 18, 12 and 24 ticks: the stages appear at ticks 0, 18, 30 and 54.
    assert_eq!([appears(0), appears(1), appears(2), appears(3)], [0, 18, 30, 54]);
    // BLINK: entry 1 changes colour every 30 ticks.
    let blinking = |tick: u32| colour(&pictures[&tick], 20, 180);
    assert_eq!(blinking(0), blinking(24));
    assert_ne!(blinking(24), blinking(30));
    assert_eq!(blinking(30), blinking(54));
    assert_eq!(blinking(60), blinking(0));
}

/// Where the reference pages are: `NAPLPS_REFERENCE_DIR`, or under the home directory.
fn reference() -> PathBuf {
    std::env::var_os("NAPLPS_REFERENCE_DIR").map_or_else(
        || PathBuf::from(std::env::var_os("HOME").expect("HOME")).join("devel/teletext-reference/NAPLPS"),
        PathBuf::from,
    )
}

/// The historical animated page played: `SAIL.NAP` of the Simtel NAPLPS collection, which
/// draws a boat in 25 stages with a WAIT after each.
const HISTORICAL_PAGE: &str = "Telidon-master/images/sail.nap";
/// The page's length and sum, taken on 18 November 2026, so that the golden pictures are of
/// the page they were made from. The sum is this file's [`fnv`] of the page; its SHA-256 is
/// d11260c3cea85bcabf60bd90f742fd795a994e0923d8d3e81cffc1d9733da7dd.
const HISTORICAL_PAGE_BYTES: usize = 8629;
/// See [`HISTORICAL_PAGE_BYTES`].
const HISTORICAL_PAGE_SUM: u64 = 0xF442_64CE_C01C_9DC2;

/// ANIM-20: "an image sequence of a historical animated page".
#[test]
#[ignore = "needs the page Telidon-master/images/sail.nap of ~/devel/teletext-reference/NAPLPS (or NAPLPS_REFERENCE_DIR), which may not be in this repository; scripts/check.sh full runs it"]
fn a_historical_animated_page_is_the_golden_sequence() {
    let path = reference().join(HISTORICAL_PAGE);
    let page = fs::read(&path).unwrap_or_else(|error| panic!("{}: {error}", path.display()));
    assert_eq!(
        (page.len(), fnv(&page)),
        (HISTORICAL_PAGE_BYTES, HISTORICAL_PAGE_SUM),
        "{} is not the page the golden pictures were made from",
        path.display()
    );
    let font = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../fonts/neoteletext.strokes");
    // A minute of the page, which is as long as a page's WAITs may hold it (ANIM-20,
    // `WAIT_BUDGET_TICKS`): a picture every three seconds.
    let sequence = Sequence {
        name: "historical-sail",
        page: &path,
        objects: None,
        script: None,
        font: Some(&font),
        frames: 3601,
        step: 180,
    };
    let pictures = held_to_golden(&sequence);
    assert_eq!(pictures.len(), 21);
    // The page draws itself over time: its pictures are not all one picture.
    let distinct: std::collections::BTreeSet<&Vec<u8>> = pictures.values().collect();
    assert!(distinct.len() >= 5, "only {} different pictures", distinct.len());
}
