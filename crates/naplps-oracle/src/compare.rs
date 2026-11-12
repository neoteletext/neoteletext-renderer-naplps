//! Judging a rendered frame against a reference frame.
//!
//! ANSI X3.110-1983 section 8.3.4 lets a decoder approximate: line widths, the edges of fills,
//! fonts and the mapping of the unit screen onto a display's pixels may all differ between two
//! conforming decoders. So the comparison never demands identical pixels. It asks whether every
//! colour one frame has at a place, the other frame also has close by: a pixel whose colour is
//! nowhere within `displacement` pixels in the other frame is *unexplained*, and only unexplained
//! pixels fail. A shape drawn one pixel wider or shifted by one pixel passes at a displacement of
//! one; a missing shape, a wrong colour or a shape in the wrong place does not.

use crate::error::Error;
use crate::frame::{CHANNELS, Frame};

/// How closely two frames must agree.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Tolerance {
    /// The largest difference in any one colour channel at which two pixels still count as the
    /// same colour: 0 against a lossless reference, more against a JPEG one.
    pub channel: u8,
    /// How far a colour may be displaced, in pixels in any direction (Chebyshev distance), and
    /// still explain the other frame's pixel.
    pub displacement: u32,
}

/// What a comparison found.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Comparison {
    /// Pixels in each frame.
    pub pixels: u64,
    /// Pixels whose colours differ beyond the channel tolerance at the same place.
    pub differing: u64,
    /// Candidate pixels whose colour the reference has nowhere within the displacement.
    pub unexplained_in_candidate: u64,
    /// Reference pixels whose colour the candidate has nowhere within the displacement.
    pub unexplained_in_reference: u64,
}

impl Comparison {
    /// Whether the frames agree within the tolerance: no pixel of either is unexplained.
    #[must_use]
    pub fn passes(&self) -> bool {
        self.unexplained_in_candidate == 0 && self.unexplained_in_reference == 0
    }
}

/// Compares a candidate frame with a reference frame of the same size.
///
/// # Errors
///
/// [`Error::Frame`] if the frames differ in size.
pub fn compare(reference: &Frame, candidate: &Frame, tolerance: Tolerance) -> Result<Comparison, Error> {
    if (reference.width(), reference.height()) != (candidate.width(), candidate.height()) {
        return Err(Error::Frame(format!(
            "the reference is {} x {} but the candidate is {} x {}",
            reference.width(),
            reference.height(),
            candidate.width(),
            candidate.height()
        )));
    }
    let mut result = Comparison {
        pixels: u64::from(reference.width()).saturating_mul(u64::from(reference.height())),
        differing: 0,
        unexplained_in_candidate: 0,
        unexplained_in_reference: 0,
    };
    for y in 0..reference.height() {
        for x in 0..reference.width() {
            let (Some(expected), Some(actual)) = (reference.pixel(x, y), candidate.pixel(x, y)) else {
                continue;
            };
            if same_colour(expected, actual, tolerance.channel) {
                continue;
            }
            result.differing = result.differing.saturating_add(1);
            if !colour_near(reference, x, y, actual, tolerance) {
                result.unexplained_in_candidate = result.unexplained_in_candidate.saturating_add(1);
            }
            if !colour_near(candidate, x, y, expected, tolerance) {
                result.unexplained_in_reference = result.unexplained_in_reference.saturating_add(1);
            }
        }
    }
    Ok(result)
}

/// Where a smaller reference sits inside a larger frame: the offset of its top left, and the mean
/// absolute difference per channel there, in 1/1000ths of a level.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Placement {
    /// Columns from the larger frame's left edge.
    pub left: u32,
    /// Rows from the larger frame's top edge.
    pub top: u32,
    /// The mean absolute difference per channel at that offset, times 1000.
    pub mean_difference_millis: u64,
}

/// Finds the offset at which `inner` best matches part of `outer`, for references cropped from a
/// screen (the `rosetta_stone` JPEGs are 634 x 476 crops of PP3's 640 x 480 screen).
///
/// # Errors
///
/// [`Error::Frame`] if `inner` is larger than `outer` on either side.
pub fn place(outer: &Frame, inner: &Frame) -> Result<Placement, Error> {
    let (Some(columns), Some(rows)) =
        (outer.width().checked_sub(inner.width()), outer.height().checked_sub(inner.height()))
    else {
        return Err(Error::Frame(format!(
            "a {} x {} reference cannot sit inside a {} x {} frame",
            inner.width(),
            inner.height(),
            outer.width(),
            outer.height()
        )));
    };
    let mut best: Option<Placement> = None;
    for top in 0..=rows {
        for left in 0..=columns {
            let total = absolute_difference_at(outer, inner, left, top);
            let channels = u64::from(inner.width())
                .saturating_mul(u64::from(inner.height()))
                .saturating_mul(u64::try_from(CHANNELS).unwrap_or(u64::MAX));
            let mean_difference_millis = total.saturating_mul(MILLIS).checked_div(channels).unwrap_or(u64::MAX);
            if best.is_none_or(|placement| mean_difference_millis < placement.mean_difference_millis) {
                best = Some(Placement { left, top, mean_difference_millis });
            }
        }
    }
    best.ok_or_else(|| Error::Frame("no placement was tried".to_owned()))
}

/// [`Placement::mean_difference_millis`] is in thousandths of a level.
const MILLIS: u64 = 1000;

