//! The object layer over a NAPLPS picture, and the damage both leave (neoteletext-common
//! `docs/animation.md`, ANIM-4, ANIM-6 and ANIM-11 to ANIM-14).
//!
//! ANSI X3.110-1983 keeps no scene: a stream draws on the picture and is forgotten. The one
//! thing it names and retains is the macro (section 6.2.2), so an object's content is a macro,
//! placed by a record outside the stream; no opcode is added and every stream stays conforming.
//! The stream draws on the caller's canvas as before, which is layer 0, the background.
//! [`Terminal::compose`] copies the damaged part of it into a second canvas and draws the
//! objects of layers 1 to 3 over the copy, so a moving object never redraws the stream.

use alloc::string::String;
use alloc::vec::Vec;

use super::{FIRST_CODE, Terminal};
use crate::Error;
use crate::limits::{
    LAYERS, MAX_ANIMATED_OBJECTS, MAX_COMPOSE_WORK, MAX_FRAME_NUMBER, MAX_LABEL_BYTES, MAX_OBJECT_BYTES,
    MAX_OBJECT_FRAMES, MAX_OBJECTS, RASTER_HEIGHT, RASTER_WIDTH,
};
use crate::surface::{Canvas, Rect, Window, join, raster_dot, raster_shift};
use crate::work::Work;

/// The last macro code, 7/15 (section 6.2.2: the 96 macro names are 2/0 to 7/15).
const LAST_CODE: u8 = 0x7F;
/// The lowest layer an object's definition may name: layer 0 is the stream's picture (ANIM-11).
const FIRST_OBJECT_LAYER: u8 = 1;

/// What an object is (ANIM-11, the record's kind byte).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ObjectKind {
    /// Drawn by executing a macro of the stream (kind 1).
    Macro,
    /// A rectangle of the stream's own picture, filled with its cover while hidden (kind 2).
    Region,
}

/// Which look of an object is drawn in place of its frame (ANIM-6: 0 none, 1 hover, 2 pressed,
/// 3 alternative).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Look {
    /// No look: the frame in force.
    #[default]
    Normal,
    /// The hover look.
    Hover,
    /// The pressed look.
    Pressed,
    /// The alternative look.
    Alternative,
}

impl Look {
    /// The look an operation's look byte names (ANIM-6); `None` above 3.
    #[must_use]
    pub fn from_code(code: u8) -> Option<Self> {
        match code {
            0 => Some(Self::Normal),
            1 => Some(Self::Hover),
            2 => Some(Self::Pressed),
            3 => Some(Self::Alternative),
            _ => None,
        }
    }
}

/// One numbered object: the fields of one entry of the `NAPLPS_OBJECTS` record (ANIM-11), which
/// the caller has read. Positions and sizes are in the picture's pixels, the origin at the top
/// left and y down.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Object {
    /// 1 to 65,535, distinct among a sub-page's objects.
    pub number: u16,
    /// A macro object or a region.
    pub kind: ObjectKind,
    /// Flags bit 0.
    pub shown: bool,
    /// Flags bit 1: pointer triggers see it.
    pub detectable: bool,
    /// 1 to 3.
    pub layer: u8,
    /// The order within the layer, lowest drawn first.
    pub order: i8,
    /// The raster dot of the rectangle's left (DEC-6853, `docs/naplps-raster.md` RAS-4: the
    /// 480 by 500 teletext raster, the origin at its top left).
    pub x: i16,
    /// The raster line of the rectangle's top.
    pub y: i16,
    /// Dots across, 1 to 480 ([`crate::limits::RASTER_WIDTH`]): the rectangle is dots `x` to
    /// `x` + `width` − 1.
    pub width: u16,
    /// Lines down, 1 to 500 ([`crate::limits::RASTER_HEIGHT`]): the rectangle is lines `y` to
    /// `y` + `height` − 1.
    pub height: u16,
    /// The raster dot at which the macro, drawn where the stream would draw it, puts what is to
    /// be the rectangle's left; 0 for a region.
    pub origin_x: i16,
    /// The raster line at which the macro puts what is to be the rectangle's top; 0 for a
    /// region.
    pub origin_y: i16,
    /// A region: the colour-map entry that fills it while hidden. A macro object: 0.
    pub cover: u8,
    /// The hover look's macro code, 2/0 to 7/15, or 0 for none.
    pub hover: u8,
    /// The pressed look's macro code, or 0 for none.
    pub pressed: u8,
    /// The alternative look's macro code, or 0 for none.
    pub alternative: u8,
    /// A macro object: 1 to 16 macro codes, one a frame. A region: none.
    pub frames: Vec<u8>,
    /// What a screen reader says for the object (DEC-6638 item 6, row 6.1): plain text of at
    /// most [`MAX_LABEL_BYTES`] bytes, or empty for none. The renderer never draws it; the
    /// caller reads it with [`Terminal::object`] and gives it to the screen-reader tree. It is
    /// not yet in the `NAPLPS_OBJECTS` record, whose engine side carries it later.
    pub label: String,
}

