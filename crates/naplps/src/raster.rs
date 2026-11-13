//! Drawing primitives: the logical pel as a brush, line textures, fills and arcs (ANSI
//! X3.110-1983 sections 5.3.2.2.6, 5.3.2.4 and 5.3.3).

use alloc::vec::Vec;

use crate::fixed::{Point, to_pixels_up_at};
use crate::limits::MAX_VERTICES;
use crate::surface::{Mask, SUBPIXELS, Surface, pixel_of, subpixel_of};

/// Line textures (section 5.3.2.4.2).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum LineTexture {
    /// Solid, the default.
    #[default]
    Solid,
    /// One pel on, one off.
    Dotted,
    /// Three pels on, three off (section 5.3.2.4.2: the dash and the inter-dash spacing are
    /// three pels).
    Dashed,
    /// Three on, one off, one on, one off.
    DotDash,
}

/// Fill patterns (section 5.3.2.4.4).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum FillPattern {
    /// Solid, the default.
    #[default]
    Solid,
    /// Vertical lines one pel wide, one pel apart.
    Vertical,
    /// Horizontal lines one pel high, one pel apart.
    Horizontal,
    /// Both.
    Cross,
    /// Programmable mask A to D (0 to 3).
    Mask(u8),
}

/// The attributes drawing uses.
#[derive(Clone, Copy, Debug)]
pub(crate) struct Style {
    /// The drawing colour's address.
    pub(crate) colour: u8,
    /// The background colour's address in colour mode 2.
    pub(crate) background: Option<u8>,
    /// Nominal black's address.
    pub(crate) black: u8,
    /// The logical pel, signed (section 5.3.2.2.6).
    pub(crate) pel: Point,
    pub(crate) line: LineTexture,
    pub(crate) fill: FillPattern,
    /// Whether filled objects are outlined (highlight, section 5.3.2.4.3).
    pub(crate) highlight: bool,
    /// The programmable mask size (section 5.3.2.4.5).
    pub(crate) mask_size: Point,
}

/// The four programmable masks.
pub(crate) type Masks = [Option<Mask>; 4];

/// Pel width and height in pixels: rounded up, at least one (section 5.3.2.2.6).
fn pel_pixels(surface: &dyn Surface, pel: Point) -> (i32, i32) {
    let (xn, xd) = surface.scale_x();
    let (yn, yd) = surface.scale_y();
    let width = to_pixels_up_at(pel.x, xn, xd).max(1);
    let height = to_pixels_up_at(pel.y, yn, yd).max(1);
    (width, height)
}

/// Hatch band width and height in pixels: the pel rounded to the nearest pixel, at least one.
/// PP3's cross-hatching with a 1/256 pel on a 640 x 480 screen has bands 3 pixels wide (2.5
/// rounded) and 2 high (2.4 rounded), registered from the left edge and the bottom line, matching
/// its every pixel; the brush itself rounds up.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn hatch_pixels(surface: &dyn Surface, pel: Point) -> (i32, i32) {
    let (xn, xd) = surface.scale_x();
    let (yn, yd) = surface.scale_y();
    let one = i64::from(crate::fixed::ONE);
    let round = |length: i64, numerator: i64, denominator: i64| {
        let whole = denominator.saturating_mul(one).max(1);
        let pixels = length.saturating_abs().saturating_mul(numerator).saturating_add(whole / 2) / whole;
        i32::try_from(pixels.max(1)).unwrap_or(1)
    };
    (round(i64::from(pel.x), xn, xd), round(i64::from(pel.y), yn, yd))
}

/// Stamps the logical pel whose drawing point is at pixel (`x`, `y`): it extends right for a
/// positive width and left for a negative one, up for a positive height and down for a negative
/// one, so the drawing point is the pel's corner named by the signs.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
pub(crate) fn stamp(surface: &mut dyn Surface, style: &Style, x: i32, y: i32, entry: u8) {
    let (width, height) = pel_pixels(surface, style.pel);
    let (x0, x1) = if style.pel.x >= 0 { (x, x.saturating_add(width - 1)) } else { (x.saturating_sub(width - 1), x) };
    let (y0, y1) = if style.pel.y >= 0 { (y.saturating_sub(height - 1), y) } else { (y, y.saturating_add(height - 1)) };
    let (x0, x1) = (x0.max(0), x1.min(surface.width().saturating_sub(1)));
    let (y0, y1) = (y0.max(0), y1.min(surface.height().saturating_sub(1)));
    for row in y0..=y1 {
        for column in x0..=x1 {
            surface.put(column, row, entry);
        }
    }
}

