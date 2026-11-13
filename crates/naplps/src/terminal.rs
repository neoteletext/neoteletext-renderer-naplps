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
        }
    }

    /// Uses `font` for the primary and supplementary sets (decision D5).
    pub fn set_font(&mut self, font: StrokeFont) {
        self.font = Some(font);
    }

    /// The colour map.
    #[must_use]
    pub fn palette(&self) -> &Palette {
        &self.palette
    }

    /// Processes bytes onto `canvas`, returning what the caller may act on.
    pub fn feed(&mut self, canvas: &mut Canvas, bytes: &[u8]) -> Vec<Event> {
        self.display_top =
            fraction(crate::surface::DISPLAY_HEIGHT_NUMERATOR, crate::surface::DISPLAY_HEIGHT_DENOMINATOR);
        if !self.started {
            // Power-up: the text cursor at the home position; the drawing point stays at (0, 0).
            self.started = true;
            self.cursor = self.home_position();
        }
        self.processed = 0;
        let mut frames: Vec<(Vec<u8>, usize)> = Vec::new();
        let mut position = 0;
        loop {
            if self.processed >= MAX_PROCESSED_BYTES {
                self.event(Event::LimitReached);
                break;
            }
            let (byte, depth) = if let Some((bytes, at)) = frames.last_mut() {
                let Some(byte) = bytes.get(*at).copied() else {
                    frames.pop();
                    continue;
                };
                *at = at.saturating_add(1);
                (byte, frames.len())
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
            if let Some(number) = self.byte(canvas, byte, depth)
                && frames.len() < MAX_MACRO_DEPTH
                && let Some(Some(body)) = self.macros.get(usize::from(number.wrapping_sub(FIRST_CODE)))
            {
                frames.push((body.clone(), 0));
            }
            if self.cancel {
                self.cancel = false;
                frames.clear();
            }
        }
        core::mem::take(&mut self.events)
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
        core::mem::take(&mut self.events)
    }

    fn event(&mut self, event: Event) {
        if self.events.len() < MAX_EVENTS {
            self.events.push(event);
        }
    }

    /// One byte. Returns a macro number to expand.
    fn byte(&mut self, canvas: &mut Canvas, byte: u8, depth: usize) -> Option<u8> {
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

    fn dispatch(&mut self, canvas: &mut Canvas, byte: u8) -> Option<u8> {
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
                if (0x40..=0x7F).contains(&byte) {
                    match first {
                        None => self.pending = Pending::Nsr(Some(byte)),
                        Some(row) => self.nsr_position(row, byte),
                    }
                    return None;
                }
                if let Some(row) = first {
                    let _ = self.dispatch(canvas, row);
                }
            }
            Pending::Repeat => {
                let count = byte & 0x7F;
                if (0x40..=0x7F).contains(&count) {
                    self.repeat(canvas, u32::from(count & DATA_MASK));
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
                self.flush(canvas);
                self.control1(canvas, byte);
                None
            }
            _ => {
                let gr = byte >= 0xA0;
                let code = byte & 0x7F;
                let set_index = if gr { self.gr } else { self.single_shift.take().unwrap_or(self.gl) };
                let set = self.g_sets.get(set_index).copied().unwrap_or(CharSet::Primary);
                self.auto_wrapped = 0;
                self.graphic(canvas, set, code)
            }
        }
    }

    fn graphic(&mut self, canvas: &mut Canvas, set: CharSet, code: u8) -> Option<u8> {
        match set {
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

    fn control0(&mut self, canvas: &mut Canvas, byte: u8) {
        // Section 6.1: these belong to other layers and neither act nor end a PDI.
        if matches!(byte, 0x00..=0x06 | 0x10..=0x17) {
            return;
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
                    _ => canvas.clear(entry),
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

    fn escape(&mut self, canvas: &mut Canvas, collected: &mut Vec<u8>, byte: u8) -> Option<u8> {
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
            _ => None,
        };
        if let (Some(target), Some(set)) = (target, set)
            && let Some(slot) = self.g_sets.get_mut(target)
        {
            *slot = set;
        }
        None
    }

    fn control1(&mut self, canvas: &mut Canvas, code: u8) {
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
            0x86 => self.pending = Pending::Repeat,
            0x87 => self.repeat_to_end(canvas),
            0x88 => self.text.reverse = true,
            0x89 => self.text.reverse = false,
            0x8A => self.text.size = Point::new(fraction(1, 80), fraction(5, 128)),
            0x8B => self.text.size = Point::new(fraction(1, 32), fraction(3, 64)),
            0x8C => self.text.size = Point::new(fraction(1, 40), fraction(5, 128)),
            0x8D => self.text.size = Point::new(fraction(1, 40), fraction(5, 64)),
            0x8E => {
                let to = if self.mode == Mode::MapWithBackground { self.background } else { self.palette.black() };
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
        match self.recording.take()? {
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
                let _ = transmit; // stored like any macro; never transmitted (decision D7)
                if let Some(slot) = self.macros.get_mut(index) {
                    *slot = if bytes.is_empty() || others.saturating_add(bytes.len()) > MAX_ALL_MACRO_BYTES {
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
    fn flush(&mut self, canvas: &mut Canvas) {
        let Some((opcode, data)) = self.pdi.take() else { return };
        let mut recording = self.recording.take();
        match &mut recording {
            Some(Recording::Drcs { mask, per_unit, .. } | Recording::Texture { mask, per_unit, .. }) => {
                let mut surface = MaskSurface { mask, per_unit: *per_unit };
                self.pdi_on(&mut surface, opcode, &data);
            }
            _ => self.pdi_on(canvas, opcode, &data),
        }
        if self.recording.is_none() {
            self.recording = recording;
        }
        if matches!(self.text.motion, Motion::Together | Motion::PointLeads) {
            self.cursor = self.point;
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
            0x28..=0x2B => {
                if opcode >= 0x2A {
                    let Some(start) = reader.point(domain) else { return };
                    self.point = start;
                }
                let relative = opcode & 1 == 1;
                while let Some(value) = reader.point(domain) {
                    let end = if relative { self.point.plus(value) } else { value };
                    raster::line(surface, &self.style(), self.point, end, self.colour, false);
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
                if let Some((origin, _)) = self.field {
                    self.point = origin;
                }
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
                self.event(Event::Wait(tenths));
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
            0b10 if self.mode != Mode::Direct => self.palette.reset(),
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
            for y in 0..surface.height() {
                for x in 0..surface.width() {
                    surface.put(x, y, entry);
                }
            }
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
        if second & 0b1_0000 != 0 {
            self.macros.fill(None);
        }
        if second & 0b10_0000 != 0 {
            self.drcs.fill(None);
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
                    self.colour = self.palette.allocate(colour);
                }
            }
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
                self.palette.mark_used(self.colour);
            }
            (Some((value, width)), Some((back, back_width))) => {
                self.mode = Mode::MapWithBackground;
                let drawing = self.palette.entry_from_operand(value, width);
                let background = self.palette.entry_from_operand(back, back_width);
                if drawing != background {
                    self.colour = drawing;
                }
                self.background = background;
                self.palette.mark_used(drawing);
                self.palette.mark_used(background);
            }
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
        let (xn, xd) = surface.scale_x();
        let (yn, yd) = surface.scale_y();
        let one = i64::from(ONE);
        let smallest_x = Unit::try_from(one.saturating_mul(xd) / xn.max(1)).unwrap_or(1).max(1);
        let smallest_y = Unit::try_from(one.saturating_mul(yd) / yn.max(1)).unwrap_or(1).max(1);
        let pel_x = if self.pel.x == 0 { smallest_x } else { self.pel.x };
        let pel_y = if self.pel.y == 0 { smallest_y } else { self.pel.y };
        let start = self.point;
        let mut at = start;
        let mut bits: Vec<bool> = Vec::new();
        while let Some(byte) = reader.byte() {
            for bit in (0..6).rev() {
                bits.push(byte & (1 << bit) != 0);
            }
        }
        let mut style = self.style();
        style.pel = Point::new(pel_x, pel_y);
        for chunk in bits.chunks(usize::try_from(packing).unwrap_or(1)) {
            if chunk.len() < usize::try_from(packing).unwrap_or(1) {
                break;
            }
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
                            if !filled {
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
            self.point = self.cursor;
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
    fn line_feed(&mut self, canvas: &mut Canvas, down: bool) {
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
    fn scroll(&mut self, canvas: &mut Canvas, area: (Unit, Unit, Unit, Unit), step: Point) {
        let top_left = pixel_of(canvas, Point::new(area.0, area.3));
        let bottom_right = pixel_of(canvas, Point::new(area.2, area.1));
        let (xn, xd) = Surface::scale_x(canvas);
        let (yn, yd) = Surface::scale_y(canvas);
        let shift_x = crate::fixed::to_pixels_at(step.x, xn, xd);
        let shift_y = crate::fixed::to_pixels_at(step.y, yn, yd);
        let blank = if self.mode == Mode::MapWithBackground { self.background } else { self.palette.black() };
        let (x0, y0) = (top_left.0.max(0), top_left.1.max(0));
        let (x1, y1) =
            (bottom_right.0.min(Surface::width(canvas) - 1), bottom_right.1.min(Surface::height(canvas) - 1));
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

    fn backspace(&mut self, canvas: &mut Canvas) {
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

    fn forward(&mut self, canvas: &mut Canvas) {
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
    fn advance(&mut self, canvas: &mut Canvas, step: Point) {
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
    fn character(&mut self, canvas: &mut Canvas, set: CharSet, code: u8) {
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
    fn end_word(&mut self, canvas: &mut Canvas, space: bool) {
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
    fn settle(&mut self, canvas: &mut Canvas) {
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
    fn draw_character(&mut self, canvas: &mut Canvas, set: CharSet, code: u8) {
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
    fn settle_accent(&mut self, canvas: &mut Canvas) {
        if let Some(accent) = self.pending_accent.take() {
            let field = self.field_now(self.cursor);
            let ink = self.ink(0);
            self.paint(canvas, CharSet::Supplementary, accent, field, ink);
        }
    }

    /// Draws one character's shape into `field`, on the definition being recorded if any.
    fn paint(&mut self, canvas: &mut Canvas, set: CharSet, code: u8, field: Field, ink: Ink) {
        let underline = |surface: &dyn Surface, terminal: &Self| {
            terminal.text.underline.then(|| text::underline_share(surface, terminal.pel.y, terminal.text.size.y))
        };
        let mut recording = self.recording.take();
        {
            let surface: &mut dyn Surface = match &mut recording {
                Some(Recording::Drcs { mask, per_unit, .. } | Recording::Texture { mask, per_unit, .. }) => {
                    &mut MaskSurface { mask, per_unit: *per_unit }
                }
                _ => canvas,
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
                CharSet::Pdi | CharSet::Macro => {}
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

    fn repeat(&mut self, canvas: &mut Canvas, count: u32) {
        let Some((set, code)) = self.last_spacing else { return };
        for _ in 0..count {
            self.character(canvas, set, code);
        }
    }

    fn repeat_to_end(&mut self, canvas: &mut Canvas) {
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
    const FONT: &str = "[primary]\n65 0 0 1,1,5,1 5,1,5,6 5,6,1,6 1,6,1,1\n69 0 0 3,1,3,6\n6c 0 0 3,1,3,8\n[supplementary]\n42 0 0 2,8,4,9\n";

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
        let row: Vec<u8> = canvas.pixels().chunks(64).find(|row| row.iter().any(|&entry| entry != 0)).unwrap().to_vec();
        assert!(!row.contains(&0), "a dotted line with the default pel is solid: {row:?}");
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
}
