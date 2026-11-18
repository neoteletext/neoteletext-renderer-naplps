//! Renderer parity PAR-15 (REQ-6765): a `naplps::Validator`'s memory is bounded by the
//! definitions' own limits and a fixed state, whatever the picture's size. Measured as the
//! growth of the process's peak resident size (`VmHWM` of `/proc/self/status`) while a new
//! validator reads the heaviest stream this test knows; alone in its test binary, so that no
//! other test's memory is counted.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::unwrap_used,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::limits::{MASK_SIDE, MAX_ALL_MACRO_BYTES, MAX_MACRO_BYTES, MAX_MACRO_DEPTH, MAX_PDI_BYTES, MAX_VERTICES};
use naplps::{Event, Refusal, Validator};

const ESC: u8 = 0x1B;
const SO: u8 = 0x0E;
const SI: u8 = 0x0F;
const SS2: u8 = 0x19;
const DEF_MACRO: u8 = 0x80;
const DEF_DRCS: u8 = 0x83;
const DEF_TEXTURE: u8 = 0x84;
const END: u8 = 0x85;
/// DRCS characters and texture masks a stream can define (ANSI X3.110-1983 sections 6.2.3 and
/// 6.2.4), and the one being defined.
const MASKS: usize = 96 + 4 + 1;
/// Bytes of one point while a polygon runs: two 32-bit coordinates.
const POINT_BYTES: usize = 8;
/// What the peak resident size may grow by besides what the definitions hold: the fixed state,
/// the allocator's own bookkeeping and the pages a resident size is counted in. A generous
/// margin, so that the test states the bound and not the allocator's habits.
const FIXED_MARGIN: usize = 256 * 1024;

/// The peak resident size in bytes, from `/proc/self/status`.
fn peak_resident() -> usize {
    let status = std::fs::read_to_string("/proc/self/status").unwrap();
    let line = status.lines().find(|line| line.starts_with("VmHWM:")).unwrap();
    let kilobytes: usize = line.split_whitespace().nth(1).unwrap().parse().unwrap();
    kilobytes * 1024
}

/// Every macro byte the limit allows, a macro nested to the depth limit, all 96 DRCS characters
/// and the 4 textures at the largest mask with every element drawn, and a polygon of the most
/// points.
fn heaviest() -> Vec<u8> {
    // The macro set into G2 (Table 1).
    let mut bytes = vec![ESC, 0x2E, 0x20, 0x7A];
    // TEXT (2/2): its defaults, then a character field of 1/16 by 1/16 (three-byte operands, x
    // and y each the nine bits 0 000 010 000: 16/256); TEXTURE (2/1): solid, and a mask size of
    // 1/16 by 1/16. Square, so that every DRCS and texture bitmap is MASK_SIDE by MASK_SIDE.
    let square = [0x40, 0x52, 0x40];
    bytes.extend_from_slice(&[SO, 0x22, 0x40, 0x40]);
    bytes.extend_from_slice(&square);
    bytes.extend_from_slice(&[0x21, 0x40]);
    bytes.extend_from_slice(&square);
    bytes.push(SI);
    // Macro 2/0 calls itself first; 2/1 to 2/15 fill the rest of the macros' limit.
    let each = MAX_ALL_MACRO_BYTES / 16;
    assert_eq!(each, MAX_MACRO_BYTES);
    bytes.extend_from_slice(&[DEF_MACRO, 0x20, SS2, 0x20]);
    bytes.extend(std::iter::repeat_n(b'.', each - 2));
    for number in 0x21..0x30u8 {
        bytes.extend_from_slice(&[DEF_MACRO, number]);
        bytes.extend(std::iter::repeat_n(b'.', each));
    }
    // A filled rectangle over the whole bitmap (RECT FILLED SET 3/1 from the drawing point, the
    // largest size), so that every element of every bitmap is written.
    let fill = [SO, 0x31, 0x5B, 0x7F, 0x7F, SI];
    // DEF DRCS 2/0, then each DEF DRCS defines the next of the 96 (section 6.2.3).
    bytes.extend_from_slice(&[DEF_DRCS, 0x20]);
    bytes.extend_from_slice(&fill);
    for _ in 1..96 {
        bytes.push(DEF_DRCS);
        bytes.extend_from_slice(&fill);
    }
    for pattern in 0x41..=0x44u8 {
        bytes.extend_from_slice(&[DEF_TEXTURE, pattern]);
        bytes.extend_from_slice(&fill);
    }
    bytes.push(END);
    // Call the self-calling macro, then POLYGON FILLED (3/7) with the most operand bytes.
    bytes.extend_from_slice(&[SS2, 0x20, SO, 0x37]);
    bytes.extend(std::iter::repeat_n(0x41, MAX_PDI_BYTES));
    bytes.push(SI);
    bytes
}

#[test]
#[cfg_attr(
    not(target_os = "linux"),
    ignore = "reads the peak resident size from /proc/self/status, which only Linux has"
)]
fn a_validators_memory_is_bounded() {
    let stream = heaviest();
    let before = peak_resident();
    let mut validator = Validator::new();
    let events = validator.feed(&stream);
    let growth = peak_resident().saturating_sub(before);
    assert!(!events.contains(&Event::LimitReached), "the stream is read whole");
    assert_eq!(validator.diagnostics().count(Refusal::MacroTooDeep), 1, "a macro nested to the limit");
    assert_eq!(validator.diagnostics().count(Refusal::MacrosFull), 0, "the macros fill the limit exactly");
    assert_eq!(validator.defined_macros().iter().filter(|on| **on).count(), 16);
    // The bound the documentation states: the macros, the copies of one while they nest, every
    // bitmap at its largest, a PDI's operands and its points, and the fixed state.
    let mask_bytes = usize::try_from(MASK_SIDE * MASK_SIDE).unwrap();
    let bound = MAX_ALL_MACRO_BYTES
        + MAX_MACRO_DEPTH * MAX_MACRO_BYTES
        + MASKS * mask_bytes
        + MAX_PDI_BYTES
        + MAX_VERTICES * POINT_BYTES
        + FIXED_MARGIN;
    println!(
        "a validator is {} bytes; reading the heaviest stream grew the peak resident size by {growth} bytes, within the bound of {bound}",
        size_of::<Validator>()
    );
    assert!(growth <= bound, "the peak resident size grew by {growth} bytes, past {bound}");
    drop(validator);
}
