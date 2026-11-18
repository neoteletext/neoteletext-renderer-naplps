//! The object layer and damage (neoteletext-common `docs/animation.md`, ANIM-4, ANIM-6 and
//! ANIM-11 to ANIM-14; REQ-6531). Each test names the ANIM-n it verifies.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::cast_possible_truncation,
    clippy::cast_possible_wrap,
    clippy::cast_sign_loss,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::limits::{MAX_OBJECT_FRAMES, MAX_OBJECTS, OBJECT_PICTURE_HEIGHT, OBJECT_PICTURE_WIDTH};
use naplps::{Animation, Canvas, Error, Look, Object, ObjectKind, Rect, Terminal, design_pixel};

const SO: u8 = 0x0E;
const ESC: u8 = 0x1B;
const SS2: u8 = 0x19;
const DEF_MACRO: u8 = 0x80;
const DEFP_MACRO: u8 = 0x81;
const DEF_DRCS: u8 = 0x83;
const DEF_TEXTURE: u8 = 0x84;
const END: u8 = 0x85;
/// SELECT COLOR (section 5.3.2.6).
const SELECT_COLOUR: u8 = 0x3E;
/// RECTANGLE, filled, from the drawing point (section 5.3.3.4).
const RECT_FILLED: u8 = 0x31;
/// POINT SET, absolute (section 5.3.3.1).
const POINT_SET: u8 = 0x24;
/// WAIT and its fixed-format byte (section 5.3.2.8).
const WAIT: [u8; 2] = [0x3D, 0x5C];
const WIDTH: u32 = OBJECT_PICTURE_WIDTH;
const HEIGHT: u32 = OBJECT_PICTURE_HEIGHT;

/// A three-byte coordinate pair in the default domain: (`x`/256, `y`/256) of the unit screen
/// (section 5.3.2.2.3: three bits of x and three of y a byte, the sign first).
fn pair(x: u8, y: u8) -> [u8; 3] {
    let (x, y) = (u16::from(x), u16::from(y));
    let byte = |shift: u16| 0x40 | ((((x >> shift) & 7) as u8) << 3) | (((y >> shift) & 7) as u8);
    [byte(6), byte(3), byte(0)]
}

/// SELECT COLOR of colour-map entry `entry` of 16.
fn select(entry: u8) -> [u8; 2] {
    [SELECT_COLOUR, 0x40 | (entry << 2)]
}

