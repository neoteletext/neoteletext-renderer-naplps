//! The NAPLPS presentation process: bytes in, drawing on a canvas out (ANSI X3.110-1983).
//!
//! [`Terminal`] keeps all state between calls, so a page may arrive in pieces. A PDI's data bytes
//! are collected until a byte that is not its data arrives, then the PDI runs; [`Terminal::finish`]
//! runs one still collecting at the end of a page.

use alloc::vec;
use alloc::vec::Vec;

use crate::fixed::{ONE, Point, Unit, fraction};
use crate::font::{FontSet, StrokeFont};
use crate::limits::{
    MASK_SIDE, MAX_ALL_MACRO_BYTES, MAX_MACRO_BYTES, MAX_MACRO_DEPTH, MAX_PDI_BYTES, MAX_PROCESSED_BYTES, MAX_VERTICES,
};
use crate::operand::{DATA_MASK, Domain, Reader};
use crate::palette::Palette;
use crate::raster::{self, FillPattern, LineTexture, Masks, Style};
use crate::surface::{Canvas, Mask, MaskSurface, Surface, pixel_of};
use crate::text::{self, Field, Ink, Shape};

mod objects;

pub use objects::{Animation, Look, Object, ObjectKind};

/// The code sets a G-set may hold (section 4.3).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CharSet {
    /// The primary set (ASCII graphics).
    Primary,
    /// The supplementary set.
    Supplementary,
    /// Picture description instructions.
    Pdi,
    /// The mosaic set.
    Mosaic,
    /// The macro set.
    Macro,
    /// The dynamically redefinable character set.
    Drcs,
    /// A null set, designated by any sequence this standard does not define: every code is a
    /// null operation (section 4.3.2).
    Null,
}

/// Something the caller may act on.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Event {
    /// WAIT: pause this many tenths of a second before what follows (section 5.3.2.8).
    Wait(u32),
    /// BEL (0/7).
    Bell,
    /// Processing stopped at the limit on bytes processed (macro expansion counts).
    LimitReached,
}

/// Character path (section 5.3.2.3.3).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Path {
    Right,
    Left,
    Up,
    Down,
}

/// How the cursor and the drawing point follow each other (section 5.3.2.3.7).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Motion {
    Together,
    CursorLeads,
    PointLeads,
    Independent,
}

/// Text attributes (section 5.3.2.3 and the C1 set).
#[derive(Clone, Copy, Debug)]
#[allow(clippy::struct_excessive_bools, reason = "four independent C1 modes of section 6.2, each on or off")]
struct TextState {
    size: Point,
    rotation: u8,
    path: Path,
    /// 0: 1, 1: 5/4, 2: 3/2, 3: proportional.
    spacing: u8,
    /// 0: 1, 1: 5/4, 2: 3/2, 3: 2.
    rows: u8,
    /// 0 underscore, 1 block, 2 cross-hair, 3 custom.
    cursor_style: u8,
    motion: Motion,
    reverse: bool,
    underline: bool,
    word_wrap: bool,
    scroll: bool,
}

impl Default for TextState {
    /// Section 5.3.2.3 defaults: a 1/40 by 5/128 field, no rotation, rightward path, single
    /// spacing, underscore cursor, cursor and drawing point moving together.
    fn default() -> Self {
        Self {
            size: Point::new(fraction(1, 40), fraction(5, 128)),
            rotation: 0,
            path: Path::Right,
            spacing: 0,
            rows: 0,
            cursor_style: 0,
            motion: Motion::Together,
            reverse: false,
            underline: false,
            word_wrap: false,
            scroll: false,
        }
    }
}

/// A definition in progress (section 6.2).
enum Recording {
    /// DEF MACRO (`execute` false), DEFP MACRO (true), DEFT MACRO (`transmit`).
    Macro { number: u8, execute: bool, transmit: bool, bytes: Vec<u8>, depth: usize },
    /// DEF DRCS: drawing goes to the mask.
    Drcs { code: u8, mask: Mask, per_unit: u32 },
    /// DEF TEXTURE: drawing goes to the mask.
    Texture { index: u8, mask: Mask, per_unit: u32 },
}

/// Multi-byte control sequences waiting for their next byte.
#[derive(Clone, Debug, PartialEq, Eq)]
enum Pending {
    None,
    Escape(Vec<u8>),
    Aps(Option<u8>),
    Nsr(Option<u8>),
    Repeat,
    /// A DEF code waiting for its number: 0 macro, 1 DEFP, 2 DEFT, 3 DRCS, 4 texture.
    DefNumber(u8),
}

/// The colour mode (section 5.3.2.6).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Mode {
    Direct,
    Map,
    MapWithBackground,
}

/// The whole presentation state.
#[allow(
    clippy::struct_excessive_bools,
    reason = "independent one-bit states of the standard: highlight, CAN, power-up, the byte before REPEAT, RESET during a DRCS download"
)]
pub struct Terminal {
    palette: Palette,
    font: Option<StrokeFont>,
    g_sets: [CharSet; 4],
    gl: usize,
    gr: usize,
    single_shift: Option<usize>,
    pending: Pending,
    pdi: Option<(u8, Vec<u8>)>,
    domain: Domain,
    point: Point,
    cursor: Point,
    mode: Mode,
    colour: u8,
    background: u8,
    pel: Point,
    line: LineTexture,
    fill: FillPattern,
    highlight: bool,
    mask_size: Point,
    masks: Masks,
    text: TextState,
    field: Option<(Point, Point)>,
    macros: Vec<Option<Vec<u8>>>,
    drcs: Vec<Option<Mask>>,
    recording: Option<Recording>,
    last_drcs_code: Option<u8>,
    last_spacing: Option<(CharSet, u8)>,
    auto_wrapped: u8,
    display_top: Unit,
    events: Vec<Event>,
    processed: usize,
    cancel: bool,
    started: bool,
    /// The border's colour-map entry (RESET, Table 15).
    border: u8,
    /// A non-spacing accent waiting for the letter it goes over.
    pending_accent: Option<u8>,
    /// Word wrap's buffered word (section 6.2.7.11).
    word: Vec<(CharSet, u8)>,
    /// Whether the byte before this one was a spacing character, which REPEAT and REPEAT TO EOL
    /// need (section 6.2.7.2).
    last_was_spacing: bool,
    /// Whether the REPEAT being processed follows a spacing character.
    repeat_allowed: bool,
    /// RESET cleared the DRCS while a DRCS definition was open.
    drcs_cleared: bool,
    /// The macros being expanded, innermost last, each with the position reached in it. Kept
    /// between calls so that [`Terminal::feed_until_wait`] can stop inside a macro and go on.
    frames: Vec<(Vec<u8>, usize)>,
    /// A WAIT ran in the byte just processed.
    waited: bool,
    /// This terminal is executing an object's macro (animation.md ANIM-11): the commands that
    /// would change the stream's state or the colour map have no effect.
    in_object: bool,
    /// The objects over the stream's picture, their animation state and the damage.
    scene: objects::Scene,
}

/// Most events kept from one call.
const MAX_EVENTS: usize = 4096;
/// The WAIT command's fixed-format byte (section 5.3.2.8.2: 1011100 in bits 7 to 1).
const WAIT_FORMAT: u8 = 0x5C;
/// Macro and DRCS codes run from 2/0 to 7/15.
const CODES: usize = 96;
/// The first macro or DRCS code.
const FIRST_CODE: u8 = 0x20;

impl Terminal {
    /// A terminal in its power-up state with a colour map of 2^`palette_bits` entries.
    #[must_use]
    pub fn new(palette_bits: u32) -> Self {
        let palette = Palette::new(palette_bits);
        let white = palette.white();
        Self {
            palette,
            font: None,
            g_sets: [CharSet::Primary, CharSet::Pdi, CharSet::Supplementary, CharSet::Mosaic],
            gl: 0,
            gr: 1,
            single_shift: None,
            pending: Pending::None,
            pdi: None,
            domain: Domain::default(),
            point: Point::default(),
            cursor: Point::default(),
            mode: Mode::Direct,
            colour: white,
            background: 0,
            pel: Point::default(),
            line: LineTexture::Solid,
            fill: FillPattern::Solid,
            highlight: false,
            mask_size: Point::new(fraction(1, 40), fraction(5, 128)),
            masks: [None, None, None, None],
            text: TextState::default(),
            field: None,
            macros: vec![None; CODES],
            drcs: vec![None; CODES],
            recording: None,
            last_drcs_code: None,
            last_spacing: None,
            auto_wrapped: 0,
            display_top: fraction(crate::surface::DISPLAY_HEIGHT_NUMERATOR, crate::surface::DISPLAY_HEIGHT_DENOMINATOR),
            events: Vec::new(),
            processed: 0,
            cancel: false,
            started: false,
            border: 0,
            pending_accent: None,
            word: Vec::new(),
            last_was_spacing: false,
            repeat_allowed: false,
            drcs_cleared: false,
            frames: Vec::new(),
            waited: false,
            in_object: false,
            scene: objects::Scene::default(),
        }
    }

    /// Uses `font` for the primary and supplementary sets (decision D5).
    pub fn set_font(&mut self, font: StrokeFont) {
        self.font = Some(font);
        self.scene.definitions_changed = true;
    }

    /// The colour map.
    #[must_use]
    pub fn palette(&self) -> &Palette {
        &self.palette
    }

    /// Processes bytes onto `canvas`, returning what the caller may act on.
    pub fn feed(&mut self, canvas: &mut Canvas, bytes: &[u8]) -> Vec<Event> {
        self.run(canvas, bytes, MAX_PROCESSED_BYTES, false);
        self.scene.wrote(canvas.take_written());
        core::mem::take(&mut self.events)
    }

    /// Processes bytes onto `canvas` up to and including the byte at which a WAIT ran (section
    /// 5.3.2.8), and says how many of `bytes` it took: all of them when no WAIT ran. A WAIT runs
    /// when the byte after its operands arrives, so that byte is taken, and nothing after the
    /// WAIT has been drawn. The caller holds the rest for the interval the [`Event::Wait`] gives
    /// and then calls again (animation.md ANIM-20). A WAIT
    /// inside a macro stops there too: the rest of the macro runs at the next call of this or of
    /// [`Terminal::feed`].
    pub fn feed_until_wait(&mut self, canvas: &mut Canvas, bytes: &[u8]) -> (usize, Vec<Event>) {
        let taken = self.run(canvas, bytes, MAX_PROCESSED_BYTES, true);
        self.scene.wrote(canvas.take_written());
        (taken, core::mem::take(&mut self.events))
    }

    /// Processes `bytes`, after any macro still expanding, until they end, `limit` bytes have
    /// been processed (macro expansion counted), or, with `stop_at_wait`, a WAIT ran. Returns
    /// how many of `bytes` were taken.
    fn run(&mut self, surface: &mut dyn Surface, bytes: &[u8], limit: usize, stop_at_wait: bool) -> usize {
        self.display_top =
            fraction(crate::surface::DISPLAY_HEIGHT_NUMERATOR, crate::surface::DISPLAY_HEIGHT_DENOMINATOR);
        if !self.started {
            // Power-up: the text cursor at the home position; the drawing point stays at (0, 0).
            self.started = true;
            self.cursor = self.home_position();
        }
        self.processed = 0;
        self.waited = false;
        let mut position = 0;
        loop {
            if self.processed >= limit {
                self.event(Event::LimitReached);
                // What was expanding is abandoned, as it was before the expansion was kept
                // between calls: the limit ends the work, it does not defer it.
                self.frames.clear();
                break;
            }
            let (byte, depth) = if let Some((body, at)) = self.frames.last_mut() {
                let Some(byte) = body.get(*at).copied() else {
                    self.frames.pop();
                    continue;
                };
                *at = at.saturating_add(1);
                (byte, self.frames.len())
            } else {
                match bytes.get(position).copied() {
                    Some(byte) => {
                        position = position.saturating_add(1);
                        (byte, 0)
                    }
                    None => break,
                }
            };
            self.processed = self.processed.saturating_add(1);
            if let Some(number) = self.byte(surface, byte, depth)
                && self.frames.len() < MAX_MACRO_DEPTH
                && let Some(Some(body)) = self.macros.get(usize::from(number.wrapping_sub(FIRST_CODE)))
            {
                self.frames.push((body.clone(), 0));
            }
            if self.cancel {
                self.cancel = false;
                self.frames.clear();
            }
            if core::mem::take(&mut self.waited) && stop_at_wait {
                break;
            }
        }
        position
    }