/// A point: one logical pel in the drawing colour (section 5.3.3.1).
pub(crate) fn point(surface: &mut dyn Surface, style: &Style, at: Point) {
    let (x, y) = pixel_of(surface, at);
    stamp(surface, style, x, y, style.colour);
}

/// Whether the pel is stamped at step `index` of a textured line; `unit` is the pel's length
/// along the line in pixels. Each stamp covers `unit` pixels, so a run of n pels is stamped at
/// its first n x unit - (unit - 1) steps: a dot and the space after it are one pel each, a dash
/// and the space after it three pels each, and dot-dash is a dash, a space, a dot and a space
/// (section 5.3.2.4.2, Table 12).
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn texture_on(texture: LineTexture, index: i64, unit: i64) -> bool {
    let unit = unit.max(1);
    let run = |pels: i64| pels * unit - (unit - 1);
    match texture {
        LineTexture::Solid => true,
        LineTexture::Dotted => index % (2 * unit) < run(1),
        LineTexture::Dashed => index % (6 * unit) < run(3),
        LineTexture::DotDash => {
            let at = index % (6 * unit);
            at < run(3) || (4 * unit..4 * unit + run(1)).contains(&at)
        }
    }
}

/// A line from `from` to `to` with the pel as brush and the line texture; gaps take the
/// background colour in colour mode 2 and are left alone otherwise; both ends are always drawn
/// (section 5.3.2.4.2). `solid` forces a solid line (outlines of filled objects).
pub(crate) fn line(surface: &mut dyn Surface, style: &Style, from: Point, to: Point, entry: u8, solid: bool) {
    let (x0, y0) = pixel_of(surface, from);
    let (x1, y1) = pixel_of(surface, to);
    let dx = i64::from(x1).saturating_sub(i64::from(x0));
    let dy = i64::from(y1).saturating_sub(i64::from(y0));
    let steps = dx.abs().max(dy.abs());
    let (pel_w, pel_h) = pel_pixels(surface, style.pel);
    // Section 5.3.2.4.2: "If logical pel size dx = 0, all nonvertical lines are solid. If logical
    // pel size dy = 0, all nonhorizontal lines are solid."
    let x_major = dx.abs() >= dy.abs();
    let textured =
        !solid && style.line != LineTexture::Solid && if x_major { style.pel.x != 0 } else { style.pel.y != 0 };
    let unit = i64::from(if x_major { pel_w } else { pel_h });
    for index in 0..=steps {
        let x = i64::from(x0).saturating_add(super_div(dx.saturating_mul(index), steps));
        let y = i64::from(y0).saturating_add(super_div(dy.saturating_mul(index), steps));
        let (x, y) = (clamp_i32(x), clamp_i32(y));
        let end = index == 0 || index == steps;
        if !textured || end || texture_on(style.line, index, unit) {
            stamp(surface, style, x, y, entry);
        } else if let Some(background) = style.background {
            stamp(surface, style, x, y, background);
        }
    }
}

/// `numerator / denominator` rounded to nearest, zero for a zero denominator.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn super_div(numerator: i64, denominator: i64) -> i64 {
    if denominator == 0 {
        return 0;
    }
    let half = denominator.abs() / 2;
    let adjusted = if numerator >= 0 { numerator.saturating_add(half) } else { numerator.saturating_sub(half) };
    adjusted / denominator
}

fn clamp_i32(value: i64) -> i32 {
    i32::try_from(value.clamp(i64::from(i32::MIN), i64::from(i32::MAX))).unwrap_or(0)
}

/// Lines through the points in order; `closed` joins the last to the first.
pub(crate) fn polyline(
    surface: &mut dyn Surface,
    style: &Style,
    points: &[Point],
    closed: bool,
    entry: u8,
    solid: bool,
) {
    for pair in points.windows(2) {
        if let [a, b] = pair {
            line(surface, style, *a, *b, entry, solid);
        }
    }
    if closed
        && points.len() > 2
        && let (Some(first), Some(last)) = (points.first(), points.last())
    {
        line(surface, style, *last, *first, entry, solid);
    }
}

