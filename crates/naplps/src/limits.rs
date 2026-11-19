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
/// The width of NeoTeletext's teletext raster, every coordinate NeoTeletext defines on a NAPLPS
/// page being one of its dots (DEC-6853 item 1, `docs/naplps-raster.md` RAS-1): 40 columns of 12
/// dots, the engine's `PAGE_WIDTH`.
pub const RASTER_WIDTH: u32 = 480;
/// The height of the teletext raster: 25 rows of 20 lines, the engine's `PAGE_HEIGHT` (RAS-1).
pub const RASTER_HEIGHT: u32 = 500;
/// The lines of one teletext row on the raster: the Noto cell's height (DEC-6857 item 3).
pub const RASTER_ROW_LINES: u32 = 20;
/// The raster line a NAPLPS display area starts on: the top of teletext row 1 (DEC-6857 item 1,
/// REQ-5819 version 2). Rows 0 and 24 are the teletext page's own, wholly outside the picture.
pub const DISPLAY_FIRST_LINE: u32 = 20;
/// The raster lines a NAPLPS display area takes, lines 20 to 479: teletext rows 1 to 23
/// (DEC-6857 item 1). Every formula of the mapping is written in this and
/// [`DISPLAY_FIRST_LINE`], so that a change of the display area is a change of these two alone.
pub const DISPLAY_LINES: u32 = 460;
const _: () = assert!(DISPLAY_FIRST_LINE + DISPLAY_LINES <= RASTER_HEIGHT);
const _: () =
    assert!(DISPLAY_FIRST_LINE.is_multiple_of(RASTER_ROW_LINES) && DISPLAY_LINES.is_multiple_of(RASTER_ROW_LINES));
const _: () = assert!(RASTER_HEIGHT.is_multiple_of(RASTER_ROW_LINES));
/// The width of the canvas a receiver draws a NAPLPS picture on: the display area's
/// [`RASTER_WIDTH`] (REQ-5819, DEC-6857, RAS-1). A [`crate::Validator`] counts drawing work on a
/// canvas of this size, so that it stops where the receiver's terminal stops (PAR-15).
pub const RECEIVER_CANVAS_WIDTH: u32 = RASTER_WIDTH;
/// The height of the receiver's canvas: the display area's [`DISPLAY_LINES`], placed at raster
/// line [`DISPLAY_FIRST_LINE`].
pub const RECEIVER_CANVAS_HEIGHT: u32 = DISPLAY_LINES;
/// The pixels of [`RECEIVER_CANVAS_WIDTH`] by [`RECEIVER_CANVAS_HEIGHT`]: one whole-screen
/// fill's work on the receiver's canvas.
pub const RECEIVER_CANVAS_PIXELS: u64 = RECEIVER_CANVAS_WIDTH as u64 * RECEIVER_CANVAS_HEIGHT as u64;
/// Work units a stream earns with each of its bytes (TODO-6844, DEC-6851). A work unit is one
/// pixel a drawing routine visits on the canvas drawn on, or one pel stamped, one edge crossed
/// by a fill's row, one step of a line: see [`crate::Terminal::work_spent`]. Earning lets a stream
/// that is appended to for a long time, a page typed on or clicked on, go on drawing; it is
/// kept small so that the allowance, not a stream's length, bounds what one drawing costs.
/// Measured on 19 November 2026 on the receiver's canvas of the time, 480 by 462, whole pages of
/// the NAPLPS corpus average at most 553 units a byte, so their drawing is paid for mostly from
/// [`WORK_CAP`].
pub const WORK_PER_BYTE: u64 = 16;
/// Work units a stream may save up, and its allowance at the start (TODO-6844, DEC-6851): 128
/// whole-screen fills of the receiver's canvas of 480 by 460, 28,262,400 units. Measured again
/// on that canvas on 19 November 2026 (DEC-6857; the ignored test
/// `the_corpus_draws_within_the_work_allowance` of `tests/work.rs`, release build) over the same
/// 680 pages: the NAPLPS corpus of `~/devel/teletext-reference/NAPLPS` (484 files), the
/// repository's 120 sample pages and the 76 pictures of the naplpsdemo channel at its
/// `livedevelopment` b0086ed. The heaviest, Telidon's `girl.nap` (20,438 bytes), needs an
/// allowance of 8,633,862 units at this earning, 39.1 screens, so the bound is 3.27 times the
/// heaviest page of the corpus; the heaviest sample page needs 6.3 screens and the heaviest
/// picture of the channel 4.2 (margins of 20 and 30). A stream of 1 MiB may spend this and
/// 16,777,216 units more; the costliest the tests know, whole-screen fills and a macro of them
/// called again and again, stop at this allowance after 345 milliseconds in a release build on
/// `x86_64` Linux (`tests/work.rs`), where they drew for about five minutes and twenty minutes
/// before. A canvas larger than the receiver's spends more for the same figures and reaches the
/// allowance sooner: the margin covers the 960 by 920 canvas `naplps-render --double` draws on
/// (4 times the pixels) for every page of the 680 but `girl.nap`, which stops there (measured on
/// 19 November 2026).
pub const WORK_CAP: u64 = 128 * RECEIVER_CANVAS_PIXELS;
/// Work units one [`crate::Terminal::compose`] may spend drawing its objects' macros and
/// covers, all together (TODO-6844, DEC-6851): 16 whole-screen fills of the receiver's
/// canvas, 3,532,800 units; 64 objects that each fill the screen 512 times compose in about 51
/// milliseconds in a release build on 480 by 460 (`tests/work.rs`, 19 November 2026). A whole
/// repaint of the picture is one screen; this leaves each of [`MAX_OBJECTS`] objects a quarter
/// of a screen besides, while 64 objects whose macros each fill the screen many times over can
/// no longer make one composing take seconds.
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
/// Pixels repainted for animation in one tick: half of the teletext raster, 120,000, the same as
/// a teletext page's (ANIM-16, RAS-1). The caller with the clock holds a page to it, by
/// composing only when `Terminal::pending` is within it or a tick has passed with nothing
/// painted.
pub const MAX_ANIMATION_PIXELS_PER_TICK: u64 = RASTER_WIDTH as u64 * RASTER_HEIGHT as u64 / 2;
/// Bytes processed in drawing one object, macro expansion counted; past it the object's drawing
/// stops (ANIM-11, ANIM-16).
pub const MAX_OBJECT_BYTES: usize = 16_384;
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

