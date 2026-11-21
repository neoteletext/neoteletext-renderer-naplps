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
#[path = "../../../fuzz/fuzz_targets/naplps_paced.rs"]
mod paced;
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

/// The most piece lengths an input of `naplps_validator` gives; what they leave is one more.
const MAX_PIECES: usize = 16;
/// ESC, which begins a designation (ANSI X3.110-1983 section 4.3).
const ESC: u8 = 0x1B;
/// SO and SI: the PDI set in G1 into GL, and G0 back (section 6.1.3).
const SO: u8 = 0x0E;
/// See [`SO`].
const SI: u8 = 0x0F;
/// SS2: the next byte from G2 (section 6.1.3.3).
const SS2: u8 = 0x19;
/// ACTIVE POSITION BACKWARD (section 6.1.2.1).
const APB: u8 = 0x08;
/// SELECT COLOR (section 5.3.2.6), whose two operands select colour mode 2.
const SELECT_COLOUR: u8 = 0x3E;
/// DEF MACRO (Table 3, C1 8/0).
const DEF_MACRO: u8 = 0x80;
/// The macro set into G2 as a 96-character set (Table 1), with the further intermediate 2/0
/// this renderer accepts.
const MACROS_INTO_G2: [u8; 4] = [ESC, 0x2E, 0x20, 0x7A];
/// ESC's intermediates that designate a 94-character set into G0 and G1 (section 4.3.1.2).
const DESIGNATE_G0: u8 = 0x28;
/// The first graphic code, 2/0, of a macro or character set.
const FIRST_CODE: u8 = 0x20;
/// The codes of a macro or 96-character set.
const CODES: u8 = 96;

/// A part of a stream of `naplps_validator` from three random bytes: mostly one byte as
/// [`biased`] makes it, and sometimes a sequence whose effect the validator must report as the
/// terminal does: colour mode 2 (where a character written after APB is counted, PAR-23), APB
/// and a character, the designation of a provided set (PAR-14 joins sets 44 to 51), the start
/// of a macro definition, or a call of a macro.
fn validator_part((kind, byte, other): (u8, u8, u8)) -> Vec<u8> {
    match kind % 13 {
        8 => vec![SO, SELECT_COLOUR, 0x40 | (byte & 0x3F), 0x40 | (other & 0x3F), SI],
        9 => vec![APB, FIRST_CODE + 1 + byte % (CODES - 2)],
        10 => {
            let number = other % u8::try_from(naplps::TELETEXT_SET_COUNT).unwrap();
            let (supplement, final_byte) = naplps::teletext::designation_of(number).unwrap();
            let mut piece = vec![ESC, DESIGNATE_G0 | (byte & 1)];
            piece.extend(supplement);
            piece.push(final_byte);
            piece
        }
        11 => vec![DEF_MACRO, FIRST_CODE + byte % CODES],
        12 => {
            let mut piece = MACROS_INTO_G2.to_vec();
            piece.extend_from_slice(&[SS2, FIRST_CODE + byte % CODES]);
            piece
        }
        _ => vec![biased((kind, byte))],
    }
}

/// An input of `naplps_validator`: the number of piece lengths, the lengths, and the stream.
fn validator_input((stream, lengths): &(Vec<(u8, u8, u8)>, Vec<usize>)) -> Vec<u8> {
    let mut input = vec![u8::try_from(lengths.len()).unwrap()];
    for &length in lengths {
        input.extend_from_slice(&u16::try_from(length).unwrap().to_le_bytes());
    }
    input.extend(stream.iter().copied().flat_map(validator_part));
    input
}

/// The inputs of a run of the push gate, and the longest of their streams in generated parts.
const VALIDATOR_QUICK: (u32, usize) = (64, 600);
/// The inputs of a run of the full gate, and the longest of their streams in generated parts.
const VALIDATOR_LONG: (u32, usize) = (4000, 1500);

fn search_validator((cases, length): (u32, usize)) {
    // A piece length may pass the stream's end, which takes the rest; most bytes a generated part makes
    // is 6, so `6 * length` covers a whole stream in one piece.
    let strategy = (vec((any::<u8>(), any::<u8>(), any::<u8>()), 0..=length), vec(0..=6 * length, 0..=MAX_PIECES));
    search("naplps_validator", validator::naplps_validator, &strategy, validator_input, cases);
}

#[test]
fn naplps_validator_holds_on_every_kept_input_and_on_the_empty_one() {
    replay("naplps_validator", validator::naplps_validator);
    validator::naplps_validator(&[]);
    validator::naplps_validator_in_pieces(&[], &[0, 0]);
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

// ----- naplps_paced --------------------------------------------------------------------------

/// The random values of one operation of `naplps_paced`: its kind, a count, two pace parts each
/// with its selector, and a piece of a stream.
type PacedOperation = (u8, u8, (u8, u32, u8, u32), Vec<(u8, u8)>);

/// One operation of `naplps_paced` from random values: a push of a piece of [`biased`] bytes, an
/// advance, a pace of two parts (each small, or whole when its selector says), the pace removed,
/// or delays turned off or on. The operation byte is the target's remainder by 5.
fn paced_operation((kind, count, parts, piece): &PacedOperation) -> Vec<u8> {
    let part = |selector: u8, whole: u32| {
        if selector.is_multiple_of(4) {
            let mut bytes = vec![0xF0];
            bytes.extend_from_slice(&whole.to_be_bytes());
            bytes
        } else {
            vec![selector % 0xF0]
        }
    };
    match kind % 8 {
        0..=2 => {
            let mut bytes = vec![0, u8::try_from(piece.len()).unwrap()];
            bytes.extend(piece.iter().copied().map(biased));
            bytes
        }
        3 | 4 => vec![1, *count],
        5 => {
            let mut bytes = vec![2];
            bytes.extend(part(parts.0, parts.1));
            bytes.extend(part(parts.2, parts.3));
            bytes
        }
        6 => vec![3],
        _ => vec![4, *count],
    }
}

/// An input of `naplps_paced`: its operations, one after another.
fn paced_input((operations,): &(Vec<PacedOperation>,)) -> Vec<u8> {
    operations.iter().flat_map(paced_operation).collect()
}

/// The inputs of a run of the push gate, and the most operations of each.
const PACED_QUICK: (u32, usize) = (48, 40);
/// The inputs of a run of the full gate, and the most operations of each.
const PACED_LONG: (u32, usize) = (1500, 120);
/// The longest piece pushed by one operation.
const PACED_PIECE: usize = 64;

fn search_paced((cases, length): (u32, usize)) {
    let operation = (
        any::<u8>(),
        any::<u8>(),
        (any::<u8>(), any::<u32>(), any::<u8>(), any::<u32>()),
        vec((any::<u8>(), any::<u8>()), 0..=PACED_PIECE),
    );
    search("naplps_paced", paced::naplps_paced, &(vec(operation, 0..=length),), paced_input, cases);
}

#[test]
fn naplps_paced_holds_on_every_kept_input_and_on_the_empty_one() {
    replay("naplps_paced", paced::naplps_paced);
    paced::naplps_paced(&[]);
}

#[test]
fn naplps_paced_holds_on_generated_inputs() {
    search_paced(PACED_QUICK);
}

#[test]
#[ignore = "the long run of the full gate: scripts/check.sh full"]
fn naplps_paced_holds_on_generated_inputs_at_length() {
    search_paced(PACED_LONG);
}