/// The colour a fill gives the pixel at (`x`, `y`), if any (section 5.3.2.4.4): hatching is one
/// pel wide and one pel apart, registered to the screen origin; a mask is scaled to the mask size
/// and tiled from the origin; mask bits that are clear, and hatching gaps, take the background
/// colour in mode 2 and are left alone otherwise.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
pub(crate) fn fill_colour(surface: &dyn Surface, style: &Style, masks: &Masks, x: i32, y: i32) -> Option<u8> {
    let (pel_w, pel_h) = hatch_pixels(surface, style.pel);
    let from_bottom = surface.height().saturating_sub(1).saturating_sub(y);
    // Section 5.3.2.4.4: "if the logical pel size is (0,0), solid texture patterns will always be
    // drawn" for the predefined patterns.
    let zero_pel = style.pel.x == 0 && style.pel.y == 0;
    let on = match style.fill {
        FillPattern::Solid => true,
        FillPattern::Vertical | FillPattern::Horizontal | FillPattern::Cross if zero_pel => true,
        FillPattern::Vertical => (x / pel_w) % 2 == 0,
        FillPattern::Horizontal => (from_bottom / pel_h) % 2 == 0,
        FillPattern::Cross => (x / pel_w) % 2 == 0 || (from_bottom / pel_h) % 2 == 0,
        FillPattern::Mask(index) => {
            let Some(Some(mask)) = masks.get(usize::from(index)) else {
                return style.background;
            };
            let (xn, xd) = surface.scale_x();
            let (yn, yd) = surface.scale_y();
            let width = i64::from(to_pixels_up_at(style.mask_size.x, xn, xd).max(1));
            let height = i64::from(to_pixels_up_at(style.mask_size.y, yn, yd).max(1));
            let mut mx = i64::from(x).rem_euclid(width);
            let mut my = i64::from(from_bottom).rem_euclid(height);
            if style.mask_size.x < 0 {
                mx = width - 1 - mx;
            }
            if style.mask_size.y < 0 {
                my = height - 1 - my;
            }
            let bx = mx.saturating_mul(i64::from(mask.width())) / width;
            let by = i64::from(mask.height()) - 1 - my.saturating_mul(i64::from(mask.height())) / height;
            mask.bit(bx, by)
        }
    };
    if on { Some(style.colour) } else { style.background }
}

/// The outline colour of a filled object: black in modes 0 and 1, the background in mode 2
/// (Dillon, TEXTURE).
pub(crate) fn outline_colour(style: &Style) -> u8 {
    style.background.unwrap_or(style.black)
}

/// A filled polygon by the even-odd rule at pixel centres, then its outline if highlighting.
pub(crate) fn polygon_filled(surface: &mut dyn Surface, style: &Style, masks: &Masks, points: &[Point]) {
    let points = points.get(..points.len().min(MAX_VERTICES)).unwrap_or(&[]);
    let vertices: Vec<(i64, i64)> = points.iter().map(|point| subpixel_of(surface, *point)).collect();
    fill_scanlines(surface, style, masks, &vertices, &|_, _| true);
    // PP3 strokes a filled object's edge with the logical pel in the fill's own colours, so a
    // fill reaches pel - 1 pixels further right and up (a 3-pixel pel: filled rectangles end 3
    // pixels right of and above the corner's pixel, measured against the oracle's captures).
    fill_edge(surface, style, masks, points, true);
    if style.highlight {
        polyline(surface, style, points, true, outline_colour(style), true);
    }
}

/// Strokes the edge through `points` with the pel, each pixel in the fill's colour there.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn fill_edge(surface: &mut dyn Surface, style: &Style, masks: &Masks, points: &[Point], closed: bool) {
    let count = points.len();
    let segments = if closed { count } else { count.saturating_sub(1) };
    for index in 0..segments {
        let (Some(from), Some(to)) = (points.get(index), points.get((index + 1) % count.max(1))) else { continue };
        let (x0, y0) = pixel_of(surface, *from);
        let (x1, y1) = pixel_of(surface, *to);
        let dx = i64::from(x1) - i64::from(x0);
        let dy = i64::from(y1) - i64::from(y0);
        let steps = dx.abs().max(dy.abs());
        for step in 0..=steps {
            let x = clamp_i32(i64::from(x0) + super_div(dx * step, steps));
            let y = clamp_i32(i64::from(y0) + super_div(dy * step, steps));
            stamp_fill(surface, style, masks, x, y);
        }
    }
}