/// PDI bytes drawing a filled rectangle of `entry` from (`x`, `y`) of size (`width`, `height`),
/// all in 256ths of the unit screen.
fn rectangle(entry: u8, x: u8, y: u8, width: u8, height: u8) -> Vec<u8> {
    let mut bytes = vec![SO];
    bytes.extend(select(entry));
    bytes.push(POINT_SET);
    bytes.extend(pair(x, y));
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

/// A macro object of one frame, macro `code`, whose rectangle is the bottom left 128 by 96
/// pixels of the macro's own drawing, placed at (`x`, `y`) on layer 2.
fn macro_object(number: u16, code: u8, x: i16, y: i16) -> Object {
    Object {
        number,
        kind: ObjectKind::Macro,
        shown: true,
        detectable: true,
        layer: 2,
        order: 0,
        x,
        y,
        width: 128,
        height: 96,
        origin_x: 0,
        origin_y: (HEIGHT - 96) as i16,
        cover: 0,
        hover: 0,
        pressed: 0,
        alternative: 0,
        frames: vec![code],
        label: String::new(),
    }
}

fn region(number: u16, x: i16, y: i16, width: u16, height: u16, cover: u8) -> Object {
    Object {
        number,
        kind: ObjectKind::Region,
        shown: true,
        detectable: true,
        layer: 1,
        order: 0,
        x,
        y,
        width,
        height,
        origin_x: 0,
        origin_y: 0,
        cover,
        hover: 0,
        pressed: 0,
        alternative: 0,
        frames: Vec::new(),
        label: String::new(),
    }
}

/// A terminal whose stream has drawn `stream`, with its background and a composed picture.
struct Page {
    terminal: Terminal,
    background: Canvas,
    presented: Canvas,
}

impl Page {
    fn new(stream: &[u8]) -> Self {
        Self::sized(stream, WIDTH, HEIGHT)
    }

    /// A page on a canvas of `width` by `height`.
    fn sized(stream: &[u8], width: u32, height: u32) -> Self {
        let mut page = Self {
            terminal: Terminal::new(4),
            background: Canvas::new(width, height).unwrap(),
            presented: Canvas::new(width, height).unwrap(),
        };
        page.feed(stream);
        page.compose();
        let _ = page.terminal.take_damage();
        page
    }

    fn feed(&mut self, stream: &[u8]) {
        let _ = self.terminal.feed(&mut self.background, stream);
        let _ = self.terminal.finish(&mut self.background);
    }

    fn compose(&mut self) -> Option<Rect> {
        self.terminal.compose(&self.background, &mut self.presented).unwrap()
    }

    /// The picture composed whole, from nothing.
    fn whole(&mut self) -> Canvas {
        let mut whole = Canvas::new(WIDTH, HEIGHT).unwrap();
        self.terminal.invalidate();
        let _ = self.terminal.compose(&self.background, &mut whole).unwrap();
        self.terminal.invalidate();
        whole
    }
}

/// The smallest rectangle holding every pixel of `canvas` equal to `entry`.
fn extent(canvas: &Canvas, entry: u8) -> Option<Rect> {
    let mut found: Option<Rect> = None;
    for y in 0..canvas.height() {
        for x in 0..canvas.width() {
            if canvas.pixel(x, y) == Some(entry) {
                let one = Rect { x, y, width: 1, height: 1 };
                found = Some(found.map_or(one, |all| all.union(&one)));
            }
        }
    }
    found
}

/// Whether two pictures are the same; a failure then prints its message and not 307,200 pixels.
fn same(a: &Canvas, b: &Canvas) -> bool {
    a == b
}

fn count(canvas: &Canvas, entry: u8) -> usize {
    canvas.pixels().iter().fold(0, |count, &pixel| count + usize::from(pixel == entry))
}

/// The pixels at which two pictures differ.
fn differing(a: &Canvas, b: &Canvas, width: u32, height: u32) -> Vec<(u32, u32)> {
    let mut differing = Vec::new();
    for y in 0..height {
        for x in 0..width {
            if a.pixel(x, y) != b.pixel(x, y) {
                differing.push((x, y));
            }
        }
    }
    differing
}

/// Macro 2/0: a rectangle of entry 3, 32/256 by 16/256 of the unit screen, from (0, 0): 80 by
/// 39 pixels at the bottom left of a 640 by 480 picture.
fn small_macro() -> Vec<u8> {
    define(0x20, &rectangle(3, 0, 0, 32, 16))
}

// ----- ANIM-4: damage ------------------------------------------------------------------------

#[test]
fn stream_drawing_reports_the_rectangle_it_changed() {
    // ANIM-4: the rectangle of pixels written since the caller last took it.
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(4);
    assert_eq!(terminal.take_damage(), None);
    let _ = terminal.feed(&mut canvas, &rectangle(5, 64, 32, 32, 16));
    let _ = terminal.finish(&mut canvas);
    let damage = terminal.take_damage().expect("a rectangle was drawn");
    assert_eq!(Some(damage), extent(&canvas, 5), "the damage is exactly the pixels that changed");
    assert_eq!(terminal.take_damage(), None, "taking it forgets it");
    // Drawing the same pixels again changes nothing, so nothing is reported.
    let _ = terminal.feed(&mut canvas, &rectangle(5, 64, 32, 32, 16));
    let _ = terminal.finish(&mut canvas);
    assert_eq!(terminal.take_damage(), None);
}

#[test]
fn no_pixel_outside_the_damage_changes_for_random_streams() {
    // ANIM-4's property for the stream's own drawing.
    let mut state = 0x0D4A_A6E5u64;
    let mut next = move || {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        state
    };
    let mut canvas = Canvas::new(160, 120).unwrap();
    let mut terminal = Terminal::new(4);
    for _ in 0..40 {
        let before = canvas.clone();
        let length = next() % 40;
        let mut bytes = vec![SO];
        bytes.extend((0..length).map(|_| {
            let value = next();
            let byte = value.to_le_bytes()[1];
            if value % 4 == 0 { 0x20 | (byte & 0x1F) } else { 0x40 | (byte & 0x3F) }
        }));
        let _ = terminal.feed(&mut canvas, &bytes);
        let damage = terminal.take_damage();
        for (x, y) in differing(&before, &canvas, 160, 120) {
            assert!(damage.is_some_and(|rect| rect.contains(x, y)), "({x}, {y}) changed outside {damage:?}");
        }
    }
}

// ----- ANIM-11: objects ----------------------------------------------------------------------

#[test]
fn an_object_at_two_positions_gives_the_same_pixels_moved() {
    // ANIM-11: every pixel moved by (x - origin x, y - origin y).
    let mut page = Page::new(&small_macro());
    page.terminal.set_objects(&[macro_object(1, 0x20, 100, 50)]).unwrap();
    page.compose();
    let first = extent(&page.presented, 3).expect("the object is drawn");
    assert_eq!((first.x, first.width), (100, 81), "the macro's left edge is at the object's x");
    assert_eq!(first.bottom(), 50 + 96, "the macro's bottom row is the object's bottom row");
    let pixels = count(&page.presented, 3);
    assert!(page.terminal.set_animation(1, Animation { position: Some((300, 200)), ..Animation::default() }));
    page.compose();
    let second = extent(&page.presented, 3).unwrap();
    assert_eq!((second.x, second.y), (first.x + 200, first.y + 150));
    assert_eq!((second.width, second.height), (first.width, first.height));
    assert_eq!(count(&page.presented, 3), pixels, "the same pixels, nothing left behind");
    assert_eq!(
        page.background.pixels().iter().filter(|&&pixel| pixel != 0).count(),
        0,
        "the stream's picture is untouched"
    );
}

#[test]
fn an_object_is_written_only_inside_its_rectangle() {
    // ANIM-11 and ANIM-13: a macro drawing far more than the rectangle is clipped to it.
    let mut page = Page::new(&define(0x20, &rectangle(3, 0, 0, 255, 199)));
    let mut object = macro_object(1, 0x20, 200, 100);
    object.width = 40;
    object.height = 30;
    page.terminal.set_objects(&[object]).unwrap();
    page.compose();
    let bounds = page.terminal.bounds(1).unwrap();
    assert_eq!(bounds, Rect { x: 200, y: 100, width: 40, height: 30 });
    assert_eq!(extent(&page.presented, 3), Some(bounds), "every written pixel lies inside the bounds, which it fills");
}

#[test]
fn a_hidden_region_is_its_cover_and_a_shown_one_changes_nothing() {
    // ANIM-11: a region.
    let mut page = Page::new(&rectangle(5, 0, 0, 255, 199));
    let stream_picture = page.presented.clone();
    page.terminal.set_objects(&[region(2, 40, 60, 100, 50, 9)]).unwrap();
    page.compose();
    assert!(same(&page.presented, &stream_picture), "shown, a region changes nothing");
    assert!(page.terminal.set_animation(2, Animation { shown: Some(false), ..Animation::default() }));
    let damage = page.compose();
    assert_eq!(damage, Some(Rect { x: 40, y: 60, width: 100, height: 50 }));
    assert_eq!(extent(&page.presented, 9), damage, "hidden, its rectangle is its cover");
    assert_eq!(page.terminal.bounds(2), None, "an object that is not shown has no bounds (ANIM-13)");
    assert!(page.terminal.clear_animation(2));
    page.compose();
    assert!(same(&page.presented, &stream_picture), "shown again, the stream's picture is back");
}

#[test]
fn the_ignored_commands_change_nothing_of_the_streams_state() {
    // ANIM-11: SET COLOR's redefinition of the colour map, BLINK, WAIT, RESET and the five
    // definitions have no effect inside an object's macro.
    let mut body = vec![SO];
    body.extend([0x20, 0x7F, 0x7F]); // RESET of everything, clearing the screen
    body.extend(WAIT);
    body.push(0x45);
    body.extend(select(1));
    body.extend([0x3C, 0x7F, 0x7F, 0x7F]); // SET COLOR: entry 1 to white
    body.extend([0x3F, 0x5C, 0x45, 0x45, 0x40]); // BLINK entry 1 to entry 7
    body.extend([0x8E, 0x07]); // BLINK START, BEL
    body.extend([DEF_MACRO, 0x21, SO, RECT_FILLED, 0x7F, 0x7F, 0x7F, END]);
    body.extend([DEFP_MACRO, 0x22, END]);
    body.extend([DEF_DRCS, 0x21, SO, RECT_FILLED, 0x7F, 0x7F, 0x7F, END]);
    body.extend([DEF_TEXTURE, 0x41, SO, RECT_FILLED, 0x7F, 0x7F, 0x7F, END]);
    body.extend(rectangle(3, 0, 0, 32, 16));
    // The stream: the macro, a second macro 2/1 that must survive, and a picture.
    let mut stream = define(0x20, &body);
    stream.extend(define(0x21, &rectangle(6, 0, 0, 8, 8)));
    stream.extend(rectangle(5, 128, 100, 32, 16));
    let mut page = Page::new(&stream);
    let colours = page.terminal.palette().clone();
    let background = page.background.clone();
    page.terminal.set_objects(&[macro_object(1, 0x20, 100, 50), macro_object(2, 0x21, 300, 50)]).unwrap();
    page.compose();
    assert!(count(&page.presented, 3) > 0, "the macro's own drawing appears");
    assert!(count(&page.presented, 6) > 0, "macro 2/1 is still the stream's definition");
    assert!(same(&page.background, &background), "RESET inside an object clears nothing of the stream's picture");
    assert!(*page.terminal.palette() == colours, "the colour map and its blinks are the stream's");
    assert_eq!(page.terminal.palette().blinks(), []);
    // The stream goes on in its own state: no event came from the object, and its drawing
    // colour is still entry 5.
    let mut more = vec![POINT_SET];
    more.extend(pair(0, 100));
    more.push(RECT_FILLED);
    more.extend(pair(8, 8));
    let events = page.terminal.feed(&mut page.background, &more);
    let finished = page.terminal.finish(&mut page.background);
    assert_eq!((events, finished), (Vec::new(), Vec::new()));
    assert!(count(&page.background, 5) > count(&background, 5));
}

#[test]
fn an_objects_macro_calls_other_macros_and_an_undefined_macro_draws_nothing() {
    // ANIM-11: calling another macro works as in the stream; a macro not defined draws nothing.
    let mut stream = small_macro();
    stream.extend(define(0x21, &[ESC, 0x2E, 0x20, 0x7A, SS2, 0x20]));
    let mut page = Page::new(&stream);
    page.terminal.set_objects(&[macro_object(1, 0x21, 10, 10), macro_object(2, 0x30, 300, 300)]).unwrap();
    page.compose();
    let drawn = extent(&page.presented, 3).unwrap();
    assert_eq!(drawn.x, 10);
    assert!(drawn.right() < 300, "object 2's macro is not defined");
}

#[test]
fn an_objects_drawing_stops_at_its_byte_limit() {
    // ANIM-11, ANIM-16: MAX_OBJECT_BYTES processed, macro expansion counted. Macro 2/1 calls
    // 2/2 sixty times, 2/2 calls 2/3 sixty times and 2/3 calls 2/4 sixty times: 216,000 calls,
    // within the stream's limit and far beyond an object's; the rectangle follows the calls.
    let mut stream = vec![];
    for code in 0x21..0x24u8 {
        let mut body = vec![ESC, 0x2E, 0x20, 0x7A];
        for _ in 0..60 {
            body.extend([SS2, code + 1]);
        }
        if code == 0x21 {
            body.extend(rectangle(3, 0, 0, 32, 16));
        }
        stream.extend(define(code, &body));
    }
    stream.extend(define(0x24, &[0x00]));
    let mut page = Page::new(&stream);
    page.terminal.set_objects(&[macro_object(1, 0x21, 10, 10)]).unwrap();
    page.compose();
    assert_eq!(count(&page.presented, 3), 0, "the object's drawing stopped before the rectangle");
    // The stream's own limit and events are untouched by an object's: called in the stream,
    // the same macro reaches its rectangle and reports nothing.
    let events = page.terminal.feed(&mut page.background, &[ESC, 0x2E, 0x20, 0x7A, SS2, 0x21]);
    let finished = page.terminal.finish(&mut page.background);
    assert_eq!((events, finished), (Vec::new(), Vec::new()));
    assert!(count(&page.background, 3) > 0);
}

#[test]
fn set_objects_refuses_what_the_record_does_not_allow() {
    // ANIM-11's table and ANIM-16: a set is refused whole.
    let mut terminal = Terminal::new(4);
    let good = macro_object(1, 0x20, 0, 0);
    let refused = |change: &dyn Fn(&mut Object)| {
        let mut object = good.clone();
        change(&mut object);
        Terminal::new(4).set_objects(&[good.clone(), object])
    };
    assert_eq!(refused(&|object| object.number = 0), Err(Error::Object(1)));
    assert_eq!(refused(&|_| {}), Err(Error::Object(1)), "a repeated number");
    let other = |change: &dyn Fn(&mut Object)| {
        refused(&|object| {
            object.number = 2;
            change(object);
        })
    };
    assert_eq!(other(&|_| {}), Ok(()));
    assert_eq!(other(&|object| object.layer = 0), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.layer = 4), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.width = 0), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.width = 641), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.height = 481), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.frames.clear()), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.frames = vec![0x20; MAX_OBJECT_FRAMES + 1]), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.frames = vec![0x1F]), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.cover = 1), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.hover = 0x80), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.kind = ObjectKind::Region), Err(Error::Object(1)), "a region has no frames");
    let many: Vec<Object> = (1..=MAX_OBJECTS as u16 + 1).map(|number| macro_object(number, 0x20, 0, 0)).collect();
    assert_eq!(terminal.set_objects(&many), Err(Error::TooManyObjects));
    assert_eq!(terminal.set_objects(&many[..MAX_OBJECTS]), Ok(()));
    assert_eq!(terminal.set_objects(&many), Err(Error::TooManyObjects));
    assert_eq!(terminal.objects().len(), MAX_OBJECTS, "a refused set changes nothing");
}

