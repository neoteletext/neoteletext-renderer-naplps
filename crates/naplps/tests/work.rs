//! The pixel work allowance (TODO-6844, DEC-6851; renderer parity section 19, threats 2 and 6):
//! a stream whose drawing would visit more pixels than [`WORK_CAP`] and [`WORK_PER_BYTE`] allow stops
//! drawing there, reports it, and passes over the rest of the stream; a validator stops where the
//! receiver's terminal stops; one composing of objects is bounded by [`MAX_COMPOSE_WORK`]; and
//! no ordinary page comes near the allowance. The timed tests print their numbers.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

use naplps::limits::{
    MAX_COMPOSE_WORK, MAX_OBJECTS, RASTER_HEIGHT, RASTER_WIDTH, RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_PIXELS,
    RECEIVER_CANVAS_WIDTH, WORK_CAP, WORK_PER_BYTE,
};
use naplps::{
    BitmapSet, Canvas, Event, Object, ObjectKind, Refusal, StrokeFont, TELETEXT_SET_COUNT, Terminal, Validator,
};

/// The colour map's bits: 16 entries, as the sample pages use.
const PALETTE_BITS: u32 = 4;
/// SO: the PDI set into use (section 4.3).
const SO: u8 = 0x0E;
/// POINT SET, absolute (ANSI X3.110-1983 section 5.3.3.1).
const POINT_SET: u8 = 0x24;
/// RECTANGLE (FILLED) from the drawing point (section 5.3.3.4).
const RECT_FILLED: u8 = 0x31;
/// ESC, and the sequence that designates the macro set as G2 (section 4.3.1).
const DESIGNATE_MACROS_AS_G2: [u8; 4] = [0x1B, 0x2E, 0x20, 0x7A];
/// SINGLE SHIFT 2 in the 7-bit code: the next code is G2's, here a macro call.
const SS2: u8 = 0x19;
/// DEF MACRO and END (section 6.2.2).
const DEF_MACRO: u8 = 0x80;
const END: u8 = 0x85;
/// The macro the tests define.
const MACRO: u8 = 0x20;
/// The stream of whole-screen fills: 1 MiB, the most a program may send in one stream.
const MEGABYTE: usize = 1 << 20;
/// The time a release build of the old renderer took for one fill of [`fill`] on the
/// receiver's canvas, measured by the server on 19 November 2026 (DEC-6842): 2.36 ms. A
/// megabyte of them took about five minutes.
const OLD_FILL: Duration = Duration::from_micros(2360);
/// The most one drawing of the costliest stream may take: two seconds in a release build, four
/// times the half second measured; a debug build draws more slowly, about 15 times.
const DRAWING_BUDGET: Duration = if cfg!(debug_assertions) { Duration::from_secs(30) } else { Duration::from_secs(2) };

/// A coordinate pair of three bytes in the default domain: (`x`/256, `y`/256) of the unit
/// screen (section 5.3.2.2.3).
fn pair(x: u8, y: u8) -> [u8; 3] {
    let (x, y) = (u16::from(x), u16::from(y));
    let byte = |shift: u16| 0x40 | ((((x >> shift) & 7) as u8) << 3) | (((y >> shift) & 7) as u8);
    [byte(6), byte(3), byte(0)]
}

/// POINT SET at the origin, then RECTANGLE (FILLED) over the whole unit screen: the eight
/// bytes the server measured (DEC-6842).
fn fill() -> Vec<u8> {
    let mut bytes = vec![POINT_SET];
    bytes.extend(pair(0, 0));
    bytes.push(RECT_FILLED);
    bytes.extend(pair(255, 255));
    bytes
}

/// SO, then whole-screen fills to [`MEGABYTE`].
fn fills() -> Vec<u8> {
    let mut bytes = vec![SO];
    while bytes.len() + fill().len() <= MEGABYTE {
        bytes.extend(fill());
    }
    bytes
}

/// DEF MACRO [`MACRO`] holding as many whole-screen fills as a macro holds (4,096 bytes).
fn macro_of_fills() -> Vec<u8> {
    let mut bytes = vec![DEF_MACRO, MACRO];
    for _ in 0..naplps::limits::MAX_MACRO_BYTES / fill().len() {
        bytes.extend(fill());
    }
    bytes.push(END);
    bytes
}