// ----- What a terminal or a validator holds (TODO-6854) ---------------------------------------

/// What the allocator adds to one allocation, at most, beyond the bytes asked for: glibc's
/// malloc keeps an 8-byte header and rounds a chunk up to 16 bytes (up to 23 more), and macOS's
/// rounds to 16; 32 covers both. The figure the `regis` renderer counts by (DEC-6850).
pub const ALLOCATION_OVERHEAD_BYTES: usize = 32;
/// The fewest elements a vector makes room for when it first grows: the standard library's
/// least non-zero capacity is 8 for one-byte elements, 4 up to 1 KiB and 1 beyond.
const LEAST_VECTOR_CAPACITY: usize = 8;

/// The memory one allocation of `bytes` holds, at most.
pub(crate) const fn held_allocation(bytes: usize) -> usize {
    bytes.saturating_add(ALLOCATION_OVERHEAD_BYTES)
}

/// The memory a vector's allocation holds, from its capacity: none until it has room.
pub(crate) fn vector_bytes<T>(vector: &alloc::vec::Vec<T>) -> usize {
    match vector.capacity().saturating_mul(size_of::<T>()) {
        0 => 0,
        bytes => held_allocation(bytes),
    }
}

/// The memory a vector of `element`-byte elements holds, at most, when it is pushed to at most
/// `limit` elements: growing by doubling leaves it room for less than twice its length, and
/// never less than [`LEAST_VECTOR_CAPACITY`].
const fn grown_vector_bytes(limit: usize, element: usize) -> usize {
    let room =
        if limit.saturating_mul(2) > LEAST_VECTOR_CAPACITY { limit.saturating_mul(2) } else { LEAST_VECTOR_CAPACITY };
    held_allocation(room.saturating_mul(element))
}

/// Macro names and DRCS characters a stream can define: 2/0 to 7/15 (ANSI X3.110-1983 sections
/// 6.2.2 and 6.2.3).
pub const DEFINABLE_CODES: usize = 96;
/// Texture masks a stream can define: patterns A to D (section 6.2.4).
pub const TEXTURE_MASKS: usize = 4;
/// The memory one DRCS character or texture mask holds, at most: a one-byte element for each
/// pixel of a bitmap of [`MASK_SIDE`] on its longer side.
pub const MASK_BYTES: usize = held_allocation((MASK_SIDE as usize).saturating_mul(MASK_SIDE as usize));
/// The memory a stream's definitions hold, at most: every macro byte [`MAX_ALL_MACRO_BYTES`]
/// allows, each macro's body kept at its length; a macro being defined, grown up to
/// [`MAX_MACRO_BYTES`]; the [`DEFINABLE_CODES`] DRCS characters and [`TEXTURE_MASKS`] textures and
/// one bitmap being defined, each [`MASK_BYTES`]; and the slots that name them.
pub const MAX_DEFINITION_BYTES: usize = MAX_ALL_MACRO_BYTES
    .saturating_add(DEFINABLE_CODES * ALLOCATION_OVERHEAD_BYTES)
    .saturating_add(grown_vector_bytes(MAX_MACRO_BYTES, 1))
    .saturating_add((DEFINABLE_CODES + TEXTURE_MASKS + 1) * MASK_BYTES)
    .saturating_add(held_allocation(DEFINABLE_CODES * size_of::<Option<alloc::vec::Vec<u8>>>()))
    .saturating_add(held_allocation(DEFINABLE_CODES * size_of::<Option<crate::surface::Mask>>()));