#[test]
fn replacing_the_objects_forgets_their_animation_state() {
    // ANIM-6: a NAPLPS_OBJECTS record forgets the state of what it replaces.
    let mut page = Page::new(&small_macro());
    let objects = [macro_object(1, 0x20, 100, 50)];
    page.terminal.set_objects(&objects).unwrap();
    let moved = Animation { position: Some((300, 200)), ..Animation::default() };
    assert!(page.terminal.set_animation(1, moved));
    assert_eq!(page.terminal.animation(1), Some(moved));
    assert!(!page.terminal.set_animation(7, moved), "a target that does not exist");
    assert!(!page.terminal.set_animation(1, Animation { layer: Some(4), ..moved }));
    assert!(!page.terminal.set_animation(1, Animation { frame: Some(16), ..moved }));
    page.terminal.set_objects(&objects).unwrap();
    assert_eq!(page.terminal.animation(1), None);
    page.compose();
    assert_eq!(extent(&page.presented, 3).unwrap().x, 100);
    assert!(!page.terminal.clear_animation(1));
}

// ----- ANIM-12: layers and order -------------------------------------------------------------

#[test]
fn objects_are_drawn_by_layer_then_order_then_number() {
    // ANIM-12. Two objects in the same place: the later drawn is seen.
    let mut stream = small_macro();
    stream.extend(define(0x21, &rectangle(6, 0, 0, 32, 16)));
    let mut page = Page::new(&stream);
    let (mut low, mut high) = (macro_object(1, 0x20, 100, 100), macro_object(2, 0x21, 100, 100));
    low.layer = 2;
    high.layer = 2;
    page.terminal.set_objects(&[high.clone(), low.clone()]).unwrap();
    page.compose();
    assert_eq!(count(&page.presented, 3), 0, "equal layer and order: the higher number is drawn last");
    assert!(page.terminal.set_animation(1, Animation { order: Some(1), ..Animation::default() }));
    page.compose();
    assert_eq!(count(&page.presented, 6), 0, "the higher order is drawn last");
    assert!(page.terminal.set_animation(2, Animation { layer: Some(3), ..Animation::default() }));
    page.compose();
    assert_eq!(count(&page.presented, 3), 0, "the higher layer is drawn last, whatever the order");
    assert_eq!(page.terminal.objects_at(110, 190), vec![1, 2], "picking gives each object, in drawing order");
    assert!(same(&page.whole(), &page.presented));
}

