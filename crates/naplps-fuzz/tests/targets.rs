//! The fuzz targets of `fuzz/fuzz_targets/`, run on their kept inputs and then driven by
//! property testing (neoteletext-common `docs/animation.md`, ANIM-23; REQ-6531, REQ-5788).
//!
//! Each target is first run on every input kept in its folder of `fuzz/corpus/`, where each
//! input that ever found a fault is kept, and then on inputs a property-testing library makes:
//! new ones on every run, so that the gates search and do not only repeat. An input that fails
//! is reduced to the least that still fails and written into the target's folder, to be
//! committed with the fix.
//!
//! cargo-fuzz would guide the search by coverage, but its engine is C++ and the renderer takes
//! no native code (DEC-6579).
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

#[path = "../../../fuzz/fuzz_targets/naplps_objects.rs"]
mod objects;
#[path = "../../../fuzz/fuzz_targets/naplps_stream.rs"]
mod stream;
#[path = "../../../fuzz/fuzz_targets/naplps_validator.rs"]
mod validator;

use std::fmt::Debug;
use std::path::{Path, PathBuf};

use proptest::collection::vec;
use proptest::prelude::{Strategy, any};
use proptest::test_runner::{Config, TestError, TestRunner};

/// The most attempts made at reducing an input that fails. The library's own default is four
/// times the cases, which leaves an input of hundreds of bytes nearly as it was found; an
/// attempt is one run of the target on a smaller input, a few milliseconds.
const MAX_REDUCTIONS: u32 = 20_000;

/// Where a target's kept inputs are.
fn corpus(target: &str) -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../fuzz/corpus").join(target)
}

/// The 64-bit FNV-1a hash (Fowler, Noll and Vo; the constants are the algorithm's): it names
/// a kept input by its contents.
fn fnv(bytes: &[u8]) -> u64 {
    const OFFSET_BASIS: u64 = 0xCBF2_9CE4_8422_2325;
    const PRIME: u64 = 0x0000_0100_0000_01B3;
    bytes.iter().fold(OFFSET_BASIS, |hash, &byte| (hash ^ u64::from(byte)).wrapping_mul(PRIME))
}

/// Runs a target on every input kept for it.
fn replay(target: &str, run: fn(&[u8])) {
    let mut names: Vec<_> = std::fs::read_dir(corpus(target)).unwrap().map(|entry| entry.unwrap().path()).collect();
    names.sort();
    assert!(!names.is_empty(), "the kept inputs of {target} are missing");
    for name in names {
        run(&std::fs::read(name).unwrap());
    }
}

/// Runs a target on `cases` inputs made anew on every run by `strategy`, each turned into the
/// target's bytes by `bytes`. An input that fails is reduced, kept in the target's folder and
/// reported.
fn search<S>(target: &str, run: fn(&[u8]), strategy: &S, bytes: fn(&S::Value) -> Vec<u8>, cases: u32)
where
    S: Strategy,
    S::Value: Debug,
{
    // The reduced input is kept as a file, which says more than the seed the library would
    // keep.
    let config = Config { cases, failure_persistence: None, max_shrink_iters: MAX_REDUCTIONS, ..Config::default() };
    let mut runner = TestRunner::new(config);
    let result = runner.run(strategy, |value| {
        run(&bytes(&value));
        Ok(())
    });
    match result {
        Ok(()) => {}
        Err(TestError::Fail(reason, value)) => {
            let input = bytes(&value);
            let kept = corpus(target).join(format!("found-{:016x}", fnv(&input)));
            std::fs::write(&kept, &input).unwrap();
            panic!(
                "an input of {} bytes fails {target}: {reason}\nit is kept as {}: commit it with the fix",
                input.len(),
                kept.display()
            );
        }
        Err(TestError::Abort(reason)) => panic!("the search of {target} stopped: {reason}"),
    }
}

// ----- naplps_objects ------------------------------------------------------------------------

/// The first bytes of the kept input `seed-macros-and-objects`: one feed of a stream that
/// defines macros 2/0 and 2/1. An input that begins with them has macros for its objects to
/// draw, which a fuzzer would otherwise have to find before it reached object drawing at all.
const MACROS_LENGTH: usize = 34;