/// The memory the macros being expanded hold between calls, at most (a stream stopped at a WAIT
/// inside a macro): a copy of a macro's body for each of [`MAX_MACRO_DEPTH`] levels.
pub const MAX_MACRO_CALL_BYTES: usize = (MAX_MACRO_DEPTH * held_allocation(MAX_MACRO_BYTES))
    .saturating_add(grown_vector_bytes(MAX_MACRO_DEPTH, size_of::<(alloc::vec::Vec<u8>, usize)>()));
/// The memory a terminal's objects and their state hold, at most (ANIM-6, ANIM-11): up to
/// [`MAX_OBJECTS`] objects, each with up to [`MAX_OBJECT_FRAMES`] frames and a label of up to
/// [`MAX_LABEL_BYTES`], with their animation states and pointer looks. A validator has none.
pub const MAX_OBJECT_STATE_BYTES: usize = grown_vector_bytes(MAX_OBJECTS, size_of::<crate::Object>())
    .saturating_add(MAX_OBJECTS * (held_allocation(MAX_OBJECT_FRAMES) + held_allocation(MAX_LABEL_BYTES)))
    .saturating_add(grown_vector_bytes(MAX_ANIMATED_OBJECTS, size_of::<(u16, crate::Animation)>()))
    .saturating_add(grown_vector_bytes(MAX_OBJECTS, size_of::<(u16, crate::Look)>()));
/// The memory the reading of a stream holds between calls besides its definitions, at most: a
/// PDI's operands up to [`MAX_PDI_BYTES`], an escape sequence's bytes, word wrap's word,
/// the joined letters held back up to [`MAX_JOINING_HELD`], a call's events, the title, the
/// colour map at its largest with its blink processes up to [`MAX_BLINKS`], and the slots of the
/// provided sets.
pub const MAX_READING_STATE_BYTES: usize = grown_vector_bytes(MAX_PDI_BYTES, 1)
    .saturating_add(grown_vector_bytes(crate::terminal::MAX_ESCAPE_BYTES, 1))
    .saturating_add(grown_vector_bytes(crate::terminal::MAX_WORD, size_of::<crate::terminal::WordEntry>()))
    .saturating_add(grown_vector_bytes(MAX_JOINING_HELD, 1))
    .saturating_add(grown_vector_bytes(crate::terminal::MAX_EVENTS, size_of::<crate::Event>()))
    .saturating_add(held_allocation(MAX_TITLE_BYTES))
    .saturating_add(held_allocation((1 << crate::palette::MAX_BITS) * size_of::<crate::Rgb>()))
    .saturating_add(held_allocation((1 << crate::palette::MAX_BITS) * size_of::<bool>()))
    .saturating_add(grown_vector_bytes(MAX_BLINKS, size_of::<crate::Blink>()))
    .saturating_add(held_allocation(crate::TELETEXT_SET_COUNT * size_of::<Option<crate::BitmapSet>>()));
/// The memory a [`crate::Terminal`] or a [`crate::Validator`] holds between calls, at most,
/// besides the stroke font and the provided sets its caller gives it, which
/// [`crate::Terminal::held_bytes`] counts as given, and the canvas, which is the caller's: its
/// own structure, [`MAX_DEFINITION_BYTES`], [`MAX_MACRO_CALL_BYTES`], [`MAX_OBJECT_STATE_BYTES`]
/// and [`MAX_READING_STATE_BYTES`]: 1,971,344 bytes on a 64-bit target. A server counts each reader
/// at [`crate::Validator::held_bytes`], or at this figure without asking (TODO-6854).
pub const MAX_HELD_BYTES: usize = size_of::<crate::Validator>()
    .saturating_add(MAX_DEFINITION_BYTES)
    .saturating_add(MAX_MACRO_CALL_BYTES)
    .saturating_add(MAX_OBJECT_STATE_BYTES)
    .saturating_add(MAX_READING_STATE_BYTES);

const _: () = assert!(MAX_BITMAP_WIDTH as u32 == u16::BITS);
const _: () = assert!(MAX_FRAME_NUMBER as usize + 1 == MAX_OBJECT_FRAMES);
const _: () = assert!(MAX_ANIMATED_OBJECTS >= MAX_OBJECTS);
const _: () = assert!(MAX_ANIMATION_PIXELS_PER_TICK == 120_000);
const _: () = assert!(RECEIVER_CANVAS_PIXELS == 220_800);
const _: () = assert!(size_of::<crate::Validator>() >= size_of::<crate::Terminal>());
const _: () = assert!(MAX_ALL_MACRO_BYTES >= MAX_MACRO_BYTES);
