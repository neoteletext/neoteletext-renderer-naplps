//! The fuzz target `naplps_objects` (neoteletext-common `docs/animation.md`, ANIM-23; REQ-6531):
//! any stream, objects, single objects redefined, and animation states. It must never panic, every object's drawing must
//! stay inside its rectangle, picking at a canvas pixel must equal picking at the design pixel
//! its centre lies in (TODO-6826), and the picture composed by damage must equal the picture
//! composed whole, with no pixel changed outside the damage reported (ANIM-4, ANIM-11). Each
//! input runs on the design picture's own canvas and on the teletext raster's 480 by 462 one
//! (DEC-6667, REQ-5819), where objects are placed by the design picture's pixels.
//!
//! This file holds the target's body, `naplps_objects`, which takes the fuzzer's bytes.
//! `crates/naplps-fuzz` runs it on its kept inputs and on inputs made by property testing
//! (DEC-6607); an engine guided by coverage would call it unchanged.

use naplps::{Animation, Canvas, Look, Object, ObjectKind, Terminal};

/// The picture objects are placed on (ANIM-11).
const WIDTH: u32 = naplps::limits::OBJECT_PICTURE_WIDTH;
/// See [`WIDTH`].
const HEIGHT: u32 = naplps::limits::OBJECT_PICTURE_HEIGHT;
/// The teletext raster's display area a NAPLPS page is drawn on (REQ-5819, DEC-6667): 40 cells
/// of 12 dots across, lines 19 to 480 of the 500-line page down.
const RASTER_WIDTH: u32 = 480;
/// See [`RASTER_WIDTH`].
const RASTER_HEIGHT: u32 = 462;
/// Bytes of one object's description in the input.
const OBJECT_BYTES: usize = 12;
/// The first macro code, 2/0; the input's macro codes are folded onto a few names from here so
/// that objects, looks and the stream's definitions meet.
const FIRST_MACRO: u8 = 0x20;
/// How many macro names the input's codes are folded onto.
const MACRO_NAMES: u8 = 8;

/// Reads the input a piece at a time; an exhausted input gives zeros.
struct Input<'a> {
    bytes: &'a [u8],
}

impl Input<'_> {
    fn byte(&mut self) -> u8 {
        match self.bytes.split_first() {
            Some((first, rest)) => {
                self.bytes = rest;
                *first
            }
            None => 0,
        }
    }

    fn word(&mut self) -> i16 {
        i16::from_be_bytes([self.byte(), self.byte()])
    }

    fn take(&mut self, count: usize) -> &[u8] {
        let (head, rest) = self.bytes.split_at(count.min(self.bytes.len()));
        self.bytes = rest;
        head
    }

    fn is_empty(&self) -> bool {
        self.bytes.is_empty()
    }
}

/// A macro code among the few the input uses, or 0 for none.
fn look_code(byte: u8) -> u8 {
    if byte & 0x80 == 0 { 0 } else { macro_code(byte) }
}

fn macro_code(byte: u8) -> u8 {
    FIRST_MACRO.saturating_add(byte % MACRO_NAMES)
}

/// An object from the input: mostly one the record allows, sometimes not, so that refusal is
/// exercised too.
fn object(input: &mut Input<'_>) -> Object {
    let description = input.take(OBJECT_BYTES).to_vec();
    let at = |index: usize| description.get(index).copied().unwrap_or(0);
    let region = at(0) & 1 == 1;
    let frames = if region {
        Vec::new()
    } else {
        (0..=(at(1) % 4)).map(|frame| macro_code(at(2).wrapping_add(frame))).collect()
    };
    Object {
        number: u16::from(at(3) % 16).saturating_add(u16::from(at(0) >> 7)),
        kind: if region { ObjectKind::Region } else { ObjectKind::Macro },
        shown: at(0) & 2 == 0,
        detectable: at(0) & 4 == 0,
        layer: 1u8.saturating_add(at(4) % 3).saturating_add(u8::from(at(4) == 0xFF)),
        order: i8::from_be_bytes([at(5)]),
        x: i16::from(at(6)).saturating_mul(3).saturating_sub(64),
        y: i16::from(at(7)).saturating_mul(2).saturating_sub(16),
        width: u16::from(at(8)).saturating_mul(2).saturating_add(1),
        height: u16::from(at(9)).saturating_add(1),
        origin_x: if region { 0 } else { i16::from(at(10)) },
        origin_y: if region { 0 } else { i16::from(at(11)).saturating_mul(2) },
        cover: if region { at(10) % 16 } else { 0 },
        hover: look_code(at(1)),
        pressed: look_code(at(2)),
        alternative: look_code(at(4)),
        frames,
        // A label is never drawn; one with a control character is refused (DEC-6638 item 6).
        label: match at(5) % 4 {
            0 => String::from("Button"),
            1 => String::from("\u{1b}[2J"),
            _ => String::new(),
        },
    }
}

