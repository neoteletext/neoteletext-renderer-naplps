//! What a validator or a terminal reports it holds (TODO-6854): a new one's figure, each kind
//! of definition raising it by at least what it allocates, and the heaviest state a stream
//! and a caller can make staying within `MAX_HELD_BYTES`. The resident size the same streams
//! cause is checked in `validator_memory.rs`, alone in its process.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::unwrap_used,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

mod common;

use common::{DEF_DRCS, DEF_MACRO, DEF_TEXTURE, END, FILL, FIRST_TEXTURE, POLYGON_FILLED, SO, WAIT, heaviest};
use naplps::limits::{
    ALLOCATION_OVERHEAD_BYTES, DEFINABLE_CODES, MASK_BYTES, MASK_SIDE, MAX_ALL_MACRO_BYTES, MAX_HELD_BYTES,
    MAX_LABEL_BYTES, MAX_MACRO_BYTES, MAX_MACRO_DEPTH, MAX_OBJECT_FRAMES, MAX_OBJECTS, MAX_PDI_BYTES, MAX_TITLE_BYTES,
    RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_WIDTH, TEXTURE_MASKS,
};
use naplps::palette::MAX_BITS;
use std::path::{Path, PathBuf};

use naplps::{BitmapSet, Canvas, Object, ObjectKind, StrokeFont, Terminal, Validator};

/// The bytes of one DRCS or texture bitmap at the largest mask: a one-byte element a pixel.
const MASK_ELEMENTS: usize = (MASK_SIDE * MASK_SIDE) as usize;

fn validator_after(stream: &[u8]) -> Validator {
    let mut validator = Validator::new();
    let _ = validator.feed(stream);
    validator
}

/// [`common::square_definitions`] with its last PDI run (END with no definition open), so that
/// what follows does not free its operands.
fn squared() -> Vec<u8> {
    let mut bytes = common::square_definitions();
    bytes.push(END);
    bytes
}

/// How much `stream` raises a new validator's figure, read after `before` set the state up.
fn raised_by(before: &[u8], stream: &[u8]) -> usize {
    let mut validator = validator_after(before);
    let held = validator.held_bytes();
    let _ = validator.feed(stream);
    validator.held_bytes() - held
}

/// An object of `MAX_OBJECT_FRAMES` frames and a label of `MAX_LABEL_BYTES`.
fn largest_object(number: u16) -> Object {
    Object {
        number,
        kind: ObjectKind::Macro,
        shown: true,
        detectable: true,
        layer: 2,
        order: 0,
        x: 0,
        y: 0,
        width: 16,
        height: 16,
        origin_x: 0,
        origin_y: 0,
        cover: 0,
        hover: 0,
        pressed: 0,
        alternative: 0,
        frames: vec![0x20; MAX_OBJECT_FRAMES],
        label: "l".repeat(MAX_LABEL_BYTES),
    }
}

#[test]
fn a_new_validator_holds_its_structure_and_its_colour_map() {
    let held = Validator::new().held_bytes();
    println!(
        "a new validator holds {held} bytes; a validator is {} bytes itself; the bound is {MAX_HELD_BYTES}",
        size_of::<Validator>()
    );
    assert!(held >= size_of::<Validator>(), "{held}");
    // Its structure and the colour map of 16 entries: no table of macros, DRCS characters or
    // provided sets until the stream or the caller fills one (TODO-6895), where a new
    // validator held 12,360 bytes with the tables made at once.
    assert!(held <= size_of::<Validator>() + 512, "{held}");
    assert_eq!(Validator::new().held_bytes(), held, "the figure depends on nothing but the state");
}

#[test]
fn a_macro_raises_the_figure_by_at_least_its_bytes() {
    let body = 1000;
    let mut stream = vec![DEF_MACRO, 0x20];
    stream.extend(std::iter::repeat_n(b'.', body));
    stream.push(END);
    let raised = raised_by(&[], &stream);
    assert!(raised >= body, "{raised}");
    // Deleting it (a definition of no bytes) gives it back.
    let mut validator = validator_after(&stream);
    let defined = validator.held_bytes();
    let _ = validator.feed(&[DEF_MACRO, 0x20, END]);
    assert!(validator.held_bytes() + body <= defined, "{} after deleting, {defined} before", validator.held_bytes());
}

#[test]
fn a_drcs_character_raises_the_figure_by_at_least_its_bitmap() {
    let mut stream = vec![DEF_DRCS, 0x20];
    stream.extend_from_slice(&FILL);
    stream.push(END);
    let raised = raised_by(&squared(), &stream);
    assert!(raised >= MASK_ELEMENTS, "{raised}");
}

#[test]
fn a_texture_raises_the_figure_by_at_least_its_bitmap() {
    let mut stream = vec![DEF_TEXTURE, FIRST_TEXTURE];
    stream.extend_from_slice(&FILL);
    stream.push(END);
    let raised = raised_by(&squared(), &stream);
    assert!(raised >= MASK_ELEMENTS, "{raised}");
}

