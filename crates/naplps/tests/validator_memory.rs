//! Renderer parity PAR-15 (REQ-6765) and TODO-6854: the memory a `naplps::Validator` holds is
//! what its `held_bytes` reports, and never more than `MAX_HELD_BYTES`. Measured as the growth
//! of the process's resident size (`VmRSS` of `/proc/self/status`) while many new validators
//! each read the heaviest stream this test knows and are kept, against the sum of the figures
//! they report: a figure that leaves out what a validator holds (its DRCS bitmaps, say, 1.6 MB
//! each) shows as growth past the sum. One test alone in its test binary, so that no other
//! test's memory is counted; Linux only, where the resident size can be read.
#![cfg(target_os = "linux")]
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::unwrap_used,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

mod common;

use naplps::limits::{MAX_ALL_MACRO_BYTES, MAX_HELD_BYTES};
use naplps::{Event, Refusal, Validator};

/// Validators kept at once, so that what each holds outweighs the allocator's rounding.
const VALIDATORS: usize = 32;
/// What the resident size may grow by beyond the figures reported: the pages the allocator
/// rounds its heap to, the scratch a call frees but the allocator keeps (a figure's points),
/// and the test's own few allocations. Measured on 19 November 2026 (`x86_64` Linux): 32
/// validators grew it by 56,139,776 bytes against 56,107,264 reported, 32,512 more.
const SLACK_BYTES: usize = 512 * 1024;

/// The process's resident size in bytes, from `/proc/self/status`.
fn resident_bytes() -> usize {
    let status = std::fs::read_to_string("/proc/self/status").unwrap();
    let line = status.lines().find(|line| line.starts_with("VmRSS:")).unwrap();
    let kilobytes: usize = line.split_whitespace().nth(1).unwrap().parse().unwrap();
    kilobytes * 1024
}

#[test]
fn validators_hold_no_more_than_they_report_and_the_bound() {
    let stream = common::heaviest(&[]);
    let mut validators = Vec::with_capacity(VALIDATORS);
    let before = resident_bytes();
    for _ in 0..VALIDATORS {
        let mut validator = Validator::new();
        let events = validator.feed(&stream);
        assert!(!events.contains(&Event::LimitReached), "the stream is read whole");
        validators.push(validator);
    }
    let grown = resident_bytes().saturating_sub(before);
    let validator = &validators[0];
    assert_eq!(validator.diagnostics().count(Refusal::MacroTooDeep), 1, "a macro nested to the limit");
    assert_eq!(validator.diagnostics().count(Refusal::MacrosFull), 0, "the macros fill the limit exactly");
    assert_eq!(validator.defined_macros().iter().filter(|on| **on).count(), MAX_ALL_MACRO_BYTES / 4096);
    let reported: usize = validators.iter().map(Validator::held_bytes).sum();
    println!(
        "{VALIDATORS} validators reading the heaviest stream grew the resident size by {grown} bytes; they report {reported} ({} each); the bound is {MAX_HELD_BYTES} each",
        reported / VALIDATORS
    );
    assert!(grown <= reported + SLACK_BYTES, "grew by {grown}, more than the {reported} reported");
    assert!(grown <= VALIDATORS * MAX_HELD_BYTES, "grew by {grown}, past the bound");
    // The figure is not loose either: what is resident is most of what is reported.
    assert!(grown * 10 >= reported * 9, "grew by {grown}, much less than the {reported} reported");
    drop(validators);
}