/// The animation state of one object (ANIM-6): each part that is set is used in place of the
/// object's own. It is the receiver's alone; nothing in a stream reads or sets it. A cycle is
/// not here because the renderer has no clock: the caller sets `frame` at each tick a cycle's
/// frame changes (ANIM-14).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Animation {
    /// Shown or hidden.
    pub shown: Option<bool>,
    /// The left and top of the object's rectangle.
    pub position: Option<(i16, i16)>,
    /// The layer, 0 to 3. In layer 0 an object is still drawn over the stream's picture, before
    /// every object of layers 1 to 3.
    pub layer: Option<u8>,
    /// The order within the layer.
    pub order: Option<i8>,
    /// The frame, 0 to 15; one beyond the object's frames shows its last.
    pub frame: Option<u8>,
    /// The forced look; [`Look::Normal`] leaves the look to the pointer.
    pub look: Look,
}

/// The objects, what is known of them, and what has changed.
pub(super) struct Scene {
    objects: Vec<Object>,
    animations: Vec<(u16, Animation)>,
    /// The look the pointer gives each object, which a forced look overrides.
    pointer: Vec<(u16, Look)>,
    /// Pixels of the stream's canvas changed since the damage was last taken or composed.
    stream_damage: Option<Rect>,
    /// Pixels of the composed picture changed since the damage was last taken.
    composed_damage: Option<Rect>,
    /// The part of the composed picture that no longer shows what it should, in the canvas's
    /// pixels: what the stream changed.
    pending: Option<Rect>,
    /// The same for what objects changed, in raster dots (ANIM-11, RAS-4), which only
    /// [`Terminal::compose`]'s canvas turns into its own pixels ([`Rect::on_canvas`]).
    object_pending: Option<Rect>,
    /// Nothing has been composed yet, or the caller asked for everything again.
    whole: bool,
    /// A macro, a DRCS character, a texture or the font changed, so every macro object may
    /// look different.
    pub(super) definitions_changed: bool,
    /// What the last [`Terminal::compose`] spent of [`MAX_COMPOSE_WORK`] (TODO-6844).
    compose_work: Work,
}

impl Default for Scene {
    fn default() -> Self {
        Self {
            objects: Vec::new(),
            animations: Vec::new(),
            pointer: Vec::new(),
            stream_damage: None,
            composed_damage: None,
            pending: None,
            compose_work: Work::with(MAX_COMPOSE_WORK),
            object_pending: None,
            whole: true,
            definitions_changed: false,
        }
    }
}

impl Scene {
    /// The memory the objects, their frames and labels, animation states and pointer looks hold
    /// beyond the structure (TODO-6854).
    pub(super) fn heap_bytes(&self) -> usize {
        let objects = self
            .objects
            .iter()
            .map(|object| {
                crate::limits::vector_bytes(&object.frames).saturating_add(match object.label.capacity() {
                    0 => 0,
                    bytes => crate::limits::held_allocation(bytes),
                })
            })
            .fold(0, usize::saturating_add);
        crate::limits::vector_bytes(&self.objects)
            .saturating_add(objects)
            .saturating_add(crate::limits::vector_bytes(&self.animations))
            .saturating_add(crate::limits::vector_bytes(&self.pointer))
    }

