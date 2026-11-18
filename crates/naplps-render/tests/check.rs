//! `naplps-render check`, the authoring check of a NAPLPS page (DEC-6638 item 7, row 9.3): it
//! reports the picture's bounds use, its objects and title, and every byte passed over or
//! refused, and exits 1 on a refusal.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

mod common;

use std::fs;
use std::path::PathBuf;
use std::process::{Command, Output};

use common::{DEF_MACRO, END, macro_rectangle, rectangle};

/// The longest macro definition the renderer keeps (`naplps::limits::MAX_MACRO_BYTES`).
const MAX_MACRO_BYTES: usize = 4096;

/// Writes `bytes` (and `objects`, if any) to files of the test's own and runs the check on them
/// with `extra` options.
fn check(name: &str, bytes: &[u8], objects: Option<&str>, extra: &[&str]) -> Output {
    let base = PathBuf::from(env!("CARGO_TARGET_TMPDIR")).join(format!("check-{name}"));
    fs::create_dir_all(&base).unwrap();
    let page = base.join("page.nap");
    fs::write(&page, bytes).unwrap();
    let mut command = Command::new(env!("CARGO_BIN_EXE_naplps-render"));
    command.arg("check").args(extra);
    if let Some(objects) = objects {
        let path = base.join("objects.txt");
        fs::write(&path, objects).unwrap();
        command.arg("--objects").arg(path);
    }
    command.arg(page).output().unwrap()
}

fn stdout(output: &Output) -> String {
    String::from_utf8(output.stdout.clone()).unwrap()
}

#[test]
fn a_clean_page_reports_its_bounds_objects_and_title_and_exits_zero() {
    // A rectangle of a quarter of the unit screen's width and an eighth of its height at its
    // origin: about 160 by 80 pixels at the bottom left of the 640 by 480 picture, as the
    // renderer rounds a rectangle's edges (its own tests fix that rounding; this one fixes the
    // report).
    let mut page = macro_rectangle(0x20, 2, 16, 16);
    page.extend(rectangle(1, 0, 0, 64, 32));
    let objects = "macro 1 2 0 300 100 41 40 0 440 20 detectable label=Next page\n";
    let output = check("clean", &page, Some(objects), &["--title", "Harbour webcam"]);
    let report = stdout(&output);
    assert_eq!(output.status.code(), Some(0), "{report}");
    assert!(report.contains("drawn: x 0 to 160, y 402 to 479 of 640 by 480 (4 % of the picture)"), "{report}");
    assert!(report.contains("title: \"Harbour webcam\""), "{report}");
    assert!(report.contains("objects: 1"), "{report}");
    assert!(
        report.contains(
            "object 1: macro, layer 2, order 0, at (300, 100) 41 by 40, frames 20, detectable, label \"Next page\""
        ),
        "{report}"
    );
    assert!(report.ends_with("result: clean\n"), "{report}");
}

#[test]
fn bytes_passed_over_are_reported_without_failing() {
    // 0/1 belongs to another layer (ANSI X3.110-1983 section 6.1), at offset 1.
    let output = check("passed-over", &[b'A', 0x01, b'B'], None, &[]);
    let report = stdout(&output);
    assert_eq!(output.status.code(), Some(0), "{report}");
    assert!(report.contains("passed over: 1 bytes with no effect, the first at offset 1"), "{report}");
    assert!(report.contains("title: none"), "{report}");
}

#[test]
fn a_refusal_is_reported_and_exits_one() {
    let mut page = vec![DEF_MACRO, 0x21];
    page.extend(std::iter::repeat_n(0x41, MAX_MACRO_BYTES + 2));
    page.push(END);
    let output = check("refused", &page, None, &[]);
    let report = stdout(&output);
    assert_eq!(output.status.code(), Some(1), "{report}");
    assert!(report.contains("REFUSED a macro definition longer than the limit: 2"), "{report}");
    assert!(report.contains("the first refusal at offset"), "{report}");
    assert!(report.ends_with("result: refused\n"), "{report}");
}

#[test]
fn objects_and_a_title_the_receiver_would_refuse_fail_the_check() {
    let objects = "macro 1 0 0 0 0 10 10 0 0 20\n"; // layer 0 is the stream's own
    let output = check("bad-objects", &[], Some(objects), &["--title", "a\u{7}"]);
    let report = stdout(&output);
    assert_eq!(output.status.code(), Some(1), "{report}");
    assert!(report.contains("REFUSED objects: object 0 of the set is not a valid object"), "{report}");
    assert!(report.contains("REFUSED title"), "{report}");
    assert!(report.contains("drawn: nothing"), "{report}");
}

#[test]
fn the_check_that_cannot_run_exits_two() {
    let output = Command::new(env!("CARGO_BIN_EXE_naplps-render")).args(["check", "--nonsense", "x"]).output().unwrap();
    assert_eq!(output.status.code(), Some(2));
    let output =
        Command::new(env!("CARGO_BIN_EXE_naplps-render")).args(["check", "/no/such/page.nap"]).output().unwrap();
    assert_eq!(output.status.code(), Some(2));
}