#[test]
fn a_definition_in_progress_and_an_open_pdi_raise_the_figure_by_at_least_their_bytes() {
    let mut macro_open = vec![DEF_MACRO, 0x20];
    macro_open.extend(std::iter::repeat_n(b'.', 1000));
    assert!(raised_by(&[], &macro_open) >= 1000);
    let mut drcs_open = vec![DEF_DRCS, 0x20];
    drcs_open.extend_from_slice(&FILL);
    assert!(raised_by(&squared(), &drcs_open) >= MASK_ELEMENTS);
    let mut pdi_open = vec![SO, POLYGON_FILLED];
    pdi_open.extend(std::iter::repeat_n(0x41, 1000));
    assert!(raised_by(&[], &pdi_open) >= 1000);
}

/// What a value shared in an `Arc` takes when one holder has it alone: the allocation of its
/// two reference counts and its structure, with the allocator's bookkeeping.
fn arc_allocation<T>() -> usize {
    (2 * size_of::<usize>() + size_of::<T>()).next_multiple_of(ALLOCATION_OVERHEAD_BYTES) + ALLOCATION_OVERHEAD_BYTES
}

#[test]
fn the_font_and_the_provided_sets_are_counted_as_given_when_held_alone() {
    let font = StrokeFont::parse(include_str!("../../../fonts/neoteletext.strokes")).unwrap();
    let font_heap = font.held_bytes() - size_of::<StrokeFont>();
    let mut validator = Validator::new();
    let held = validator.held_bytes();
    validator.set_font(font);
    let font_raised = validator.held_bytes() - held;
    assert!(font_raised >= font_heap + size_of::<StrokeFont>(), "{font_raised}");
    assert!(font_raised <= font_heap + arc_allocation::<StrokeFont>(), "{font_raised}");
    let mut set = BitmapSet::new(12, 20).unwrap();
    set.set_glyph(0x41, &[0xFFF; 20]).unwrap();
    let set_heap = set.held_bytes() - size_of::<BitmapSet>();
    assert!(set_heap >= 96 * 20 * size_of::<u16>(), "{set_heap}");
    let held = validator.held_bytes();
    validator.set_teletext_set(44, set).unwrap();
    let set_raised = validator.held_bytes() - held;
    assert!(set_raised >= set_heap + size_of::<BitmapSet>(), "{set_raised}");
    println!("the stroke font holds {font_heap} bytes beyond its structure; a 12 by 20 set {set_heap}");
}

/// TODO-6895: a server's many validators share one stroke font and one copy of each provided
/// set, each counted once by the server, not once in every validator (17 KB of a NAPLPS
/// reader's 32,600 bytes was its own copy of the font).
#[test]
fn a_shared_font_and_shared_sets_are_counted_by_their_sharer_not_by_each_validator() {
    let font = std::sync::Arc::new(StrokeFont::parse(include_str!("../../../fonts/neoteletext.strokes")).unwrap());
    let set = std::sync::Arc::new(BitmapSet::new(12, 20).unwrap());
    let alone = Validator::new().held_bytes();
    let validators: Vec<Validator> = (0..3)
        .map(|_| {
            let mut validator = Validator::new();
            validator.set_font(std::sync::Arc::clone(&font));
            validator.set_teletext_set(44, std::sync::Arc::clone(&set)).unwrap();
            validator
        })
        .collect();
    // Each holds the slots of the provided sets and no copy of the font or the set.
    for validator in &validators {
        let held = validator.held_bytes();
        assert!(held < alone + 1024, "{held} against {alone} with nothing given");
    }
    assert_eq!(std::sync::Arc::strong_count(&font), 4, "one font among them, not a copy each");
    // A validator left holding them alone counts them.
    drop(font);
    drop(set);
    let mut validators = validators;
    let last = validators.pop().unwrap();
    drop(validators);
    assert!(last.held_bytes() > alone + 17_000, "{}", last.held_bytes());
}

#[test]
fn objects_and_a_title_raise_a_terminals_figure_by_at_least_their_bytes() {
    let mut terminal = Terminal::new(4);
    let held = terminal.held_bytes();
    let objects: Vec<Object> = (1..=u16::try_from(MAX_OBJECTS).unwrap()).map(largest_object).collect();
    terminal.set_objects(&objects).unwrap();
    let raised = terminal.held_bytes() - held;
    let least = MAX_OBJECTS * (size_of::<Object>() + MAX_OBJECT_FRAMES + MAX_LABEL_BYTES);
    assert!(raised >= least, "{raised} raised, {least} allocated");
    let held = terminal.held_bytes();
    terminal.set_title(&"t".repeat(MAX_TITLE_BYTES)).unwrap();
    assert!(terminal.held_bytes() - held >= MAX_TITLE_BYTES);
    // A replaced object holds its bytes, not the room its caller gave it.
    let held = terminal.held_bytes();
    let mut roomy = largest_object(1);
    roomy.frames.reserve(1 << 20);
    roomy.label.reserve(1 << 20);
    terminal.replace_object(roomy).unwrap();
    assert_eq!(terminal.held_bytes(), held);
}