    /// The border's colour-map entry: the area of the screen outside the display area, which the
    /// caller draws, if it has one (RESET, section 5.3.2.9, Table 15). Nominal black at first.
    #[must_use]
    pub fn border(&self) -> u8 {
        self.border
    }

    /// Ends a page: draws a word or accent still buffered and runs a PDI still collecting data.
    pub fn finish(&mut self, canvas: &mut Canvas) -> Vec<Event> {
        self.settle(canvas);
        self.flush(canvas);
        self.scene.wrote(canvas.take_written());
        core::mem::take(&mut self.events)
    }

    fn event(&mut self, event: Event) {
        // An object's macro reports nothing: its bell and its limit are not the stream's.
        if self.events.len() < MAX_EVENTS && !self.in_object {
            self.events.push(event);
        }
    }

    /// One byte. Returns a macro number to expand.
    fn byte(&mut self, canvas: &mut dyn Surface, byte: u8, depth: usize) -> Option<u8> {
        // Definitions that record without executing.
        if let Some(Recording::Macro { execute: false, bytes, .. }) = &mut self.recording {
            let escaped = bytes.last() == Some(&ESC);
            let terminator = (0x80..=0x85).contains(&byte) || (escaped && (0x40..=0x45).contains(&byte));
            if !terminator {
                if bytes.len() < MAX_MACRO_BYTES {
                    bytes.push(byte);
                }
                return None;
            }
            if escaped {
                bytes.pop();
            }
            let code = if byte >= 0x80 { byte } else { byte.wrapping_add(0x40) };
            self.end_recording();
            self.control1(canvas, code);
            return None;
        }
        // DEFP records at its own depth while executing.
        if let Some(Recording::Macro { execute: true, bytes, depth: recording_depth, .. }) = &mut self.recording
            && depth == *recording_depth
            && bytes.len() < MAX_MACRO_BYTES
        {
            bytes.push(byte);
        }
        self.dispatch(canvas, byte)
    }

    fn dispatch(&mut self, canvas: &mut dyn Surface, byte: u8) -> Option<u8> {
        // REPEAT is ESC 4/6 in the 7-bit form, so the ESC does not come between REPEAT and the
        // character before it; nor do the shifts, which pages send between a character in GL and
        // a REPEAT (PP3 repeats across them: sample page 113's dot leaders, SI . SO ESC 4/6).
        self.repeat_allowed = self.last_was_spacing;
        if !matches!(byte, ESC | SO | SI | SS2 | SS3) {
            self.last_was_spacing = false;
        }
        match core::mem::replace(&mut self.pending, Pending::None) {
            Pending::None => {}
            Pending::Escape(mut collected) => return self.escape(canvas, &mut collected, byte),
            Pending::Aps(first) => {
                if (0x20..0x80).contains(&(byte & 0x7F)) && (byte & 0x7F) >= 0x20 && !(0x80..0xA0).contains(&byte) {
                    match first {
                        None => self.pending = Pending::Aps(Some(byte)),
                        Some(row) => self.active_position_set(row, byte),
                    }
                    return None;
                }
                // A control code in the sequence discards it (Dillon, Cursor Position).
            }
            Pending::Nsr(first) => {
                // Section 6.1.6.5 item 6: two bytes from columns 4 to 7 (or 12 to 15) position the
                // cursor; bytes from columns 2 and 3 (or 10 and 11) are ignored; a control ends
                // the sequence and is executed.
                let column = byte & 0x7F;
                let control = byte < 0x20 || (0x80..0xA0).contains(&byte);
                if !control {
                    match first {
                        None => self.pending = Pending::Nsr(Some(column)),
                        Some(row) if row >= 0x40 && column >= 0x40 => self.nsr_position(row, column),
                        Some(_) => {}
                    }
                    return None;
                }
            }
            Pending::Repeat => {
                let count = byte & 0x7F;
                if (0x40..=0x7F).contains(&count) {
                    if self.last_spacing.is_some() {
                        self.repeat(canvas, u32::from(count & DATA_MASK));
                    }
                    return None;
                }
            }
            Pending::DefNumber(kind) => {
                self.begin_definition(kind, byte);
                return None;
            }
        }
        match byte {
            0x00..=0x1F => {
                self.control0(canvas, byte);
                None
            }
            0x80..=0x9F => {
                self.single_shift = None;
                self.flush(canvas);
                self.control1(canvas, byte);
                None
            }
            _ => {
                let gr = byte >= 0xA0;
                let code = byte & 0x7F;
                // A byte after SS2 or SS3 comes from the shifted set, from GR too with b8 ignored
                // (section 6.1.3.3).
                let shifted = self.single_shift.take();
                let set_index = shifted.unwrap_or(if gr { self.gr } else { self.gl });
                let set = self.g_sets.get(set_index).copied().unwrap_or(CharSet::Primary);
                self.auto_wrapped = 0;
                self.graphic(canvas, set, code)
            }
        }
    }

    fn graphic(&mut self, canvas: &mut dyn Surface, set: CharSet, code: u8) -> Option<u8> {
        match set {
            CharSet::Null => None,
            CharSet::Macro => {
                if code == 0x7F {
                    return None;
                }
                if let Some(Recording::Macro { number, execute: true, .. }) = &self.recording
                    && *number == code
                {
                    return None; // DEFP: a reference to the macro being defined is undefined.
                }
                Some(code)
            }
            CharSet::Pdi => {
                if code < 0x40 {
                    self.settle(canvas);
                    self.flush(canvas);
                    self.pdi = Some((code, Vec::new()));
                } else if let Some((_, data)) = &mut self.pdi
                    && data.len() < MAX_PDI_BYTES
                {
                    data.push(code);
                }
                None
            }
            _ => {
                self.flush(canvas);
                self.character(canvas, set, code);
                None
            }
        }
    }

    // ----- C0 and C1 ------------------------------------------------------------------------

    fn control0(&mut self, canvas: &mut dyn Surface, byte: u8) {
        // Section 6.1: these belong to other layers and neither act nor end a PDI.
        if matches!(byte, 0x00..=0x06 | 0x10..=0x17) {
            return;
        }
        // A C0 control after SS2 or SS3 cancels the single shift (section 6.1.3.3).
        if !matches!(byte, SS2 | SS3) {
            self.single_shift = None;
        }
        if matches!(byte, SO | SI | SS2 | SS3) {
            // Code-set shifts do not end a PDI's data (the next bytes may still be data), nor a
            // word (section 6.2.7.11).
        } else {
            self.settle(canvas);
            self.flush(canvas);
        }
        let wrapped = self.auto_wrapped;
        self.auto_wrapped = 0;
        match byte {
            0x07 => self.event(Event::Bell),
            0x08 => self.backspace(canvas),
            0x09 => self.forward(canvas),
            0x0A => {
                if wrapped == 2 || wrapped == 1 {
                    return; // the line feed after an automatic new line is ignored once
                }
                self.line_feed(canvas, true);
            }
            0x0B => self.line_feed(canvas, false),
            0x0C => {
                self.home();
                let entry = if self.mode == Mode::MapWithBackground { self.background } else { self.palette.black() };
                // During DEF DRCS or DEF TEXTURE, drawing goes to the definition, never the
                // display (section 6.2): clear screen clears the bitmap being defined. (SHARK.NAP
                // sends CS inside DEF TEXTURE; clearing the display there blanked the page.)
                match &mut self.recording {
                    Some(Recording::Drcs { mask, .. } | Recording::Texture { mask, .. }) => mask.clear(),
                    _ => canvas.fill_all(entry),
                }
            }
            0x0D => {
                if wrapped == 2 {
                    self.auto_wrapped = 1;
                    return;
                }
                self.carriage_return();
            }
            SO => self.gl = 1,
            SI => self.gl = 0,
            0x18 => {
                self.cancel = true;
            }
            SS2 => self.single_shift = Some(2),
            0x1A => {}
            ESC => self.pending = Pending::Escape(Vec::new()),
            0x1C => self.pending = Pending::Aps(None),
            SS3 => self.single_shift = Some(3),
            0x1E => self.home(),
            0x1F => {
                self.nsr();
                self.pending = Pending::Nsr(None);
            }
            _ => {}
        }
    }

    fn escape(&mut self, canvas: &mut dyn Surface, collected: &mut Vec<u8>, byte: u8) -> Option<u8> {
        if !(0x20..0x80).contains(&byte) {
            // A control interrupts the sequence; the sequence is dropped.
            return self.dispatch(canvas, byte);
        }
        if collected.is_empty() {
            match byte {
                0x40..=0x5F => {
                    self.flush(canvas);
                    self.control1(canvas, byte.wrapping_add(0x40));
                    return None;
                }
                0x6E => self.gl = 2,
                0x6F => self.gl = 3,
                0x7E | 0x6B => self.gr = 1,
                0x7D | 0x6C => self.gr = 2,
                0x7C | 0x6D => self.gr = 3,
                0x20..=0x2F => {
                    collected.push(byte);
                    self.pending = Pending::Escape(core::mem::take(collected));
                }
                _ => {}
            }
            return None;
        }
        if (0x20..=0x2F).contains(&byte) && collected.len() < 3 {
            collected.push(byte);
            self.pending = Pending::Escape(core::mem::take(collected));
            return None;
        }
        // The final byte.
        let first = collected.first().copied().unwrap_or(0);
        let target = match first {
            0x28 => Some(0),
            0x29 | 0x2D => Some(1),
            0x2A | 0x2E => Some(2),
            0x2B | 0x2F => Some(3),
            _ => None, // ESC 2/1 4/11, ESC 2/2 4/6 (C0, C1) and ESC 2/5 (PP3's NAPLPS switch)
        };
        let set = match byte {
            0x42 => Some(CharSet::Primary),
            0x7C => Some(CharSet::Supplementary),
            0x57 => Some(CharSet::Pdi),
            0x7D => Some(CharSet::Mosaic),
            0x7A => Some(CharSet::Macro),
            0x7B => Some(CharSet::Drcs),
            // Section 4.3.2: "All other designation sequences shall designate ... a null G-set".
            _ => Some(CharSet::Null),
        };
        if let (Some(target), Some(set)) = (target, set)
            && let Some(slot) = self.g_sets.get_mut(target)
        {
            *slot = set;
        }
        None
    }

    fn control1(&mut self, canvas: &mut dyn Surface, code: u8) {
        self.settle(canvas);
        match code {
            0x80..=0x84 => {
                let previous_drcs = matches!(self.recording, Some(Recording::Drcs { .. }));
                let previous = self.end_recording();
                let kind = code.wrapping_sub(0x80);
                if kind == 3 && previous_drcs {
                    // DEF DRCS ending a DEF DRCS: the next code, 7/15 wrapping to 2/0.
                    let next = previous
                        .map_or(FIRST_CODE, |code| if code >= 0x7F { FIRST_CODE } else { code.saturating_add(1) });
                    self.begin_definition(3, next);
                } else {
                    self.pending = Pending::DefNumber(kind);
                }
            }
            0x85 => {
                self.end_recording();
            }
            0x86 => {
                if !self.repeat_allowed {
                    self.last_spacing = None; // a null operation; its count byte is still consumed
                }
                self.pending = Pending::Repeat;
            }
            0x87 => {
                if self.repeat_allowed {
                    self.repeat_to_end(canvas);
                }
            }
            0x88 => self.text.reverse = true,
            0x89 => self.text.reverse = false,
            0x8A => self.text.size = Point::new(fraction(1, 80), fraction(5, 128)),
            0x8B => self.text.size = Point::new(fraction(1, 32), fraction(3, 64)),
            0x8C => self.text.size = Point::new(fraction(1, 40), fraction(5, 128)),
            0x8D => self.text.size = Point::new(fraction(1, 40), fraction(5, 64)),
            // BLINK START and BLINK STOP have no effect inside an object's macro (ANIM-11).
            0x8E | 0x9E if self.in_object => {}
            0x8E => {
                let to = if self.mode == Mode::MapWithBackground { self.background } else { self.palette.black() };
                if self.mode == Mode::Direct {
                    // Section 6.2.8.1: in colour mode 0 BLINK START gives the drawing colour an
                    // entry of its own, so that only what is drawn from now on blinks.
                    let colour = self.palette.colour(self.colour);
                    if let Some(entry) = self.palette.allocate_unused(colour) {
                        self.colour = entry;
                    }
                }
                self.palette.blink(self.colour, to, BLINK_START_ON, BLINK_START_OFF, 0);
            }
            0x8F => self.text.size = Point::new(fraction(1, 20), fraction(5, 64)),
            0x95 => self.text.word_wrap = true,
            0x96 => self.text.word_wrap = false,
            0x97 => self.text.scroll = true,
            0x98 => self.text.scroll = false,
            0x99 => self.text.underline = true,
            0x9A => self.text.underline = false,
            0x9E => self.palette.stop_blinks_from(self.colour),
            // PROTECT, UNPROTECT, cursor display and the reserved codes: no display effect here.
            _ => {}
        }
    }

