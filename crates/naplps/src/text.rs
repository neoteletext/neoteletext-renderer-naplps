//! Drawing one character into its character field (ANSI X3.110-1983 sections 5.3.2.3, 5.4, 5.6
//! and 6.2).
//!
//! The field is a rectangle of the character field's size with its origin, the lower left
//! corner at rotation 0, at the cursor; rotation turns it counterclockwise about that origin and
//! a negative width or height mirrors the pattern inside it (section 5.3.2.3.2, 5.3.2.3.9). Every
//! character is first turned into a coverage map over the field's pixels, then composited:
//! covered pixels in the drawing colour; in colour mode 2 the rest of the field in the background
//! colour; reverse video draws the uncovered pixels instead, or swaps the colours in mode 2
//! (Dillon, REVERSE VIDEO).

use alloc::vec;
use alloc::vec::Vec;

use crate::fixed::{Point, Unit};
use crate::surface::{Mask, SUBPIXELS, Surface, subpixel_of};

/// Where a stroke glyph's 7 x 10 grid sits in the field: grid x at x/8 of the width and grid y
/// at y/10 of the height from the field's bottom, drawn with a square pen about 1/12 of the
/// field's height that extends right and up from each point, as the logical pel does. Fitted to
/// PP3's drawing of its font at the default field (16 x 24 pixels; 75 % pixel agreement over the
/// 94 primary glyphs, the best of the mappings tried). PP3 scales its font differently at large
/// sizes (a 195 x 288 field puts grid columns 16 pixels apart, not 24), which this does not
/// reproduce.
pub(crate) const STROKE_X_DIVISOR: i64 = 8;
/// See [`STROKE_X_DIVISOR`].
const STROKE_Y_DIVISOR: i64 = 10;
/// See [`STROKE_X_DIVISOR`]: the pen's side as a share of the field height.
const PEN_DIVISOR: i64 = 12;
/// Fraction precision of field coordinates.
pub(crate) const FIELD_ONE: i64 = 1 << 16;

