//! Builds the fuzz target `naplps_objects` and runs it on fixed and generated inputs (ANIM-23,
//! REQ-6531), until a fuzzing engine is approved to drive it (the file's own header).
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: a fixed generator, and failure is a panic"
)]

#[path = "../../../fuzz/fuzz_targets/naplps_objects.rs"]
mod target;

/// Inputs generated on every run.
const INPUTS: usize = 12;
/// Bytes of a generated input at most.
const MAX_LENGTH: u64 = 200;
/// The generator's fixed seed, so every run tests the same inputs.
const SEED: u64 = 0x00A1_11A7_E0B1;

/// xorshift64*: a fixed, dependency-free generator.
struct Generator(u64);

impl Generator {
    fn next(&mut self) -> u64 {
        self.0 ^= self.0 >> 12;
        self.0 ^= self.0 << 25;
        self.0 ^= self.0 >> 27;
        self.0.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }
}

/// A stream that defines macro 2/0 as a filled rectangle and 2/1 as text-free drawing with the
/// commands an object's macro must ignore, then objects that use them: the inputs a fuzzer
/// would have to find before it reached object drawing at all.
const SEEDED: &[u8] = &[
    // feed 30 bytes: DEF MACRO 2/0 SO RECT FILLED END; DEF MACRO 2/1 SO RESET WAIT SET COLOR RECT END.
    4, 30, 0x80, 0x20, 0x0E, 0x31, 0x51, 0x40, 0x40, 0x85, 0x80, 0x21, 0x0E, 0x20, 0x7F, 0x7F, 0x3D, 0x5C, 0x45, 0x3C,
    0x7F, 0x40, 0x31, 0x49, 0x40, 0x40, 0x85, 0x0E, 0x31, 0x52, 0x40, 0x40,
    // set two objects, a macro object and a region.
    0, 2, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00, 0x40, 0x40, 0x60, 0x60, 0x00, 0x60, 0x03, 0x00, 0x00, 0x02, 0x00, 0x05,
    0x30, 0x30, 0x40, 0x40, 0x09, 0x00, // move object 1, hide object 2, clear, pointer look.
    1, 1, 0x05, 0x00, 0x90, 0x00, 0x30, 1, 2, 0x01, 2, 1, 3, 1, 1,
];

#[test]
fn the_seeded_input_holds_the_properties() {
    target::naplps_objects(SEEDED);
}

#[test]
fn generated_inputs_hold_the_properties() {
    let mut generator = Generator(SEED);
    for _ in 0..INPUTS {
        let length = generator.next() % MAX_LENGTH;
        let mut input: Vec<u8> = SEEDED[..34].to_vec();
        input.extend((0..length).map(|_| generator.next().to_le_bytes()[2]));
        target::naplps_objects(&input);
    }
}

#[test]
fn the_empty_input_is_taken() {
    target::naplps_objects(&[]);
}