    /// Starts DEF MACRO (0), DEFP (1), DEFT (2), DEF DRCS (3) or DEF TEXTURE (4) for `number`.
    fn begin_definition(&mut self, kind: u8, number: u8) {
        let number = number & 0x7F;
        match kind {
            0..=2 => {
                if !(FIRST_CODE..=0x7F).contains(&number) {
                    return;
                }
                self.recording = Some(Recording::Macro {
                    number,
                    execute: kind == 1,
                    transmit: kind == 2,
                    bytes: Vec::new(),
                    depth: 0,
                });
            }
            3 => {
                if !(FIRST_CODE..=0x7F).contains(&number) {
                    return;
                }
                let (mask, per_unit) = mask_for(self.text.size);
                self.recording = Some(Recording::Drcs { code: number, mask, per_unit });
                self.point = Point::default();
            }
            _ => {
                if !(0x41..=0x44).contains(&number) {
                    return;
                }
                let (mask, per_unit) = mask_for(self.mask_size);
                self.recording = Some(Recording::Texture { index: number.wrapping_sub(0x41), mask, per_unit });
                self.point = Point::default();
            }
        }
    }

    /// Ends the definition in progress and stores it; returns the DRCS code it defined, if any.
    fn end_recording(&mut self) -> Option<u8> {
        if self.in_object {
            // ANIM-11: DEF MACRO, DEFP MACRO, DEFT MACRO, DEF DRCS and DEF TEXTURE have no effect
            // inside an object's macro. The definition's bytes are still read as a definition's
            // (so they are not drawn as if they were the macro's own), and it is dropped here.
            let dropped = self.recording.take()?;
            if !matches!(dropped, Recording::Macro { .. }) {
                self.point = Point::default();
            }
            return None;
        }
        let recording = self.recording.take()?;
        // An object's macro may call or draw with what was defined (ANIM-11).
        self.scene.definitions_changed = true;
        match recording {
            Recording::Macro { number, bytes, transmit, .. } => {
                let index = usize::from(number.wrapping_sub(FIRST_CODE));
                let others: usize = self
                    .macros
                    .iter()
                    .enumerate()
                    .filter(|(i, _)| *i != index)
                    .filter_map(|(_, m)| m.as_ref())
                    .map(Vec::len)
                    .sum();
                // Section 6.2.2.3: transmit macros "when called, are not executed, but are
                // transmitted". Nothing is ever transmitted (REQ-5910), so a transmit macro is kept
                // as nothing: defining one deletes any macro of its name (they share the 96 names)
                // and calling it does nothing.
                if let Some(slot) = self.macros.get_mut(index) {
                    *slot = if transmit || bytes.is_empty() || others.saturating_add(bytes.len()) > MAX_ALL_MACRO_BYTES
                    {
                        None
                    } else {
                        Some(bytes)
                    };
                }
                None
            }
            Recording::Drcs { code, mask, .. } => {
                if let Some(slot) = self.drcs.get_mut(usize::from(code.wrapping_sub(FIRST_CODE))) {
                    *slot = Some(mask);
                }
                self.point = Point::default();
                self.last_drcs_code = Some(code);
                Some(code)
            }
            Recording::Texture { index, mask, .. } => {
                if let Some(slot) = self.masks.get_mut(usize::from(index)) {
                    *slot = Some(mask);
                }
                self.point = Point::default();
                None
            }
        }
    }

    // ----- PDIs -----------------------------------------------------------------------------

    /// Runs the PDI collecting data, if any.
    fn flush(&mut self, canvas: &mut dyn Surface) {
        let Some((opcode, data)) = self.pdi.take() else { return };
        let mut recording = self.recording.take();
        match &mut recording {
            Some(Recording::Drcs { mask, per_unit, .. } | Recording::Texture { mask, per_unit, .. }) => {
                let mut surface = MaskSurface { mask, per_unit: *per_unit };
                self.pdi_on(&mut surface, opcode, &data);
            }
            _ => self.pdi_on(canvas, opcode, &data),
        }
        if core::mem::take(&mut self.drcs_cleared)
            && let Some(Recording::Drcs { mask, .. }) = &mut recording
        {
            // Section 6.2.3: such a RESET "will clear the character pattern definition in
            // progress, but the downloading operation will continue".
            mask.clear();
        }
        if self.recording.is_none() {
            self.recording = recording;
        }
        if opcode == TEXT_OPCODE && matches!(self.text.motion, Motion::Together | Motion::CursorLeads) {
            // Section 5.3.2.3.7: TEXT aligns the drawing point with the cursor.
            self.sync_point();
        } else if matches!(self.text.motion, Motion::Together | Motion::PointLeads) {
            self.cursor = self.inside_unit_screen(self.point.plus(self.alignment().negated()));
        }
    }

    fn style(&self) -> Style {
        Style {
            colour: self.colour,
            background: (self.mode == Mode::MapWithBackground).then_some(self.background),
            black: self.palette.black(),
            pel: self.pel,
            line: self.line,
            fill: self.fill,
            highlight: self.highlight,
            mask_size: self.mask_size,
        }
    }

    #[allow(clippy::too_many_lines, reason = "one arm per PDI of section 5.3; splitting hides the table")]
    fn pdi_on(&mut self, surface: &mut dyn Surface, opcode: u8, data: &[u8]) {
        let mut reader = Reader::new(data);
        let domain = self.domain;
        match opcode {
            // RESET and BLINK have no effect inside an object's macro (ANIM-11).
            0x20 | 0x3F if self.in_object => {}
            0x20 => self.reset(surface, &mut reader),
            0x21 => {
                let Some(byte) = reader.byte() else { return };
                self.domain = Domain::from_byte(byte);
                if let Some(pel) = reader.point(self.domain) {
                    self.pel = pel;
                }
            }
            0x22 => self.text_command(&mut reader),
            0x23 => {
                if let Some(byte) = reader.byte() {
                    self.fill = match (byte >> 3) & 0b111 {
                        0 => FillPattern::Solid,
                        1 => FillPattern::Vertical,
                        2 => FillPattern::Horizontal,
                        3 => FillPattern::Cross,
                        mask => FillPattern::Mask(mask.wrapping_sub(4)),
                    };
                    self.highlight = byte & 0b100 != 0;
                    self.line = match byte & 0b11 {
                        0 => LineTexture::Solid,
                        1 => LineTexture::Dotted,
                        2 => LineTexture::Dashed,
                        _ => LineTexture::DotDash,
                    };
                }
                if let Some(size) = reader.point(domain) {
                    self.mask_size = size;
                }
            }
            0x24 => {
                while let Some(point) = reader.point(domain) {
                    self.point = point;
                }
            }
            0x25 => {
                while let Some(step) = reader.point(domain) {
                    self.point = self.point.plus(step);
                }
            }
            0x26 | 0x27 => {
                while let Some(value) = reader.point(domain) {
                    self.point = if opcode == 0x26 { value } else { self.point.plus(value) };
                    raster::point(surface, &self.style(), self.point);
                }
            }
            0x28 | 0x29 => {
                // Each further operand continues from the last end point: a line graph
                // (section 5.3.3.2.1).
                let relative = opcode & 1 == 1;
                while let Some(value) = reader.point(domain) {
                    let end = if relative { self.point.plus(value) } else { value };
                    raster::line(surface, &self.style(), self.point, end, self.colour, false);
                    self.point = end;
                }
            }
            0x2A | 0x2B => {
                // Section 5.3.3.2.4: "If more than two operands are present, lines are drawn from
                // the first to the second point, then from the third to the fourth point, etc."
                // A start point with no end point after it only moves the drawing point.
                let relative = opcode & 1 == 1;
                while let Some(start) = reader.point(domain) {
                    self.point = start;
                    let Some(value) = reader.point(domain) else { break };
                    let end = if relative { start.plus(value) } else { value };
                    raster::line(surface, &self.style(), start, end, self.colour, false);
                    self.point = end;
                }
            }
            0x2C..=0x2F => {
                if opcode >= 0x2E {
                    let Some(start) = reader.point(domain) else { return };
                    self.point = start;
                }
                let filled = opcode & 1 == 1;
                let mut points = vec![self.point];
                while let Some(step) = reader.point(domain) {
                    if points.len() >= MAX_VERTICES {
                        break;
                    }
                    let last = points.last().copied().unwrap_or_default();
                    points.push(last.plus(step));
                }
                let style = self.style();
                match points.as_slice() {
                    [_] => {}
                    [start, middle] => raster::arc(surface, &style, &self.masks, *start, *middle, *start, filled),
                    [start, middle, end] => raster::arc(surface, &style, &self.masks, *start, *middle, *end, filled),
                    many => {
                        // Decision D9: a spline is drawn as straight segments through its points.
                        if filled {
                            raster::polygon_filled(surface, &style, &self.masks, many);
                        } else {
                            raster::polyline(surface, &style, many, false, style.colour, false);
                        }
                    }
                }
                if points.len() > 2 {
                    self.point = points.last().copied().unwrap_or(self.point);
                }
            }
            0x30..=0x33 => {
                if opcode >= 0x32 {
                    let Some(start) = reader.point(domain) else { return };
                    self.point = start;
                }
                let filled = opcode & 1 == 1;
                while let Some(size) = reader.point(domain) {
                    raster::rectangle(surface, &self.style(), &self.masks, self.point, size, filled);
                    self.point = Point::new(self.point.x.saturating_add(size.x), self.point.y);
                }
            }
            0x34..=0x37 => {
                if opcode >= 0x36 {
                    let Some(start) = reader.point(domain) else { return };
                    self.point = start;
                }
                let filled = opcode & 1 == 1;
                let mut points = vec![self.point];
                while let Some(step) = reader.point(domain) {
                    if points.len() >= MAX_VERTICES {
                        break;
                    }
                    let last = points.last().copied().unwrap_or_default();
                    points.push(last.plus(step));
                }
                let style = self.style();
                if filled {
                    raster::polygon_filled(surface, &style, &self.masks, &points);
                } else {
                    raster::polyline(surface, &style, &points, true, style.colour, false);
                }
            }
            0x38 => {
                let first = reader.point(domain);
                let second = reader.point(domain);
                self.field = match (first, second) {
                    (Some(origin), Some(size)) => Some((origin, size)),
                    (Some(size), None) => Some((self.point, size)),
                    _ => None,
                };
                // With no operands the field is the unit screen and its origin (0, 0).
                self.point = self.field.map_or(Point::default(), |(origin, _)| origin);
            }
            0x39 => self.incremental_point(surface, &mut reader),
            0x3A | 0x3B => self.incremental_line(surface, &mut reader, opcode == 0x3B),
            0x3C => self.set_colour(&mut reader),
            0x3D => {
                if reader.byte() != Some(WAIT_FORMAT & DATA_MASK) {
                    return;
                }
                let mut tenths: u32 = 0;
                while let Some(interval) = reader.byte() {
                    tenths = tenths.saturating_add(u32::from(interval));
                }
                // WAIT has no effect inside an object's macro (ANIM-11).
                if !self.in_object {
                    self.event(Event::Wait(tenths));
                    self.waited = true;
                }
            }
            0x3E => self.select_colour(&mut reader),
            0x3F => self.blink(&mut reader),
            _ => {}
        }
    }

