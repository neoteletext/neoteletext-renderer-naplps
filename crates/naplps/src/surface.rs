//! What drawing lands on: the caller's canvas of colour-map addresses, and the one-bit masks
//! DRCS characters and fill patterns are drawn into (ANSI X3.110-1983 sections 5.6 and 6.2).

use alloc::vec;
use alloc::vec::Vec;

use crate::Error;
use crate::fixed::{Point, scale};
use crate::limits::MAX_CANVAS_SIDE;

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
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Canvas {
    width: u32,
    height: u32,
    pixels: Vec<u8>,
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
        Ok(Self { width, height, pixels: vec![0; count] })
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
    /// Sets a pixel, counted from the top left; outside is ignored.
    fn put(&mut self, x: i32, y: i32, entry: u8);
    /// A pixel's value.
    fn get(&self, x: i32, y: i32) -> Option<u8>;
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
        if x >= self.width || y >= self.height {
            return;
        }
        let index = u64::from(y).saturating_mul(u64::from(self.width)).saturating_add(u64::from(x));
        if let Some(pixel) = usize::try_from(index).ok().and_then(|index| self.pixels.get_mut(index)) {
            *pixel = entry;
        }
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
    let x = scale(i64::from(point.x), xn.saturating_mul(SUBPIXELS), xd.saturating_mul(one));
    let bottom = i64::from(surface.height()).saturating_sub(1).saturating_mul(SUBPIXELS);
    let y = bottom.saturating_sub(scale(i64::from(point.y), yn.saturating_mul(SUBPIXELS), yd.saturating_mul(one)));
    (x, y)
}