/// Stamps the pel at a pixel with the fill's colour at each covered pixel.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn stamp_fill(surface: &mut dyn Surface, style: &Style, masks: &Masks, x: i32, y: i32) {
    let (width, height) = pel_pixels(surface, style.pel);
    let (x0, x1) = if style.pel.x >= 0 { (x, x.saturating_add(width - 1)) } else { (x.saturating_sub(width - 1), x) };
    let (y0, y1) = if style.pel.y >= 0 { (y.saturating_sub(height - 1), y) } else { (y, y.saturating_add(height - 1)) };
    for row in y0.max(0)..=y1.min(surface.height() - 1) {
        for column in x0.max(0)..=x1.min(surface.width() - 1) {
            if let Some(entry) = fill_colour(surface, style, masks, column, row) {
                surface.put(column, row, entry);
            }
        }
    }
}

/// Fills the even-odd interior of `vertices` (sub-pixels), restricted by `keep`.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn fill_scanlines(
    surface: &mut dyn Surface,
    style: &Style,
    masks: &Masks,
    vertices: &[(i64, i64)],
    keep: &dyn Fn(i64, i64) -> bool,
) {
    if vertices.len() < 3 {
        return;
    }
    let top = vertices.iter().map(|v| v.1).min().unwrap_or(0).div_euclid(SUBPIXELS);
    let bottom = vertices.iter().map(|v| v.1).max().unwrap_or(0).div_euclid(SUBPIXELS).saturating_add(1);
    let top = i32::try_from(top.max(0)).unwrap_or(0);
    let bottom = i32::try_from(bottom.min(i64::from(surface.height()) - 1)).unwrap_or(0);
    let half = 0; // pixel centres sit on whole multiples of SUBPIXELS
    let mut crossings: Vec<i64> = Vec::new();
    for row in top..=bottom {
        let centre = i64::from(row) * SUBPIXELS + half;
        crossings.clear();
        for (index, start) in vertices.iter().enumerate() {
            let end = vertices.get((index + 1) % vertices.len()).unwrap_or(start);
            let (x0, y0) = *start;
            let (x1, y1) = *end;
            if (y0 <= centre && centre < y1) || (y1 <= centre && centre < y0) {
                let x = x0 + (x1 - x0).saturating_mul(centre - y0) / (y1 - y0);
                crossings.push(x);
            }
        }
        crossings.sort_unstable();
        for pair in crossings.chunks(2) {
            if let [left, right] = pair {
                let first = (left + SUBPIXELS - 1).div_euclid(SUBPIXELS).max(0);
                let last = (right - 1).div_euclid(SUBPIXELS).min(i64::from(surface.width()) - 1);
                for column in first..=last {
                    let x = i32::try_from(column).unwrap_or(0);
                    if keep(column * SUBPIXELS + half, centre)
                        && let Some(entry) = fill_colour(surface, style, masks, x, row)
                    {
                        surface.put(x, row, entry);
                    }
                }
            }
        }
    }
}

/// The circle through three unit-screen points: centre and radius in units; `None` if collinear.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn circle(a: Point, b: Point, c: Point) -> Option<(Point, i64)> {
    let (ax, ay) = (i128::from(a.x), i128::from(a.y));
    let (bx, by) = (i128::from(b.x), i128::from(b.y));
    let (cx, cy) = (i128::from(c.x), i128::from(c.y));
    let d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by));
    if d == 0 {
        return None;
    }
    let a2 = ax * ax + ay * ay;
    let b2 = bx * bx + by * by;
    let c2 = cx * cx + cy * cy;
    let ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d;
    let uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d;
    let radius = isqrt((ax - ux) * (ax - ux) + (ay - uy) * (ay - uy));
    Some((Point::new(i32::try_from(ux).ok()?, i32::try_from(uy).ok()?), i64::try_from(radius).ok()?))
}

/// Integer square root, rounded down.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn isqrt(value: i128) -> i128 {
    if value <= 0 {
        return 0;
    }
    let mut x = value;
    let mut y = (x + 1) / 2;
    while y < x {
        x = y;
        y = i128::midpoint(x, value / x);
    }
    x
}