    /// RESET (section 5.3.2.9): byte 1 then byte 2, bit 1 to bit 6 each; missing bytes are
    /// zero.
    fn reset(&mut self, surface: &mut dyn Surface, reader: &mut Reader<'_>) {
        let first = reader.byte().unwrap_or(0);
        let second = reader.byte().unwrap_or(0);
        if first & 1 != 0 {
            self.domain = Domain::default();
            self.pel = Point::default();
        }
        match (first >> 1) & 0b11 {
            0b01 => {
                self.mode = Mode::Direct;
                self.palette.reset();
                self.colour = self.palette.white();
            }
            0b10 if self.mode != Mode::Direct => {
                self.mode = Mode::Map;
                self.palette.reset();
            }
            0b10 | 0b11 => {
                self.mode = Mode::Map;
                self.palette.reset();
                self.colour = self.palette.white();
            }
            _ => {}
        }
        let screen = (first >> 3) & 0b111;
        // Table 15: 011 border to nominal black, 100 border to the drawing colour, 101 both to
        // the drawing colour, 110 the display to the drawing colour and the border to black, 111
        // both to black.
        match screen {
            0b011 | 0b110 | 0b111 => self.border = self.palette.black(),
            0b100 | 0b101 => self.border = self.colour,
            _ => {}
        }
        let clear = match screen {
            0b001 | 0b111 => Some(self.palette.black()),
            0b010 | 0b101 | 0b110 => Some(self.colour),
            _ => None, // border only, or nothing: this display has no border
        };
        if let Some(entry) = clear {
            surface.fill_all(entry);
        }
        if second & 0b1 != 0 {
            self.text = TextState::default();
            self.field = None;
            self.home();
        }
        if second & 0b10 != 0 {
            self.palette.stop_blinks();
        }
        if second & 0b1000 != 0 {
            self.line = LineTexture::Solid;
            self.fill = FillPattern::Solid;
            self.highlight = false;
            self.mask_size = Point::new(fraction(1, 40), fraction(5, 128));
        }
        if second & 0b11_0000 != 0 {
            self.scene.definitions_changed = true;
        }
        if second & 0b1_0000 != 0 {
            self.macros.fill(None);
        }
        if second & 0b10_0000 != 0 {
            self.drcs.fill(None);
            self.drcs_cleared = true;
        }
    }

    /// TEXT (section 5.3.2.3): missing bytes leave their attributes unchanged.
    fn text_command(&mut self, reader: &mut Reader<'_>) {
        let domain = self.domain;
        if let Some(byte) = reader.byte() {
            self.text.spacing = (byte >> 4) & 0b11;
            self.text.path = match (byte >> 2) & 0b11 {
                0 => Path::Right,
                1 => Path::Left,
                2 => Path::Up,
                _ => Path::Down,
            };
            self.text.rotation = byte & 0b11;
        }
        if let Some(byte) = reader.byte() {
            self.text.cursor_style = (byte >> 4) & 0b11;
            self.text.motion = match (byte >> 2) & 0b11 {
                0 => Motion::Together,
                1 => Motion::CursorLeads,
                2 => Motion::PointLeads,
                _ => Motion::Independent,
            };
            self.text.rows = byte & 0b11;
        }
        if let Some(size) = reader.point(domain)
            && size.x != 0
            && size.y != 0
        {
            self.text.size = size;
        }
    }

    /// SET COLOR (section 5.3.2.5.1).
    fn set_colour(&mut self, reader: &mut Reader<'_>) {
        let domain = self.domain;
        if reader.is_empty() {
            // No data: the transparent colour, shown as black here (Dillon, SET COLOR).
            self.colour = self.palette.black();
            return;
        }
        match self.mode {
            Mode::Direct => {
                if let Some(colour) = reader.colour(domain) {
                    // An object's macro redefines no entry of the colour map (ANIM-11): it draws
                    // with the entry whose colour is nearest.
                    self.colour =
                        if self.in_object { self.palette.nearest(colour) } else { self.palette.allocate(colour) };
                }
            }
            Mode::Map | Mode::MapWithBackground if self.in_object => {}
            Mode::Map | Mode::MapWithBackground => {
                let mut entry = Some(self.colour);
                while let Some(colour) = reader.colour(domain) {
                    let Some(current) = entry else { break };
                    self.palette.set(current, colour);
                    entry = self.palette.next_entry(current);
                }
            }
        }
    }

    /// SELECT COLOR (section 5.3.2.6).
    fn select_colour(&mut self, reader: &mut Reader<'_>) {
        let domain = self.domain;
        let first = reader.single(domain);
        let second = reader.single(domain);
        match (first, second) {
            (None, _) => self.mode = Mode::Direct,
            (Some((value, width)), None) => {
                self.mode = Mode::Map;
                self.colour = self.palette.entry_from_operand(value, width);
                self.mark_used(self.colour);
            }
            (Some((value, width)), Some((back, back_width))) => {
                self.mode = Mode::MapWithBackground;
                let drawing = self.palette.entry_from_operand(value, width);
                let background = self.palette.entry_from_operand(back, back_width);
                if drawing != background {
                    self.colour = drawing;
                }
                self.background = background;
                self.mark_used(drawing);
                self.mark_used(background);
            }
        }
    }

    /// Notes that SELECT COLOR named an entry, which keeps colour mode 0 from redefining it;
    /// an object's macro leaves the colour map's record as the stream has it (ANIM-11).
    fn mark_used(&mut self, entry: u8) {
        if !self.in_object {
            self.palette.mark_used(entry);
        }
    }

    /// BLINK (section 5.3.2.7).
    fn blink(&mut self, reader: &mut Reader<'_>) {
        let domain = self.domain;
        if reader.is_empty() {
            self.palette.stop_blinks_from(self.colour);
            return;
        }
        let mut from = Some(self.colour);
        while let Some((value, width)) = reader.single(domain) {
            let Some(current) = from else { break };
            let to = self.palette.entry_from_operand(value, width);
            let on = reader.byte().map_or(0, u32::from);
            let off = reader.byte().map_or(0, u32::from);
            let delay = reader.byte().map_or(0, u32::from);
            self.palette.blink(current, to, on, off, delay);
            from = self.palette.next_entry(current);
        }
    }