/// What fills a character field.
pub(crate) enum Shape<'a> {
    /// Nothing: a space.
    Blank,
    /// A stroke glyph's segments on the 7 x 10 grid.
    Strokes(&'a [[u8; 4]]),
    /// A DRCS character's bitmap, scaled to the field.
    Bitmap(&'a Mask),
    /// A glyph of a NeoTeletext character set (REQ-6668): rows from the top, the most
    /// significant of `width` bits the leftmost pixel, scaled to the field as a DRCS bitmap is.
    Glyph { rows: &'a [u16], width: u8 },
    /// A mosaic character's code (section 5.4): bits 1 to 5 and 7 are the six blocks. In
    /// separated mode, how much each lit block is reduced across and up, in fractions of
    /// [`FIELD_ONE`] of the field.
    Mosaic { code: u8, separation: Option<(i64, i64)> },
}

/// One character's placement.
#[derive(Clone, Copy, Debug)]
pub(crate) struct Field {
    /// The origin: lower left at rotation 0.
    pub(crate) origin: Point,
    /// Width and height, signed.
    pub(crate) size: Point,
    /// Quarter turns counterclockwise, 0 to 3.
    pub(crate) rotation: u8,
}

impl Field {
    /// The field's width and height directions in unit-screen terms after rotation.
    pub(crate) fn axes(&self) -> (Point, Point) {
        let width = self.size.x.saturating_abs();
        let height = self.size.y.saturating_abs();
        match self.rotation & 3 {
            0 => (Point::new(width, 0), Point::new(0, height)),
            1 => (Point::new(0, width), Point::new(height.saturating_neg(), 0)),
            2 => (Point::new(width.saturating_neg(), 0), Point::new(0, height.saturating_neg())),
            _ => (Point::new(0, width.saturating_neg()), Point::new(height, 0)),
        }
    }

    /// The field's extent along x and y on the screen after rotation.
    pub(crate) fn extent(&self) -> (Unit, Unit) {
        let width = self.size.x.saturating_abs();
        let height = self.size.y.saturating_abs();
        if self.rotation & 1 == 0 { (width, height) } else { (height, width) }
    }
}

/// How the character is coloured.
#[derive(Clone, Copy, Debug)]
pub(crate) struct Ink {
    pub(crate) colour: u8,
    /// The background colour in colour mode 2.
    pub(crate) background: Option<u8>,
    pub(crate) reverse: bool,
    /// Underline height in field fractions of [`FIELD_ONE`], zero for none.
    pub(crate) underline: Option<Unit>,
    /// Where along the field's width, in fractions of [`FIELD_ONE`], painting the field itself
    /// (the background in colour mode 2, the field in reverse video) begins: 0 for the whole
    /// field. A proportionally spaced glyph's field starts before the cursor, over the previous
    /// character, so its field is painted from the cursor on (section 5.3.2.3.4: the character
    /// field's width does not change, and the background fills it); [`FIELD_ONE`] paints only
    /// the strokes, as for an accent drawn over its letter.
    pub(crate) field_from: i64,
}

/// Draws one character.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry inside one character field: coordinates within 2^27 sub-pixels, field fractions within 2^16, products within i64"
)]
pub(crate) fn draw(surface: &mut dyn Surface, field: Field, shape: &Shape<'_>, ink: Ink) {
    let (u_axis, v_axis) = field.axes();
    let origin = subpixel_of(surface, field.origin);
    let u_end = subpixel_of(surface, field.origin.plus(u_axis));
    let v_end = subpixel_of(surface, field.origin.plus(v_axis));
    let u_vector = (u_end.0 - origin.0, u_end.1 - origin.1);
    let v_vector = (v_end.0 - origin.0, v_end.1 - origin.1);
    let corners = [origin, u_end, v_end, (u_end.0 + v_vector.0, u_end.1 + v_vector.1)];
    let left = corners.iter().map(|c| c.0).min().unwrap_or(0).div_euclid(SUBPIXELS).max(0);
    let right =
        (corners.iter().map(|c| c.0).max().unwrap_or(0).div_euclid(SUBPIXELS) + 1).min(i64::from(surface.width()) - 1);
    let top = corners.iter().map(|c| c.1).min().unwrap_or(0).div_euclid(SUBPIXELS).max(0);
    let bottom =
        (corners.iter().map(|c| c.1).max().unwrap_or(0).div_euclid(SUBPIXELS) + 1).min(i64::from(surface.height()) - 1);
    if left > right || top > bottom {
        return;
    }
    let box_width = usize::try_from(right - left + 1).unwrap_or(0);
    let box_height = usize::try_from(bottom - top + 1).unwrap_or(0);
    let strokes = match shape {
        Shape::Strokes(segments) => {
            let frame = Frame { origin, u_vector, v_vector, left, top, right, bottom, box_width, box_height };
            stroke_coverage(&frame, field, segments)
        }
        _ => Vec::new(),
    };
    let u_length = u_vector.0 * u_vector.0 + u_vector.1 * u_vector.1;
    let v_length = v_vector.0 * v_vector.0 + v_vector.1 * v_vector.1;
    if u_length == 0 || v_length == 0 {
        return;
    }
    let half = 0; // pixel centres sit on whole multiples of SUBPIXELS
    // A glyph is sampled at the middle of each pixel's share of the field: the field's corner
    // lies on a pixel centre, so the pixels' own centres fall on the edges between glyph rows
    // and columns, where an error of one sub-pixel in the field's size would take the row
    // below or the column to the left. Half a pixel in field fractions along each axis (the
    // axes are along x or y at every rotation, so a length is the sum of the components).
    let half_u = FIELD_ONE * SUBPIXELS / (2 * (u_vector.0.abs() + u_vector.1.abs())).max(1);
    let half_v = FIELD_ONE * SUBPIXELS / (2 * (v_vector.0.abs() + v_vector.1.abs())).max(1);
    for row in top..=bottom {
        for column in left..=right {
            let offset = (column * SUBPIXELS + half - origin.0, row * SUBPIXELS + half - origin.1);
            let u = (offset.0 * u_vector.0 + offset.1 * u_vector.1) * FIELD_ONE / u_length;
            let v = (offset.0 * v_vector.0 + offset.1 * v_vector.1) * FIELD_ONE / v_length;
            if !(0..FIELD_ONE).contains(&u) || !(0..FIELD_ONE).contains(&v) {
                continue;
            }
            let (mu, mv) = (
                if field.size.x < 0 { FIELD_ONE - 1 - u } else { u },
                if field.size.y < 0 { FIELD_ONE - 1 - v } else { v },
            );
            let mut covered = match shape {
                Shape::Blank => false,
                Shape::Strokes(_) => {
                    let index = usize::try_from(row - top).unwrap_or(0) * box_width
                        + usize::try_from(column - left).unwrap_or(0);
                    strokes.get(index).copied().unwrap_or(false)
                }
                Shape::Bitmap(mask) => {
                    let mask_x = mu * i64::from(mask.width()) / FIELD_ONE;
                    let mask_y = i64::from(mask.height()) - 1 - mv * i64::from(mask.height()) / FIELD_ONE;
                    mask.bit(mask_x, mask_y)
                }
                Shape::Glyph { rows, width } => {
                    let width = i64::from(*width);
                    let height = i64::try_from(rows.len()).unwrap_or(0);
                    let glyph_x = ((mu + half_u) * width / FIELD_ONE).min(width - 1);
                    let glyph_y = height - 1 - ((mv + half_v) * height / FIELD_ONE).min(height - 1);
                    let row = usize::try_from(glyph_y).ok().and_then(|y| rows.get(y)).copied().unwrap_or(0);
                    u32::try_from(width - 1 - glyph_x).is_ok_and(|shift| (u32::from(row) >> shift) & 1 != 0)
                }
                Shape::Mosaic { code, separation } => mosaic(*code, mu, mv, *separation),
            };
            if let Some(height) = ink.underline
                && v < i64::from(height)
            {
                covered = true;
            }
            // Normal: the shape in the drawing colour, the rest of the field in the background
            // (mode 2 only). Reverse: the other way round; in modes 0 and 1 that leaves the shape
            // undrawn and fills the rest in the drawing colour.
            let stroke = covered && !ink.reverse;
            if !stroke && u < ink.field_from {
                continue;
            }
            let entry = match (ink.reverse, covered) {
                (false, true) | (true, false) => Some(ink.colour),
                (false, false) | (true, true) => ink.background,
            };
            if let Some(entry) = entry {
                surface.put(i32::try_from(column).unwrap_or(0), i32::try_from(row).unwrap_or(0), entry);
            }
        }
    }
}

