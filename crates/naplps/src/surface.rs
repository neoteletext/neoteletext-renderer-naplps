//! What drawing lands on: the caller's canvas of colour-map addresses, and the one-bit masks
//! DRCS characters and fill patterns are drawn into (ANSI X3.110-1983 sections 5.6 and 6.2).

use alloc::vec;
use alloc::vec::Vec;

use crate::Error;
use crate::fixed::{Point, scale};
use crate::limits::{MAX_CANVAS_SIDE, OBJECT_PICTURE_HEIGHT, OBJECT_PICTURE_WIDTH};

/// Sub-pixel steps per pixel used for fills and arcs.
pub(crate) const SUBPIXELS: i64 = 256;

/// The share of the unit screen's height a display shows: 25/32 = 0.78125, the 256 x 200
/// display of ANSI X3.110-1983 Table D1, and what PP3 shows (its 5/128 text rows are exactly 24
/// of its 480 lines: 480 x 32/25 x 5/128 = 24).
pub const DISPLAY_HEIGHT_NUMERATOR: i64 = 25;
/// See [`DISPLAY_HEIGHT_NUMERATOR`].
pub const DISPLAY_HEIGHT_DENOMINATOR: i64 = 32;

/// A picture of colour-map addresses, row by row from the top left. The unit screen's width
/// spans the canvas's width and the visible 25/32 of its height spans the canvas's height
/// (decision D3).
#[derive(Clone, Debug)]
pub struct Canvas {
    width: u32,
    height: u32,
    pixels: Vec<u8>,
    /// The rectangle holding every pixel whose value changed since [`Canvas::take_written`]
    /// (animation.md ANIM-4): what `Terminal::take_damage` reports.
    written: Option<Rect>,
}

/// Two canvases are equal when they show the same picture; what has been reported of their
/// changes is not part of the picture.
impl PartialEq for Canvas {
    fn eq(&self, other: &Self) -> bool {
        self.width == other.width && self.height == other.height && self.pixels == other.pixels
    }
}

impl Eq for Canvas {}

/// A rectangle of a picture's pixels, counted from the top left; never empty.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Rect {
    /// The leftmost column.
    pub x: u32,
    /// The topmost row.
    pub y: u32,
    /// Columns, at least one.
    pub width: u32,
    /// Rows, at least one.
    pub height: u32,
}

impl Rect {
    /// The rectangle from (`left`, `top`) up to but not including (`right`, `bottom`), cut to a
    /// picture of `width` by `height` pixels; `None` when nothing of it is on the picture.
    #[must_use]
    pub fn cut(left: i64, top: i64, right: i64, bottom: i64, width: u32, height: u32) -> Option<Self> {
        let left = left.max(0);
        let top = top.max(0);
        let right = right.min(i64::from(width));
        let bottom = bottom.min(i64::from(height));
        if left >= right || top >= bottom {
            return None;
        }
        Some(Self {
            x: u32::try_from(left).ok()?,
            y: u32::try_from(top).ok()?,
            width: u32::try_from(right.saturating_sub(left)).ok()?,
            height: u32::try_from(bottom.saturating_sub(top)).ok()?,
        })
    }

    /// The column after the rightmost.
    #[must_use]
    pub fn right(&self) -> u32 {
        self.x.saturating_add(self.width)
    }

    /// The row after the lowest.
    #[must_use]
    pub fn bottom(&self) -> u32 {
        self.y.saturating_add(self.height)
    }

    /// Pixels inside.
    #[must_use]
    pub fn area(&self) -> u64 {
        u64::from(self.width).saturating_mul(u64::from(self.height))
    }

    /// Whether the pixel (`x`, `y`) is inside.
    #[must_use]
    pub fn contains(&self, x: u32, y: u32) -> bool {
        x >= self.x && x < self.right() && y >= self.y && y < self.bottom()
    }

    /// The smallest rectangle holding both.
    #[must_use]
    pub fn union(&self, other: &Self) -> Self {
        let x = self.x.min(other.x);
        let y = self.y.min(other.y);
        Self {
            x,
            y,
            width: self.right().max(other.right()).saturating_sub(x),
            height: self.bottom().max(other.bottom()).saturating_sub(y),
        }
    }

    /// What both hold; `None` when they do not meet.
    #[must_use]
    pub fn intersection(&self, other: &Self) -> Option<Self> {
        let x = self.x.max(other.x);
        let y = self.y.max(other.y);
        let right = self.right().min(other.right());
        let bottom = self.bottom().min(other.bottom());
        (x < right && y < bottom).then(|| Self {
            x,
            y,
            width: right.saturating_sub(x),
            height: bottom.saturating_sub(y),
        })
    }
}