    /// INCREMENTAL POINT (section 5.3.3.6.3): a bitmap of pels inside the active field.
    #[allow(
        clippy::arithmetic_side_effects,
        reason = "unit lengths below 2^31 and pixel counts below 2^12 multiplied within i64; colour bits assembled below 48 bits; mask sides at most MASK_SIDE"
    )]
    fn incremental_point(&mut self, surface: &mut dyn Surface, reader: &mut Reader<'_>) {
        let Some(packing) = reader.byte() else { return };
        let packing = u32::from(packing);
        if packing == 0 || packing > 48 {
            return;
        }
        let (origin, size) = self.field.unwrap_or((Point::default(), Point::new(ONE, self.display_top)));
        let (left, right) = ordered(origin.x, origin.x.saturating_add(size.x));
        let (bottom, top) = ordered(origin.y, origin.y.saturating_add(size.y));
        // Section 5.3.3.6.3: a zero pel dimension is "the smallest positive value specifiable
        // within the current domain".
        let bits_per_axis =
            u32::try_from(self.domain.multi_bytes).unwrap_or(3) * if self.domain.three_d { 2 } else { 3 };
        let smallest = (ONE >> bits_per_axis.saturating_sub(1).min(24)).max(1);
        let pel_x = if self.pel.x == 0 { smallest } else { self.pel.x };
        let pel_y = if self.pel.y == 0 { smallest } else { self.pel.y };
        let start = self.point;
        if start.x < left || start.x >= right || start.y < bottom || start.y >= top {
            return; // a starting pel outside the active field: the command is not executed
        }
        let mut at = start;
        let mut bits: Vec<bool> = Vec::new();
        while let Some(byte) = reader.byte() {
            for bit in (0..6).rev() {
                bits.push(byte & (1 << bit) != 0);
            }
        }
        let mut style = self.style();
        style.pel = Point::new(pel_x, pel_y);
        let packing_bits = usize::try_from(packing).unwrap_or(1);
        let mut position = 0usize;
        while let Some(chunk) = bits.get(position..position + packing_bits) {
            position += packing_bits;
            let entry = if self.mode == Mode::Direct {
                {
                    let mut primaries = [0u32; 3];
                    let mut widths = [0u32; 3];
                    for (index, bit) in chunk.iter().enumerate() {
                        // The bits run G R B G R B; the colour's slots are R G B.
                        let primary = match index % 3 {
                            0 => 1,
                            1 => 0,
                            _ => 2,
                        };
                        if let (Some(value), Some(width)) = (primaries.get_mut(primary), widths.get_mut(primary)) {
                            *value = (*value << 1) | u32::from(*bit);
                            *width += 1;
                        }
                    }
                    let colour = [0, 1, 2].map(|i| {
                        eight_bits(primaries.get(i).copied().unwrap_or(0), widths.get(i).copied().unwrap_or(0))
                    });
                    self.palette.allocate(colour)
                }
            } else {
                let value = chunk.iter().fold(0u32, |value, bit| (value << 1) | u32::from(*bit));
                self.palette.entry_from_operand(value, packing.min(32))
            };
            style.colour = entry;
            let (x, y) = pixel_of(surface, at);
            raster::stamp(surface, &style, x, y, entry);
            at.x = at.x.saturating_add(pel_x);
            let beyond = if pel_x > 0 { at.x.saturating_add(pel_x) > right } else { at.x.saturating_add(pel_x) < left };
            if beyond {
                // "any remaining bits in the byte of the string operand currently being
                // interpreted are discarded" at the end of a row.
                position = position.div_ceil(6) * 6;
                at.x = if pel_x > 0 { left } else { right.saturating_sub(pel_x.saturating_abs()) };
                at.y = at.y.saturating_add(pel_y);
                let outside =
                    if pel_y > 0 { at.y.saturating_add(pel_y) > top } else { at.y.saturating_add(pel_y) < bottom };
                if outside {
                    break;
                }
            }
        }
        self.point = origin;
        let _ = start;
    }

    /// INCREMENTAL LINE and INCREMENTAL POLY FILLED (section 5.3.3.6.4, 5.3.3.6.5).
    fn incremental_line(&mut self, surface: &mut dyn Surface, reader: &mut Reader<'_>, filled: bool) {
        let domain = self.domain;
        let Some(step) = reader.point(domain) else { return };
        let (mut dx, mut dy) = (step.x, step.y);
        let mut draw = true;
        let mut points = vec![self.point];
        let mut escape = false;
        let style = self.style();
        'bytes: while let Some(byte) = reader.byte() {
            for shift in [4u8, 2, 0] {
                let opcode = (byte >> shift) & 0b11;
                if escape {
                    escape = false;
                    match opcode {
                        0 => {
                            if filled {
                                // Section 5.3.3.6.5: treated as a null, "and the following nibble is
                                // interpreted as the 'modify parameter' instruction".
                                escape = true;
                            } else {
                                draw = !draw;
                            }
                        }
                        1 => dx = dx.saturating_neg(),
                        2 => dy = dy.saturating_neg(),
                        _ => {
                            dx = dx.saturating_neg();
                            dy = dy.saturating_neg();
                        }
                    }
                    continue;
                }
                let delta = match opcode {
                    0 => {
                        escape = true;
                        continue;
                    }
                    1 => Point::new(dx, 0),
                    2 => Point::new(0, dy),
                    _ => Point::new(dx, dy),
                };
                let next = self.point.plus(delta);
                if filled {
                    if points.len() >= MAX_VERTICES {
                        break 'bytes;
                    }
                    points.push(next);
                } else if draw {
                    raster::line(surface, &style, self.point, next, style.colour, false);
                }
                self.point = next;
            }
        }
        if filled {
            raster::polygon_filled(surface, &style, &self.masks, &points);
            self.point = points.first().copied().unwrap_or(self.point);
        }
    }

    // ----- Text -----------------------------------------------------------------------------

    fn field_now(&self, origin: Point) -> Field {
        Field { origin, size: self.text.size, rotation: self.text.rotation }
    }

    /// The area text wraps within: the active field if the character field lies wholly inside
    /// it, else the display (Dillon, C0 Control Set).
    fn area(&self) -> (Unit, Unit, Unit, Unit) {
        let display = (0, 0, ONE, self.display_top);
        if let Some((origin, size)) = self.field {
            let (x0, x1) = ordered(origin.x, origin.x.saturating_add(size.x));
            let (y0, y1) = ordered(origin.y, origin.y.saturating_add(size.y));
            let field = (x0, y0, x1, y1);
            if self.fits(self.cursor, field) {
                return field;
            }
        }
        display
    }

    /// The character field's box with its origin at `origin`.
    fn field_box(&self, origin: Point) -> (Unit, Unit, Unit, Unit) {
        let (u, v) = self.field_now(origin).axes();
        let xs = [
            origin.x,
            origin.x.saturating_add(u.x),
            origin.x.saturating_add(v.x),
            origin.x.saturating_add(u.x).saturating_add(v.x),
        ];
        let ys = [
            origin.y,
            origin.y.saturating_add(u.y),
            origin.y.saturating_add(v.y),
            origin.y.saturating_add(u.y).saturating_add(v.y),
        ];
        let x0 = xs.iter().copied().min().unwrap_or(0);
        let x1 = xs.iter().copied().max().unwrap_or(0);
        let y0 = ys.iter().copied().min().unwrap_or(0);
        let y1 = ys.iter().copied().max().unwrap_or(0);
        (x0, y0, x1, y1)
    }

    fn fits(&self, origin: Point, area: (Unit, Unit, Unit, Unit)) -> bool {
        let (x0, y0, x1, y1) = self.field_box(origin);
        x0 >= area.0 && y0 >= area.1 && x1 <= area.2 && y1 <= area.3
    }

    /// The cursor's step along the path for one character (section 5.3.2.3.4). Proportional
    /// spacing steps by a whole field here; [`Self::character`] narrows it for a stroke glyph.
    fn advance_step(&self) -> Point {
        let (ex, ey) = self.field_now(self.cursor).extent();
        let scale_by = |value: Unit| match self.text.spacing {
            1 => crate::fixed::scale(i64::from(value), 5, 4),
            2 => crate::fixed::scale(i64::from(value), 3, 2),
            _ => i64::from(value),
        };
        let x = Unit::try_from(scale_by(ex)).unwrap_or(ex);
        let y = Unit::try_from(scale_by(ey)).unwrap_or(ey);
        match self.text.path {
            Path::Right => Point::new(x, 0),
            Path::Left => Point::new(x.saturating_neg(), 0),
            Path::Up => Point::new(0, y),
            Path::Down => Point::new(0, y.saturating_neg()),
        }
    }

    /// The step of a line feed (section 5.3.2.3.5): perpendicular to the path, down for
    /// horizontal paths and right for vertical ones.
    fn row_step(&self) -> Point {
        let (ex, ey) = self.field_now(self.cursor).extent();
        let scale_by = |value: Unit| {
            let scaled = match self.text.rows {
                1 => crate::fixed::scale(i64::from(value), 5, 4),
                2 => crate::fixed::scale(i64::from(value), 3, 2),
                3 => i64::from(value).saturating_mul(2),
                _ => i64::from(value),
            };
            Unit::try_from(scaled).unwrap_or(value)
        };
        match self.text.path {
            Path::Right | Path::Left => Point::new(0, scale_by(ey).saturating_neg()),
            Path::Up | Path::Down => Point::new(scale_by(ex), 0),
        }
    }

    fn sync_point(&mut self) {
        if matches!(self.text.motion, Motion::Together | Motion::CursorLeads) {
            self.point = self.cursor.plus(self.alignment());
        }
    }

    /// `cursor` moved as little as possible so that its character field lies inside the unit
    /// screen (section 5.3.2.3.7: "Should such a situation arise, the cursor shall be adjusted
    /// as close as possible to the drawing point without violating the above condition").
    fn inside_unit_screen(&self, cursor: Point) -> Point {
        let (x0, y0, x1, y1) = self.field_box(cursor);
        let shift = |low: Unit, high: Unit| {
            if low < 0 {
                low.saturating_neg()
            } else if high > ONE {
                ONE.saturating_sub(high)
            } else {
                0
            }
        };
        cursor.plus(Point::new(shift(x0, x1), shift(y0, y1)))
    }

    /// Where the drawing point sits relative to the cursor when they are aligned: the character
    /// field's origin for the underscore and block cursors, its centre for the cross-hair and
    /// custom cursors (section 5.3.2.3.7).
    fn alignment(&self) -> Point {
        if self.text.cursor_style >= CURSOR_CROSS_HAIR {
            let (u, v) = self.field_now(Point::default()).axes();
            Point::new(u.x.saturating_add(v.x) / 2, u.y.saturating_add(v.y) / 2)
        } else {
            Point::default()
        }
    }

    /// The upper left character position of the display.
    fn home_position(&self) -> Point {
        let (x0, _, _, y1) = self.field_box(Point::default());
        Point::new(0i32.saturating_sub(x0), self.display_top.saturating_sub(y1))
    }

    fn home(&mut self) {
        self.cursor = self.home_position();
        self.sync_point();
    }

    fn carriage_return(&mut self) {
        self.cursor = self.line_start();
        self.sync_point();
    }

    /// Where a carriage return puts the cursor: the start of the current line along the path.
    fn line_start(&self) -> Point {
        let area = self.area();
        let (x0, y0, x1, y1) = self.field_box(self.cursor);
        match self.text.path {
            Path::Right => Point::new(self.cursor.x.saturating_add(area.0.saturating_sub(x0)), self.cursor.y),
            Path::Left => Point::new(self.cursor.x.saturating_add(area.2.saturating_sub(x1)), self.cursor.y),
            Path::Up => Point::new(self.cursor.x, self.cursor.y.saturating_add(area.1.saturating_sub(y0))),
            Path::Down => Point::new(self.cursor.x, self.cursor.y.saturating_add(area.3.saturating_sub(y1))),
        }
    }

    /// Line feed (`down`) or vertical tab: wraps to the opposite boundary, or scrolls in scroll
    /// mode (Dillon, Line Feed).
    fn line_feed(&mut self, canvas: &mut dyn Surface, down: bool) {
        let area = self.area();
        let step = self.row_step();
        let step = if down { step } else { Point::new(step.x.saturating_neg(), step.y.saturating_neg()) };
        let next = self.cursor.plus(step);
        if self.fits(next, area) {
            self.cursor = next;
        } else if self.text.scroll {
            self.scroll(canvas, area, step);
        } else {
            let (x0, y0, x1, y1) = self.field_box(self.cursor);
            self.cursor = if step.y < 0 {
                Point::new(self.cursor.x, self.cursor.y.saturating_add(area.3.saturating_sub(y1)))
            } else if step.y > 0 {
                Point::new(self.cursor.x, self.cursor.y.saturating_add(area.1.saturating_sub(y0)))
            } else if step.x > 0 {
                Point::new(self.cursor.x.saturating_add(area.0.saturating_sub(x0)), self.cursor.y)
            } else {
                Point::new(self.cursor.x.saturating_add(area.2.saturating_sub(x1)), self.cursor.y)
            };
        }
        self.sync_point();
    }

    /// Moves the area's pixels opposite to `step` and clears what scrolls in.
    #[allow(
        clippy::arithmetic_side_effects,
        reason = "unit lengths below 2^31 and pixel counts below 2^12 multiplied within i64; colour bits assembled below 48 bits; mask sides at most MASK_SIDE"
    )]
    fn scroll(&mut self, canvas: &mut dyn Surface, area: (Unit, Unit, Unit, Unit), step: Point) {
        let top_left = pixel_of(canvas, Point::new(area.0, area.3));
        let bottom_right = pixel_of(canvas, Point::new(area.2, area.1));
        let (xn, xd) = canvas.scale_x();
        let (yn, yd) = canvas.scale_y();
        let shift_x = crate::fixed::to_pixels_at(step.x, xn, xd);
        let shift_y = crate::fixed::to_pixels_at(step.y, yn, yd);
        let blank = if self.mode == Mode::MapWithBackground { self.background } else { self.palette.black() };
        let (x0, y0) = (top_left.0.max(0), top_left.1.max(0));
        let (x1, y1) = (bottom_right.0.min(canvas.width() - 1), bottom_right.1.min(canvas.height() - 1));
        // Scrolling up (a line feed downward) moves content up the screen: rows read from below.
        let rows: Vec<i32> = if shift_y < 0 { (y0..=y1).collect() } else { (y0..=y1).rev().collect() };
        let columns: Vec<i32> = if shift_x > 0 { (x0..=x1).collect() } else { (x0..=x1).rev().collect() };
        for &y in &rows {
            for &x in &columns {
                let (sx, sy) = (x.saturating_add(shift_x), y.saturating_sub(shift_y));
                let value = if (x0..=x1).contains(&sx) && (y0..=y1).contains(&sy) {
                    canvas.get(sx, sy).unwrap_or(blank)
                } else {
                    blank
                };
                canvas.put(x, y, value);
            }
        }
    }

    fn backspace(&mut self, canvas: &mut dyn Surface) {
        let step = self.advance_step();
        let next = Point::new(self.cursor.x.saturating_sub(step.x), self.cursor.y.saturating_sub(step.y));
        if self.fits(next, self.area()) {
            self.cursor = next;
            self.sync_point();
        } else {
            self.end_of_line();
            self.line_feed(canvas, false);
        }
    }

    fn forward(&mut self, canvas: &mut dyn Surface) {
        let next = self.cursor.plus(self.advance_step());
        if self.fits(next, self.area()) {
            self.cursor = next;
            self.sync_point();
        } else {
            self.carriage_return();
            self.line_feed(canvas, true);
        }
    }

    /// The last character position on the path.
    fn end_of_line(&mut self) {
        let area = self.area();
        let (x0, y0, x1, y1) = self.field_box(self.cursor);
        self.cursor = match self.text.path {
            Path::Right => Point::new(self.cursor.x.saturating_add(area.2.saturating_sub(x1)), self.cursor.y),
            Path::Left => Point::new(self.cursor.x.saturating_add(area.0.saturating_sub(x0)), self.cursor.y),
            Path::Up => Point::new(self.cursor.x, self.cursor.y.saturating_add(area.3.saturating_sub(y1))),
            Path::Down => Point::new(self.cursor.x, self.cursor.y.saturating_add(area.1.saturating_sub(y0))),
        };
    }

    /// Moves along the path after a character; at the edge, a new line (section 5.3.2.3.6).
    fn advance(&mut self, canvas: &mut dyn Surface, step: Point) {
        let next = self.cursor.plus(step);
        if self.fits(next, self.area()) {
            self.cursor = next;
            self.sync_point();
        } else {
            self.carriage_return();
            self.line_feed(canvas, true);
            self.auto_wrapped = 2;
        }
    }

    fn active_position_set(&mut self, row: u8, column: u8) {
        let row = i64::from((row & 0x7F).saturating_sub(0x20));
        let column = i64::from((column & 0x7F).saturating_sub(0x20));
        let (ex, ey) = self.field_now(self.cursor).extent();
        self.cursor = Point::new(
            Unit::try_from(column.saturating_mul(i64::from(ex))).unwrap_or(0),
            Unit::try_from(row.saturating_mul(i64::from(ey))).unwrap_or(0),
        );
        self.sync_point();
    }

    /// NSR (section 6.1.6.5): designations, DOMAIN, text, texture and colour mode to their
    /// defaults; the colour map and fill masks are kept.
    fn nsr(&mut self) {
        self.g_sets = [CharSet::Primary, CharSet::Pdi, CharSet::Supplementary, CharSet::Mosaic];
        self.gl = 0;
        self.gr = 1;
        self.single_shift = None;
        self.domain = Domain::default();
        self.pel = Point::default();
        self.text = TextState::default();
        self.field = None;
        self.line = LineTexture::Solid;
        self.fill = FillPattern::Solid;
        self.highlight = false;
        self.mask_size = Point::new(fraction(1, 40), fraction(5, 128));
        self.mode = Mode::Direct;
        self.colour = self.palette.white();
    }

    /// NSR's optional position: row and column from the top left (Dillon, NSR).
    fn nsr_position(&mut self, row: u8, column: u8) {
        let row = i64::from(row & DATA_MASK);
        let column = i64::from(column & DATA_MASK);
        let (ex, ey) = self.field_now(self.cursor).extent();
        let x = column.saturating_mul(i64::from(ex));
        let y = i64::from(self.display_top).saturating_sub(row.saturating_add(1).saturating_mul(i64::from(ey)));
        self.cursor = Point::new(Unit::try_from(x).unwrap_or(0), Unit::try_from(y.max(0)).unwrap_or(0));
        self.sync_point();
    }

    /// One character from a graphic set. In word wrap mode, primary, supplementary and DRCS
    /// characters are buffered into words and a word that does not fit on the rest of the line
    /// starts the next (section 6.2.7.11); anything else ends the word first.
    fn character(&mut self, canvas: &mut dyn Surface, set: CharSet, code: u8) {
        self.last_was_spacing = !is_accent(set, code) && set != CharSet::Null;
        let alphanumeric = matches!(set, CharSet::Primary | CharSet::Supplementary | CharSet::Drcs);
        if self.text.word_wrap && alphanumeric {
            if set == CharSet::Primary && code == SPACE {
                self.end_word(canvas, true);
                return;
            }
            if self.word.len() >= MAX_WORD {
                self.end_word(canvas, false);
            }
            self.word.push((set, code));
            return;
        }
        self.end_word(canvas, false);
        self.draw_character(canvas, set, code);
    }

    /// Draws a buffered word, first starting a new line if it does not fit on this one, and then
    /// the SPACE that ended it, which is dropped if the word filled the line (section 6.2.7.11).
    fn end_word(&mut self, canvas: &mut dyn Surface, space: bool) {
        let word = core::mem::take(&mut self.word);
        if !word.is_empty() && !self.word_fits(&word) && self.cursor != self.line_start() {
            self.carriage_return();
            self.line_feed(canvas, true);
        }
        self.auto_wrapped = 0;
        for &(set, code) in &word {
            self.draw_character(canvas, set, code);
        }
        if space {
            if self.auto_wrapped == 2 {
                self.auto_wrapped = 0; // the line ended with the word: the SPACE is dropped
            } else {
                self.draw_character(canvas, CharSet::Primary, SPACE);
            }
        }
    }

    /// Whether every character of `word` fits on the rest of the current line.
    fn word_fits(&self, word: &[(CharSet, u8)]) -> bool {
        let area = self.area();
        let mut at = self.cursor;
        for &(set, code) in word {
            if is_accent(set, code) {
                continue;
            }
            if !self.fits(at, area) {
                return false;
            }
            at = at.plus(self.step_for(set, code));
        }
        true
    }

    /// Draws a buffered word and a waiting accent: before anything that is not text.
    fn settle(&mut self, canvas: &mut dyn Surface) {
        self.end_word(canvas, false);
        if let Some(accent) = self.pending_accent.take() {
            let field = self.field_now(self.cursor);
            let ink = self.ink(0);
            self.paint(canvas, CharSet::Supplementary, accent, field, ink);
        }
    }

    /// The step along the path after `code`: proportional for a stroke glyph in proportional
    /// spacing (DEC-5813), otherwise the spacing's fixed step.
    fn step_for(&self, set: CharSet, code: u8) -> Point {
        let step = self.advance_step();
        match self.proportional_extent(set, code) {
            Some((left, right)) => {
                let width = i64::from(right.saturating_sub(left)).saturating_add(PROPORTIONAL_GAP);
                Point::new(eighths(step.x, width), eighths(step.y, width))
            }
            None => step,
        }
    }

    fn ink(&self, field_from: i64) -> Ink {
        Ink {
            colour: self.colour,
            background: (self.mode == Mode::MapWithBackground).then_some(self.background),
            reverse: self.text.reverse,
            underline: None,
            field_from,
        }
    }

    /// Draws one character at the cursor and moves the cursor on. A non-spacing accent (the
    /// supplementary set's 4/0 to 4/15) waits for the next character and is drawn over it, so
    /// that the letter's field, painted in colour mode 2, does not cover it (section 5.3.2.3.4).
    fn draw_character(&mut self, canvas: &mut dyn Surface, set: CharSet, code: u8) {
        if code == 0x7F && matches!(set, CharSet::Primary | CharSet::Supplementary) {
            return; // DEL
        }
        if is_accent(set, code) {
            self.settle_accent(canvas);
            self.pending_accent = Some(code);
            return;
        }
        let mut field = self.field_now(self.cursor);
        let mut field_from = 0;
        if let Some((left, _)) = self.proportional_extent(set, code) {
            // The glyph's leftmost stroke sits at the cursor; its field is painted from there on.
            let (u, _) = field.axes();
            let shift = Point::new(eighths(u.x, left), eighths(u.y, left));
            field.origin = field.origin.plus(Point::new(shift.x.saturating_neg(), shift.y.saturating_neg()));
            field_from = i64::from(left).saturating_mul(text::FIELD_ONE) / text::STROKE_X_DIVISOR;
        }
        let ink = self.ink(field_from);
        self.paint(canvas, set, code, field, ink);
        if let Some(accent) = self.pending_accent.take() {
            let over = Ink { field_from: text::FIELD_ONE, ..ink };
            self.paint(canvas, CharSet::Supplementary, accent, field, over);
        }
        self.last_spacing = Some((set, code));
        let step = self.step_for(set, code);
        self.advance(canvas, step);
    }

    /// Draws a waiting accent on its own, before another accent replaces it.
    fn settle_accent(&mut self, canvas: &mut dyn Surface) {
        if let Some(accent) = self.pending_accent.take() {
            let field = self.field_now(self.cursor);
            let ink = self.ink(0);
            self.paint(canvas, CharSet::Supplementary, accent, field, ink);
        }
    }

    /// Draws one character's shape into `field`, on the definition being recorded if any.
    fn paint(&mut self, canvas: &mut dyn Surface, set: CharSet, code: u8, field: Field, ink: Ink) {
        let underline = |surface: &dyn Surface, terminal: &Self| {
            terminal.text.underline.then(|| text::underline_share(surface, terminal.pel.y, terminal.text.size.y))
        };
        let mut recording = self.recording.take();
        {
            let surface: &mut dyn Surface = match &mut recording {
                Some(Recording::Drcs { mask, per_unit, .. } | Recording::Texture { mask, per_unit, .. }) => {
                    &mut MaskSurface { mask, per_unit: *per_unit }
                }
                _ => &mut *canvas,
            };
            let mut ink = ink;
            match set {
                CharSet::Primary | CharSet::Supplementary => {
                    if ink.field_from < text::FIELD_ONE {
                        ink.underline = underline(surface, self);
                    }
                    let font_set = if set == CharSet::Primary { FontSet::Primary } else { FontSet::Supplementary };
                    let glyph = if code == SPACE && set == CharSet::Primary {
                        None
                    } else {
                        self.font.as_ref().and_then(|font| font.glyph(font_set, code))
                    };
                    let shape = glyph.map_or(Shape::Blank, |glyph| Shape::Strokes(&glyph.segments));
                    text::draw(surface, field, &shape, ink);
                }
                CharSet::Mosaic => {
                    let code = if code == 0x5F { 0x7F } else { code };
                    let is_mosaic = (0x20..=0x3F).contains(&code) || (0x60..=0x7F).contains(&code);
                    let separation = self.text.underline.then(|| text::separation(surface, self.pel, self.text.size));
                    let shape = if is_mosaic { Shape::Mosaic { code, separation } } else { Shape::Blank };
                    text::draw(surface, field, &shape, ink);
                }
                CharSet::Drcs => {
                    ink.underline = underline(surface, self);
                    let mask = self.drcs.get(usize::from(code.wrapping_sub(FIRST_CODE))).and_then(Option::as_ref);
                    let shape = mask.map_or(Shape::Blank, Shape::Bitmap);
                    text::draw(surface, field, &shape, ink);
                }
                CharSet::Pdi | CharSet::Macro | CharSet::Null => {}
            }
        }
        if self.recording.is_none() {
            self.recording = recording;
        }
    }

    /// The leftmost and rightmost stroke columns of a glyph drawn with proportional spacing on
    /// a horizontal path; `None` for fixed spacing, vertical paths and glyphs without strokes,
    /// which step by the whole field (PP3, SEAPORT.NAP: a space steps 20 pixels on a 20-pixel
    /// field).
    fn proportional_extent(&self, set: CharSet, code: u8) -> Option<(u8, u8)> {
        if self.text.spacing != SPACING_PROPORTIONAL || !matches!(self.text.path, Path::Right | Path::Left) {
            return None;
        }
        let font_set = match set {
            CharSet::Primary => FontSet::Primary,
            CharSet::Supplementary => FontSet::Supplementary,
            _ => return None,
        };
        let glyph = self.font.as_ref()?.glyph(font_set, code)?;
        let columns = glyph.segments.iter().flat_map(|segment| [segment[0], segment[2]]);
        let left = columns.clone().min()?;
        let right = columns.max()?;
        Some((left, right))
    }

    fn repeat(&mut self, canvas: &mut dyn Surface, count: u32) {
        let Some((set, code)) = self.last_spacing else { return };
        for _ in 0..count {
            self.character(canvas, set, code);
        }
    }

    fn repeat_to_end(&mut self, canvas: &mut dyn Surface) {
        let Some((set, code)) = self.last_spacing else { return };
        let area = self.area();
        for _ in 0..MAX_REPEAT_TO_END {
            if !self.fits(self.cursor.plus(self.advance_step()), area) {
                self.character(canvas, set, code);
                break;
            }
            self.character(canvas, set, code);
        }
    }
}