/// SO, the macro set as G2, the macro of fills, then calls of it to [`MEGABYTE`]: the
/// processing limit would let some 500,000 fills run (DEC-6842).
fn macro_calls() -> Vec<u8> {
    let mut bytes = vec![SO];
    bytes.extend(DESIGNATE_MACROS_AS_G2);
    bytes.extend(macro_of_fills());
    while bytes.len() + 2 <= MEGABYTE {
        bytes.extend([SS2, MACRO]);
    }
    bytes
}

/// A receiver's canvas: the teletext raster's display area.
fn receiver_canvas() -> Canvas {
    Canvas::new(RECEIVER_CANVAS_WIDTH, RECEIVER_CANVAS_HEIGHT).unwrap()
}

/// The most a stream of `bytes` may spend.
fn allowance(bytes: usize) -> u64 {
    WORK_CAP + WORK_PER_BYTE * bytes as u64
}

/// Draws `stream` in one call on the receiver's canvas, then reads it with a validator, and
/// checks both stopped at the allowance, at the same place, within the time budget.
fn stops_at_the_allowance(name: &str, stream: &[u8], old_fills: u32) {
    let mut canvas = receiver_canvas();
    let mut terminal = Terminal::new(PALETTE_BITS);
    let start = Instant::now();
    let mut events = terminal.feed(&mut canvas, stream);
    events.extend(terminal.finish(&mut canvas));
    let drawn = start.elapsed();
    let mut validator = Validator::new();
    let start = Instant::now();
    let mut read = validator.feed(stream);
    read.extend(validator.finish());
    let validated = start.elapsed();
    let spent = terminal.work_spent();
    println!(
        "{name}: {} bytes drawn in {drawn:?} and validated in {validated:?}; {spent} work units spent of {} allowed \
         ({:.1} screens); {} bytes passed over at the limit; the old renderer drew {old_fills} fills, about {:?}",
        stream.len(),
        allowance(stream.len()),
        spent as f64 / RECEIVER_CANVAS_PIXELS as f64,
        terminal.diagnostics().count(Refusal::WorkLimit),
        OLD_FILL * old_fills,
    );
    assert!(events.contains(&Event::WorkLimitReached), "{name}: the work limit is reported");
    assert!(terminal.diagnostics().count(Refusal::WorkLimit) > 0, "{name}: the bytes passed over are counted");
    assert!(spent <= allowance(stream.len()), "{name}: no more is spent than the allowance");
    assert!(drawn < DRAWING_BUDGET, "{name}: drawn in {drawn:?}, over the budget of {DRAWING_BUDGET:?}");
    assert!(validated < DRAWING_BUDGET, "{name}: validated in {validated:?}, over the budget of {DRAWING_BUDGET:?}");
    assert_eq!(read, events, "{name}: the validator's events are the receiver's");
    assert_eq!(*validator.diagnostics(), terminal.diagnostics(), "{name}: the validator stops where the receiver does");
    assert_eq!(validator.work_spent(), spent, "{name}: the validator counts the receiver's work");
}

/// TODO-6844: a megabyte of whole-screen fills, which took the old renderer about five minutes
/// in a release build, stops at the allowance within the budget.
#[test]
fn a_megabyte_of_whole_screen_fills_stops_at_the_allowance() {
    let stream = fills();
    let old_fills = u32::try_from(stream.len() / fill().len()).unwrap();
    stops_at_the_allowance("whole-screen fills", &stream, old_fills);
}

/// TODO-6844: a macro of 512 whole-screen fills called until the stream is a megabyte, which
/// the processing limit alone would let draw some 500,000 fills, stops at the allowance.
#[test]
fn a_macro_repeating_fills_stops_at_the_allowance() {
    let stream = macro_calls();
    // The processing limit counts every byte the macros run: a fill is eight of them.
    let old_fills = u32::try_from(naplps::limits::MAX_PROCESSED_BYTES / fill().len()).unwrap();
    stops_at_the_allowance("a macro of fills called again and again", &stream, old_fills);
}