#[test]
fn the_heaviest_stream_a_validator_reads_stays_within_the_bound() {
    let stream = heaviest(&[]);
    let validator = validator_after(&stream);
    let held = validator.held_bytes();
    let definitions = MAX_ALL_MACRO_BYTES + (DEFINABLE_CODES + TEXTURE_MASKS) * MASK_ELEMENTS + MAX_PDI_BYTES;
    println!(
        "the heaviest stream ({} bytes) makes a validator hold {held} bytes; the bound is {MAX_HELD_BYTES}",
        stream.len()
    );
    assert!(held >= definitions, "{held} held, {definitions} defined");
    assert!(held <= MAX_HELD_BYTES, "{held} held, past the bound {MAX_HELD_BYTES}");
    const { assert!(MASK_BYTES >= MASK_ELEMENTS + ALLOCATION_OVERHEAD_BYTES) };
}

#[test]
fn the_heaviest_state_of_a_terminal_stays_within_the_bound_without_what_it_was_given() {
    // The largest colour map, every object at its largest, a title, every definition, and a
    // call stopped at a WAIT in the deepest of the nested macros, with a macro being defined.
    let mut terminal = Terminal::new(MAX_BITS);
    let objects: Vec<Object> = (1..=u16::try_from(MAX_OBJECTS).unwrap()).map(largest_object).collect();
    terminal.set_objects(&objects).unwrap();
    terminal.set_title(&"t".repeat(MAX_TITLE_BYTES)).unwrap();
    let mut wait = vec![SO];
    wait.extend_from_slice(&WAIT);
    wait.push(common::SI);
    let stream = heaviest(&wait);
    let mut canvas = Canvas::new(RECEIVER_CANVAS_WIDTH, RECEIVER_CANVAS_HEIGHT).unwrap();
    let (taken, _) = terminal.feed_until_wait(&mut canvas, &stream);
    assert!(taken < stream.len(), "the call stops at the WAIT");
    let held = terminal.held_bytes();
    let copies = MAX_MACRO_DEPTH * MAX_MACRO_BYTES;
    let least = MAX_ALL_MACRO_BYTES + (DEFINABLE_CODES + TEXTURE_MASKS) * MASK_ELEMENTS + copies;
    println!("the heaviest state makes a terminal hold {held} bytes; the bound is {MAX_HELD_BYTES}");
    assert!(held >= least, "{held} held, {least} defined and copied");
    assert!(held <= MAX_HELD_BYTES, "{held} held, past the bound {MAX_HELD_BYTES}");
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

/// What a validator holds after reading each page of `folder` whole, sorted.
fn held_by_pages(folder: &Path) -> Vec<usize> {
    let mut held: Vec<usize> = pages(folder)
        .iter()
        .map(|path| {
            let mut validator = Validator::new();
            let _ = validator.feed(&std::fs::read(path).unwrap());
            validator.held_bytes()
        })
        .collect();
    held.sort_unstable();
    held
}

/// The figures a server counts NAPLPS readers by (TODO-6854): what a validator holds after
/// reading each page of the NAPLPS corpus, the repository's samples and, when
/// `NAPLPS_EXTRA_PAGES_DIR` names one, another folder (the naplpsdemo channel's `pictures`),
/// without the font and the sets a server gives it. It prints the median and the largest of
/// each and checks the largest within the bound.
#[test]
#[ignore = "needs the NAPLPS pages of ~/devel/teletext-reference/NAPLPS (or NAPLPS_REFERENCE_DIR); a measurement printed for the record"]
fn what_the_corpus_makes_a_validator_hold() {
    let reference = std::env::var_os("NAPLPS_REFERENCE_DIR").map_or_else(
        || PathBuf::from(std::env::var_os("HOME").unwrap()).join("devel/teletext-reference/NAPLPS"),
        PathBuf::from,
    );
    assert!(reference.is_dir(), "{} holds the NAPLPS corpus", reference.display());
    let mut folders = vec![reference, PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../../samples"))];
    folders.extend(std::env::var_os("NAPLPS_EXTRA_PAGES_DIR").map(PathBuf::from));
    let font = StrokeFont::parse(include_str!("../../../fonts/neoteletext.strokes")).unwrap();
    println!(
        "a new validator holds {}; the stroke font adds {}",
        Validator::new().held_bytes(),
        font.held_bytes() - size_of::<StrokeFont>()
    );
    for folder in folders {
        let held = held_by_pages(&folder);
        assert!(!held.is_empty(), "{} holds pages", folder.display());
        let largest = *held.last().unwrap();
        println!(
            "{}: {} pages; a validator holds {} at the median, {} at the largest",
            folder.display(),
            held.len(),
            held[held.len() / 2],
            largest
        );
        assert!(largest <= MAX_HELD_BYTES);
    }
}
