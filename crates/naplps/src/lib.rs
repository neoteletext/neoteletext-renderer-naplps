//! A NAPLPS renderer: ANSI X3.110-1983 / CSA T500-1983 / CCITT T.101 Annex D.
//!
//! [`Terminal`] is the presentation process. Feed it a page's bytes, in one call or many, then
//! call [`Terminal::finish`]; it draws colour-map addresses onto a [`Canvas`] the caller owns,
//! and [`Terminal::palette`] turns them into colours. The library does no input or output, keeps
//! no clock (WAIT and BEL come back as [`Event`]s, and [`Palette::at`] gives the colour map at a
//! time for BLINK), contains no font ([`Terminal::set_font`] takes a [`StrokeFont`] the caller
//! supplies), and bounds everything a page can make it hold or do ([`limits`]).
//!
//! ```
//! use naplps::{Canvas, Terminal};
//! let mut canvas = Canvas::new(640, 480).unwrap();
//! let mut terminal = Terminal::new(4);
//! // SO, then RECT FILLED from the drawing point (0, 0): half the screen wide, a quarter high.
//! terminal.feed(&mut canvas, &[0x0E, 0x31, 0x51, 0x40, 0x40]);
//! terminal.finish(&mut canvas);
//! assert_eq!(canvas.pixel(10, 470), Some(terminal.palette().white()));
//! ```
#![no_std]
#![deny(
    clippy::indexing_slicing,
    clippy::string_slice,
    clippy::unwrap_used,
    clippy::expect_used,
    clippy::panic,
    clippy::arithmetic_side_effects,
    clippy::unreachable,
    clippy::todo,
    clippy::unimplemented
)]

extern crate alloc;

pub mod fixed;
pub mod font;
pub mod limits;
pub mod operand;
pub mod palette;
mod play;
mod raster;
mod surface;
mod terminal;
mod text;

pub use font::{FontSet, Glyph, StrokeFont};
pub use palette::{Blink, Palette, Rgb};
pub use play::Player;
pub use raster::{FillPattern, LineTexture};
pub use surface::{Canvas, Rect};
pub use terminal::{Animation, CharSet, Event, Look, Object, ObjectKind, Terminal};

/// What can go wrong outside drawing itself.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    /// A canvas side is zero or above [`limits::MAX_CANVAS_SIDE`].
    CanvasSize,
    /// A font's text is malformed at this line (0: the text is too long).
    Font(usize),
    /// More objects than [`limits::MAX_OBJECTS`] were given.
    TooManyObjects,
    /// The object at this index of the set given is not one the `NAPLPS_OBJECTS` record allows,
    /// or repeats an earlier object's number.
    Object(usize),
}

impl core::fmt::Display for Error {
    fn fmt(&self, formatter: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match self {
            Self::CanvasSize => write!(formatter, "a canvas side must be 1 to {} pixels", limits::MAX_CANVAS_SIDE),
            Self::Font(0) => write!(formatter, "the font is longer than {} bytes", font::MAX_TEXT_BYTES),
            Self::Font(line) => write!(formatter, "the font is malformed at line {line}"),
            Self::TooManyObjects => write!(formatter, "a sub-page has at most {} objects", limits::MAX_OBJECTS),
            Self::Object(index) => write!(formatter, "object {index} of the set is not a valid object"),
        }
    }
}

impl core::error::Error for Error {}