impl Rect {
    /// This rectangle of the design picture (ANIM-11: 640 by 480, the origin at the top left, y
    /// down) on a canvas of `width` by `height`: every canvas pixel whose centre lies in one of
    /// its design pixels, as [`design_pixel`] places a centre. The unit screen spans both
    /// pictures, so the canvas pixels of adjacent design rectangles neither overlap nor leave a
    /// gap: an object's clip never reaches a canvas pixel that belongs to the next row's or
    /// column's cells (TODO-6826), and every canvas pixel whose centre lies inside the
    /// rectangle is kept, so nothing the object draws there is cut. A filled RECTANGLE covers
    /// the pixel its far edge lies in (ANSI X3.110-1983 sections 5.3.3.4.1 and 5.3.2.2.6: the
    /// outline's region traced by the logical pel is filled, and a drawing lights every pixel
    /// its locus lies under), so a fill reaching the next cell's first design line lights a
    /// canvas pixel whose centre is in that cell; the clip cuts it. On a 640 by 480 canvas it
    /// is the rectangle itself; `None` when no canvas pixel's centre lies in it.
    #[must_use]
    pub fn on_canvas(&self, width: u32, height: u32) -> Option<Self> {
        let (design_width, design_height) = (i64::from(OBJECT_PICTURE_WIDTH), i64::from(OBJECT_PICTURE_HEIGHT));
        let (canvas_width, canvas_height) = (i64::from(width), i64::from(height));
        let (left, top) = (i64::from(self.x), i64::from(self.y));
        let (right, bottom) = (i64::from(self.right()), i64::from(self.bottom()));
        // Across: design_pixel puts column c in design column floor((2 c Wd + W) / 2 W), which
        // is at least `edge` exactly when c >= (2 edge - 1) W / 2 Wd; the first column is that
        // rounded up, for the left edge and for the right one after the last.
        let twice_design_width = design_width.saturating_mul(2);
        let column_from = |edge: i64| {
            ceiling(edge.saturating_mul(2).saturating_sub(1).saturating_mul(canvas_width), twice_design_width)
        };
        // Down: design_pixel puts row r in design row floor((2 Hd (r + 1) - H) / 2 H), which is
        // at least `edge` exactly when r + 1 >= (2 edge + 1) H / 2 Hd.
        let twice_design_height = design_height.saturating_mul(2);
        let row_from = |edge: i64| {
            ceiling(edge.saturating_mul(2).saturating_add(1).saturating_mul(canvas_height), twice_design_height)
                .saturating_sub(1)
        };
        Self::cut(column_from(left), row_from(top), column_from(right), row_from(bottom), width, height)
    }
}

/// `value / divisor` rounded up, for a positive divisor.
fn ceiling(value: i64, divisor: i64) -> i64 {
    scale(value.saturating_neg(), 1, divisor).saturating_neg()
}

/// The pixel of the design picture (ANIM-11) the centre of pixel (`x`, `y`) of a canvas of
/// `width` by `height` lies in, rounded as [`pixel_of`] rounds a point: where a point given on
/// the canvas lies in the design picture. On a 640 by 480 canvas it is (`x`, `y`). It may lie
/// past the design picture's right or bottom edge, where no object is. [`Rect::on_canvas`] is
/// exactly the canvas pixels whose design pixel this gives lies in the rectangle, so picking
/// at this design pixel ([`crate::Terminal::objects_at`]) and at the canvas pixel
/// ([`crate::Terminal::objects_on_canvas`]) agree.
#[must_use]
pub fn design_pixel(x: u32, y: u32, width: u32, height: u32) -> (u32, u32) {
    let (design_width, design_height) = (i64::from(OBJECT_PICTURE_WIDTH), i64::from(OBJECT_PICTURE_HEIGHT));
    let (width, height) = (i64::from(width.max(1)), i64::from(height.max(1)));
    // Across: x Wd / W rounded half up, floor((2 x Wd + W) / 2W).
    let across = scale(
        i64::from(x).saturating_mul(2).saturating_mul(design_width).saturating_add(width),
        1,
        width.saturating_mul(2),
    );
    // Down: canvas row r is design row d with (H - 1 - r) / H = (Hd - 1 - d) / Hd, rounded half
    // up: floor((2 Hd (r + 1) - H) / 2H).
    let down = scale(
        i64::from(y).saturating_add(1).saturating_mul(2).saturating_mul(design_height).saturating_sub(height),
        1,
        height.saturating_mul(2),
    );
    let narrow = |value: i64| u32::try_from(value.max(0)).unwrap_or(u32::MAX);
    (narrow(across), narrow(down))
}

