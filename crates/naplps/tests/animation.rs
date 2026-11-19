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

use naplps::limits::{
    DISPLAY_FIRST_LINE, DISPLAY_LINES, MAX_OBJECT_FRAMES, MAX_OBJECTS, RASTER_HEIGHT, RASTER_WIDTH,
    RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_WIDTH,
};
use naplps::{Animation, Canvas, Error, Look, Object, ObjectKind, Rect, Terminal, raster_dot};

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
/// The receiver's canvas, 480 by 460, which shows raster lines 20 to 479 (DEC-6857): an
/// object's dot (x, y) is its pixel (x, y − 20).
const WIDTH: u32 = RECEIVER_CANVAS_WIDTH;
/// See [`WIDTH`].
const HEIGHT: u32 = RECEIVER_CANVAS_HEIGHT;
/// The raster line of the canvas's first row.
const TOP: u32 = DISPLAY_FIRST_LINE;
/// The raster line after the display area's last.
const FOOT: u32 = DISPLAY_FIRST_LINE + DISPLAY_LINES;

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
/// dots of the macro's own drawing, the display area's foot being raster line 479, placed at
/// raster dot (`x`, `y`) on layer 2.
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
        origin_y: (FOOT - 96) as i16,
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

/// Macro 2/0: a rectangle of entry 3, 32/256 by 16/256 of the unit screen, from (0, 0): 61 by
/// 38 pixels at the bottom left of the receiver's canvas (60 dots and 36.8 lines, and the pixel
/// of the far edge).
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
    assert_eq!((first.x, first.width), (100, 61), "the macro's left edge is at the object's x");
    assert_eq!(first.bottom() + TOP, 50 + 96, "the macro's bottom row is the object's bottom line");
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
    assert_eq!(bounds, Rect { x: 200, y: 100, width: 40, height: 30 }, "in raster dots");
    assert_eq!(
        extent(&page.presented, 3),
        Some(Rect { y: 100 - TOP, ..bounds }),
        "every written pixel lies inside the bounds, which it fills, 20 lines up on the canvas"
    );
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
    assert_eq!(damage, Some(Rect { x: 40, y: 60 - TOP, width: 100, height: 50 }));
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
    // RAS-4: 1 to 480 dots across and 1 to 500 lines down, the raster's own size.
    assert_eq!(other(&|object| object.width = RASTER_WIDTH as u16 + 1), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.height = RASTER_HEIGHT as u16 + 1), Err(Error::Object(1)));
    assert_eq!(other(&|object| object.width = RASTER_WIDTH as u16), Ok(()));
    assert_eq!(other(&|object| object.height = RASTER_HEIGHT as u16), Ok(()));
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
    assert_eq!(pending, Rect { x: 100, y: 50 - TOP, width: 148, height: 106 }, "what it left and what it reaches");
    let changed = page.compose().unwrap();
    assert_eq!(page.terminal.take_damage(), Some(changed));
    assert!(pending.intersection(&changed) == Some(changed), "only pixels inside the pending rectangle changed");
    assert!(same(&page.background, &background));
    assert_eq!(page.terminal.pending(&page.presented), None);
    assert!(same(&page.whole(), &page.presented));
}

// ----- ANIM-13: bounds -----------------------------------------------------------------------