#[test]
fn a_moving_object_does_not_draw_the_stream_again() {
    // ANIM-12: the damaged rectangle is filled by copying the background's pixels.
    let mut page = Page::new(&[small_macro(), rectangle(5, 0, 0, 255, 199)].concat());
    let background = page.background.clone();
    page.terminal.set_objects(&[macro_object(1, 0x20, 100, 50)]).unwrap();
    page.compose();
    let _ = page.terminal.take_damage();
    assert!(page.terminal.set_animation(1, Animation { position: Some((120, 60)), ..Animation::default() }));
    let pending = page.terminal.pending(&page.presented).unwrap();
    assert_eq!(pending, Rect { x: 100, y: 50, width: 148, height: 106 }, "what it left and what it reaches");
    let changed = page.compose().unwrap();
    assert_eq!(page.terminal.take_damage(), Some(changed));
    assert!(pending.intersection(&changed) == Some(changed), "only pixels inside the pending rectangle changed");
    assert!(same(&page.background, &background));
    assert_eq!(page.terminal.pending(&page.presented), None);
    assert!(same(&page.whole(), &page.presented));
}

// ----- ANIM-13: bounds -----------------------------------------------------------------------

#[test]
fn bounds_are_the_objects_rectangle_cut_to_the_picture() {
    // ANIM-13.
    let mut page = Page::new(&small_macro());
    page.terminal.set_objects(&[macro_object(1, 0x20, -28, 400)]).unwrap();
    assert_eq!(page.terminal.bounds(1), Some(Rect { x: 0, y: 400, width: 100, height: 80 }));
    assert_eq!(page.terminal.bounds(9), None, "no such object");
    assert!(page.terminal.set_animation(1, Animation { position: Some((640, 0)), ..Animation::default() }));
    assert_eq!(page.terminal.bounds(1), None, "wholly outside the picture");
    assert!(page.terminal.set_animation(1, Animation { position: Some((i16::MIN, i16::MAX)), ..Animation::default() }));
    assert_eq!(page.terminal.bounds(1), None);
    page.compose();
    assert_eq!(count(&page.presented, 3), 0);
}

// ----- ANIM-14 and ANIM-6: frames and looks --------------------------------------------------