/// An input of `naplps_objects`: with or without the macro definitions before it.
fn objects_input((with_macros, rest): &(bool, Vec<u8>)) -> Vec<u8> {
    let mut input = Vec::new();
    if *with_macros {
        let seed = std::fs::read(corpus("naplps_objects").join("seed-macros-and-objects")).unwrap();
        input.extend_from_slice(&seed[..MACROS_LENGTH]);
    }
    input.extend_from_slice(rest);
    input
}

/// The inputs of a run of the push gate, and the longest of their bytes.
const OBJECTS_QUICK: (u32, usize) = (24, 200);
/// The inputs of a run of the full gate, and the longest of their bytes.
const OBJECTS_LONG: (u32, usize) = (1500, 400);

fn search_objects((cases, length): (u32, usize)) {
    let strategy = (any::<bool>(), vec(any::<u8>(), 0..=length));
    search("naplps_objects", objects::naplps_objects, &strategy, objects_input, cases);
}

#[test]
fn naplps_objects_holds_on_every_kept_input_and_on_the_empty_one() {
    replay("naplps_objects", objects::naplps_objects);
    objects::naplps_objects(&[]);
}

#[test]
fn naplps_objects_holds_on_generated_inputs() {
    search_objects(OBJECTS_QUICK);
}

#[test]
#[ignore = "the long run of the full gate: scripts/check.sh full"]
fn naplps_objects_holds_on_generated_inputs_at_length() {
    search_objects(OBJECTS_LONG);
}

// ----- naplps_stream -------------------------------------------------------------------------

/// A byte of a stream from two random ones, biased toward what NAPLPS reads: controls, PDI
/// opcodes, operand bytes, C1 controls, the shifts and ESC. Uniform bytes seldom make a
/// command with its operands.
fn biased((kind, byte): (u8, u8)) -> u8 {
    match kind % 8 {
        0 => byte & 0x1F,
        1 => 0x20 | (byte & 0x1F),
        2 | 3 => 0x40 | (byte & 0x3F),
        4 => 0x80 | (byte & 0x1F),
        5 => [0x0E, 0x0F, 0x19, 0x1D, 0x1B][usize::from(byte % 5)],
        _ => byte,
    }
}

/// An input of `naplps_stream`: the byte that seeds how the stream is divided, then the
/// stream.
fn stream_input((seed, stream): &(u8, Vec<(u8, u8)>)) -> Vec<u8> {
    std::iter::once(*seed).chain(stream.iter().copied().map(biased)).collect()
}

/// The inputs of a run of the push gate, and the longest of their streams.
const STREAM_QUICK: (u32, usize) = (64, 600);
/// The inputs of a run of the full gate, and the longest of their streams.
const STREAM_LONG: (u32, usize) = (4000, 1500);

fn search_stream((cases, length): (u32, usize)) {
    let strategy = (any::<u8>(), vec((any::<u8>(), any::<u8>()), 0..=length));
    search("naplps_stream", stream::naplps_stream, &strategy, stream_input, cases);
}

#[test]
fn naplps_stream_holds_on_every_kept_input_and_on_the_empty_one() {
    replay("naplps_stream", stream::naplps_stream);
    stream::naplps_stream(&[]);
}

#[test]
fn naplps_stream_holds_on_generated_inputs() {
    search_stream(STREAM_QUICK);
}

#[test]
#[ignore = "the long run of the full gate: scripts/check.sh full"]
fn naplps_stream_holds_on_generated_inputs_at_length() {
    search_stream(STREAM_LONG);
}

// ----- naplps_validator ----------------------------------------------------------------------

/// The inputs of a run of the push gate, and the longest of their streams.
const VALIDATOR_QUICK: (u32, usize) = (64, 600);
/// The inputs of a run of the full gate, and the longest of their streams.
const VALIDATOR_LONG: (u32, usize) = (4000, 1500);

fn search_validator((cases, length): (u32, usize)) {
    let strategy = (any::<u8>(), vec((any::<u8>(), any::<u8>()), 0..=length));
    search("naplps_validator", validator::naplps_validator, &strategy, stream_input, cases);
}

#[test]
fn naplps_validator_holds_on_every_kept_input_and_on_the_empty_one() {
    replay("naplps_validator", validator::naplps_validator);
    validator::naplps_validator(&[]);
}

#[test]
fn naplps_validator_holds_on_generated_inputs() {
    search_validator(VALIDATOR_QUICK);
}

#[test]
#[ignore = "the long run of the full gate: scripts/check.sh full"]
fn naplps_validator_holds_on_generated_inputs_at_length() {
    search_validator(VALIDATOR_LONG);
}
