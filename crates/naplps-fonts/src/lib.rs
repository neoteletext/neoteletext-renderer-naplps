//! The fonts this repository makes, as the text `naplps::StrokeFont::parse`
//! reads.
//!
//! The renderer takes its font as data and reads no file (decision D5). A
//! program that builds the renderer in and has no file to read, such as a
//! confined process, takes the text from here.
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

/// NeoTeletext's own stroke font for the primary and supplementary sets, written by
/// `scripts/make_font.py` (`fonts/neoteletext.strokes`; REQ-6408 item 1).
pub const NEOTELETEXT: &str = include_str!("../../../fonts/neoteletext.strokes");
