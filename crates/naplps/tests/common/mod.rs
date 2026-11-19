//! Streams the memory tests share: the definitions a stream can make at their largest
//! (`held.rs` and `validator_memory.rs`, TODO-6854).
#![allow(dead_code, reason = "each test binary uses a part of what is shared")]

use naplps::limits::{DEFINABLE_CODES, MAX_ALL_MACRO_BYTES, MAX_MACRO_BYTES, MAX_PDI_BYTES, TEXTURE_MASKS};

pub const NUL: u8 = 0x00;
pub const ESC: u8 = 0x1B;
pub const SO: u8 = 0x0E;
pub const SI: u8 = 0x0F;
pub const SS2: u8 = 0x19;
pub const DEF_MACRO: u8 = 0x80;
pub const DEF_DRCS: u8 = 0x83;
pub const DEF_TEXTURE: u8 = 0x84;
pub const END: u8 = 0x85;
/// TEXTURE (section 5.3.2.5), an opcode of the PDI set.
pub const TEXTURE: u8 = 0x23;
/// POLYGON FILLED (section 5.3.3.5), an opcode of the PDI set.
pub const POLYGON_FILLED: u8 = 0x37;
/// WAIT and its fixed-format byte (section 5.3.2.8), then a wait of one tenth.
pub const WAIT: [u8; 3] = [0x3D, 0x5C, 0x41];
/// The first texture pattern, A (section 6.2.4).
pub const FIRST_TEXTURE: u8 = 0x41;

/// The macro set designated into G2 (Table 1), and a character field and a texture mask of 1/16
/// by 1/16, so that every DRCS and texture bitmap defined after it is `MASK_SIDE` by `MASK_SIDE`.
pub fn square_definitions() -> Vec<u8> {
    let mut bytes = vec![ESC, 0x2E, 0x20, 0x7A];
    // TEXT (2/2): its defaults, then a character field of 1/16 by 1/16 (three-byte operands, x
    // and y each the nine bits 0 000 010 000: 16/256); TEXTURE (2/3): solid, and a mask size of
    // 1/16 by 1/16; then SI, and the PDI runs at the next control.
    let square = [0x40, 0x52, 0x40];
    bytes.extend_from_slice(&[SO, 0x22, 0x40, 0x40]);
    bytes.extend_from_slice(&square);
    bytes.extend_from_slice(&[TEXTURE, 0x40]);
    bytes.extend_from_slice(&square);
    bytes.push(SI);
    bytes
}

/// A filled rectangle over the whole bitmap (RECT FILLED SET 3/1 from the drawing point, the
/// largest size), so that every element of a DRCS or texture bitmap is written.
pub const FILL: [u8; 6] = [SO, 0x31, 0x5B, 0x7F, 0x7F, SI];

/// Every macro byte the limit allows, a macro nested to the depth limit whose deepest copy
/// runs `in_deepest` (after its self-call is refused), all 96 DRCS characters and the 4
/// textures at the largest mask with every element drawn, the self-calling macro called, and a
/// polygon of the most operand bytes left open.
pub fn heaviest(in_deepest: &[u8]) -> Vec<u8> {
    let mut bytes = square_definitions();
    // Macro 2/0 calls itself first; 2/1 to 2/15 fill the rest of the macros' limit. The bodies
    // are NUL, which a terminal passes over (section 6.1), so that calling them costs no
    // drawing work: drawn characters would spend the work allowance (TODO-6844), and every
    // byte after it would be refused.
    let each = MAX_ALL_MACRO_BYTES / 16;
    assert_eq!(each, MAX_MACRO_BYTES);
    bytes.extend_from_slice(&[DEF_MACRO, 0x20, SS2, 0x20]);
    bytes.extend_from_slice(in_deepest);
    bytes.extend(std::iter::repeat_n(NUL, each - 2 - in_deepest.len()));
    for number in 0x21..0x30u8 {
        bytes.extend_from_slice(&[DEF_MACRO, number]);
        bytes.extend(std::iter::repeat_n(NUL, each));
    }
    // DEF DRCS 2/0, then each DEF DRCS defines the next of the 96 (section 6.2.3).
    bytes.extend_from_slice(&[DEF_DRCS, 0x20]);
    bytes.extend_from_slice(&FILL);
    for _ in 1..DEFINABLE_CODES {
        bytes.push(DEF_DRCS);
        bytes.extend_from_slice(&FILL);
    }
    for pattern in (FIRST_TEXTURE..).take(TEXTURE_MASKS) {
        bytes.extend_from_slice(&[DEF_TEXTURE, pattern]);
        bytes.extend_from_slice(&FILL);
    }
    bytes.push(END);
    // Call the self-calling macro, then POLYGON FILLED with the most operand bytes.
    bytes.extend_from_slice(&[SS2, 0x20, SO, POLYGON_FILLED]);
    bytes.extend(std::iter::repeat_n(0x41, MAX_PDI_BYTES));
    bytes
}