fn absolute_difference_at(outer: &Frame, inner: &Frame, left: u32, top: u32) -> u64 {
    let mut total: u64 = 0;
    for y in 0..inner.height() {
        for x in 0..inner.width() {
            let (Some(a), Some(b)) = (outer.pixel(x.saturating_add(left), y.saturating_add(top)), inner.pixel(x, y))
            else {
                continue;
            };
            for (first, second) in a.into_iter().zip(b) {
                total = total.saturating_add(u64::from(first.abs_diff(second)));
            }
        }
    }
    total
}

fn same_colour(first: [u8; 3], second: [u8; 3], channel_tolerance: u8) -> bool {
    first.into_iter().zip(second).all(|(a, b)| a.abs_diff(b) <= channel_tolerance)
}

/// Whether `frame` has `colour` anywhere within the displacement of (`x`, `y`).
fn colour_near(frame: &Frame, x: u32, y: u32, colour: [u8; 3], tolerance: Tolerance) -> bool {
    let reach = tolerance.displacement;
    for near_y in y.saturating_sub(reach)..=y.saturating_add(reach) {
        for near_x in x.saturating_sub(reach)..=x.saturating_add(reach) {
            if frame.pixel(near_x, near_y).is_some_and(|found| same_colour(found, colour, tolerance.channel)) {
                return true;
            }
        }
    }
    false
}

#[cfg(test)]
#[allow(clippy::arithmetic_side_effects, reason = "tests compute offsets in small fixed frames")]
mod tests {
    use super::*;

    const WHITE: [u8; 3] = [255, 255, 255];
    const RED: [u8; 3] = [255, 0, 0];
    const EXACT: Tolerance = Tolerance { channel: 0, displacement: 0 };
    const ONE_PIXEL: Tolerance = Tolerance { channel: 0, displacement: 1 };

    /// A black frame with the listed pixels painted.
    fn frame(width: u32, height: u32, painted: &[(u32, u32, [u8; 3])]) -> Frame {
        let mut rgb = vec![0; (width * height * 3) as usize];
        for &(x, y, colour) in painted {
            let start = ((y * width + x) * 3) as usize;
            rgb[start..start + 3].copy_from_slice(&colour);
        }
        Frame::new(width, height, rgb).unwrap()
    }

    #[test]
    fn identical_frames_pass_with_nothing_differing() {
        let a = frame(8, 8, &[(3, 3, WHITE)]);
        let result = compare(&a, &a.clone(), EXACT).unwrap();
        assert_eq!(
            result,
            Comparison { pixels: 64, differing: 0, unexplained_in_candidate: 0, unexplained_in_reference: 0 }
        );
        assert!(result.passes());
    }

    #[test]
    fn a_shape_moved_one_pixel_fails_exactly_and_passes_at_displacement_one() {
        let reference = frame(8, 8, &[(3, 3, WHITE)]);
        let candidate = frame(8, 8, &[(4, 3, WHITE)]);
        let exact = compare(&reference, &candidate, EXACT).unwrap();
        assert_eq!((exact.differing, exact.unexplained_in_candidate, exact.unexplained_in_reference), (2, 2, 2));
        assert!(!exact.passes());
        assert!(compare(&reference, &candidate, ONE_PIXEL).unwrap().passes());
    }

    #[test]
    fn a_shape_moved_two_pixels_fails_at_displacement_one() {
        let reference = frame(8, 8, &[(3, 3, WHITE)]);
        let candidate = frame(8, 8, &[(5, 3, WHITE)]);
        assert!(!compare(&reference, &candidate, ONE_PIXEL).unwrap().passes());
    }

    #[test]
    fn a_wrong_colour_fails_whatever_the_displacement() {
        let reference = frame(8, 8, &[(3, 3, WHITE)]);
        let candidate = frame(8, 8, &[(3, 3, RED)]);
        let result = compare(&reference, &candidate, Tolerance { channel: 0, displacement: 4 }).unwrap();
        assert_eq!((result.unexplained_in_candidate, result.unexplained_in_reference), (1, 1));
    }

    #[test]
    fn a_missing_shape_is_unexplained_in_the_reference_only() {
        let reference = frame(8, 8, &[(3, 3, WHITE)]);
        let candidate = frame(8, 8, &[]);
        let result = compare(&reference, &candidate, ONE_PIXEL).unwrap();
        assert_eq!((result.differing, result.unexplained_in_candidate, result.unexplained_in_reference), (1, 0, 1));
    }

    #[test]
    fn channel_tolerance_absorbs_small_colour_noise_only() {
        let reference = frame(4, 4, &[(1, 1, [200, 200, 200])]);
        let candidate = frame(4, 4, &[(1, 1, [210, 190, 200])]);
        assert!(compare(&reference, &candidate, Tolerance { channel: 10, displacement: 0 }).unwrap().passes());
        assert!(!compare(&reference, &candidate, Tolerance { channel: 9, displacement: 0 }).unwrap().passes());
    }

    #[test]
    fn frames_of_different_sizes_are_refused() {
        assert!(compare(&frame(4, 4, &[]), &frame(4, 5, &[]), EXACT).is_err());
    }

    #[test]
    fn place_finds_a_crop_at_its_offset() {
        let outer = frame(10, 8, &[(6, 5, WHITE), (2, 1, RED)]);
        let inner = outer.crop(2, 1, 6, 5).unwrap();
        assert_eq!(place(&outer, &inner).unwrap(), Placement { left: 2, top: 1, mean_difference_millis: 0 });
        assert!(place(&inner, &outer).is_err());
    }
}