/// Which side of the line from `a` to `c` a point lies on: the sign of the cross product.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
fn side(a: (i64, i64), c: (i64, i64), q: (i64, i64)) -> i128 {
    let cross = i128::from(c.0 - a.0) * i128::from(q.1 - a.1) - i128::from(c.1 - a.1) * i128::from(q.0 - a.0);
    cross.signum()
}

/// A circle on the unit screen as an ellipse in sub-pixels: the two axes scale differently
/// (the unit screen's width spans the canvas, 25/32 of its height spans the canvas's height), so
/// a circle on the unit screen is wider than tall in pixels, as PP3 draws it (a circle of
/// diameter 0.35 is 225 pixels wide and 217 high on its 640 x 480 screen).
struct Ellipse {
    centre: (i64, i64),
    rx: i64,
    ry: i64,
}

impl Ellipse {
    #[allow(
        clippy::arithmetic_side_effects,
        reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
    )]
    fn new(surface: &dyn Surface, centre: Point, radius: i64) -> Self {
        let (xn, xd) = surface.scale_x();
        let (yn, yd) = surface.scale_y();
        let one = i64::from(crate::fixed::ONE);
        let rx = crate::fixed::scale(radius, xn * SUBPIXELS, xd * one);
        let ry = crate::fixed::scale(radius, yn * SUBPIXELS, yd * one);
        // Whole pixels, as PP3 draws: the centre rounded to the nearest pixel and each radius
        // truncated (a radius of 111.9 pixels draws 111; measured against the oracle's circles).
        let (x, y) = subpixel_of(surface, centre);
        let round = |value: i64| value.saturating_add(SUBPIXELS / 2).div_euclid(SUBPIXELS).saturating_mul(SUBPIXELS);
        let whole = |value: i64| value.div_euclid(SUBPIXELS).max(1).saturating_mul(SUBPIXELS);
        Self { centre: (round(x), round(y)), rx: whole(rx), ry: whole(ry) }
    }

    /// Whether a sub-pixel position is inside or on the ellipse.
    #[allow(
        clippy::arithmetic_side_effects,
        reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
    )]
    fn contains(&self, q: (i64, i64)) -> bool {
        let dx = i128::from(q.0 - self.centre.0) * i128::from(self.ry);
        let dy = i128::from(q.1 - self.centre.1) * i128::from(self.rx);
        let r = i128::from(self.rx) * i128::from(self.ry);
        dx * dx + dy * dy <= r * r
    }

    /// The outline's pixels: for each column the top and bottom rows, and for each row the left
    /// and right columns, so the outline is connected at every slope.
    #[allow(
        clippy::arithmetic_side_effects,
        reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
    )]
    fn pixels(&self) -> Vec<(i64, i64)> {
        let mut pixels = Vec::new();
        let (cx, cy) = self.centre;
        let rx2 = i128::from(self.rx) * i128::from(self.rx);
        let ry2 = i128::from(self.ry) * i128::from(self.ry);
        let round = |value: i64| value.saturating_add(SUBPIXELS / 2).div_euclid(SUBPIXELS);
        let first = (cx - self.rx).div_euclid(SUBPIXELS);
        let last = (cx + self.rx).div_euclid(SUBPIXELS) + 1;
        for column in first..=last {
            let dx = i128::from(column * SUBPIXELS - cx);
            if dx * dx > rx2 {
                continue;
            }
            let dy = isqrt(ry2 - dx * dx * ry2 / rx2.max(1));
            let dy = i64::try_from(dy).unwrap_or(0);
            pixels.push((column, round(cy - dy)));
            pixels.push((column, round(cy + dy)));
        }
        let first = (cy - self.ry).div_euclid(SUBPIXELS);
        let last = (cy + self.ry).div_euclid(SUBPIXELS) + 1;
        for row in first..=last {
            let dy = i128::from(row * SUBPIXELS - cy);
            if dy * dy > ry2 {
                continue;
            }
            let dx = isqrt(rx2 - dy * dy * rx2 / ry2.max(1));
            let dx = i64::try_from(dx).unwrap_or(0);
            pixels.push((round(cx - dx), row));
            pixels.push((round(cx + dx), row));
        }
        pixels
    }
}