/// TODO-6844: a stream fed in many calls stops too, and each later call earns only what its
/// bytes bring: the whole stream spends no more than its allowance.
#[test]
fn a_stream_in_pieces_spends_no_more_than_its_allowance() {
    let stream = fills();
    let mut canvas = receiver_canvas();
    let mut terminal = Terminal::new(PALETTE_BITS);
    let mut validator = Validator::new();
    let start = Instant::now();
    for piece in stream.chunks(4096) {
        let drawn = terminal.feed(&mut canvas, piece);
        assert_eq!(validator.feed(piece), drawn, "the validator's events are the receiver's");
    }
    let elapsed = start.elapsed();
    println!("whole-screen fills in pieces of 4,096 bytes: {elapsed:?}, {} units", terminal.work_spent());
    assert!(terminal.work_spent() <= allowance(stream.len()));
    assert!(terminal.diagnostics().count(Refusal::WorkLimit) > 0);
    assert_eq!(*validator.diagnostics(), terminal.diagnostics());
    assert!(elapsed < DRAWING_BUDGET * 2, "drawn and validated in {elapsed:?}");
}

/// TODO-6844: the most objects a sub-page may have, each a macro of 512 whole-screen fills
/// over the whole picture, compose within [`MAX_COMPOSE_WORK`] and the time it allows.
#[test]
fn composing_objects_that_fill_the_screen_is_bounded() {
    let mut stream = vec![SO];
    stream.extend(macro_of_fills());
    let mut canvas = receiver_canvas();
    let mut terminal = Terminal::new(PALETTE_BITS);
    terminal.feed(&mut canvas, &stream);
    terminal.finish(&mut canvas);
    let objects: Vec<Object> = (1..=u16::try_from(MAX_OBJECTS).unwrap())
        .map(|number| Object {
            number,
            kind: ObjectKind::Macro,
            shown: true,
            detectable: false,
            layer: 1,
            order: 0,
            x: 0,
            y: 0,
            width: u16::try_from(RASTER_WIDTH).unwrap(),
            height: u16::try_from(RASTER_HEIGHT).unwrap(),
            origin_x: 0,
            origin_y: 0,
            cover: 0,
            hover: 0,
            pressed: 0,
            alternative: 0,
            frames: vec![MACRO],
            label: String::new(),
        })
        .collect();
    terminal.set_objects(&objects).unwrap();
    let mut presented = receiver_canvas();
    let start = Instant::now();
    terminal.compose(&canvas, &mut presented).unwrap();
    let elapsed = start.elapsed();
    // The work allowed at about 10 nanoseconds a unit, ten times over for a slow machine, and
    // 15 times that in a debug build.
    let budget = Duration::from_nanos(MAX_COMPOSE_WORK * 100) * if cfg!(debug_assertions) { 15 } else { 1 };
    println!("{MAX_OBJECTS} objects of 512 whole-screen fills each composed in {elapsed:?} (budget {budget:?})");
    assert!(elapsed < budget, "composed in {elapsed:?}, over {budget:?}");
}

/// A receiver's terminal: the repository's stroke font and a stand-in for each provided set, of
/// the engine's 12 by 20 cell. A provided set's character costs the pixels of its field
/// whatever its glyph, so the stand-ins cost what the real sets do.
fn receiver() -> Terminal {
    let mut terminal = Terminal::new(PALETTE_BITS);
    terminal.set_font(StrokeFont::parse(include_str!("../../../fonts/neoteletext.strokes")).unwrap());
    for number in 0..TELETEXT_SET_COUNT {
        let mut set = BitmapSet::new(12, 20).unwrap();
        for code in 0x20..=0x7F_u8 {
            set.set_glyph(code, &[0x0FFF_u16; 20]).unwrap();
        }
        terminal.set_teletext_set(u8::try_from(number).unwrap(), set).unwrap();
    }
    terminal
}

/// The least allowance at the start that draws a page whose bytes cost `costs` (the work each
/// byte spent, fed one at a time) and its end `last` without stopping, at [`WORK_PER_BYTE`].
fn allowance_needed(costs: &[u64], last: u64) -> u64 {
    let draws = |cap: u64| {
        let mut left = cap;
        for &cost in costs {
            left = (left + WORK_PER_BYTE).min(cap);
            let Some(after) = left.checked_sub(cost) else { return false };
            left = after;
        }
        left >= last
    };
    let (mut low, mut high) = (0, costs.iter().sum::<u64>() + last);
    while low < high {
        let middle = u64::midpoint(low, high);
        if draws(middle) { high = middle } else { low = middle + 1 }
    }
    low
}

