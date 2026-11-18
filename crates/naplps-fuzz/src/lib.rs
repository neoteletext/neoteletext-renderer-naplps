//! The renderer's fuzz targets (neoteletext-common `docs/animation.md`,
//! ANIM-23; REQ-5788), driven by property testing.
//!
//! The targets' bodies are the files of `fuzz/fuzz_targets/`, each a plain
//! function of a fuzzer's bytes; the tests of this crate run them. They
//! live apart from the renderer because the library that drives them is a
//! dependency, and the crate `naplps` has none: a program that builds the
//! renderer in builds nothing of this crate.
//!
//! Every input that ever found a fault is kept in `fuzz/corpus/`, in a
//! folder named for its target, and replayed before anything else.
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
