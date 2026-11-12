//! Reference frames for NAPLPS rendering, captured from period software, and the comparison a
//! renderer is judged by.
//!
//! A NAPLPS renderer cannot be checked against the standard alone, because ANSI X3.110-1983
//! section 8.3.4 lets decoders approximate. It is checked against what period decoders drew:
//! [`session`] runs PP3 (Personality+III, 1991) under DOSBox and captures each page it draws, and
//! [`compare`] judges another frame against such a reference within the tolerance the standard
//! allows.
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

pub mod compare;
pub mod error;
pub mod frame;
pub mod screen;
pub mod session;
pub mod tools;