#[test]
fn bounds_are_the_objects_rectangle_cut_to_the_raster() {
    // ANIM-13, RAS-4: cut to the raster of 480 by 500, so a rectangle keeps the lines of row 24
    // it reaches, where nothing is drawn.
    let mut page = Page::new(&small_macro());
    page.terminal.set_objects(&[macro_object(1, 0x20, -28, 420)]).unwrap();
    assert_eq!(page.terminal.bounds(1), Some(Rect { x: 0, y: 420, width: 100, height: 80 }));
    assert_eq!(page.terminal.objects_at(10, 499), vec![1], "a dot of row 24 picks an object reaching it");
    page.compose();
    let drawn = extent(&page.presented, 3).unwrap();
    assert_eq!(drawn.bottom(), HEIGHT, "drawn to the canvas's last row and no further");
    assert_eq!(page.terminal.bounds(9), None, "no such object");
    assert!(page.terminal.set_animation(1, Animation { position: Some((0, 500)), ..Animation::default() }));
    assert_eq!(page.terminal.bounds(1), None, "wholly below the raster");
    assert!(page.terminal.set_animation(1, Animation { position: Some((480, 0)), ..Animation::default() }));
    assert_eq!(page.terminal.bounds(1), None, "wholly outside the raster");
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
                        position: (next(2) == 0).then(|| (next(540) as i16 - 40, next(560) as i16 - 30)),
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

// ----- ANIM-11 and RAS-3 on every canvas (DEC-6853, DEC-6857) ------------------------------------

/// The canvases an object is checked on: the receiver's 480 by 460, `naplps-render --double`'s
/// 960 by 920, and PP3's 640 by 480, which show the same display area scaled (RAS-3).
const CANVASES: [(u32, u32); 3] = [(WIDTH, HEIGHT), (2 * WIDTH, 2 * HEIGHT), (640, 480)];

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

/// A macro object of macro `code` whose rectangle is `rect` of raster dots, its drawing moved
/// there from the raster dot `origin`.
fn object_at(number: u16, code: u8, rect: Rect, origin: (i16, i16)) -> Object {
    let mut object = macro_object(number, code, rect.x as i16, rect.y as i16);
    object.width = rect.width as u16;
    object.height = rect.height as u16;
    (object.origin_x, object.origin_y) = origin;
    object
}

/// The teletext cells of row `row`, columns `column` onwards for `columns`, in raster dots: 12
/// dots by 20 lines a cell (DEC-6857 item 3).
fn cells(row: u32, column: u32, columns: u32) -> Rect {
    Rect { x: 12 * column, y: 20 * row, width: 12 * columns, height: 20 }
}

/// `rect` of raster dots on the receiver's canvas: moved up 20 lines and cut (RAS-3).
fn on_receiver(rect: Rect) -> Option<Rect> {
    Rect::cut(
        i64::from(rect.x),
        i64::from(rect.y) - i64::from(TOP),
        i64::from(rect.right()),
        i64::from(rect.bottom()) - i64::from(TOP),
        WIDTH,
        HEIGHT,
    )
}

#[test]
fn an_object_is_clipped_to_its_rectangle_on_every_canvas() {
    // ANIM-11, RAS-3: a macro drawing far more than its object is cut to the object's rectangle
    // of dots as it lies on the canvas. The rectangle is the cells of row 7, columns 12 to 15:
    // on the receiver's canvas exactly those dots 20 lines up; on twice it, twice them, a pixel
    // to the left (a canvas pixel's centre is a dot's when even and half a dot on when odd,
    // rounded half up, RAS-3); on 640 by 480, scaled.
    let dots = cells(7, 12, 4);
    let expected = [
        Rect { x: 144, y: 120, width: 48, height: 20 },
        Rect { x: 287, y: 240, width: 96, height: 40 },
        Rect { x: 192, y: 125, width: 64, height: 21 },
    ];
    for ((width, height), expected) in CANVASES.into_iter().zip(expected) {
        assert_eq!(dots.on_canvas(width, height), Some(expected), "{width} by {height}");
        let mut page = Page::sized(&define(0x20, &rectangle(3, 0, 0, 255, 199)), width, height);
        page.terminal.set_objects(&[object_at(1, 0x20, dots, (144, 140))]).unwrap();
        page.compose();
        assert_eq!(page.terminal.bounds(1), Some(dots), "bounds stay in raster dots (ANIM-13)");
        assert_eq!(pixels_of(&page.presented, 3), pixels_in(expected), "{width} by {height}: exactly its cells");
    }
}

#[test]
fn an_object_at_two_positions_is_moved_by_the_same_dots_and_twice_on_the_double_canvas() {
    // RAS-4's verification: the same pixels moved by the same dots on 480 by 460, by twice that
    // on 960 by 920.
    for (scale, (width, height)) in [(1, CANVASES[0]), (2, CANVASES[1])] {
        let mut page = Page::sized(&small_macro(), width, height);
        page.terminal.set_objects(&[macro_object(1, 0x20, 100, 50)]).unwrap();
        page.compose();
        let first = pixels_of(&page.presented, 3);
        assert!(page.terminal.set_animation(1, Animation { position: Some((137, 211)), ..Animation::default() }));
        page.compose();
        let moved: Vec<(u32, u32)> = first.iter().map(|&(x, y)| (x + 37 * scale, y + 161 * scale)).collect();
        assert_eq!(pixels_of(&page.presented, 3), moved, "{width} by {height}");
    }
}

#[test]
fn a_hidden_region_of_the_whole_raster_covers_the_whole_canvas() {
    // RAS-4's verification: a region of (0, 0, 480, 500) hidden covers every pixel of the
    // receiver's canvas; shown, its bounds are the whole raster and dot (0, 0), on row 0, picks
    // it. A hidden object has no bounds (ANIM-13), so the bounds are read shown.
    let mut page = Page::new(&[]);
    let mut whole = region(1, 0, 0, RASTER_WIDTH as u16, RASTER_HEIGHT as u16, 9);
    whole.shown = false;
    page.terminal.set_objects(&[whole]).unwrap();
    page.compose();
    assert_eq!(count(&page.presented, 9), (WIDTH * HEIGHT) as usize, "every pixel is the cover");
    assert_eq!(page.terminal.bounds(1), None);
    assert!(page.terminal.set_animation(1, Animation { shown: Some(true), ..Animation::default() }));
    assert_eq!(page.terminal.bounds(1), Some(Rect { x: 0, y: 0, width: RASTER_WIDTH, height: RASTER_HEIGHT }));
    assert_eq!(page.terminal.objects_at(0, 0), vec![1]);
    assert_eq!(page.terminal.objects_at(479, 499), vec![1]);
    assert_eq!(page.terminal.objects_at(480, 0), Vec::<u16>::new());
}

#[test]
fn an_object_wholly_on_row_0_or_24_is_never_drawn() {
    // RAS-3, RAS-4: rows 0 and 24 are the teletext page's; no canvas shows them.
    for row in [0, 24] {
        for (width, height) in CANVASES {
            assert_eq!(cells(row, 0, 40).on_canvas(width, height), None, "{width} by {height}, row {row}");
            let mut page = Page::sized(&define(0x20, &rectangle(3, 0, 0, 255, 199)), width, height);
            page.terminal.set_objects(&[object_at(1, 0x20, cells(row, 0, 40), (0, 0))]).unwrap();
            page.compose();
            assert_eq!(count(&page.presented, 3), 0, "{width} by {height}, row {row}");
            assert_eq!(page.terminal.bounds(1), Some(cells(row, 0, 40)), "its bounds are kept");
        }
    }
}

#[test]
fn an_object_draws_on_every_canvas_whatever_its_macro_draws_inside_its_rectangle() {
    // ANIM-11: a macro that fills its object's rectangle is drawn on the canvas at every pixel
    // whose centre lies in the rectangle, nothing of those cut, and at no other, wherever the
    // object is moved. On a canvas coarser or finer than the raster the fill lights pixels
    // straddling its edge whose centre is outside (a drawing lights every pixel its locus lies
    // under, ANSI X3.110-1983 section 5.3.2.2.6); those are the neighbouring rectangle's and
    // are cut, and are never more than one pixel out (TODO-6826).
    let body = rectangle(3, 64, 40, 31, 23);
    let fill = define(0x20, &body);
    // What the macro draws on the receiver's canvas, in raster dots: its pixels 20 lines down.
    let drawn = extent(&Page::new(&body).background, 3).expect("the macro draws");
    let drawn = Rect { y: drawn.y + TOP, ..drawn };
    let origin = (drawn.x as i16, drawn.y as i16);
    for (width, height) in CANVASES {
        let as_stream = pixels_of(&Page::sized(&body, width, height).background, 3);
        for (x, y) in [
            (drawn.x, drawn.y),
            (0, 1),
            (1, 0),
            (144, 140),
            (17, 301),
            (RASTER_WIDTH - drawn.width, FOOT - drawn.height),
            (5, FOOT - drawn.height / 2),
        ] {
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
            // The same move with a rectangle reaching to the raster's right and bottom edges.
            let unclipped = object_pixels(Rect { x, y, width: RASTER_WIDTH - x, height: RASTER_HEIGHT - y });
            assert_eq!(object, inside(&unclipped), "{width} by {height} at ({x}, {y}): nothing inside cut");
            // The whole rectangle on the receiver's canvas and on coarser ones. On a canvas finer
            // than the raster (twice it, or PP3's 640 across) a dot is more than one pixel, and a
            // fill from the rectangle's first dot and line starts at their centre, so the
            // pixels of the first dot column and first line before it may be left undrawn, as
            // the stream's own drawing leaves them: those and no others.
            let all = pixels_in(on_canvas);
            assert!(object.iter().all(|pixel| all.contains(pixel)), "{width} by {height} at ({x}, {y}): inside it");
            let undrawn: Vec<(u32, u32)> = all.iter().copied().filter(|pixel| !object.contains(pixel)).collect();
            if (width, height) == (WIDTH, HEIGHT) {
                assert_eq!(undrawn, [], "{width} by {height} at ({x}, {y}): the whole rectangle");
            }
            for &(column, row) in &undrawn {
                let (across, down) = raster_dot(column, row, width, height);
                assert!(
                    across == x || down == y,
                    "{width} by {height} at ({x}, {y}): ({column}, {row}) undrawn, of dot ({across}, {down})"
                );
            }
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
                assert_eq!(Some(on_canvas), on_receiver(rect), "the receiver's canvas: the dots 20 lines up");
                assert_eq!(
                    object,
                    unclipped
                        .iter()
                        .copied()
                        .filter(|&(_, y)| y < on_canvas.bottom())
                        .collect::<Vec<_>>()
                        .into_iter()
                        .filter(|&(x, _)| x < on_canvas.right())
                        .collect::<Vec<_>>(),
                    "the receiver's canvas: nothing cut but what lies past the rectangle"
                );
            }
        }
    }
}