/// What a page needs: the allowance it needs at the start, fed byte by byte, and whether
/// drawing it in one call stopped.
fn measure(page: &[u8]) -> (u64, bool) {
    let mut canvas = receiver_canvas();
    let mut terminal = receiver();
    let mut costs = Vec::with_capacity(page.len());
    for byte in page {
        let before = terminal.work_spent();
        terminal.feed(&mut canvas, &[*byte]);
        costs.push(terminal.work_spent() - before);
    }
    let before = terminal.work_spent();
    terminal.finish(&mut canvas);
    let needed = allowance_needed(&costs, terminal.work_spent() - before);
    let mut whole = receiver();
    whole.feed(&mut canvas, page);
    whole.finish(&mut canvas);
    (needed, whole.diagnostics().count(Refusal::WorkLimit) > 0)
}

/// The `.nap` files under `folder`, at any depth, in order.
fn pages(folder: &Path) -> Vec<PathBuf> {
    let mut found = Vec::new();
    let Ok(entries) = std::fs::read_dir(folder) else { return found };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            found.extend(pages(&path));
        } else if path.extension().is_some_and(|extension| extension.eq_ignore_ascii_case("nap")) {
            found.push(path);
        }
    }
    found.sort();
    found
}

/// Measures every page under `folders` and checks none stops and none needs more than
/// `share` of [`WORK_CAP`]; prints the heaviest.
fn within_the_allowance(folders: &[PathBuf], share: u64) {
    let mut measured: Vec<(u64, PathBuf)> = Vec::new();
    for path in folders.iter().flat_map(|folder| pages(folder)) {
        let page = std::fs::read(&path).unwrap();
        let (needed, stopped) = measure(&page);
        assert!(!stopped, "{} stops at the work limit", path.display());
        measured.push((needed, path));
    }
    assert!(!measured.is_empty(), "pages were found");
    measured.sort();
    for (needed, path) in measured.iter().rev().take(5) {
        println!(
            "{} needs {needed} units ({:.1} screens): {:.2} times under WORK_CAP",
            path.display(),
            *needed as f64 / RECEIVER_CANVAS_PIXELS as f64,
            WORK_CAP as f64 / *needed as f64
        );
    }
    println!("{} pages", measured.len());
    let (heaviest, path) = measured.last().unwrap();
    assert!(heaviest * share <= WORK_CAP, "{} needs more than 1/{share} of WORK_CAP", path.display());
}

/// TODO-6844: the repository's sample pages draw within the allowance, each needing less than a
/// third of it, the same margin the corpus is held to (DEC-6851). The samples have no size limit of
/// their own (the owner, 21 November 2026), so they are held to the renderer's real margin, not a
/// stricter one; the heaviest prints, so a page nearing it is seen.
#[test]
fn the_sample_pages_draw_within_the_work_allowance() {
    within_the_allowance(&[PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../../samples"))], 3);
}

/// The measurement [`WORK_CAP`] was chosen by (TODO-6844, DEC-6851): every page of the NAPLPS
/// corpus (`~/devel/teletext-reference/NAPLPS`, or `NAPLPS_REFERENCE_DIR`), of the repository's
/// samples and, when `NAPLPS_EXTRA_PAGES_DIR` names one, of another folder (the naplpsdemo
/// channel's `pictures` were measured so) draws without stopping and needs less than a third
/// of the allowance.
#[test]
#[ignore = "needs the NAPLPS pages of ~/devel/teletext-reference/NAPLPS (or NAPLPS_REFERENCE_DIR); measures every page byte by byte"]
fn the_corpus_draws_within_the_work_allowance() {
    let reference = std::env::var_os("NAPLPS_REFERENCE_DIR").map_or_else(
        || PathBuf::from(std::env::var_os("HOME").expect("HOME")).join("devel/teletext-reference/NAPLPS"),
        PathBuf::from,
    );
    assert!(reference.is_dir(), "{} holds the NAPLPS corpus", reference.display());
    let mut folders = vec![reference, PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../../samples"))];
    folders.extend(std::env::var_os("NAPLPS_EXTRA_PAGES_DIR").map(PathBuf::from));
    within_the_allowance(&folders, 3);
}