    /// The stream changed these pixels of its canvas.
    pub(super) fn wrote(&mut self, rect: Option<Rect>) {
        self.stream_damage = join(self.stream_damage, rect);
        self.pending = join(self.pending, rect);
    }
}

/// What an object draws as its state stands.
#[derive(Clone, Copy, PartialEq, Eq)]
enum Content {
    Nothing,
    Cover(u8),
    Macro(u8),
}

/// An object as it is to be drawn: its own values with the animation state's in their place.
#[derive(Clone, Copy, PartialEq, Eq)]
struct Placed {
    shown: bool,
    x: i16,
    y: i16,
    layer: u8,
    order: i8,
    content: Content,
    /// Its rectangle, cut to the picture; `None` when none of it is on the picture.
    rect: Option<Rect>,
}

impl Placed {
    /// The pixels it writes.
    fn drawn(&self) -> Option<Rect> {
        if self.content == Content::Nothing { None } else { self.rect }
    }
}

/// Whether `code` is 0 or a macro's code.
fn is_look(code: u8) -> bool {
    code == 0 || (FIRST_CODE..=LAST_CODE).contains(&code)
}

/// Whether an object is one the `NAPLPS_OBJECTS` record can carry (ANIM-11's table).
fn is_valid(object: &Object) -> bool {
    let common = object.number != 0
        && (FIRST_OBJECT_LAYER..LAYERS).contains(&object.layer)
        && (1..=RASTER_WIDTH).contains(&u32::from(object.width))
        && (1..=RASTER_HEIGHT).contains(&u32::from(object.height))
        && is_look(object.hover)
        && is_look(object.pressed)
        && is_look(object.alternative)
        && crate::is_plain_text(&object.label, MAX_LABEL_BYTES);
    let kind = match object.kind {
        ObjectKind::Macro => {
            object.cover == 0
                && (1..=MAX_OBJECT_FRAMES).contains(&object.frames.len())
                && object.frames.iter().all(|code| (FIRST_CODE..=LAST_CODE).contains(code))
        }
        ObjectKind::Region => object.frames.is_empty() && object.origin_x == 0 && object.origin_y == 0,
    };
    common && kind
}

impl Terminal {
    /// Gives the sub-page all its objects, replacing any it had and forgetting every animation
    /// state and pointer look (ANIM-6: a `NAPLPS_OBJECTS` record forgets the state of what it
    /// replaces). An empty slice removes the objects.
    ///
    /// # Errors
    ///
    /// [`Error::TooManyObjects`] above [`MAX_OBJECTS`]; [`Error::Object`] with the index of the
    /// first object the record's format does not allow, or that repeats a number. Nothing is
    /// changed then: a set is taken whole or refused whole (ANIM-16).
    pub fn set_objects(&mut self, objects: &[Object]) -> Result<(), Error> {
        if objects.len() > MAX_OBJECTS {
            return Err(Error::TooManyObjects);
        }
        for (index, object) in objects.iter().enumerate() {
            let repeated = objects.iter().take(index).any(|earlier| earlier.number == object.number);
            if repeated || !is_valid(object) {
                return Err(Error::Object(index));
            }
        }
        self.damage_every_object();
        self.scene.objects = objects.to_vec();
        self.scene.animations.clear();
        self.scene.pointer.clear();
        self.damage_every_object();
        Ok(())
    }