#[test]
fn the_frame_in_force_is_drawn_and_a_frame_beyond_the_last_shows_the_last() {
    // ANIM-14.
    let mut stream = Vec::new();
    for (code, entry) in [(0x20u8, 3u8), (0x21, 4), (0x22, 5), (0x23, 6)] {
        stream.extend(define(code, &rectangle(entry, 0, 0, 32, 16)));
    }
    let mut page = Page::new(&stream);
    let mut object = macro_object(1, 0x20, 100, 50);
    object.frames = vec![0x20, 0x21, 0x22, 0x23];
    page.terminal.set_objects(&[object]).unwrap();
    page.compose();
    assert!(count(&page.presented, 3) > 0, "frame 0 without animation state");
    for (frame, entry) in [(1u8, 4u8), (2, 5), (3, 6), (15, 6), (0, 3)] {
        assert!(page.terminal.set_animation(1, Animation { frame: Some(frame), ..Animation::default() }));
        page.compose();
        let lit: Vec<u8> = (3..=6).filter(|&entry| count(&page.presented, entry) > 0).collect();
        assert_eq!(lit, vec![entry], "frame {frame}");
    }
}

#[test]
fn a_forced_look_is_drawn_before_the_pointers_look_and_the_frame() {
    // ANIM-6: the forced look; without one the pointer decides the look.
    let mut stream = Vec::new();
    for (code, entry) in [(0x20u8, 3u8), (0x21, 4), (0x22, 5), (0x23, 6)] {
        stream.extend(define(code, &rectangle(entry, 0, 0, 32, 16)));
    }
    let mut page = Page::new(&stream);
    let mut object = macro_object(1, 0x20, 100, 50);
    object.hover = 0x21;
    object.pressed = 0x22;
    page.terminal.set_objects(&[object]).unwrap();
    let shows = |page: &mut Page| {
        page.compose();
        (3..=6u8).filter(|&entry| count(&page.presented, entry) > 0).collect::<Vec<u8>>()
    };
    assert_eq!(shows(&mut page), vec![3]);
    assert!(page.terminal.set_pointer_look(1, Look::Hover));
    assert_eq!(shows(&mut page), vec![4]);
    assert!(page.terminal.set_animation(1, Animation { look: Look::Pressed, ..Animation::default() }));
    assert_eq!(shows(&mut page), vec![5], "the forced look, whatever the pointer does");
    assert!(page.terminal.set_animation(1, Animation { look: Look::Alternative, ..Animation::default() }));
    assert_eq!(shows(&mut page), vec![3], "a look the object does not have leaves the frame");
    assert!(page.terminal.clear_animation(1));
    assert_eq!(shows(&mut page), vec![4], "the pointer's look again");
    assert!(page.terminal.set_pointer_look(1, Look::Normal));
    assert_eq!(shows(&mut page), vec![3]);
    assert!(!page.terminal.set_pointer_look(5, Look::Hover));
}

#[test]
fn redefining_a_macro_repaints_the_objects_that_draw_it() {
    // ANIM-11: an object's macro is executed "as the stream last defined it".
    let mut page = Page::new(&small_macro());
    page.terminal.set_objects(&[macro_object(1, 0x20, 100, 50)]).unwrap();
    page.compose();
    page.feed(&define(0x20, &rectangle(6, 0, 0, 32, 16)));
    page.compose();
    assert_eq!((count(&page.presented, 3) > 0, count(&page.presented, 6) > 0), (false, true));
    assert!(same(&page.whole(), &page.presented));
}

// ----- ANIM-4 for objects: the damage property -----------------------------------------------

#[test]
fn composing_by_damage_equals_composing_whole_for_random_changes() {
    // ANIM-4: for random sequences of changes, the damaged rendering equals the whole
    // rendering, and no pixel outside the reported rectangle differs.
    let mut state = 0x0B1E_C75Du64;
    let mut next = move |below: u64| {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        state % below
    };
    let mut stream = Vec::new();
    for (code, entry) in [(0x20u8, 3u8), (0x21, 4), (0x22, 5), (0x23, 6)] {
        stream.extend(define(code, &rectangle(entry, 0, 0, 24 + 8 * (code - 0x20), 20)));
    }
    stream.extend(rectangle(1, 10, 10, 200, 150));
    let mut page = Page::new(&stream);
    let mut objects = Vec::new();
    for number in 1..=6u16 {
        let mut object = macro_object(number, 0x20 + (number % 4) as u8, (number * 80) as i16, (number * 50) as i16);
        object.frames = vec![0x20, 0x21, 0x22, 0x23];
        object.hover = 0x23;
        object.layer = 1 + (number % 3) as u8;
        objects.push(object);
    }
    objects.push(region(7, 200, 100, 150, 120, 9));
    objects.push(region(8, 250, 150, 150, 120, 10));
    page.terminal.set_objects(&objects).unwrap();
    page.compose();
    let _ = page.terminal.take_damage();
    for step in 0..120 {
        let before = page.presented.clone();
        for _ in 0..=next(3) {
            let number = 1 + next(8) as u16;
            match next(8) {
                0 => {
                    let _ = page.terminal.clear_animation(number);
                }
                1 => {
                    let look = Look::from_code(next(4) as u8).unwrap();
                    let _ = page.terminal.set_pointer_look(number, look);
                }
                2 => page.feed(&rectangle(next(16) as u8, next(200) as u8, next(150) as u8, 30, 30)),
                3 => page.feed(&define(0x20 + next(4) as u8, &rectangle(next(16) as u8, 0, 0, 30, 24))),
                _ => {
                    let animation = Animation {
                        shown: (next(3) == 0).then(|| next(2) == 0),
                        position: (next(2) == 0).then(|| (next(700) as i16 - 40, next(520) as i16 - 30)),
                        layer: (next(3) == 0).then(|| next(4) as u8),
                        order: (next(3) == 0).then(|| next(5) as i8 - 2),
                        frame: (next(2) == 0).then(|| next(6) as u8),
                        look: Look::from_code(next(4) as u8).unwrap(),
                    };
                    assert!(page.terminal.set_animation(number, animation));
                }
            }
        }
        let pending = page.terminal.pending(&page.presented);
        let changed = page.compose();
        let damage = page.terminal.take_damage();
        assert_eq!(damage, changed, "step {step}");
        for (x, y) in differing(&before, &page.presented, WIDTH, HEIGHT) {
            assert!(damage.is_some_and(|rect| rect.contains(x, y)), "step {step}: ({x}, {y}) outside {damage:?}");
            assert!(pending.is_some_and(|rect| rect.contains(x, y)), "step {step}: ({x}, {y}) outside {pending:?}");
        }
        if step % 10 == 9 {
            assert!(same(&page.whole(), &page.presented), "step {step}: damage and whole composition differ");
            let _ = page.compose();
            let _ = page.terminal.take_damage();
        }
    }
}