/// A displacement of the design picture (ANIM-11) in sub-pixels of a canvas of `width` by
/// `height`, rounded down: what moves an object's drawing by (`across`, `down`) design pixels.
/// Moving in sub-pixels before [`pixel_of`] rounds, rather than in whole canvas pixels after,
/// lands every point where it would land were the macro drawn at the place moved to, so the
/// drawing lies inside the object's rectangle ([`Rect::on_canvas`]) on every canvas as it does on the design picture.
pub(crate) fn design_shift(across: i64, down: i64, width: u32, height: u32) -> (i64, i64) {
    (
        scale(across, i64::from(width).saturating_mul(SUBPIXELS), i64::from(OBJECT_PICTURE_WIDTH)),
        scale(down, i64::from(height).saturating_mul(SUBPIXELS), i64::from(OBJECT_PICTURE_HEIGHT)),
    )
}

/// The union of two rectangles either of which may be absent.
pub(crate) fn join(a: Option<Rect>, b: Option<Rect>) -> Option<Rect> {
    match (a, b) {
        (Some(a), Some(b)) => Some(a.union(&b)),
        (a, b) => a.or(b),
    }
}

impl Canvas {
    /// A canvas filled with colour-map address 0, nominal black.
    ///
    /// # Errors
    ///
    /// [`Error::CanvasSize`] if a side is zero or larger than the limit.
    pub fn new(width: u32, height: u32) -> Result<Self, Error> {
        if width == 0 || height == 0 || width > MAX_CANVAS_SIDE || height > MAX_CANVAS_SIDE {
            return Err(Error::CanvasSize);
        }
        let count =
            usize::try_from(u64::from(width).saturating_mul(u64::from(height))).map_err(|_| Error::CanvasSize)?;
        Ok(Self { width, height, pixels: vec![0; count], written: None })
    }

    /// Width in pixels.
    #[must_use]
    pub fn width(&self) -> u32 {
        self.width
    }

    /// Height in pixels.
    #[must_use]
    pub fn height(&self) -> u32 {
        self.height
    }

    /// The colour-map addresses, row by row from the top left.
    #[must_use]
    pub fn pixels(&self) -> &[u8] {
        &self.pixels
    }

    /// The address at (`x`, `y`), counted from the top left.
    #[must_use]
    pub fn pixel(&self, x: u32, y: u32) -> Option<u8> {
        if x >= self.width || y >= self.height {
            return None;
        }
        let index =
            usize::try_from(u64::from(y).saturating_mul(u64::from(self.width)).saturating_add(u64::from(x))).ok()?;
        self.pixels.get(index).copied()
    }

    /// Fills the whole canvas with one address.
    pub fn clear(&mut self, entry: u8) {
        self.pixels.fill(entry);
        self.written = Some(self.whole());
    }

    /// The whole picture as a rectangle.
    #[must_use]
    pub fn whole(&self) -> Rect {
        Rect { x: 0, y: 0, width: self.width, height: self.height }
    }

    /// The rectangle holding every pixel changed since this was last called, and forgets it.
    pub(crate) fn take_written(&mut self) -> Option<Rect> {
        self.written.take()
    }

    /// Copies `rect` of `source`, a canvas of the same size, onto this one (animation.md
    /// ANIM-12: the damaged rectangle is filled by copying the background's pixels).
    pub(crate) fn copy_from(&mut self, source: &Self, rect: Rect) {
        if self.width != source.width || self.height != source.height {
            return;
        }
        for y in rect.y..rect.bottom().min(self.height) {
            for x in rect.x..rect.right().min(self.width) {
                if let Some(entry) = source.pixel(x, y) {
                    self.set(x, y, entry);
                }
            }
        }
    }

    /// Sets the pixel (`x`, `y`) and notes the change; outside is ignored.
    pub(crate) fn set(&mut self, x: u32, y: u32, entry: u8) {
        if x >= self.width || y >= self.height {
            return;
        }
        let index = u64::from(y).saturating_mul(u64::from(self.width)).saturating_add(u64::from(x));
        if let Some(pixel) = usize::try_from(index).ok().and_then(|index| self.pixels.get_mut(index))
            && *pixel != entry
        {
            *pixel = entry;
            let one = Rect { x, y, width: 1, height: 1 };
            self.written = Some(self.written.map_or(one, |written| written.union(&one)));
        }
    }
}

/// A one-bit picture: a DRCS character's or a fill mask's shape.
#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Mask {
    width: u32,
    height: u32,
    bits: Vec<bool>,
}

