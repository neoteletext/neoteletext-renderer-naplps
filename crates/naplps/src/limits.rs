//! Every bound on what a page may make the renderer hold or do (the security analysis of NAPLPS
//! input; ANSI X3.110-1983 section 5.5 warns that the application must guard against infinite
//! macro loops).

/// Macros that may be expanding inside one another at once.
pub const MAX_MACRO_DEPTH: usize = 16;
/// Bytes one macro definition may hold.
pub const MAX_MACRO_BYTES: usize = 4096;
/// Bytes all macro definitions together may hold.
pub const MAX_ALL_MACRO_BYTES: usize = 65_536;
/// Bytes processed by one call of `feed` or `finish`, counting macro expansion, before
/// processing stops and the limit is reported.
pub const MAX_PROCESSED_BYTES: usize = 4_000_000;
/// Data bytes one PDI may carry; more are dropped (section 5.3.1: the standard sets no limit,
/// but a polygon of 4096 vertices at 8 bytes each fits).
pub const MAX_PDI_BYTES: usize = 32_768;
/// Vertices of one polygon, scribble or arc spline (the standard asks for at least 256).
pub const MAX_VERTICES: usize = 4096;
/// Pixels on the longer side of the one-bit bitmap a DRCS character or fill mask is drawn into
/// (section 5.6 leaves the resolution to the implementation).
pub const MASK_SIDE: u32 = 128;
/// Pixels across one glyph of a bitmap character set (REQ-6668): room for the engine's 12-pixel
/// cell with margin, and the width of a `u16` row.
pub const MAX_BITMAP_WIDTH: u8 = 16;
/// Pixel rows of one glyph of a bitmap character set (REQ-6668): room for the engine's 20-line
/// cell with margin.
pub const MAX_BITMAP_HEIGHT: u8 = 32;
/// Codes held back for joining (renderer parity PAR-14): one letter of a joined set waiting for
/// the letter after it, and the transparent codes (combining marks) after it. A letter carries
/// a few marks at most; past this many the run ends and the letter is drawn as the last of it.
pub const MAX_JOINING_HELD: usize = 16;
/// Bytes of a stroke font's text form that `StrokeFont::parse` reads; longer text is refused
/// (renderer parity PAR-35: the browser's user-loadable fonts are bounded by this name). The
/// bound the crate already had, 256 KiB, is kept: the repository's one font,
/// `fonts/neoteletext.strokes`, is 8,971 bytes, and the specification gives 1,048,576 only for
/// a crate that had no bound.
pub const MAX_STROKE_FONT_BYTES: usize = 262_144;
/// The width of the canvas a receiver draws a NAPLPS picture on: the teletext raster's 480 by
/// 462 display area (REQ-5819, DEC-6667). A [`crate::Validator`] counts drawing work on a
/// canvas of this size, so that it stops where the receiver's terminal stops (PAR-15).
pub const RECEIVER_CANVAS_WIDTH: u32 = 480;
/// See [`RECEIVER_CANVAS_WIDTH`].
pub const RECEIVER_CANVAS_HEIGHT: u32 = 462;
/// The pixels of [`RECEIVER_CANVAS_WIDTH`] by [`RECEIVER_CANVAS_HEIGHT`]: one whole-screen
/// fill's work on the receiver's canvas.
pub const RECEIVER_CANVAS_PIXELS: u64 = RECEIVER_CANVAS_WIDTH as u64 * RECEIVER_CANVAS_HEIGHT as u64;
/// Work units a stream earns with each of its bytes (TODO-6844, DEC-6851). A work unit is one
/// pixel a drawing routine visits on the canvas drawn on, or one pel stamped, one edge crossed
/// by a fill's row, one step of a line: see [`crate::Terminal::work_spent`]. Earning lets a stream
/// that is appended to for a long time, a page typed on or clicked on, go on drawing; it is
/// kept small so that the allowance, not a stream's length, bounds what one drawing costs.
/// Measured on 19 November 2026 on the receiver's canvas, whole pages of the NAPLPS corpus
/// average at most 553 units a byte, so their drawing is paid for mostly from [`WORK_CAP`].
pub const WORK_PER_BYTE: u64 = 16;
/// Work units a stream may save up, and its allowance at the start (TODO-6844, DEC-6851): 128
/// whole-screen fills of the receiver's canvas, 28,385,280 units. Measured on 19 November 2026
/// (the ignored test `the_corpus_draws_within_the_work_allowance` of `tests/work.rs`) over 680 pages: the
/// NAPLPS corpus of `~/devel/teletext-reference/NAPLPS` (484 files), the repository's 120
/// sample pages and the 76 pictures of the naplpsdemo channel. The heaviest, Telidon's
/// `girl.nap` (20,438 bytes), needs an allowance of 8,672,322 units at this earning, 39.1
/// screens, so the bound is 3.27 times the heaviest page of the corpus; the heaviest sample page
/// needs 6.3 screens and the heaviest picture of the channel 4.2 (a margin of 30). A stream of
/// 1 MiB may spend this and 16,777,216 units more; the costliest the tests know, whole-screen
/// fills and a macro of them called again and again, stop at this allowance after 354
/// milliseconds in a release build on `x86_64` Linux (`tests/work.rs`), where they drew for
/// about five minutes and twenty minutes before. A canvas larger than the receiver's spends more for
/// the same figures and reaches the allowance sooner: the margin covers the 960 by 1,000 canvas
/// `naplps-render --neoteletext --double` draws on (4.3 times the pixels) for every page of the
/// corpus but `girl.nap`, which stops there (measured on 19 November 2026).
pub const WORK_CAP: u64 = 128 * RECEIVER_CANVAS_PIXELS;
/// Work units one [`crate::Terminal::compose`] may spend drawing its objects' macros and
/// covers, all together (TODO-6844, DEC-6851): 16 whole-screen fills of the receiver's
/// canvas, 3,548,160 units; 64 objects that each fill the screen 512 times compose in about 50
/// milliseconds in a release build (`tests/work.rs`). A whole repaint of the picture is one screen; this leaves
/// each of [`MAX_OBJECTS`] objects a quarter of a screen besides, while 64 objects whose macros
/// each fill the screen many times over can no longer make one composing take seconds.
pub const MAX_COMPOSE_WORK: u64 = 16 * RECEIVER_CANVAS_PIXELS;
/// Blink processes at once (Dillon, BLINK: at least 16).
pub const MAX_BLINKS: usize = 32;
/// Width or height of a canvas.
pub const MAX_CANVAS_SIDE: u32 = 4096;