#[test]
fn compose_refuses_canvases_of_different_sizes() {
    let mut terminal = Terminal::new(4);
    let background = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut presented = Canvas::new(320, 240).unwrap();
    assert_eq!(terminal.compose(&background, &mut presented), Err(Error::CanvasSize));
}

// ----- ANIM-11 on a canvas other than the design picture (DEC-6667, REQ-5819) -----------------

/// The teletext raster's display area a NAPLPS page is drawn on: 40 cells of 12 dots across and
/// lines 19 to 480 of the 500-line page down (REQ-5819, DEC-6667).
const RASTER_WIDTH: u32 = 480;
const RASTER_HEIGHT: u32 = 462;
/// The canvases an object is checked on: the design picture's own and the teletext raster's.
const CANVASES: [(u32, u32); 2] = [(WIDTH, HEIGHT), (RASTER_WIDTH, RASTER_HEIGHT)];

/// Every pixel of `canvas` equal to `entry`.
fn pixels_of(canvas: &Canvas, entry: u8) -> Vec<(u32, u32)> {
    let mut found = Vec::new();
    for y in 0..canvas.height() {
        for x in 0..canvas.width() {
            if canvas.pixel(x, y) == Some(entry) {
                found.push((x, y));
            }
        }
    }
    found
}

/// Every pixel of `rect`.
fn pixels_in(rect: Rect) -> Vec<(u32, u32)> {
    (rect.y..rect.bottom()).flat_map(|y| (rect.x..rect.right()).map(move |x| (x, y))).collect()
}

/// A macro object of macro `code` whose rectangle is `rect` of the design picture, its drawing
/// moved there from (`origin_x`, `origin_y`).
fn object_at(number: u16, code: u8, rect: Rect, origin: (i16, i16)) -> Object {
    let mut object = macro_object(number, code, rect.x as i16, rect.y as i16);
    object.width = rect.width as u16;
    object.height = rect.height as u16;
    (object.origin_x, object.origin_y) = origin;
    object
}

#[test]
fn an_object_on_the_teletext_raster_is_clipped_to_its_rectangle_scaled() {
    // ANIM-11 on the raster of DEC-6667: a macro drawing far more than its object is cut to the
    // object's design rectangle as it lies on the canvas. The rectangle is the cells of row 7,
    // columns 12 to 15, as the component library writes them (design y 126 to 146 for raster
    // lines 140 to 159, which are canvas rows 121 to 140; 16 design pixels a column, 12 canvas
    // pixels): before this was fixed the design rectangle was used as canvas pixels, cutting
    // its top five lines and a quarter of its width. Canvas column 192, the first dot of
    // column 16, is not the object's: its centre is design x 256, the next cell's (TODO-6826).
    let design = Rect { x: 192, y: 126, width: 64, height: 20 };
    let expected = [design, Rect { x: 144, y: 121, width: 48, height: 20 }];
    for ((width, height), expected) in CANVASES.into_iter().zip(expected) {
        assert_eq!(design.on_canvas(width, height), Some(expected), "{width} by {height}");
        let mut page = Page::sized(&define(0x20, &rectangle(3, 0, 0, 255, 199)), width, height);
        page.terminal.set_objects(&[object_at(1, 0x20, design, (192, 126))]).unwrap();
        page.compose();
        assert_eq!(page.terminal.bounds(1), Some(design), "bounds stay in the design picture (ANIM-13)");
        assert_eq!(pixels_of(&page.presented, 3), pixels_in(expected), "{width} by {height}: exactly its cells");
    }
}