/// Whether a mosaic block covers field position (`u`, `v`) (section 5.4): the field is cut into
/// two columns and three rows; bits 1 and 2 are the top row, 3 and 4 the middle, 5 and 7 the
/// bottom. In separated mode each lit block is reduced across by the logical pel's width and up
/// by its height, kept against the block's left and bottom edges (section 5.4: "left and bottom
/// justified within the normal element area"); a pel as large as the block leaves nothing lit.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry inside one character field: coordinates within 2^27 sub-pixels, field fractions within 2^16, products within i64"
)]
fn mosaic(code: u8, u: i64, v: i64, separation: Option<(i64, i64)>) -> bool {
    let column = i64::from(u * 2 >= FIELD_ONE);
    let row_from_bottom = (v * 3 / FIELD_ONE).clamp(0, 2);
    if let Some((across, up)) = separation {
        let right = (column + 1) * FIELD_ONE / 2;
        let top = (row_from_bottom + 1) * FIELD_ONE / 3;
        if u >= right - across || v >= top - up {
            return false;
        }
    }
    let bit = match (2 - row_from_bottom, column) {
        (0, 0) => 0x01,
        (0, _) => 0x02,
        (1, 0) => 0x04,
        (1, _) => 0x08,
        (_, 0) => 0x10,
        _ => 0x40,
    };
    code & bit != 0
}