impl Mask {
    /// An empty mask; sides are at least one pixel.
    pub(crate) fn new(width: u32, height: u32) -> Self {
        let width = width.clamp(1, MAX_CANVAS_SIDE);
        let height = height.clamp(1, MAX_CANVAS_SIDE);
        let count = usize::try_from(u64::from(width).saturating_mul(u64::from(height))).unwrap_or(0);
        Self { width, height, bits: vec![false; count] }
    }

    /// Whether (`x`, `y`) from the top left is set; false outside.
    pub(crate) fn bit(&self, x: i64, y: i64) -> bool {
        let (Ok(x), Ok(y)) = (u32::try_from(x), u32::try_from(y)) else { return false };
        if x >= self.width || y >= self.height {
            return false;
        }
        let index = u64::from(y).saturating_mul(u64::from(self.width)).saturating_add(u64::from(x));
        usize::try_from(index).ok().and_then(|index| self.bits.get(index)).copied().unwrap_or(false)
    }

    /// Width in pixels.
    pub(crate) fn width(&self) -> u32 {
        self.width
    }

    /// Height in pixels.
    pub(crate) fn height(&self) -> u32 {
        self.height
    }

    /// Clears every bit.
    pub(crate) fn clear(&mut self) {
        self.bits.fill(false);
    }
}

/// Anything drawing can land on.
pub(crate) trait Surface {
    /// Width in pixels.
    fn width(&self) -> i32;
    /// Height in pixels.
    fn height(&self) -> i32;
    /// Pixels per unit along x, as a fraction.
    fn scale_x(&self) -> (i64, i64);
    /// Pixels per unit along y, as a fraction.
    fn scale_y(&self) -> (i64, i64);
    /// Sub-pixels every unit-screen point is moved by before it is rounded to a pixel, across
    /// and down: an object's move (ANIM-11), nothing elsewhere.
    fn subpixel_shift(&self) -> (i64, i64) {
        (0, 0)
    }
    /// Sets a pixel, counted from the top left; outside is ignored.
    fn put(&mut self, x: i32, y: i32, entry: u8);
    /// A pixel's value.
    fn get(&self, x: i32, y: i32) -> Option<u8>;
    /// Pays for `units` of drawing work, the pixels about to be visited, before they are
    /// visited; false when the allowance is spent, and the work is then not done (TODO-6844).
    /// Drawing straight onto a surface is free: a terminal draws through a
    /// [`crate::work::Metered`] one.
    fn spend(&mut self, _units: u64) -> bool {
        true
    }
    /// Whether pixels written are kept. A surface that keeps none (a validator's) is paid for
    /// every pixel a drawing would visit, the same as a canvas of its size, but the drawing
    /// routines pass over the visiting itself.
    fn keeps_pixels(&self) -> bool {
        true
    }
    /// Sets every pixel (clear screen, and RESET's clearing of the display).
    fn fill_all(&mut self, entry: u8) {
        for y in 0..self.height() {
            for x in 0..self.width() {
                self.put(x, y, entry);
            }
        }
    }
}

/// An object's view of the picture it is composed into (animation.md ANIM-11): the whole
/// picture's geometry, every point moved by a translation in sub-pixels and every pixel written
/// only inside a rectangle.
/// It reads nothing back, so that what an object draws never depends on what lies outside the
/// rectangle being repainted, and a damage repaint equals a whole one (ANIM-4).
pub(crate) struct Window<'a> {
    pub(crate) canvas: &'a mut Canvas,
    /// The move across and down, in sub-pixels of the canvas ([`design_shift`]).
    pub(crate) shift: (i64, i64),
    pub(crate) clip: Rect,
}

impl Surface for Window<'_> {
    fn width(&self) -> i32 {
        Surface::width(self.canvas)
    }
    fn height(&self) -> i32 {
        Surface::height(self.canvas)
    }
    fn scale_x(&self) -> (i64, i64) {
        self.canvas.scale_x()
    }
    fn scale_y(&self) -> (i64, i64) {
        self.canvas.scale_y()
    }
    fn subpixel_shift(&self) -> (i64, i64) {
        self.shift
    }
    fn put(&mut self, x: i32, y: i32, entry: u8) {
        let (Ok(x), Ok(y)) = (u32::try_from(x), u32::try_from(y)) else { return };
        if self.clip.contains(x, y) {
            self.canvas.set(x, y, entry);
        }
    }
    fn get(&self, _x: i32, _y: i32) -> Option<u8> {
        None
    }
    fn fill_all(&mut self, entry: u8) {
        // Only the rectangle can be written, so only it is visited: an object's clear screen
        // costs its rectangle and not the picture.
        for y in self.clip.y..self.clip.bottom() {
            for x in self.clip.x..self.clip.right() {
                self.canvas.set(x, y, entry);
            }
        }
    }
}