#[test]
fn a_pointer_picks_an_object_exactly_where_it_is_drawn() {
    // ANIM-11, picking, RAS-3: objects_on_canvas picks an object exactly at the canvas pixels
    // compose clips it to, and a canvas pixel's raster dot lies in the object only where it is
    // drawn.
    let dots = cells(7, 12, 4);
    for (width, height) in CANVASES {
        let mut page = Page::sized(&define(0x20, &rectangle(3, 0, 0, 255, 199)), width, height);
        page.terminal.set_objects(&[object_at(1, 0x20, dots, (144, 140))]).unwrap();
        page.compose();
        for y in 0..height {
            for x in 0..width {
                let drawn = page.presented.pixel(x, y) == Some(3);
                let picked = page.terminal.objects_on_canvas(x, y, width, height) == [1];
                assert_eq!(picked, drawn, "{width} by {height}: ({x}, {y})");
                let (across, down) = raster_dot(x, y, width, height);
                assert_eq!(
                    page.terminal.objects_at(across, down) == [1],
                    drawn,
                    "{width} by {height}: ({x}, {y}) is drawn exactly when its centre is in the object's dots"
                );
                if (width, height) == (WIDTH, HEIGHT) {
                    assert_eq!(
                        page.terminal.objects_at(x, y + TOP),
                        page.terminal.objects_on_canvas(x, y, width, height)
                    );
                }
            }
        }
    }
}