#[test]
fn an_object_draws_on_every_canvas_whatever_its_macro_draws_inside_its_rectangle() {
    // ANIM-11: a macro that fills its object's rectangle in the design picture is drawn on the
    // canvas at every pixel whose centre lies in the rectangle, nothing of those cut, and at no
    // other, wherever the object is moved. On a canvas coarser than the design picture the
    // fill lights pixels straddling its edge whose centre is outside (a drawing lights every
    // pixel its locus lies under, ANSI X3.110-1983 section 5.3.2.2.6); those are the
    // neighbouring rectangle's and are cut, and are never more than one pixel out (TODO-6826).
    let body = rectangle(3, 64, 40, 31, 23);
    let fill = define(0x20, &body);
    // What the macro draws on the design picture is the object's rectangle, at its origin.
    let drawn = extent(&Page::new(&body).background, 3).expect("the macro draws");
    let origin = (drawn.x as i16, drawn.y as i16);
    for (width, height) in CANVASES {
        let as_stream = pixels_of(&Page::sized(&body, width, height).background, 3);
        for (x, y) in
            [(drawn.x, drawn.y), (0, 1), (1, 0), (192, 126), (17, 301), (639 - drawn.width, 479 - drawn.height)]
        {
            let rect = Rect { x, y, ..drawn };
            let object_pixels = |rect: Rect| {
                let mut page = Page::sized(&fill, width, height);
                page.terminal.set_objects(&[object_at(1, 0x20, rect, origin)]).unwrap();
                page.compose();
                pixels_of(&page.presented, 3)
            };
            let object = object_pixels(rect);
            let on_canvas = rect.on_canvas(width, height).unwrap();
            let inside = |pixels: &[(u32, u32)]| -> Vec<(u32, u32)> {
                pixels.iter().copied().filter(|&(x, y)| on_canvas.contains(x, y)).collect()
            };
            // The same move with a rectangle reaching to the picture's right and bottom edges.
            let unclipped = object_pixels(Rect { x, y, width: WIDTH - x, height: HEIGHT - y });
            assert_eq!(object, inside(&unclipped), "{width} by {height} at ({x}, {y}): nothing inside cut");
            assert_eq!(object, pixels_in(on_canvas), "{width} by {height} at ({x}, {y}): the whole rectangle");
            let ring = Rect::cut(
                i64::from(on_canvas.x) - 1,
                i64::from(on_canvas.y) - 1,
                i64::from(on_canvas.right()) + 1,
                i64::from(on_canvas.bottom()) + 1,
                width,
                height,
            )
            .unwrap();
            assert!(
                unclipped.iter().all(|&(x, y)| ring.contains(x, y)),
                "{width} by {height} at ({x}, {y}): what is cut is one pixel out at most"
            );
            if (x, y) == (drawn.x, drawn.y) {
                assert_eq!(object, inside(&as_stream), "{width} by {height}: unmoved, as the stream draws it");
            }
            if (width, height) == (WIDTH, HEIGHT) {
                assert_eq!(object, pixels_in(rect), "the design picture: exactly its rectangle");
                assert_eq!(object, unclipped, "the design picture: nothing cut");
            }
        }
    }
}

#[test]
fn a_pointer_picks_an_object_exactly_where_it_is_drawn() {
    // ANIM-11, picking: objects_on_canvas picks an object exactly at the canvas pixels compose
    // clips it to, and a canvas pixel's design pixel lies in the object only where it is drawn.
    let design = Rect { x: 192, y: 126, width: 64, height: 20 };
    for (width, height) in CANVASES {
        let mut page = Page::sized(&define(0x20, &rectangle(3, 0, 0, 255, 199)), width, height);
        page.terminal.set_objects(&[object_at(1, 0x20, design, (192, 126))]).unwrap();
        page.compose();
        for y in 0..height {
            for x in 0..width {
                let drawn = page.presented.pixel(x, y) == Some(3);
                let picked = page.terminal.objects_on_canvas(x, y, width, height) == [1];
                assert_eq!(picked, drawn, "{width} by {height}: ({x}, {y})");
                let (across, down) = design_pixel(x, y, width, height);
                assert_eq!(
                    page.terminal.objects_at(across, down) == [1],
                    drawn,
                    "{width} by {height}: ({x}, {y}) is drawn exactly when its centre is in the object's design pixels"
                );
                if (width, height) == (WIDTH, HEIGHT) {
                    assert_eq!(page.terminal.objects_at(x, y), page.terminal.objects_on_canvas(x, y, width, height));
                }
            }
        }
    }
}

#[test]
fn design_rectangles_share_out_every_canvas_and_are_the_identity_on_the_design_picture() {
    // Adjacent design rectangles share no canvas pixel and leave none out: every canvas column
    // and row whose centre is on the design picture belongs to exactly one of them
    // (TODO-6826), one whose centre lies past its right or bottom edge to none, and the design
    // picture's own canvas maps every pixel and rectangle to itself. A rectangle narrower than a canvas pixel may
    // hold no canvas pixel's centre and so have none.
    for y in 0..HEIGHT {
        for x in 0..WIDTH {
            assert_eq!(design_pixel(x, y, WIDTH, HEIGHT), (x, y));
        }
    }
    for (width, height) in [(RASTER_WIDTH, RASTER_HEIGHT), (320, 240), (800, 600), (1280, 960), (WIDTH, HEIGHT)] {
        for side in [1, 5, 12, 16] {
            let columns: Vec<Rect> = (0..WIDTH.div_ceil(side))
                .filter_map(|column| {
                    Rect::cut(
                        i64::from(column * side),
                        0,
                        i64::from(column * side + side),
                        i64::from(HEIGHT),
                        WIDTH,
                        HEIGHT,
                    )
                })
                .filter_map(|rect| rect.on_canvas(width, height))
                .collect();
            let mut owners = vec![0u32; width as usize];
            for rect in &columns {
                for x in rect.x..rect.right() {
                    owners[x as usize] += 1;
                }
            }
            for (x, &owners) in owners.iter().enumerate() {
                let on_picture = design_pixel(x as u32, 0, width, height).0 < WIDTH;
                assert_eq!(owners, u32::from(on_picture), "{width} by {height}, side {side}: column {x}");
            }
            let rows: Vec<Rect> = (0..HEIGHT.div_ceil(side))
                .filter_map(|row| {
                    Rect::cut(0, i64::from(row * side), i64::from(WIDTH), i64::from(row * side + side), WIDTH, HEIGHT)
                })
                .filter_map(|rect| rect.on_canvas(width, height))
                .collect();
            let mut owners = vec![0u32; height as usize];
            for rect in &rows {
                for y in rect.y..rect.bottom() {
                    owners[y as usize] += 1;
                }
            }
            for (y, &owners) in owners.iter().enumerate() {
                let on_picture = design_pixel(0, y as u32, width, height).1 < HEIGHT;
                assert_eq!(owners, u32::from(on_picture), "{width} by {height}, side {side}: row {y}");
            }
            if (width, height) == (WIDTH, HEIGHT) {
                assert!(columns.iter().all(|rect| rect.width == side.min(WIDTH - rect.x)));
                assert!(rows.iter().all(|rect| rect.height == side.min(HEIGHT - rect.y)));
            }
        }
    }
}