/// ESC, SO, SI, SS2, SS3.
const ESC: u8 = 0x1B;
/// See [`ESC`].
const SO: u8 = 0x0E;
/// See [`ESC`].
const SI: u8 = 0x0F;
/// See [`ESC`].
const SS2: u8 = 0x19;
/// See [`ESC`].
const SS3: u8 = 0x1D;
/// BLINK START's intervals, which section 6.2 leaves to the implementation: half a second each.
const BLINK_START_ON: u32 = 5;
/// See [`BLINK_START_ON`].
const BLINK_START_OFF: u32 = 5;
/// Characters REPEAT TO EOL may draw.
const MAX_REPEAT_TO_END: usize = 1024;

/// A one-bit bitmap of [`MASK_SIDE`] pixels on the longer side with the shape of `size`, and its
/// scale: the longer side is one unit (Dillon, DEF DRCS).
#[allow(
    clippy::arithmetic_side_effects,
    reason = "unit lengths below 2^31 and pixel counts below 2^12 multiplied within i64; colour bits assembled below 48 bits; mask sides at most MASK_SIDE"
)]
fn mask_for(size: Point) -> (Mask, u32) {
    let width = i64::from(size.x.saturating_abs()).max(1);
    let height = i64::from(size.y.saturating_abs()).max(1);
    let longer = width.max(height);
    let mask_side = i64::from(MASK_SIDE);
    let mask_width = u32::try_from((width * mask_side / longer).max(1)).unwrap_or(1);
    let mask_height = u32::try_from((height * mask_side / longer).max(1)).unwrap_or(1);
    (Mask::new(mask_width, mask_height), MASK_SIDE)
}

fn ordered(a: Unit, b: Unit) -> (Unit, Unit) {
    if a <= b { (a, b) } else { (b, a) }
}

#[allow(
    clippy::arithmetic_side_effects,
    reason = "unit lengths below 2^31 and pixel counts below 2^12 multiplied within i64; colour bits assembled below 48 bits; mask sides at most MASK_SIDE"
)]
fn eight_bits(value: u32, width: u32) -> u8 {
    if width == 0 {
        return 0;
    }
    let all_ones = (1u32 << width.min(31)) - 1;
    if value == all_ones {
        return u8::MAX;
    }
    let scaled = if width >= 8 { value >> (width - 8) } else { value << (8 - width) };
    u8::try_from(scaled & 0xFF).unwrap_or(u8::MAX)
}

/// The TEXT opcode (section 5.3.2.3).
const TEXT_OPCODE: u8 = 0x22;
/// TEXT's cursor style for the cross-hair cursor; the custom cursor (3) aligns as it does.
const CURSOR_CROSS_HAIR: u8 = 2;

/// SPACE in the primary set.
const SPACE: u8 = 0x20;

/// The longest word word wrap buffers: a word as long as the longest possible line (section
/// 6.2.7.11: a character that makes a word as long as a line ends it). 80 columns of SMALL TEXT
/// at proportional spacing's narrowest step (two eighths of a field) is 320 characters.
const MAX_WORD: usize = 320;

/// Whether a character is a non-spacing accent: the supplementary set's 4/0 to 4/15 (section 5.2).
fn is_accent(set: CharSet, code: u8) -> bool {
    set == CharSet::Supplementary && (0x40..=0x4F).contains(&code)
}

/// TEXT's spacing field value for proportional spacing (section 5.3.2.3.4: 11).
const SPACING_PROPORTIONAL: u8 = 0b11;

/// A proportionally spaced stroke glyph steps by its strokes' width plus this many eighths of
/// the field. Measured from PP3 (SEAPORT.NAP, a 20-pixel field): F, e, a, u, r, n, g (strokes
/// spanning 4 columns) step 15 pixels, t (2 columns) 10 and i (one column) 5.
const PROPORTIONAL_GAP: i64 = 2;

/// `count` eighths of `value`, the stroke grid's column width (`text::STROKE_X_DIVISOR`).
fn eighths(value: Unit, count: impl Into<i64>) -> Unit {
    Unit::try_from(crate::fixed::scale(i64::from(value), count.into(), text::STROKE_X_DIVISOR)).unwrap_or(value)
}

