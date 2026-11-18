//! What the NAPLPS renderer gained so that the three renderers are equals (DEC-6638): a label on
//! each object (item 6, row 6.1), a title on the picture (item 3, row 2.8) and one object
//! redefined without a new stream (item 3, row 3.2). Each section names the requirement it
//! verifies.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::cast_possible_truncation,
    clippy::cast_possible_wrap,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::limits::{MAX_LABEL_BYTES, MAX_OBJECTS, MAX_TITLE_BYTES, OBJECT_PICTURE_HEIGHT, OBJECT_PICTURE_WIDTH};
use naplps::{Animation, Canvas, Error, Object, ObjectKind, Terminal};

const SO: u8 = 0x0E;
const DEF_MACRO: u8 = 0x80;
const END: u8 = 0x85;
/// SELECT COLOR (section 5.3.2.6).
const SELECT_COLOUR: u8 = 0x3E;
/// RECTANGLE, filled, from the drawing point (section 5.3.3.4).
const RECT_FILLED: u8 = 0x31;
/// POINT SET, absolute (section 5.3.3.1).
const POINT_SET: u8 = 0x24;
const WIDTH: u32 = OBJECT_PICTURE_WIDTH;
const HEIGHT: u32 = OBJECT_PICTURE_HEIGHT;
/// The object's rectangle: the bottom left 128 by 96 pixels of its macro's drawing.
const OBJECT_WIDTH: u16 = 128;
const OBJECT_HEIGHT: u16 = 96;

/// A three-byte coordinate pair in the default domain: (`x`/256, `y`/256) of the unit screen
/// (section 5.3.2.2.3).
fn pair(x: u8, y: u8) -> [u8; 3] {
    let (x, y) = (u16::from(x), u16::from(y));
    let byte = |shift: u16| 0x40 | ((((x >> shift) & 7) as u8) << 3) | (((y >> shift) & 7) as u8);
    [byte(6), byte(3), byte(0)]
}

/// PDI bytes drawing a filled rectangle of colour-map entry `entry` at the unit screen's origin,
/// (`width`, `height`) 256ths of it in size.
fn rectangle(entry: u8, width: u8, height: u8) -> Vec<u8> {
    let mut bytes = vec![SO, SELECT_COLOUR, 0x40 | (entry << 2), POINT_SET];
    bytes.extend(pair(0, 0));
    bytes.push(RECT_FILLED);
    bytes.extend(pair(width, height));
    bytes
}

/// DEF MACRO `code` holding `body`.
fn define(code: u8, body: &[u8]) -> Vec<u8> {
    let mut bytes = vec![DEF_MACRO, code];
    bytes.extend_from_slice(body);
    bytes.push(END);
    bytes
}

fn macro_object(number: u16, code: u8, x: i16, y: i16, label: &str) -> Object {
    Object {
        number,
        kind: ObjectKind::Macro,
        shown: true,
        detectable: true,
        layer: 2,
        order: 0,
        x,
        y,
        width: OBJECT_WIDTH,
        height: OBJECT_HEIGHT,
        origin_x: 0,
        origin_y: (HEIGHT - u32::from(OBJECT_HEIGHT)) as i16,
        cover: 0,
        hover: 0,
        pressed: 0,
        alternative: 0,
        frames: vec![code],
        label: label.to_owned(),
    }
}

/// The stream defines macro 2/0, a red rectangle, and macro 2/1, a green one.
fn stream() -> Vec<u8> {
    let mut bytes = define(0x20, &rectangle(2, 32, 32));
    bytes.extend(define(0x21, &rectangle(3, 32, 32)));
    bytes
}

/// The picture composed from `terminal`'s stream drawn on a fresh background.
fn composed(terminal: &mut Terminal, background: &Canvas, presented: &mut Canvas) {
    terminal.compose(background, presented).unwrap();
}

fn page() -> (Terminal, Canvas, Canvas) {
    let mut terminal = Terminal::new(4);
    let mut background = Canvas::new(WIDTH, HEIGHT).unwrap();
    let presented = Canvas::new(WIDTH, HEIGHT).unwrap();
    terminal.feed(&mut background, &stream());
    terminal.finish(&mut background);
    (terminal, background, presented)
}

// ----- The label (REQ for DEC-6638 item 6) -----------------------------------------------------

#[test]
fn a_label_is_carried_and_never_drawn() {
    let (mut with_label, background, mut labelled) = page();
    let (mut without, _, mut plain) = page();
    with_label.set_objects(&[macro_object(1, 0x20, 100, 100, "Play the next clip")]).unwrap();
    without.set_objects(&[macro_object(1, 0x20, 100, 100, "")]).unwrap();
    composed(&mut with_label, &background, &mut labelled);
    composed(&mut without, &background, &mut plain);
    assert_eq!(with_label.object(1).unwrap().label, "Play the next clip");
    assert!(labelled == plain, "a label changes no pixel");
}

