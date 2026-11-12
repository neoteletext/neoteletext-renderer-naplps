//! A captured or rendered picture: 8-bit RGB, row by row from the top left.

use crate::error::Error;

/// The largest width or height accepted. The period displays are 640 x 480 at most; a reference
/// photographed or scanned at a higher resolution would still fit.
pub const MAX_SIDE: u32 = 4096;
/// Bytes per pixel: red, green, blue.
pub const CHANNELS: usize = 3;

/// One picture.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Frame {
    width: u32,
    height: u32,
    rgb: Vec<u8>,
}

impl Frame {
    /// Takes ownership of RGB data, checking that it holds exactly `width` x `height` pixels.
    ///
    /// # Errors
    ///
    /// [`Error::Frame`] if a side is zero or above [`MAX_SIDE`], or the data is the wrong length.
    pub fn new(width: u32, height: u32, rgb: Vec<u8>) -> Result<Self, Error> {
        if width == 0 || height == 0 || width > MAX_SIDE || height > MAX_SIDE {
            return Err(Error::Frame(format!("a frame of {width} x {height} is outside 1 to {MAX_SIDE} on a side")));
        }
        let expected = byte_length(width, height)?;
        if rgb.len() != expected {
            return Err(Error::Frame(format!(
                "a {width} x {height} frame needs {expected} bytes of RGB, but {} were given",
                rgb.len()
            )));
        }
        Ok(Self { width, height, rgb })
    }

    /// The width in pixels.
    #[must_use]
    pub fn width(&self) -> u32 {
        self.width
    }

    /// The height in pixels.
    #[must_use]
    pub fn height(&self) -> u32 {
        self.height
    }

    /// The RGB data, row by row.
    #[must_use]
    pub fn rgb(&self) -> &[u8] {
        &self.rgb
    }

    /// The colour at (`x`, `y`), or `None` outside the frame.
    #[must_use]
    pub fn pixel(&self, x: u32, y: u32) -> Option<[u8; 3]> {
        if x >= self.width || y >= self.height {
            return None;
        }
        let start = byte_offset(self.width, x, y)?;
        let bytes = self.rgb.get(start..start.checked_add(CHANNELS)?)?;
        match bytes {
            [red, green, blue] => Some([*red, *green, *blue]),
            _ => None,
        }
    }

    /// The `width` x `height` rectangle whose top left is at (`left`, `top`).
    ///
    /// # Errors
    ///
    /// [`Error::Frame`] if the rectangle is empty or reaches outside this frame.
    pub fn crop(&self, left: u32, top: u32, width: u32, height: u32) -> Result<Self, Error> {
        let fits = left.checked_add(width).is_some_and(|right| right <= self.width)
            && top.checked_add(height).is_some_and(|bottom| bottom <= self.height);
        if !fits {
            return Err(Error::Frame(format!(
                "a {width} x {height} crop at ({left}, {top}) reaches outside a {} x {} frame",
                self.width, self.height
            )));
        }
        let mut rgb = Vec::with_capacity(byte_length(width, height)?);
        let row_bytes = usize::try_from(width).ok().and_then(|w| w.checked_mul(CHANNELS)).ok_or_else(too_large)?;
        for y in top..top.saturating_add(height) {
            let start = byte_offset(self.width, left, y).ok_or_else(too_large)?;
            let row = self.rgb.get(start..start.saturating_add(row_bytes)).ok_or_else(too_large)?;
            rgb.extend_from_slice(row);
        }
        Self::new(width, height, rgb)
    }
}

/// Where pixel (`x`, `y`) starts in the RGB data of a frame `width` pixels wide.
fn byte_offset(width: u32, x: u32, y: u32) -> Option<usize> {
    let index = u64::from(y).checked_mul(u64::from(width))?.checked_add(u64::from(x))?;
    usize::try_from(index).ok()?.checked_mul(CHANNELS)
}

/// The bytes of RGB a `width` x `height` frame holds.
fn byte_length(width: u32, height: u32) -> Result<usize, Error> {
    u64::from(width)
        .checked_mul(u64::from(height))
        .and_then(|pixels| usize::try_from(pixels).ok())
        .and_then(|pixels| pixels.checked_mul(CHANNELS))
        .ok_or_else(too_large)
}

fn too_large() -> Error {
    Error::Frame("a frame's size does not fit this machine's addresses".to_owned())
}

#[cfg(test)]
#[allow(clippy::arithmetic_side_effects, reason = "tests compute offsets in small fixed frames")]
mod tests {
    use super::*;

    fn gradient(width: u32, height: u32) -> Frame {
        let mut rgb = Vec::new();
        for y in 0..height {
            for x in 0..width {
                rgb.extend_from_slice(&[u8::try_from(x).unwrap(), u8::try_from(y).unwrap(), 7]);
            }
        }
        Frame::new(width, height, rgb).unwrap()
    }

    #[test]
    fn pixel_reads_the_right_place_and_none_outside() {
        let frame = gradient(4, 3);
        assert_eq!(frame.pixel(3, 2), Some([3, 2, 7]));
        assert_eq!(frame.pixel(4, 0), None);
        assert_eq!(frame.pixel(0, 3), None);
    }

    #[test]
    fn new_refuses_wrong_lengths_and_sizes() {
        assert!(Frame::new(2, 2, vec![0; 11]).is_err());
        assert!(Frame::new(0, 2, Vec::new()).is_err());
        assert!(Frame::new(MAX_SIDE + 1, 1, vec![0; (MAX_SIDE as usize + 1) * 3]).is_err());
    }

    #[test]
    fn crop_takes_the_named_rectangle_and_refuses_overreach() {
        let frame = gradient(5, 4);
        let crop = frame.crop(1, 2, 3, 2).unwrap();
        assert_eq!((crop.width(), crop.height()), (3, 2));
        assert_eq!(crop.pixel(0, 0), Some([1, 2, 7]));
        assert_eq!(crop.pixel(2, 1), Some([3, 3, 7]));
        assert!(frame.crop(3, 0, 3, 1).is_err());
        assert!(frame.crop(0, 3, 1, 2).is_err());
    }
}