/// How much separated mosaics reduce each block, across and up, in fractions of [`FIELD_ONE`] of
/// a field of `size`: the logical pel, or one pixel where the pel is the default, zero size
/// (section 5.3.2.2: the smallest the display can show).
#[allow(
    clippy::arithmetic_side_effects,
    reason = "unit lengths below 2^31 and field fractions within 2^16: products within i64, divisors checked"
)]
pub(crate) fn separation(surface: &dyn Surface, pel: Point, size: Point) -> (i64, i64) {
    let one = i64::from(crate::fixed::ONE);
    let (xn, xd) = surface.scale_x();
    let (yn, yd) = surface.scale_y();
    let pixel_x = (one * xd + xn - 1) / xn.max(1);
    let pixel_y = (one * yd + yn - 1) / yn.max(1);
    let across = i64::from(pel.x.saturating_abs()).max(pixel_x);
    let up = i64::from(pel.y.saturating_abs()).max(pixel_y);
    let width = i64::from(size.x.saturating_abs()).max(1);
    let height = i64::from(size.y.saturating_abs()).max(1);
    ((across * FIELD_ONE / width).min(FIELD_ONE), (up * FIELD_ONE / height).min(FIELD_ONE))
}

/// The underline's height as a share of the field ([`FIELD_ONE`] is the whole field): one pel
/// (Dillon, UNDERLINE START), at least one pixel.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry inside one character field: coordinates within 2^27 sub-pixels, field fractions within 2^16, products within i64"
)]
pub(crate) fn underline_share(surface: &dyn Surface, pel_height: Unit, field_height: Unit) -> Unit {
    let field = i64::from(field_height.saturating_abs()).max(1);
    let (yn, yd) = surface.scale_y();
    let one_pixel = i64::from(crate::fixed::ONE).saturating_mul(yd) / yn.max(1);
    let pel = i64::from(pel_height.saturating_abs()).max(one_pixel);
    Unit::try_from((pel * FIELD_ONE / field).min(FIELD_ONE)).unwrap_or(0)
}

/// Where a character's field lands in pixels, and the box of pixels it covers.
struct Frame {
    origin: (i64, i64),
    u_vector: (i64, i64),
    v_vector: (i64, i64),
    left: i64,
    top: i64,
    right: i64,
    bottom: i64,
    box_width: usize,
    box_height: usize,
}

/// The pixels a stroke glyph covers within the frame's box, row by row.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry inside one character field: coordinates within 2^27 sub-pixels, field fractions within 2^16, products within i64"
)]
fn stroke_coverage(frame: &Frame, field: Field, segments: &[[u8; 4]]) -> Vec<bool> {
    let Frame { origin, u_vector, v_vector, left, top, right, bottom, box_width, box_height } = *frame;
    let mut strokes = vec![false; box_width.saturating_mul(box_height)];
    let field_height = (v_vector.0.abs() + v_vector.1.abs()) / SUBPIXELS;
    let pen = ((field_height + PEN_DIVISOR / 2) / PEN_DIVISOR).max(1);
    let place = |gx: u8, gy: u8| {
        let mut u = i64::from(gx) * FIELD_ONE / STROKE_X_DIVISOR;
        let mut v = i64::from(gy) * FIELD_ONE / STROKE_Y_DIVISOR;
        if field.size.x < 0 {
            u = FIELD_ONE - u;
        }
        if field.size.y < 0 {
            v = FIELD_ONE - v;
        }
        let x = origin.0 + (u_vector.0 * u + v_vector.0 * v) / FIELD_ONE;
        let y = origin.1 + (u_vector.1 * u + v_vector.1 * v) / FIELD_ONE;
        ((x + SUBPIXELS / 2).div_euclid(SUBPIXELS), (y + SUBPIXELS / 2).div_euclid(SUBPIXELS))
    };
    for segment in segments {
        let [x1, y1, x2, y2] = *segment;
        let (ax, ay) = place(x1, y1);
        let (bx, by) = place(x2, y2);
        let steps = (bx - ax).abs().max((by - ay).abs()).max(1);
        for step in 0..=steps {
            let x = ax + (bx - ax) * step / steps;
            let y = ay + (by - ay) * step / steps;
            // A square pen extending right and up from the stroke, as the logical pel does.
            for dy in -(pen - 1)..=0 {
                for dx in 0..pen {
                    let (px, py) = (x + dx - left, y + dy - top);
                    if px >= 0 && py >= 0 && px <= right - left && py <= bottom - top {
                        let index = usize::try_from(py).unwrap_or(0) * box_width + usize::try_from(px).unwrap_or(0);
                        if let Some(cell) = strokes.get_mut(index) {
                            *cell = true;
                        }
                    }
                }
            }
        }
    }
    strokes
}