#[cfg(test)]
#[allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "tests build byte strings and read pixels directly"
)]
mod tests {
    use super::*;

    /// RECT FILLED (3/1) from the drawing point with size (1/2, 1/4), three-byte operands.
    const RECT_HALF_QUARTER: [u8; 4] = [0x31, 0x51, 0x40, 0x40];
    const DEF_MACRO: u8 = 0x80;
    const DEFP_MACRO: u8 = 0x81;
    const DEF_DRCS: u8 = 0x83;
    const END: u8 = 0x85;

    fn run(bytes: &[u8]) -> (Terminal, Canvas, Vec<Event>) {
        let mut canvas = Canvas::new(640, 480).unwrap();
        let mut terminal = Terminal::new(4);
        let mut events = terminal.feed(&mut canvas, bytes);
        events.extend(terminal.finish(&mut canvas));
        (terminal, canvas, events)
    }

    fn lit(canvas: &Canvas) -> usize {
        canvas.pixels().iter().filter(|&&entry| entry != 0).count()
    }

    #[test]
    fn a_macro_draws_when_invoked_not_when_defined() {
        // DEF MACRO 2/1: SO, RECT; END. Then the macro set into G2 (ESC 2/14 2/0 7/10) and SS2 2/1.
        let mut bytes = vec![DEF_MACRO, 0x21, SO];
        bytes.extend_from_slice(&RECT_HALF_QUARTER);
        bytes.push(END);
        let (_, canvas, _) = run(&bytes);
        assert_eq!(lit(&canvas), 0, "DEF MACRO records without executing");
        bytes.extend_from_slice(&[ESC, 0x2E, 0x20, 0x7A, SS2, 0x21]);
        let (_, canvas, _) = run(&bytes);
        assert!(lit(&canvas) > 0, "invoking the macro draws the rectangle");
    }

    #[test]
    fn defp_executes_while_recording_and_ignores_itself() {
        let mut bytes = vec![ESC, 0x2E, 0x20, 0x7A, DEFP_MACRO, 0x21, SO];
        bytes.extend_from_slice(&RECT_HALF_QUARTER);
        // A reference to the macro being defined is treated as undefined (section 6.2).
        bytes.extend_from_slice(&[SS2, 0x21, END]);
        let (terminal, canvas, events) = run(&bytes);
        assert!(lit(&canvas) > 0);
        assert_eq!(events, Vec::new());
        assert!(terminal.macros[1].is_some());
    }

    #[test]
    fn self_invoking_macros_stop_at_the_depth_limit() {
        // Macro 2/1 invokes itself: expansion stops at MAX_MACRO_DEPTH, without the budget.
        let bytes = [ESC, 0x2E, 0x20, 0x7A, DEF_MACRO, 0x21, SS2, 0x21, END, SS2, 0x21];
        let (terminal, _, events) = run(&bytes);
        assert!(!events.contains(&Event::LimitReached));
        assert!(terminal.processed < 1000);
    }

    #[test]
    fn exponential_macros_stop_at_the_processing_budget() {
        // Each of 16 macros invokes the next one 60 times: far beyond the budget, which stops it.
        let mut bytes = vec![ESC, 0x2E, 0x20, 0x7A];
        for number in 0x21..0x31u8 {
            bytes.extend_from_slice(&[DEF_MACRO, number]);
            for _ in 0..60 {
                bytes.extend_from_slice(&[SS2, number + 1]);
            }
        }
        bytes.extend_from_slice(&[DEF_MACRO, 0x31, b'x', END, SS2, 0x21]);
        let (_, _, events) = run(&bytes);
        assert!(events.contains(&Event::LimitReached));
    }

    #[test]
    fn cancel_ends_executing_macros() {
        // The macro draws only after CAN; CAN inside it ends the expansion first.
        let mut bytes = vec![ESC, 0x2E, 0x20, 0x7A, DEF_MACRO, 0x21, 0x18, SO];
        bytes.extend_from_slice(&RECT_HALF_QUARTER);
        bytes.extend_from_slice(&[END, SS2, 0x21]);
        let (_, canvas, _) = run(&bytes);
        assert_eq!(lit(&canvas), 0);
    }

    #[test]
    fn wait_reports_its_tenths_and_needs_its_format_byte() {
        let (_, _, events) = run(&[SO, 0x3D, 0x5C, 0x45, 0x43]);
        assert_eq!(events, vec![Event::Wait(8)]);
        let (_, _, events) = run(&[SO, 0x3D, 0x45, 0x43]);
        assert_eq!(events, Vec::new(), "without 1011100 first the WAIT is discarded");
    }

    #[test]
    fn select_colour_with_two_operands_is_mode_two() {
        // SELECT COLOR 3/14 with two one-byte single values: drawing entry 12, background 3.
        let (terminal, _, _) = run(&[SO, 0x3E, 0x70, 0x4C]);
        assert_eq!(terminal.mode, Mode::MapWithBackground);
        assert_eq!(terminal.colour, 12);
        assert_eq!(terminal.background, 3);
        // A space then fills its field with the background colour.
        let (_, canvas, _) = run(&[SO, 0x3E, 0x70, 0x4C, SI, b' ']);
        assert!(canvas.pixels().contains(&3));
    }

    #[test]
    fn a_drcs_character_draws_its_definition() {
        // DEF DRCS 2/1: a filled rectangle over the whole bitmap; END; the DRCS into G3; SS3 2/1.
        let mut bytes = vec![DEF_DRCS, 0x21, SO, 0x31, 0x5B, 0x7F, 0x7F, END];
        let (_, canvas, _) = run(&bytes);
        assert_eq!(lit(&canvas), 0, "the definition draws into the bitmap, not the screen");
        bytes.extend_from_slice(&[ESC, 0x2F, 0x20, 0x7B, SS3, 0x21]);
        let (_, canvas, _) = run(&bytes);
        assert!(lit(&canvas) > 0);
    }

    #[test]
    fn clear_screen_inside_a_definition_clears_only_the_definition() {
        // White screen; DEF TEXTURE mask A (ESC 4/4 4/1) containing CS; END: the screen stays.
        let (_, canvas, _) = run(&[SO, 0x20, 0x50, 0x40, ESC, 0x44, 0x41, 0x0C, END]);
        assert!(canvas.pixels().iter().all(|&entry| entry == 7));
    }

    #[test]
    fn eight_bit_pdi_bytes_work_from_gr() {
        // 8-bit form: RECT FILLED and its operands in GR (bit 8 set), as Prodigy pages send them.
        let bytes: Vec<u8> = RECT_HALF_QUARTER.iter().map(|byte| byte | 0x80).collect();
        let (_, canvas, _) = run(&bytes);
        assert!(lit(&canvas) > 0);
    }

    #[test]
    fn incremental_line_draws_a_scribble() {
        // INCREMENTAL LINE 3/10, step (1/16, 1/16): opcodes 01 01 11 (right, right, diagonal).
        let (_, canvas, _) = run(&[SO, 0x3A, 0x40, 0x52, 0x40, 0x40 | 0b01_01_11]);
        assert!(lit(&canvas) > 0);
    }
    #[test]
    fn proportional_spacing_steps_by_the_strokes_width() {
        // TEXT with proportional spacing and a 1/32 field, whose eighths are whole units; then
        // "il " in a font where i is one column (x = 3) and l spans four (x = 1 to 5).
        let font = StrokeFont::parse("[primary]\n69 0 0 3,2,3,6\n6c 0 0 1,2,5,2\n[supplementary]\n").unwrap();
        let mut canvas = Canvas::new(640, 480).unwrap();
        let mut terminal = Terminal::new(4);
        terminal.set_font(font);
        let _ = terminal.feed(&mut canvas, &[SO, 0x22, 0x70, 0x40]);
        terminal.text.size = Point::new(ONE / 32, ONE / 32);
        terminal.cursor = Point::new(0, ONE / 2);
        let _ = terminal.feed(&mut canvas, &[SI, b'i']);
        // i: one column wide, so it steps 0 + 2 eighths.
        assert_eq!(terminal.cursor.x, ONE / 32 / 8 * 2);
        let _ = terminal.feed(&mut canvas, b"l");
        assert_eq!(terminal.cursor.x, ONE / 32 / 8 * 2 + ONE / 32 / 8 * 6);
        let _ = terminal.feed(&mut canvas, b" ");
        assert_eq!(terminal.cursor.x, ONE / 32 / 8 * 8 + ONE / 32, "a space steps the whole field");
    }
    /// A test font: e (primary 6/5) a box, i one column, l one column at x = 3 (so that a
    /// proportional l's field starts a column before the previous l's stroke), and the acute
    /// accent (supplementary 4/2) a stroke above the field's top grid row.
    const FONT: &str = "[primary]\n30 0 0 1,1,5,8\n65 0 0 1,1,5,1 5,1,5,6 5,6,1,6 1,6,1,1\n69 0 0 3,1,3,6\n6c 0 0 3,1,3,8\n[supplementary]\n42 0 0 2,8,4,9\n";

    fn on_large_canvas(bytes: &[u8]) -> (Terminal, Canvas) {
        let mut canvas = Canvas::new(640, 480).unwrap();
        let mut terminal = Terminal::new(4);
        terminal.set_font(StrokeFont::parse(FONT).unwrap());
        let _ = terminal.feed(&mut canvas, bytes);
        let _ = terminal.finish(&mut canvas);
        (terminal, canvas)
    }

    /// RESET, a 1/16 by 1/10 field (TEXT with `spacing` in its first byte), mode 2 drawing in
    /// entry 7 on entry 12, the cursor at (1/8, 1/4), then `text` in the primary set.
    fn mode_two_text(spacing: u8, text: &[u8]) -> Canvas {
        let mut bytes = vec![
            SO,
            0x20,
            0x7F,
            0x7F,
            0x22,
            0x40 | spacing,
            0x40,
            0x40,
            0x53,
            0x42,
            0x3E,
            0x5C,
            0x70,
            0x24,
            0x41,
            0x60,
            0x40,
            SI,
        ];
        bytes.extend_from_slice(text);
        on_large_canvas(&bytes).1
    }

    #[test]
    fn an_accent_survives_its_letter_in_colour_mode_two() {
        let accented = mode_two_text(0, &[SS2, 0x42, b'e']);
        let plain = mode_two_text(0, b"e");
        assert_ne!(accented.pixels(), plain.pixels(), "the accent was painted over (TODO-5902)");
    }

    #[test]
    fn proportional_text_in_colour_mode_two_keeps_earlier_letters() {
        let all = mode_two_text(0b11_0000, b"lll");
        let ink =
            |canvas: &Canvas| canvas.pixels().iter().fold(0usize, |count, &entry| count + usize::from(entry == 7));
        let one_l = mode_two_text(0b11_0000, b"l");
        // Three l: more ink than two would leave (TODO-5903 left only the last l).
        assert!(ink(&all) > 2 * ink(&one_l), "{} against {}", ink(&all), ink(&one_l));
    }

    #[test]
    fn separated_mosaics_are_reduced_by_the_pel() {
        // A 1/16 by 1/10 field, DOMAIN with a 1/64 pel, a full mosaic block, contiguous then
        // separated (UNDERLINE START).
        let page = |separated: bool| {
            let mut bytes =
                vec![SO, 0x20, 0x7F, 0x7F, 0x21, 0x48, 0x40, 0x40, 0x64, 0x22, 0x40, 0x40, 0x40, 0x53, 0x42];
            bytes.extend_from_slice(&[0x24, 0x41, 0x60, 0x40, SI]);
            if separated {
                bytes.extend_from_slice(&[ESC, 0x59]);
            }
            bytes.extend_from_slice(&[SS3, 0x7F]);
            lit(&on_large_canvas(&bytes).1)
        };
        let (contiguous, separated) = (page(false), page(true));
        // Each block is 1/32 of the screen wide and the pel 1/64, so a lit block keeps about half
        // its width and half its height: about a quarter of the area (a tenth of the field would
        // keep four fifths).
        assert!(separated > 0 && separated * 3 < contiguous, "{separated} of {contiguous}");
    }