    /// Replaces the definition of one object, the one numbered `object.number`, with `object`,
    /// or adds it when the sub-page has no object of that number, without a new stream and
    /// without touching any other object (DEC-6638 item 3, row 3.2: a whole object redefined by
    /// a record). The object's animation state and pointer look are forgotten, as a set of
    /// objects forgets those of what it replaces (ANIM-6); every other object keeps its own.
    /// What it drew before and what it draws now are repainted by the next
    /// [`Terminal::compose`].
    ///
    /// # Errors
    ///
    /// [`Error::Object`] with index 0 when `object` is not one the `NAPLPS_OBJECTS` record
    /// allows; [`Error::TooManyObjects`] when it would be a new object beyond [`MAX_OBJECTS`].
    /// Nothing is changed then.
    pub fn replace_object(&mut self, mut object: Object) -> Result<(), Error> {
        if !is_valid(&object) {
            return Err(Error::Object(0));
        }
        // The caller's frames and label may have room past their bounds; what is kept holds
        // only their bytes (`MAX_OBJECT_STATE_BYTES`, TODO-6854).
        object.frames.shrink_to_fit();
        object.label.shrink_to_fit();
        let number = object.number;
        let before = self.placed_by_number(number);
        let count = self.scene.objects.len();
        match self.scene.objects.iter_mut().find(|existing| existing.number == number) {
            Some(existing) => *existing = object,
            None if count < MAX_OBJECTS => self.scene.objects.push(object),
            None => return Err(Error::TooManyObjects),
        }
        self.scene.animations.retain(|(of, _)| *of != number);
        self.scene.pointer.retain(|(of, _)| *of != number);
        self.damage_change(before, number);
        Ok(())
    }

    /// The objects, as [`Terminal::set_objects`] took them.
    #[must_use]
    pub fn objects(&self) -> &[Object] {
        &self.scene.objects
    }

    /// Sets the whole animation state of object `number` (ANIM-6). Returns false, changing
    /// nothing, when there is no such object or the state names a layer above 3 or a frame
    /// above 15.
    pub fn set_animation(&mut self, number: u16, animation: Animation) -> bool {
        let in_range = animation.layer.is_none_or(|layer| layer < LAYERS)
            && animation.frame.is_none_or(|frame| frame <= MAX_FRAME_NUMBER);
        if !in_range || self.object(number).is_none() {
            return false;
        }
        let before = self.placed_by_number(number);
        if let Some((_, slot)) = self.scene.animations.iter_mut().find(|(of, _)| *of == number) {
            *slot = animation;
        } else if self.scene.animations.len() < MAX_ANIMATED_OBJECTS {
            self.scene.animations.push((number, animation));
        } else {
            return false;
        }
        self.damage_change(before, number);
        true
    }

    /// Forgets the animation state of object `number`, which is then drawn as its definition
    /// says (ANIM-6, `reset`). Returns false when it had none.
    pub fn clear_animation(&mut self, number: u16) -> bool {
        let before = self.placed_by_number(number);
        let count = self.scene.animations.len();
        self.scene.animations.retain(|(of, _)| *of != number);
        self.damage_change(before, number);
        self.scene.animations.len() != count
    }

    /// The animation state of object `number`, if it has any.
    #[must_use]
    pub fn animation(&self, number: u16) -> Option<Animation> {
        self.scene.animations.iter().find(|(of, _)| *of == number).map(|(_, animation)| *animation)
    }

    /// Sets the look the pointer gives object `number`: hover while the pointer is in it,
    /// pressed while a button is held on it. A forced look of the animation state is drawn
    /// instead while there is one (ANIM-6). Returns false when there is no such object.
    pub fn set_pointer_look(&mut self, number: u16, look: Look) -> bool {
        if self.object(number).is_none() {
            return false;
        }
        let before = self.placed_by_number(number);
        self.scene.pointer.retain(|(of, _)| *of != number);
        if look != Look::Normal {
            self.scene.pointer.push((number, look));
        }
        self.damage_change(before, number);
        true
    }