/// An arc from `start` through `middle` to `end` (section 5.3.3.3): the points of the circle
/// on `middle`'s side of the chord. `end` equal to `start` draws the whole circle with `start`
/// and `middle` as a diameter; collinear points draw a line from `start` to `end`. Filled, the
/// area between arc and chord is filled and the edge stroked; highlighting outlines the curve.
#[allow(
    clippy::arithmetic_side_effects,
    reason = "pixel geometry: unit coordinates are at most 2^31 in Q8.24, so pixels and sub-pixels stay within 2^27 and their products within i64; circle construction uses i128; no operation here can overflow"
)]
pub(crate) fn arc(
    surface: &mut dyn Surface,
    style: &Style,
    masks: &Masks,
    start: Point,
    middle: Point,
    end: Point,
    filled: bool,
) {
    let full = start == end;
    let geometry = if full {
        let centre = Point::new(
            i32::try_from(i64::midpoint(i64::from(start.x), i64::from(middle.x))).unwrap_or(0),
            i32::try_from(i64::midpoint(i64::from(start.y), i64::from(middle.y))).unwrap_or(0),
        );
        let dx = i128::from(start.x) - i128::from(centre.x);
        let dy = i128::from(start.y) - i128::from(centre.y);
        i64::try_from(isqrt(dx * dx + dy * dy)).ok().map(|radius| (centre, radius))
    } else {
        circle(start, middle, end)
    };
    let Some((centre, radius)) = geometry else {
        line(surface, style, start, end, style.colour, false);
        return;
    };
    let ellipse = Ellipse::new(surface, centre, radius);
    let first = subpixel_of(surface, start);
    let through = subpixel_of(surface, middle);
    let last = subpixel_of(surface, end);
    let wanted = side(first, last, through);
    let on_arc = |point: (i64, i64)| full || side(first, last, point) == wanted;
    if filled {
        let top = ((ellipse.centre.1 - ellipse.ry).div_euclid(SUBPIXELS)).max(0);
        let bottom = ((ellipse.centre.1 + ellipse.ry).div_euclid(SUBPIXELS) + 1).min(i64::from(surface.height()) - 1);
        let left = ((ellipse.centre.0 - ellipse.rx).div_euclid(SUBPIXELS)).max(0);
        let right = ((ellipse.centre.0 + ellipse.rx).div_euclid(SUBPIXELS) + 1).min(i64::from(surface.width()) - 1);
        for row in top..=bottom {
            for column in left..=right {
                let centre = (column * SUBPIXELS, row * SUBPIXELS);
                if ellipse.contains(centre) && on_arc(centre) {
                    let (x, y) = (i32::try_from(column).unwrap_or(0), i32::try_from(row).unwrap_or(0));
                    if let Some(entry) = fill_colour(surface, style, masks, x, y) {
                        surface.put(x, y, entry);
                    }
                }
            }
        }
        for (x, y) in ellipse.pixels() {
            if on_arc((x * SUBPIXELS, y * SUBPIXELS)) {
                stamp_fill(surface, style, masks, clamp_i32(x), clamp_i32(y));
            }
        }
        if !full {
            fill_edge(surface, style, masks, &[start, end], false);
        }
        if style.highlight {
            for (x, y) in ellipse.pixels() {
                if on_arc((x * SUBPIXELS, y * SUBPIXELS)) {
                    stamp(surface, style, clamp_i32(x), clamp_i32(y), outline_colour(style));
                }
            }
        }
    } else {
        for (x, y) in ellipse.pixels() {
            if on_arc((x * SUBPIXELS, y * SUBPIXELS)) {
                stamp(surface, style, clamp_i32(x), clamp_i32(y), style.colour);
            }
        }
    }
}

/// A rectangle with its drawing-point corner at `at` and signed size (section 5.3.3.4).
pub(crate) fn rectangle(surface: &mut dyn Surface, style: &Style, masks: &Masks, at: Point, size: Point, filled: bool) {
    let corners = [
        at,
        Point::new(at.x.saturating_add(size.x), at.y),
        at.plus(size),
        Point::new(at.x, at.y.saturating_add(size.y)),
    ];
    if filled {
        polygon_filled(surface, style, masks, &corners);
    } else {
        polyline(surface, style, &corners, true, style.colour, false);
    }
}