#[test]
fn raster_rectangles_share_out_every_canvas_and_are_the_dots_on_the_receivers() {
    // RAS-3: adjacent rectangles of dots share no canvas pixel and leave none out: every canvas
    // column whose centre is on the raster and every canvas row belongs to exactly one of them
    // (TODO-6826), a column whose centre lies past the raster's right edge (half a dot, on a
    // canvas twice as wide) to none; and on the receiver's canvas every pixel is its dot 20
    // lines down and every rectangle its dots 20 lines up. A rectangle narrower than a canvas
    // pixel may hold no canvas pixel's centre and so have none.
    for y in 0..HEIGHT {
        for x in 0..WIDTH {
            assert_eq!(raster_dot(x, y, WIDTH, HEIGHT), (x, y + TOP));
        }
    }
    for y in 0..2 * HEIGHT {
        for x in 0..2 * WIDTH {
            assert_eq!(raster_dot(x, y, 2 * WIDTH, 2 * HEIGHT), (x.div_ceil(2), TOP + y / 2), "({x}, {y})");
        }
    }
    for (width, height) in [CANVASES[0], CANVASES[1], CANVASES[2], (320, 240), (800, 600), (1280, 960)] {
        for side in [1, 5, 12, 16, 20] {
            let columns: Vec<Rect> = (0..RASTER_WIDTH.div_ceil(side))
                .filter_map(|column| {
                    Rect::cut(
                        i64::from(column * side),
                        0,
                        i64::from(column * side + side),
                        i64::from(RASTER_HEIGHT),
                        RASTER_WIDTH,
                        RASTER_HEIGHT,
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
                let on_raster = raster_dot(x as u32, 0, width, height).0 < RASTER_WIDTH;
                assert_eq!(owners, u32::from(on_raster), "{width} by {height}, side {side}: column {x}");
            }
            let rows: Vec<Rect> = (0..RASTER_HEIGHT.div_ceil(side))
                .filter_map(|row| {
                    Rect::cut(
                        0,
                        i64::from(row * side),
                        i64::from(RASTER_WIDTH),
                        i64::from(row * side + side),
                        RASTER_WIDTH,
                        RASTER_HEIGHT,
                    )
                })
                .filter_map(|rect| rect.on_canvas(width, height))
                .collect();
            let mut owners = vec![0u32; height as usize];
            for rect in &rows {
                for y in rect.y..rect.bottom() {
                    owners[y as usize] += 1;
                }
            }
            assert!(owners.iter().all(|&owners| owners == 1), "{width} by {height}, side {side}: every row once");
            if (width, height) == (WIDTH, HEIGHT) {
                for rect in columns.iter().chain(&rows) {
                    let dots = Rect { y: rect.y + TOP, ..*rect };
                    assert_eq!(on_receiver(dots), Some(*rect));
                }
            }
        }
    }
}

#[test]
fn a_canvas_pixel_is_in_a_rectangle_exactly_when_its_centre_is() {
    // RAS-3: Rect::on_canvas is exactly the canvas pixels whose centre raster_dot places inside
    // the rectangle of dots, on canvases smaller and larger than the receiver's.
    let rects = [
        Rect { x: 0, y: 0, width: 1, height: 1 },
        Rect { x: 0, y: 20, width: 1, height: 1 },
        Rect { x: 0, y: 0, width: RASTER_WIDTH, height: RASTER_HEIGHT },
        Rect { x: 144, y: 140, width: 48, height: 20 },
        Rect { x: 1, y: 84, width: 15, height: 21 },
        Rect { x: 37, y: 101, width: 3, height: 7 },
        Rect { x: 450, y: 470, width: 30, height: 30 },
        Rect { x: 255, y: 105, width: 2, height: 2 },
        Rect { x: 0, y: 0, width: 480, height: 20 },
        Rect { x: 0, y: 479, width: 480, height: 21 },
    ];
    for (width, height) in [CANVASES[0], CANVASES[1], CANVASES[2], (320, 240), (800, 600), (1280, 960), (7, 5)] {
        for dots in rects {
            let on_canvas = dots.on_canvas(width, height);
            for y in 0..height {
                for x in 0..width {
                    let (across, down) = raster_dot(x, y, width, height);
                    assert_eq!(
                        on_canvas.is_some_and(|rect| rect.contains(x, y)),
                        dots.contains(across, down),
                        "{width} by {height}, {dots:?}: ({x}, {y}) has its centre in ({across}, {down})"
                    );
                }
            }
        }
    }
}

#[test]
fn every_cell_of_rows_1_to_23_is_exactly_its_dots_on_the_receivers_canvas() {
    // DEC-6857, RAS-3: each cell of rows 1 to 23 is on the 480 by 460 canvas exactly its 12 dots
    // and 20 lines, 20 lines up; rows 0 and 24 are on no canvas.
    for row in 0..25 {
        for column in 0..40 {
            let expected =
                (1..=23).contains(&row).then(|| Rect { x: 12 * column, y: 20 * row - TOP, width: 12, height: 20 });
            assert_eq!(cells(row, column, 1).on_canvas(WIDTH, HEIGHT), expected, "row {row}, column {column}");
        }
    }
}

#[test]
fn a_row_of_objects_never_paints_the_first_line_of_the_row_below() {
    // TODO-6826, from the component library's audio player: the buttons on row 5 are objects
    // whose macro fills past their cells (a filled RECTANGLE covers the pixel its far edge lies
    // in, ANSI X3.110-1983 section 5.3.3.4.1). Row 6 is the stream's, its text in entry 2. The
    // clip keeps only the pixels whose centre is in the buttons' cells, so no button paints row
    // 6's top line or the first dot of the cell after it.
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
                let dots = cells(5, column, columns);
                object_at(number, 0x20, dots, (dots.x as i16, dots.y as i16))
            })
            .collect();
        page.terminal.set_objects(&objects).unwrap();
        page.compose();
        let on_canvas = |dots: Rect| dots.on_canvas(width, height).unwrap();
        let mut expected: Vec<(u32, u32)> =
            buttons.iter().flat_map(|&(column, columns)| pixels_in(on_canvas(cells(5, column, columns)))).collect();
        expected.sort_by_key(|&(x, y)| (y, x));
        assert_eq!(pixels_of(&page.presented, 3), expected, "{width} by {height}: exactly the buttons' cells");
        if (width, height) == (WIDTH, HEIGHT) {
            let first = buttons
                .iter()
                .flat_map(|&(column, columns)| pixels_in(on_receiver(cells(5, column, columns)).unwrap()));
            let mut first: Vec<(u32, u32)> = first.collect();
            first.sort_by_key(|&(x, y)| (y, x));
            assert_eq!(expected, first, "the receiver's canvas: the cells' own dots");
        }
        let below = on_canvas(cells(6, 0, 40));
        assert!(
            pixels_in(below).into_iter().all(|(x, y)| page.presented.pixel(x, y) == page.background.pixel(x, y)),
            "{width} by {height}: row 6 from its first line is the stream's"
        );
        assert_eq!(count(&page.background, 3), 0, "the stream draws no entry 3");
    }
}