fn animation(input: &mut Input<'_>) -> Animation {
    let flags = input.byte();
    Animation {
        shown: (flags & 1 != 0).then_some(flags & 2 != 0),
        position: (flags & 4 != 0).then(|| (input.word(), input.word())),
        layer: (flags & 8 != 0).then(|| input.byte() % 5),
        order: (flags & 16 != 0).then(|| i8::from_be_bytes([input.byte()])),
        frame: (flags & 32 != 0).then(|| input.byte() % 17),
        look: Look::from_code(flags >> 6).unwrap_or_default(),
    }
}

/// The pixels of `canvas` as a vector, for comparing two pictures.
fn differing(before: &Canvas, after: &Canvas) -> Vec<(u32, u32)> {
    let mut differing = Vec::new();
    for y in 0..after.height() {
        for x in 0..after.width() {
            if before.pixel(x, y) != after.pixel(x, y) {
                differing.push((x, y));
            }
        }
    }
    differing
}

/// Runs one input. Panics when a property fails, as a fuzzing engine expects.
///
/// # Panics
///
/// When the composed picture differs from a whole composition, or a pixel changed outside the
/// damage reported.
pub fn naplps_objects(data: &[u8]) {
    on_canvas(data, WIDTH, HEIGHT);
    on_canvas(data, RASTER_WIDTH, RASTER_HEIGHT);
}

/// Runs one input on a canvas of `width` by `height`.
fn on_canvas(data: &[u8], width: u32, height: u32) {
    let mut input = Input { bytes: data };
    let (Ok(mut background), Ok(mut presented)) = (Canvas::new(width, height), Canvas::new(width, height)) else {
        return;
    };
    let mut terminal = Terminal::new(4);
    let _ = terminal.compose(&background, &mut presented);
    let _ = terminal.take_damage();
    while !input.is_empty() {
        let before = presented.clone();
        let command = input.byte();
        match command % 6 {
            0 => {
                let count = usize::from(input.byte() % 6);
                let objects: Vec<Object> = (0..count).map(|_| object(&mut input)).collect();
                let _ = terminal.set_objects(&objects);
            }
            1 => {
                let number = u16::from(input.byte() % 16);
                let _ = terminal.set_animation(number, animation(&mut input));
            }
            2 => {
                let _ = terminal.clear_animation(u16::from(input.byte() % 16));
            }
            3 => {
                let number = u16::from(input.byte() % 16);
                let _ = terminal.set_pointer_look(number, Look::from_code(input.byte() % 4).unwrap_or_default());
            }
            4 => {
                // One object redefined by a record (DEC-6638 item 3, row 3.2).
                let _ = terminal.replace_object(object(&mut input));
            }
            _ => {
                let length = usize::from(input.byte());
                let stream = input.take(length).to_vec();
                let _ = terminal.feed(&mut background, &stream);
            }
        }
        // TODO-6826: an object owns exactly the canvas pixels whose centre lies in its design
        // rectangle, so picking at a canvas pixel is picking at its centre's design pixel.
        // The probe comes from the command byte, not a byte of its own, so that the kept inputs
        // read as they always have; doubled, it reaches across the raster's canvas.
        let probe = (u32::from(command) * 2, u32::from(command.reverse_bits()) * 2);
        let (across, down) = naplps::design_pixel(probe.0, probe.1, width, height);
        assert_eq!(
            terminal.objects_on_canvas(probe.0, probe.1, width, height),
            terminal.objects_at(across, down),
            "picking at canvas pixel {probe:?} and at its centre's design pixel ({across}, {down})"
        );
        let composed = terminal.compose(&background, &mut presented);
        assert!(composed.is_ok(), "two canvases of one size compose");
        let damage = terminal.take_damage();
        for (x, y) in differing(&before, &presented) {
            assert!(
                damage.is_some_and(|rect| rect.contains(x, y)),
                "pixel ({x}, {y}) changed outside the damage {damage:?}"
            );
        }
        // ANIM-13: an object's bounds lie on the picture.
        for object in terminal.objects() {
            if let Some(bounds) = terminal.bounds(object.number) {
                assert!(bounds.right() <= WIDTH && bounds.bottom() <= HEIGHT);
            }
        }
    }
    // ANIM-4: the picture composed by damage is the picture composed whole.
    let Ok(mut whole) = Canvas::new(width, height) else { return };
    terminal.invalidate();
    assert!(terminal.compose(&background, &mut whole).is_ok());
    let same = whole == presented;
    assert!(same, "the picture composed by damage differs from the picture composed whole");
}