impl Surface for Canvas {
    fn width(&self) -> i32 {
        i32::try_from(self.width).unwrap_or(i32::MAX)
    }
    fn height(&self) -> i32 {
        i32::try_from(self.height).unwrap_or(i32::MAX)
    }
    fn scale_x(&self) -> (i64, i64) {
        (i64::from(self.width), 1)
    }
    fn scale_y(&self) -> (i64, i64) {
        (i64::from(self.height).saturating_mul(DISPLAY_HEIGHT_DENOMINATOR), DISPLAY_HEIGHT_NUMERATOR)
    }
    fn put(&mut self, x: i32, y: i32, entry: u8) {
        let (Ok(x), Ok(y)) = (u32::try_from(x), u32::try_from(y)) else { return };
        self.set(x, y, entry);
    }
    fn get(&self, x: i32, y: i32) -> Option<u8> {
        self.pixel(u32::try_from(x).ok()?, u32::try_from(y).ok()?)
    }
}

/// A mask as a drawing surface: the unit screen's larger extent fills its larger side; anything
/// drawn in nominal black (address 0) clears, anything else sets (section 5.6, Dillon, DEF DRCS).
pub(crate) struct MaskSurface<'a> {
    pub(crate) mask: &'a mut Mask,
    pub(crate) per_unit: u32,
}

impl Surface for MaskSurface<'_> {
    fn width(&self) -> i32 {
        i32::try_from(self.mask.width).unwrap_or(i32::MAX)
    }
    fn height(&self) -> i32 {
        i32::try_from(self.mask.height).unwrap_or(i32::MAX)
    }
    fn scale_x(&self) -> (i64, i64) {
        (i64::from(self.per_unit), 1)
    }
    fn scale_y(&self) -> (i64, i64) {
        (i64::from(self.per_unit), 1)
    }
    fn put(&mut self, x: i32, y: i32, entry: u8) {
        let (Ok(x), Ok(y)) = (u32::try_from(x), u32::try_from(y)) else { return };
        if x >= self.mask.width || y >= self.mask.height {
            return;
        }
        let index = u64::from(y).saturating_mul(u64::from(self.mask.width)).saturating_add(u64::from(x));
        if let Some(bit) = usize::try_from(index).ok().and_then(|index| self.mask.bits.get_mut(index)) {
            *bit = entry != 0;
        }
    }
    fn get(&self, x: i32, y: i32) -> Option<u8> {
        let x = u32::try_from(x).ok()?;
        let y = u32::try_from(y).ok()?;
        if x >= self.mask.width || y >= self.mask.height {
            return None;
        }
        Some(u8::from(self.mask.bit(i64::from(x), i64::from(y))))
    }
}

/// The pixel nearest a unit-screen point: PP3 rounds coordinates to the nearest pixel (a corner
/// at 0.40771, 0.33350 of a 640 x 480 screen lands on column 261 and line 274, measured against
/// the oracle's captures).
pub(crate) fn pixel_of(surface: &dyn Surface, point: Point) -> (i32, i32) {
    let (x, y) = subpixel_of(surface, point);
    let half = SUBPIXELS / 2;
    let column = x.saturating_add(half).div_euclid(SUBPIXELS);
    let row = y.saturating_add(half).div_euclid(SUBPIXELS);
    (i32::try_from(column).unwrap_or(i32::MAX), i32::try_from(row).unwrap_or(i32::MAX))
}

/// A unit-screen point in sub-pixels from the top left (x right, y down), with pixel (i, j)'s
/// centre at (i, j) x [`SUBPIXELS`].
pub(crate) fn subpixel_of(surface: &dyn Surface, point: Point) -> (i64, i64) {
    let (xn, xd) = surface.scale_x();
    let (yn, yd) = surface.scale_y();
    let one = i64::from(crate::fixed::ONE);
    let (shift_x, shift_y) = surface.subpixel_shift();
    let x = scale(i64::from(point.x), xn.saturating_mul(SUBPIXELS), xd.saturating_mul(one)).saturating_add(shift_x);
    let bottom = i64::from(surface.height()).saturating_sub(1).saturating_mul(SUBPIXELS);
    let y = bottom
        .saturating_sub(scale(i64::from(point.y), yn.saturating_mul(SUBPIXELS), yd.saturating_mul(one)))
        .saturating_add(shift_y);
    (x, y)
}