    /// The bounding rectangle of object `number` as its state stands, in raster dots, cut to the
    /// raster of 480 by 500 (ANIM-13, RAS-4); `None` while it does not exist, is not shown, or
    /// lies wholly outside. Collision and pointer tests are made on these rectangles, never on
    /// pixels. A rectangle reaching rows 0 or 24 keeps those lines, where nothing is drawn.
    #[must_use]
    pub fn bounds(&self, number: u16) -> Option<Rect> {
        let placed = self.placed_by_number(number)?;
        if placed.shown { placed.rect } else { None }
    }

    /// The numbers of the objects a pointer at raster dot (`x`, `y`) is inside, in the order
    /// they are drawn: each object that is shown, detectable and whose bounds hold the dot
    /// (ANIM-11, picking; RAS-4). A dot of rows 0 or 24 picks an object whose bounds reach it.
    /// Nothing else of a NAPLPS picture can be picked.
    #[must_use]
    pub fn objects_at(&self, x: u32, y: u32) -> Vec<u16> {
        self.drawing_order()
            .into_iter()
            .filter(|(object, placed)| {
                object.detectable && placed.shown && placed.rect.is_some_and(|rect| rect.contains(x, y))
            })
            .map(|(object, _)| object.number)
            .collect()
    }

    /// The numbers of the objects a pointer at pixel (`x`, `y`) of a canvas of `width` by
    /// `height`, showing the display area, is inside, in the order they are drawn:
    /// [`Terminal::objects_at`] of the raster dot the canvas pixel's centre lies in
    /// ([`crate::raster_dot`]), so a pointer picks an object exactly where [`Terminal::compose`]
    /// can draw it ([`Rect::on_canvas`]). On the receiver's canvas it is the dot (`x`, `y` + 20).
    #[must_use]
    pub fn objects_on_canvas(&self, x: u32, y: u32, width: u32, height: u32) -> Vec<u16> {
        let (across, down) = raster_dot(x, y, width, height);
        self.objects_at(across, down)
    }

    /// The rectangle of pixels changed since this was last called: on the stream's canvas by
    /// [`Terminal::feed`], [`Terminal::feed_until_wait`] and [`Terminal::finish`], and on the
    /// composed picture by [`Terminal::compose`] (ANIM-4). No pixel outside it differs from
    /// what the caller last had. A caller that composes takes the damage after composing.
    pub fn take_damage(&mut self) -> Option<Rect> {
        join(self.scene.stream_damage.take(), self.scene.composed_damage.take())
    }

    /// Makes the next [`Terminal::compose`] repaint the whole picture: for a caller that
    /// composes into another canvas than before, or that changed either canvas itself.
    pub fn invalidate(&mut self) {
        self.scene.whole = true;
    }

    /// The rectangle [`Terminal::compose`] would repaint on `presented` now, or `None` when the
    /// composed picture is up to date. A caller holding a page to
    /// [`crate::limits::MAX_ANIMATION_PIXELS_PER_TICK`] reads its area before composing; damage
    /// left for a later tick merges into one rectangle (ANIM-16).
    #[must_use]
    pub fn pending(&self, presented: &Canvas) -> Option<Rect> {
        let whole = presented.whole();
        if self.scene.whole {
            return Some(whole);
        }
        let mut objects = self.scene.object_pending;
        if self.scene.definitions_changed {
            for (object, placed) in self.drawing_order() {
                if object.kind == ObjectKind::Macro || matches!(placed.content, Content::Macro(_)) {
                    objects = join(objects, placed.drawn());
                }
            }
        }
        let objects = objects.and_then(|rect| rect.on_canvas(presented.width(), presented.height()));
        join(self.scene.pending, objects).and_then(|rect| rect.intersection(&whole))
    }