#[test]
fn a_label_too_long_or_with_a_control_character_is_refused_with_its_set() {
    let (mut terminal, ..) = page();
    let longest = "a".repeat(MAX_LABEL_BYTES);
    assert_eq!(terminal.set_objects(&[macro_object(1, 0x20, 0, 0, &longest)]), Ok(()));
    let too_long = "a".repeat(MAX_LABEL_BYTES + 1);
    let good = macro_object(1, 0x20, 0, 0, "fine");
    assert_eq!(terminal.set_objects(&[good.clone(), macro_object(2, 0x20, 0, 0, &too_long)]), Err(Error::Object(1)));
    assert_eq!(terminal.set_objects(&[macro_object(2, 0x20, 0, 0, "line\nbreak")]), Err(Error::Object(0)));
    assert_eq!(terminal.set_objects(&[macro_object(2, 0x20, 0, 0, "\u{1b}[2J")]), Err(Error::Object(0)));
    // A refused set changes nothing: the longest label is still there.
    assert_eq!(terminal.object(1).unwrap().label, longest);
    // Plain text is any script: the bound is bytes, not characters.
    assert_eq!(terminal.set_objects(&[macro_object(3, 0x20, 0, 0, "Prochaine séquence, 次へ")]), Ok(()));
}

// ----- The title (REQ for DEC-6638 item 3, row 2.8) ----------------------------------------------

#[test]
fn a_title_is_carried_bounded_and_never_drawn() {
    let (mut terminal, mut background, _) = page();
    assert_eq!(terminal.title(), None);
    let before = background.clone();
    assert_eq!(terminal.set_title("Harbour webcam"), Ok(()));
    terminal.finish(&mut background);
    assert_eq!(terminal.title(), Some("Harbour webcam"));
    assert!(background == before, "a title changes no pixel");
    assert_eq!(terminal.set_title(&"t".repeat(MAX_TITLE_BYTES)), Ok(()));
    assert_eq!(terminal.set_title(&"t".repeat(MAX_TITLE_BYTES + 1)), Err(Error::Title));
    assert_eq!(terminal.set_title("tab\there"), Err(Error::Title));
    assert_eq!(terminal.title(), Some("t".repeat(MAX_TITLE_BYTES).as_str()), "a refused title leaves the old one");
    assert_eq!(terminal.set_title(""), Ok(()));
    assert_eq!(terminal.title(), None, "an empty title removes it");
}

// ----- One object redefined (REQ for DEC-6638 item 3, row 3.2) -----------------------------------

#[test]
fn replacing_one_object_redraws_it_and_leaves_the_others_and_their_state() {
    let (mut terminal, background, mut presented) = page();
    terminal
        .set_objects(&[macro_object(1, 0x20, 100, 100, "first"), macro_object(2, 0x20, 400, 100, "second")])
        .unwrap();
    assert!(terminal.set_animation(2, Animation { position: Some((400, 300)), ..Animation::default() }));
    assert!(terminal.set_animation(1, Animation { position: Some((50, 50)), ..Animation::default() }));
    composed(&mut terminal, &background, &mut presented);
    let _ = terminal.take_damage();
    // Ten pixels in from the bottom left of object 2's rectangle, where its macro's
    // rectangle (80 pixels square at the screen's bottom left) lands.
    let red = presented.pixel(410, 390).unwrap();
    assert_ne!(red, 0, "object 2 draws");

    // Object 1 becomes the green macro at a new place, with a new label.
    terminal.replace_object(macro_object(1, 0x21, 200, 200, "replaced")).unwrap();
    composed(&mut terminal, &background, &mut presented);
    let damage = terminal.take_damage().unwrap();

    // The result is what a whole set of the same objects, with object 2's state, composes.
    let (mut expected, _, mut whole) = page();
    expected
        .set_objects(&[macro_object(1, 0x21, 200, 200, "replaced"), macro_object(2, 0x20, 400, 100, "second")])
        .unwrap();
    assert!(expected.set_animation(2, Animation { position: Some((400, 300)), ..Animation::default() }));
    composed(&mut expected, &background, &mut whole);
    assert!(presented == whole, "the redefined picture is the picture of the new definitions");
    assert_eq!(presented.pixel(410, 390), Some(red), "object 2 keeps its moved position");
    let green = presented.pixel(210, 290).unwrap();
    assert!(green != red && green != 0, "object 1 draws its new macro");
    // Object 1's animation state is forgotten; object 2's is kept.
    assert_eq!(terminal.animation(1), None);
    assert!(terminal.animation(2).is_some());
    assert_eq!(terminal.object(1).unwrap().label, "replaced");
    // The damage covers where object 1 was (moved to 50, 50) and where it is now.
    assert!(damage.contains(60, 140) && damage.contains(210, 290), "{damage:?}");
    assert!(!damage.contains(410, 390), "object 2 is not repainted: {damage:?}");
}

#[test]
fn replacing_an_absent_object_adds_it_within_the_limit() {
    let (mut terminal, ..) = page();
    let many: Vec<Object> = (1..=MAX_OBJECTS as u16).map(|number| macro_object(number, 0x20, 0, 0, "")).collect();
    terminal.set_objects(&many[..MAX_OBJECTS - 1]).unwrap();
    assert_eq!(terminal.replace_object(many[MAX_OBJECTS - 1].clone()), Ok(()));
    assert_eq!(terminal.objects().len(), MAX_OBJECTS);
    let one_more = macro_object(MAX_OBJECTS as u16 + 1, 0x20, 0, 0, "");
    assert_eq!(terminal.replace_object(one_more), Err(Error::TooManyObjects));
    // A definition the record does not allow is refused and nothing changes.
    let mut bad = macro_object(1, 0x20, 0, 0, "");
    bad.layer = 0;
    assert_eq!(terminal.replace_object(bad), Err(Error::Object(0)));
    assert_eq!(terminal.object(1).unwrap().layer, 2);
}