// ----- Animation (neoteletext-common docs/animation.md, ANIM-16 and ANIM-20) ---------------------

/// Layers of a page, drawn in this order: 0 the background (the stream's picture), 1 the scene,
/// 2 the sprites, 3 the overlay (ANIM-12).
pub const LAYERS: u8 = 4;
/// Objects a sub-page may have (ANIM-11, ANIM-16).
pub const MAX_OBJECTS: usize = 64;
/// Objects holding animation state at once (ANIM-6, ANIM-16).
pub const MAX_ANIMATED_OBJECTS: usize = 64;
/// Objects of a page cycling through their frames at once (ANIM-14). The renderer keeps no
/// clock and so no cycle: the caller that plays cycles holds a page to this.
pub const MAX_CYCLING_OBJECTS: usize = 16;
/// Frames of one object (ANIM-14).
pub const MAX_OBJECT_FRAMES: usize = 16;
/// Pixels repainted for animation in one tick: half of 640 by 480 (ANIM-16). The caller with
/// the clock holds a page to it, by composing only when `Terminal::pending` is within it or a
/// tick has passed with nothing painted.
pub const MAX_ANIMATION_PIXELS_PER_TICK: u64 = 153_600;
/// Bytes processed in drawing one object, macro expansion counted; past it the object's drawing
/// stops (ANIM-11, ANIM-16).
pub const MAX_OBJECT_BYTES: usize = 16_384;
/// The width of the picture an object's position, size and rectangle are in (ANIM-11).
pub const OBJECT_PICTURE_WIDTH: u32 = 640;
/// The height of the picture an object's position, size and rectangle are in (ANIM-11).
pub const OBJECT_PICTURE_HEIGHT: u32 = 480;
/// The highest frame number the animation state holds (ANIM-6: 0 to 15).
pub const MAX_FRAME_NUMBER: u8 = 15;
/// Ticks of the presentation clock in a tenth of a second, the unit of WAIT and BLINK intervals
/// (ANSI X3.110-1983 sections 5.3.2.8 and 5.3.2.7; ANIM-1: 60 ticks a second).
pub const TENTH_TICKS: u32 = 6;
/// Ticks for which a stream's WAITs together are played in one generation, one minute; after
/// that each WAIT passes without delay (ANIM-20).
pub const WAIT_BUDGET_TICKS: u32 = 3_600;
/// Bytes held while a WAIT is played; when more arrive the wait ends at once (ANIM-20).
pub const MAX_WAIT_HELD_BYTES: usize = 262_144;

// ----- Text a picture carries and never draws (DEC-6638 items 3 and 6) ---------------------------

/// Bytes of an object's label, UTF-8: the text a screen reader speaks for it (DEC-6638 item 6,
/// row 6.1). The same bound as a sound's label in the engine's OBJECT record (REQ-37), the one
/// other label NeoTeletext carries for a reader.
pub const MAX_LABEL_BYTES: usize = 64;
/// Bytes of a picture's title, UTF-8: the name a page list shows for the picture when the
/// program's index gives none (DEC-6638 item 3, row 2.8). The same bound as a label: both are
/// one short line of plain text.
pub const MAX_TITLE_BYTES: usize = 64;

const _: () = assert!(MAX_BITMAP_WIDTH as u32 == u16::BITS);
const _: () = assert!(MAX_FRAME_NUMBER as usize + 1 == MAX_OBJECT_FRAMES);
const _: () = assert!(MAX_ANIMATED_OBJECTS >= MAX_OBJECTS);
const _: () = assert!(MAX_ANIMATION_PIXELS_PER_TICK * 2 == OBJECT_PICTURE_WIDTH as u64 * OBJECT_PICTURE_HEIGHT as u64);