    #[test]
    fn line_textures_are_solid_with_the_default_pel() {
        // Section 5.3.2.4.2: with a pel width of zero, nonvertical lines are solid. TEXTURE
        // dotted, then a horizontal line across the screen.
        let (_, canvas, _) = run(&[SO, 0x20, 0x7F, 0x7F, 0x23, 0x41, 0x2A, 0x41, 0x44, 0x40, 0x59, 0x7C, 0x78]);
        let row: Vec<u8> =
            canvas.pixels().chunks(640).find(|row| row.iter().any(|&entry| entry != 0)).unwrap().to_vec();
        let first = row.iter().position(|&entry| entry != 0).unwrap();
        let last = row.iter().rposition(|&entry| entry != 0).unwrap();
        assert!(
            row[first..=last].iter().all(|&entry| entry != 0),
            "a dotted line with the default pel is solid: {row:?}"
        );
    }

    #[test]
    fn reset_sets_the_border() {
        // SELECT COLOR entry 12, then RESET with b6 b5 b4 = 100: the border to the drawing colour.
        let (terminal, _, _) = run(&[SO, 0x3E, 0x70, 0x20, 0x60]);
        assert_eq!(terminal.border(), 12);
        let (terminal, _, _) = run(&[SO, 0x3E, 0x70, 0x20, 0x60, 0x20, 0x58]);
        assert_eq!(terminal.border(), 0, "011: the border to nominal black");
    }

    #[test]
    fn word_wrap_moves_a_word_that_does_not_fit_to_the_next_line() {
        // A 1/8 field: 8 per line. The cursor at column 6, then WORD WRAP ON and "ll ll".
        let mut bytes =
            vec![SO, 0x20, 0x7F, 0x7F, 0x22, 0x40, 0x40, 0x40, 0x63, 0x42, 0x24, 0x5A, 0x40, 0x40, SI, ESC, 0x55];
        bytes.extend_from_slice(b"llll ll");
        let (terminal, _) = on_large_canvas(&bytes);
        // "llll" does not fit in the two columns left, so it starts the next line and "ll" follows
        // a space: the cursor ends 7 columns along the second line.
        let column = ONE / 8;
        assert_eq!(terminal.cursor.x, 7 * column);
        assert!(terminal.cursor.y < ONE / 2, "the word moved down a line");
    }
    #[test]
    fn set_and_line_draws_pairs_of_points() {
        // SET & LINE (absolute) with three points: a line from the first to the second; the third,
        // with no end point after it, only moves the drawing point (section 5.3.3.2.4).
        let (terminal, canvas, _) =
            run(&[SO, 0x20, 0x7F, 0x7F, 0x2A, 0x42, 0x58, 0x50, 0x4A, 0x48, 0x68, 0x58, 0x63, 0x72]);
        let lit_right_of =
            |x: usize| canvas.pixels().chunks(640).any(|row| row.iter().skip(x).any(|&entry| entry != 0));
        assert!(!lit_right_of(240), "no line from the second point to the third");
        assert!(terminal.point.x > ONE / 2, "the drawing point moved to the third point");
    }

    #[test]
    fn an_unknown_designation_makes_a_null_set() {
        // ESC 2/8 7/9 designates an undefined set into G0: its characters are null operations.
        let (_, canvas) = on_large_canvas(&[SO, 0x20, 0x7F, 0x7F, ESC, 0x28, 0x79, SI, b'e']);
        assert_eq!(lit(&canvas), 0);
    }

    #[test]
    fn a_control_cancels_a_single_shift() {
        // SS2, CR, e: the e is the primary set's (section 6.1.3.3), which the test font draws.
        let (_, canvas) = on_large_canvas(&[SO, 0x20, 0x7F, 0x7F, SI, SS2, 0x0D, b'e']);
        assert!(lit(&canvas) > 0);
    }

    #[test]
    fn hatching_with_a_zero_pel_is_solid() {
        // TEXTURE vertical hatching (0x48), a filled rectangle, the default pel (section 5.3.2.4.4).
        let (_, canvas, _) = run(&[SO, 0x20, 0x7F, 0x7F, 0x23, 0x48, 0x33, 0x49, 0x40, 0x40, 0x51, 0x40, 0x40]);
        let row: Vec<u8> =
            canvas.pixels().chunks(640).find(|row| row.iter().any(|&entry| entry != 0)).unwrap().to_vec();
        let lit_row: Vec<u8> =
            row.iter().copied().skip_while(|&entry| entry == 0).take_while(|&entry| entry != 0).collect();
        assert!(lit_row.len() >= 300, "a solid run across the rectangle, not one-pixel bands: {row:?}");
    }

    #[test]
    fn reset_colour_bits_10_select_colour_mode_one() {
        // SELECT COLOR with two operands (mode 2), then RESET byte 1 with b3 b2 = 10.
        let (terminal, _, _) = run(&[SO, 0x3E, 0x70, 0x4C, 0x20, 0x44]);
        assert_eq!(terminal.mode, Mode::Map);
    }

    #[test]
    fn reset_during_a_drcs_download_clears_the_character_being_defined() {
        // DEF DRCS 2/1: a filled rectangle, then RESET clearing the DRCS (byte 2 b6), END; the
        // character, designated into G3 and shown, is blank (section 6.2.3).
        let mut bytes = vec![DEF_DRCS, 0x21, SO, 0x31, 0x5B, 0x7F, 0x7F, 0x20, 0x40, 0x60, END];
        bytes.extend_from_slice(&[ESC, 0x2F, 0x20, 0x7B, SS3, 0x21]);
        let (_, canvas, _) = run(&bytes);
        assert_eq!(lit(&canvas), 0);
    }

    #[test]
    fn field_with_no_operands_moves_the_drawing_point_home() {
        let (terminal, _, _) = run(&[SO, 0x24, 0x52, 0x40, 0x40, 0x38, 0x24]);
        assert_eq!(terminal.point, Point::default());
    }

    #[test]
    fn incremental_polygon_reads_a_modify_after_a_null_toggle() {
        // Moves: dx, dy, then escape 00 00 (a null toggle in a polygon), whose following pair 01
        // reverses dx (section 5.3.3.6.5), then dx (now leftward): a square, not a long sliver.
        let (_, canvas, _) = run(&[
            SO,
            0x20,
            0x7F,
            0x7F,
            0x24,
            0x49,
            0x40,
            0x40,
            0x3B,
            0x40,
            0x64,
            0x40,
            0x40 | 0b01_10_00,
            0x40 | 0b00_01_01,
        ]);
        let rightmost =
            canvas.pixels().chunks(640).filter_map(|row| row.iter().rposition(|&entry| entry != 0)).max().unwrap();
        assert!(rightmost < 300, "rightmost lit column {rightmost}");
    }

    #[test]
    fn nsr_ignores_bytes_from_columns_two_and_three() {
        // NSR followed by two digits: they are ignored, not drawn (section 6.1.6.5 item 6).
        let (_, canvas) = on_large_canvas(&[SO, 0x20, 0x7F, 0x7F, SI, 0x1F, b'0', b'0']);
        assert_eq!(lit(&canvas), 0);
    }

    #[test]
    fn repeat_after_a_control_does_nothing() {
        // e, CR, REPEAT 3: the byte before REPEAT is a control, so REPEAT is a null operation.
        let (_, once) = on_large_canvas(&[SO, 0x20, 0x7F, 0x7F, SI, b'e']);
        let (_, repeated) = on_large_canvas(&[SO, 0x20, 0x7F, 0x7F, SI, b'e', 0x0D, ESC, 0x46, 0x43]);
        assert_eq!(lit(&once), lit(&repeated));
        // Straight after the e, it repeats, and a shift between them does not count.
        let (_, after_e) = on_large_canvas(&[SO, 0x20, 0x7F, 0x7F, SI, b'e', ESC, 0x46, 0x43]);
        assert!(lit(&after_e) > lit(&once));
        let (_, across_so) = on_large_canvas(&[SO, 0x20, 0x7F, 0x7F, SI, b'e', SO, ESC, 0x46, 0x43]);
        assert_eq!(lit(&across_so), lit(&after_e));
    }

    #[test]
    fn blink_start_in_colour_mode_zero_blinks_only_what_follows() {
        // RESET to colour mode 0 (byte 1 b3 b2 = 01), a white rectangle, then BLINK START: the
        // rectangle's entry does not blink (section 6.2.8.1).
        let (terminal, canvas, _) = run(&[SO, 0x20, 0x4A, 0x40, 0x33, 0x49, 0x40, 0x40, 0x49, 0x40, 0x40, ESC, 0x4E]);
        let drawn = *canvas.pixels().iter().find(|&&entry| entry != 0).unwrap();
        assert!(terminal.palette().blinks().iter().all(|blink| blink.from != drawn));
        assert!(terminal.palette().blinks().iter().any(|blink| blink.from == terminal.colour));
    }

    #[test]
    fn dashes_and_their_gaps_are_three_pels() {
        // DOMAIN with a 1/64 pel (ten pixels on this 640-pixel canvas), TEXTURE dashed, a line.
        let (_, canvas, _) = run(&[
            SO, 0x20, 0x7F, 0x7F, 0x21, 0x48, 0x40, 0x40, 0x64, 0x23, 0x42, 0x2A, 0x41, 0x44, 0x40, 0x59, 0x7C, 0x78,
        ]);
        let row: Vec<u8> =
            canvas.pixels().chunks(640).find(|row| row.iter().any(|&entry| entry != 0)).unwrap().to_vec();
        let gap = row.iter().skip(1).skip_while(|&&entry| entry != 0).take_while(|&&entry| entry == 0).count();
        assert_eq!(gap, 30, "three pels: {row:?}");
    }

    #[test]
    fn text_with_a_cross_hair_cursor_aligns_the_drawing_point_to_the_field_centre() {
        // POINT SET, then TEXT choosing the cross-hair cursor (byte 2 b6 b5 = 10).
        let (terminal, _, _) = run(&[SO, 0x24, 0x52, 0x40, 0x40, 0x22, 0x40, 0x60]);
        let half = Point::new(fraction(1, 80), fraction(5, 256));
        assert_eq!(terminal.point, terminal.cursor.plus(half));
    }

    #[test]
    fn incremental_point_outside_the_field_draws_nothing() {
        // FIELD at (1/2, 1/4) of size (1/4, 1/4), then the drawing point moved outside it.
        let (_, canvas, _) = run(&[
            SO, 0x20, 0x7F, 0x7F, 0x38, 0x51, 0x40, 0x40, 0x49, 0x40, 0x40, 0x24, 0x40, 0x5B, 0x52, 0x39, 0x44, 0x7F,
            0x7F, 0x7F,
        ]);
        assert_eq!(lit(&canvas), 0);
    }
    #[test]
    fn outlined_arcs_take_the_line_texture() {
        // DOMAIN with a 1/64 pel, TEXTURE dotted, then a circle (SET & ARC outlined with one
        // step): a dotted circle lights fewer pixels than a solid one.
        let circle = |texture: u8| {
            let mut bytes = vec![SO, 0x20, 0x7F, 0x7F, 0x21, 0x48, 0x40, 0x40, 0x64, 0x23, 0x40 | texture];
            bytes.extend_from_slice(&[0x2E, 0x49, 0x44, 0x46, 0x50, 0x40, 0x40]);
            lit(&run(&bytes).1)
        };
        let (solid, dotted) = (circle(0), circle(1));
        assert!(dotted * 3 < solid * 2, "dotted {dotted} against solid {solid}");
    }
    #[test]
    fn the_cursor_field_stays_inside_the_unit_screen() {
        // POINT SET at x = 0.99: the cursor follows the drawing point, but its 1/40 field may not
        // cross the right edge (section 5.3.2.3.7).
        let (terminal, _, _) = run(&[SO, 0x24, 0x5A, 0x78, 0x68]);
        assert!(terminal.cursor.x.saturating_add(fraction(1, 40)) <= ONE, "{}", terminal.cursor.x);
        assert!(terminal.point.x > terminal.cursor.x, "the drawing point itself is not moved");
    }
    #[test]
    fn a_transmit_macro_is_not_executed_when_called() {
        // DEFT MACRO 2/1 holding a rectangle, then the macro set into G2 and SS2 2/1: nothing is
        // drawn (section 6.2.2.3), and nothing is sent (REQ-5910).
        let mut bytes = vec![ESC, 0x2E, 0x20, 0x7A, 0x82, 0x21, SO];
        bytes.extend_from_slice(&RECT_HALF_QUARTER);
        bytes.extend_from_slice(&[END, SS2, 0x21]);
        let (_, canvas, events) = run(&bytes);
        assert_eq!(lit(&canvas), 0);
        assert_eq!(events, Vec::new());
    }
}