#[test]
fn a_canvas_pixel_is_in_a_rectangle_exactly_when_its_centre_is() {
    // Rect::on_canvas is exactly the canvas pixels whose centre design_pixel places inside the
    // design rectangle, on canvases smaller and larger than the design picture.
    let rects = [
        Rect { x: 0, y: 0, width: 1, height: 1 },
        Rect { x: 0, y: 0, width: WIDTH, height: HEIGHT },
        Rect { x: 192, y: 126, width: 64, height: 20 },
        Rect { x: 1, y: 84, width: 15, height: 21 },
        Rect { x: 37, y: 101, width: 3, height: 7 },
        Rect { x: 600, y: 470, width: 40, height: 10 },
        Rect { x: 255, y: 105, width: 2, height: 2 },
    ];
    for (width, height) in [(RASTER_WIDTH, RASTER_HEIGHT), (320, 240), (800, 600), (1280, 960), (WIDTH, HEIGHT), (7, 5)]
    {
        for design in rects {
            let on_canvas = design.on_canvas(width, height);
            for y in 0..height {
                for x in 0..width {
                    let (across, down) = design_pixel(x, y, width, height);
                    assert_eq!(
                        on_canvas.is_some_and(|rect| rect.contains(x, y)),
                        design.contains(across, down),
                        "{width} by {height}, {design:?}: ({x}, {y}) has its centre in ({across}, {down})"
                    );
                }
            }
        }
    }
}

/// The teletext raster's cells as the component library writes them in the design picture:
/// column c from design x 16 c, row r from the design line nearest raster line 20 r, counted
/// from the display area's first line, 19, times 480/462 (REQ-5819, DEC-6667).
const RASTER_CELL_DOTS: u32 = 12;
const RASTER_ROW_LINES: u32 = 20;
const RASTER_FIRST_LINE: u32 = 19;
const DESIGN_COLUMN: u32 = WIDTH / 40;
fn design_line(line: u32) -> u32 {
    let from_top = line.saturating_sub(RASTER_FIRST_LINE).min(RASTER_HEIGHT);
    (2 * from_top * HEIGHT + RASTER_HEIGHT) / (2 * RASTER_HEIGHT)
}
fn design_cells(row: u32, column: u32, columns: u32) -> Rect {
    let top = design_line(RASTER_ROW_LINES * row);
    Rect {
        x: DESIGN_COLUMN * column,
        y: top,
        width: DESIGN_COLUMN * columns,
        height: design_line(RASTER_ROW_LINES * (row + 1)) - top,
    }
}
/// The same cells on the 480 by 462 canvas: the display area's lines from line 19.
fn raster_cells(row: u32, column: u32, columns: u32) -> Rect {
    let top = (RASTER_ROW_LINES * row).max(RASTER_FIRST_LINE) - RASTER_FIRST_LINE;
    let bottom = RASTER_ROW_LINES * (row + 1) - RASTER_FIRST_LINE;
    Rect { x: RASTER_CELL_DOTS * column, y: top, width: RASTER_CELL_DOTS * columns, height: bottom - top }
}

#[test]
fn every_cell_of_the_teletext_raster_is_exactly_its_canvas_dots_and_lines() {
    // DEC-6667: each cell's design rectangle, as the component library writes it, is on the
    // 480 by 462 canvas exactly the cell's 12 dots and its 20 lines (row 0's one line), no line
    // or dot of a neighbour (TODO-6826).
    for row in 0..24 {
        for column in 0..40 {
            assert_eq!(
                design_cells(row, column, 1).on_canvas(RASTER_WIDTH, RASTER_HEIGHT),
                Some(raster_cells(row, column, 1)),
                "row {row}, column {column}"
            );
        }
    }
}

#[test]
fn a_row_of_objects_never_paints_the_first_line_of_the_row_below() {
    // TODO-6826, from the component library's audio player: the buttons on row 5 are objects
    // whose macro fills past their cells, as the library's cell fills reach the next row's
    // first design line (a filled RECTANGLE covers the pixel its far edge lies in, ANSI
    // X3.110-1983 section 5.3.3.4.1). Row 6 is the stream's, its text in entry 2. Before this
    // was fixed the clip kept every canvas pixel straddling the object's edge, so the buttons
    // painted canvas row 101 (raster line 120, row 6's top line, cutting "ff" of "Repeat off"
    // to "tt") and the first dot of the cell after each button.
    let buttons = [(0, 4), (7, 4), (13, 5), (20, 4)];
    for (width, height) in CANVASES {
        let mut page = Page::sized(
            &[define(0x20, &rectangle(3, 0, 0, 255, 199)), rectangle(2, 0, 0, 255, 199)].concat(),
            width,
            height,
        );
        let objects: Vec<Object> = buttons
            .iter()
            .zip(1..)
            .map(|(&(column, columns), number)| {
                let design = design_cells(5, column, columns);
                object_at(number, 0x20, design, (design.x as i16, design.y as i16))
            })
            .collect();
        page.terminal.set_objects(&objects).unwrap();
        page.compose();
        let cells = |(column, columns): (u32, u32)| {
            if (width, height) == (WIDTH, HEIGHT) {
                design_cells(5, column, columns)
            } else {
                raster_cells(5, column, columns)
            }
        };
        let mut expected: Vec<(u32, u32)> = buttons.iter().flat_map(|&button| pixels_in(cells(button))).collect();
        expected.sort_by_key(|&(x, y)| (y, x));
        assert_eq!(pixels_of(&page.presented, 3), expected, "{width} by {height}: exactly the buttons' cells");
        let below = if (width, height) == (WIDTH, HEIGHT) { design_cells(6, 0, 40) } else { raster_cells(6, 0, 40) };
        assert!(
            pixels_in(below).into_iter().all(|(x, y)| page.presented.pixel(x, y) == page.background.pixel(x, y)),
            "{width} by {height}: row 6 from its first line is the stream's"
        );
        assert_eq!(count(&page.background, 3), 0, "the stream draws no entry 3");
    }
}