    /// Composes the stream's picture, `background`, and the objects into `presented`, a canvas
    /// of the same size, repainting only what changed since the last call (ANIM-11, ANIM-12):
    /// the damaged rectangle is filled from the background, then every object reaching into it
    /// is drawn, clipped to it, in order of layer, order and number. The stream is not drawn
    /// again. An object's rectangle and move are in raster dots (ANIM-11, RAS-4), so it is
    /// clipped to [`Rect::on_canvas`] of its rectangle, nothing on rows 0 and 24, and its
    /// drawing moved by the same distance in the canvas's sub-pixels ([`crate::raster_shift`]). Returns the rectangle of `presented` whose pixels changed, which
    /// [`Terminal::take_damage`] then also reports.
    ///
    /// # Errors
    ///
    /// [`Error::CanvasSize`] when the two canvases differ in size.
    pub fn compose(&mut self, background: &Canvas, presented: &mut Canvas) -> Result<Option<Rect>, Error> {
        if background.width() != presented.width() || background.height() != presented.height() {
            return Err(Error::CanvasSize);
        }
        let Some(area) = self.pending(presented) else { return Ok(None) };
        let whole = core::mem::take(&mut self.scene.whole);
        self.scene.pending = None;
        self.scene.object_pending = None;
        self.scene.definitions_changed = false;
        // What the stream changed is inside the area and reaches the picture by this copy.
        self.scene.stream_damage = None;
        let _ = presented.take_written();
        presented.copy_from(background, area);
        let order: Vec<(Placed, i16, i16)> = self
            .drawing_order()
            .into_iter()
            .map(|(object, placed)| (placed, object.origin_x, object.origin_y))
            .collect();
        let (width, height) = (presented.width(), presented.height());
        // TODO-6844: every object's drawing in this composing is paid for from one allowance,
        // so that a page of many objects whose macros fill the screen costs a bounded time.
        let mut work = Work::with(MAX_COMPOSE_WORK);
        for (placed, origin_x, origin_y) in order {
            let on_canvas = placed.rect.and_then(|rect| rect.on_canvas(width, height));
            let Some(clip) = on_canvas.and_then(|rect| rect.intersection(&area)) else { continue };
            match placed.content {
                Content::Nothing => {}
                Content::Cover(entry) => {
                    if !work.spend(clip.area()) {
                        continue;
                    }
                    for y in clip.y..clip.bottom() {
                        for x in clip.x..clip.right() {
                            presented.set(x, y, entry);
                        }
                    }
                }
                Content::Macro(code) => {
                    // ANIM-11, RAS-4: every point moved by (x - origin x, y - origin y) dots.
                    let across = i64::from(placed.x).saturating_sub(i64::from(origin_x));
                    let down = i64::from(placed.y).saturating_sub(i64::from(origin_y));
                    let shift = raster_shift(across, down, width, height);
                    self.draw_macro(&mut Window { canvas: presented, shift, clip }, code, &mut work);
                }
            }
        }
        self.scene.compose_work = work;
        // A canvas composed into for the first time holds nothing the caller has seen.
        let changed = if whole { Some(area) } else { presented.take_written() };
        let _ = presented.take_written();
        self.scene.composed_damage = join(self.scene.composed_damage, changed);
        Ok(changed)
    }

    /// The pixel work the last [`Terminal::compose`] spent drawing objects, at most
    /// [`MAX_COMPOSE_WORK`], and whether it stopped there with objects left undrawn (TODO-6844).
    /// While a composing stays within its allowance, a picture composed by damage is the
    /// picture composed whole (ANIM-4); one that stopped shows only what was paid for.
    #[must_use]
    pub fn compose_work(&self) -> (u64, bool) {
        (self.scene.compose_work.spent(), self.scene.compose_work.stopped())
    }

    /// Executes macro `code`, as the stream last defined it, onto `window` in a fresh
    /// presentation state (ANIM-11): the state a terminal powers up in, which is the state
    /// after a RESET of every attribute (section 5.3.2.9), sharing the stream's macros, DRCS
    /// characters, textures, font and colour map and changing none of them. Its drawing is
    /// paid for from `work`.
    fn draw_macro(&mut self, window: &mut Window<'_>, code: u8, work: &mut Work) {
        let Some(Some(body)) = self.macros.get(usize::from(code.wrapping_sub(FIRST_CODE))) else { return };
        let body = body.clone();
        let mut state = Self::new(self.palette.bits());
        state.in_object = true;
        self.exchange_definitions(&mut state);
        state.frames.push((body, 0));
        state.work = *work;
        state.run(window, &[], MAX_OBJECT_BYTES, false);
        state.end(window);
        *work = state.work;
        self.exchange_definitions(&mut state);
    }

