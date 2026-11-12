//! The oracle reproduces independently made PP3 screenshots.
//!
//! The 18 JPEGs of the `rosetta_stone` testbed (Telidon project, Nick Fox-Gieg, 2018) are
//! screenshots of PP3 drawing the testbed's 18 pages, cropped from a larger screen. Capturing the
//! same pages through the oracle and finding them the same is evidence that the oracle's PP3 is
//! the PP3 those screenshots came from, set up the same way. The tolerance absorbs JPEG: a
//! channel tolerance of 64 for chroma smear on saturated edges, a displacement of one pixel for
//! JPEG ringing, and a one-pixel trim because one crop (`arc.jpg`) caught two pixels of whatever
//! was beside PP3's screen.
#![allow(clippy::unwrap_used, clippy::expect_used, clippy::panic, reason = "a test fails by panicking")]

use std::path::PathBuf;
use std::process::Command;

/// The SHA-256 of every page and screenshot used, as `sha256sum` prints them, relative to the
/// testbed directory. The files are not copied here (they belong to the Telidon project); they
/// are read from the reference collection and must be exactly these.
const PINNED: &str = include_str!("rosetta.sha256");

fn testbed() -> PathBuf {
    std::env::var_os("NAPLPS_ROSETTA_DIR").map_or_else(
        || {
            PathBuf::from(std::env::var_os("HOME").expect("HOME"))
                .join("devel/teletext-reference/NAPLPS/Telidon-master/tools/rosetta_stone/testbed")
        },
        PathBuf::from,
    )
}

#[test]
#[ignore = "needs DOSBox, Xvfb, socat, xdotool and ffmpeg, and PP3 and the rosetta_stone testbed from ~/devel/teletext-reference (or NAPLPS_PP3_DIR and NAPLPS_ROSETTA_DIR); takes about a minute"]
fn the_oracle_reproduces_the_rosetta_stone_screenshots() {
    let testbed = testbed();
    let pins = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/rosetta.sha256");
    let checked = Command::new("sha256sum").args(["--quiet", "-c"]).arg(&pins).current_dir(&testbed).status().unwrap();
    assert!(checked.success(), "the testbed in {} differs from tests/rosetta.sha256", testbed.display());

    let pages: Vec<PathBuf> = PINNED
        .lines()
        .filter_map(|line| line.split_whitespace().nth(1))
        .filter(|path| {
            std::path::Path::new(path).extension().is_some_and(|extension| extension.eq_ignore_ascii_case("nap"))
        })
        .map(|path| testbed.join(path))
        .collect();
    let mut names: Vec<String> =
        pages.iter().map(|page| page.file_stem().unwrap().to_string_lossy().into_owned()).collect();
    names.sort();
    assert_eq!(names.len(), 18);

    let scratch = PathBuf::from(env!("CARGO_TARGET_TMPDIR")).join("rosetta");
    let _ = std::fs::remove_dir_all(&scratch);
    let oracle = env!("CARGO_BIN_EXE_naplps-oracle");
    let captured = Command::new(oracle)
        .arg("capture")
        .arg("--out")
        .arg(scratch.join("frames"))
        .arg("--work")
        .arg(scratch.join("work"))
        .args(&pages)
        .status()
        .unwrap();
    assert!(captured.success(), "capture failed");

    let compared = Command::new(oracle)
        .args(["compare", "--place", "--trim", "1", "--channel", "64", "--displacement", "1"])
        .arg(testbed.join("jpg"))
        .arg(scratch.join("frames"))
        .output()
        .unwrap();
    let report = String::from_utf8_lossy(&compared.stdout);
    let mut passed: Vec<&str> =
        report.lines().filter(|line| line.contains(": pass ")).filter_map(|line| line.split(':').next()).collect();
    passed.sort_unstable();
    assert_eq!(passed, names, "every screenshot must match its capture:\n{report}");
    assert!(compared.status.success(), "{report}");
}