    /// Lends what a stream defines to the state an object's macro runs in, or takes it back.
    fn exchange_definitions(&mut self, other: &mut Self) {
        core::mem::swap(&mut self.palette, &mut other.palette);
        core::mem::swap(&mut self.font, &mut other.font);
        core::mem::swap(&mut self.teletext_sets, &mut other.teletext_sets);
        core::mem::swap(&mut self.macros, &mut other.macros);
        core::mem::swap(&mut self.drcs, &mut other.drcs);
        core::mem::swap(&mut self.masks, &mut other.masks);
    }

    /// The object numbered `number`.
    #[must_use]
    pub fn object(&self, number: u16) -> Option<&Object> {
        self.scene.objects.iter().find(|object| object.number == number)
    }

    fn placed_by_number(&self, number: u16) -> Option<Placed> {
        self.object(number).map(|object| self.placed(object))
    }

    /// An object with its animation state and looks applied.
    fn placed(&self, object: &Object) -> Placed {
        let animation = self.animation(object.number).unwrap_or_default();
        let shown = animation.shown.unwrap_or(object.shown);
        let (x, y) = animation.position.unwrap_or((object.x, object.y));
        let pointer =
            self.scene.pointer.iter().find(|(of, _)| *of == object.number).map_or(Look::Normal, |(_, look)| *look);
        let look = if animation.look == Look::Normal { pointer } else { animation.look };
        let look_code = match look {
            Look::Normal => 0,
            Look::Hover => object.hover,
            Look::Pressed => object.pressed,
            Look::Alternative => object.alternative,
        };
        let content = match object.kind {
            // A hidden region is its cover; a shown one is the stream's picture, or its look.
            ObjectKind::Region if !shown => Content::Cover(object.cover),
            _ if !shown => Content::Nothing,
            _ if look_code != 0 => Content::Macro(look_code),
            ObjectKind::Region => Content::Nothing,
            ObjectKind::Macro => {
                // ANIM-14: a frame number beyond an object's frames shows its last.
                let frame = usize::from(animation.frame.unwrap_or(0)).min(object.frames.len().saturating_sub(1));
                object.frames.get(frame).map_or(Content::Nothing, |code| Content::Macro(*code))
            }
        };
        let (left, top) = (i64::from(x), i64::from(y));
        let rect = Rect::cut(
            left,
            top,
            left.saturating_add(i64::from(object.width)),
            top.saturating_add(i64::from(object.height)),
            RASTER_WIDTH,
            RASTER_HEIGHT,
        );
        Placed {
            shown,
            x,
            y,
            layer: animation.layer.unwrap_or(object.layer),
            order: animation.order.unwrap_or(object.order),
            content,
            rect,
        }
    }

    /// Every object with its state applied, in drawing order: layer, then order, then number
    /// (ANIM-12).
    fn drawing_order(&self) -> Vec<(&Object, Placed)> {
        let mut order: Vec<(&Object, Placed)> =
            self.scene.objects.iter().map(|object| (object, self.placed(object))).collect();
        order.sort_by_key(|(object, placed)| (placed.layer, placed.order, object.number));
        order
    }

    /// Notes for repainting what object `number` wrote before a change and what it writes now.
    fn damage_change(&mut self, before: Option<Placed>, number: u16) {
        let after = self.placed_by_number(number);
        if before == after {
            return;
        }
        for placed in [before, after].into_iter().flatten() {
            self.scene.object_pending = join(self.scene.object_pending, placed.drawn());
        }
    }

    fn damage_every_object(&mut self) {
        let drawn = self.drawing_order().into_iter().fold(None, |all, (_, placed)| join(all, placed.drawn()));
        self.scene.object_pending = join(self.scene.object_pending, drawn);
    }
}
