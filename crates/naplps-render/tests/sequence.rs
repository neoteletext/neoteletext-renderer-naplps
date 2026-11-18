//! `naplps-render --frames`: a page played into a sequence of pictures (neoteletext-common
//! `docs/animation.md`, ANIM-18; REQ-6531). The fixture is played twice and the two runs are
//! compared, and the pictures are checked against what ANIM-14 (a cycle), ANIM-6 (a move) and
//! ANIM-20 (WAIT and BLINK on ticks) say each tick shows.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

/// The sequence's format: raised, with the reason, when a change alters any picture
/// (DEVELOPMENT.md section 8). 1: the first sequence, 18 November 2026.
const SEQUENCE_FORMAT: u32 = 1;
const WIDTH: usize = 640;
const HEIGHT: usize = 480;
/// The bytes before a 640 by 480 picture's pixels: `P6\n640 480\n255\n`.
const HEADER: usize = 15;

const SO: u8 = 0x0E;
const DEF_MACRO: u8 = 0x80;
const END: u8 = 0x85;

/// A three-byte coordinate pair, (`x`/256, `y`/256) of the unit screen (ANSI X3.110-1983
/// section 5.3.2.2.3).
fn pair(x: u16, y: u16) -> [u8; 3] {
    let byte = |shift: u16| 0x40 | u8::try_from(((x >> shift) & 7) << 3 | ((y >> shift) & 7)).unwrap();
    [byte(6), byte(3), byte(0)]
}

/// SELECT COLOR `entry`, POINT SET to (`x`, `y`), RECT FILLED of (`width`, `height`).
fn rectangle(entry: u8, x: u16, y: u16, width: u16, height: u16) -> Vec<u8> {
    let mut bytes = vec![SO, 0x3E, 0x40 | (entry << 2), 0x24];
    bytes.extend(pair(x, y));
    bytes.push(0x31);
    bytes.extend(pair(width, height));
    bytes
}

/// The page: macros 2/0 to 2/3, a rectangle of entries 3 to 6 each; a rectangle of entry 1
/// that blinks to entry 7, 5 tenths on and 5 off; a WAIT of 2 tenths; a rectangle of entry 2.
fn page() -> Vec<u8> {
    let mut page = Vec::new();
    for frame in 0..4u8 {
        page.extend([DEF_MACRO, 0x20 + frame]);
        page.extend(rectangle(3 + frame, 0, 0, 16, 16));
        page.push(END);
    }
    page.extend(rectangle(1, 0, 0, 64, 32));
    page.extend([0x3F, 0x40 | (7 << 2), 0x45, 0x45, 0x40]);
    page.extend([0x3D, 0x5C, 0x42]);
    page.extend(rectangle(2, 128, 0, 64, 32));
    page
}

const OBJECTS: &str = "# one four-frame sprite and a region that covers part of the page\n\
                       macro 1 2 0 300 100 41 40 0 440 20,21,22,23\n\
                       region 2 1 0 0 440 40 40 9\n";

const SCRIPT: &str = "0 cycle 1 0 3 2\n\
                      10 move 1 20 0 relative\n\
                      12 hide 2\n\
                      14 stop_cycle 1\n\
                      14 frame 1 3\n\
                      99 show 7\n";

/// Plays the fixture into `directory` and returns each picture's tick and bytes.
fn play(directory: &Path) -> Vec<(u32, Vec<u8>)> {
    let _ = fs::remove_dir_all(directory);
    fs::create_dir_all(directory).unwrap();
    let file = |name: &str, content: &[u8]| {
        let path = directory.join(name);
        fs::write(&path, content).unwrap();
        path
    };
    let page = file("page.nap", &page());
    let objects = file("objects.txt", OBJECTS.as_bytes());
    let script = file("script.txt", SCRIPT.as_bytes());
    let output = Command::new(env!("CARGO_BIN_EXE_naplps-render"))
        .args(["--frames", "40", "--frame-step", "3", "--objects"])
        .arg(&objects)
        .arg("--script")
        .arg(&script)
        .arg(&page)
        .arg(directory.join("frame.ppm"))
        .output()
        .unwrap();
    assert!(output.status.success(), "{}", String::from_utf8_lossy(&output.stderr));
    let mut pictures = Vec::new();
    for tick in 0..40u32 {
        let path = directory.join(format!("frame-{tick:05}.ppm"));
        if let Ok(bytes) = fs::read(path) {
            pictures.push((tick, bytes));
        }
    }
    pictures
}

/// The colour at (`x`, `y`) of a picture.
fn colour(picture: &[u8], x: usize, y: usize) -> [u8; 3] {
    let at = HEADER + (y * WIDTH + x) * 3;
    [picture[at], picture[at + 1], picture[at + 2]]
}

#[test]
fn a_page_played_twice_gives_the_same_pictures_and_they_are_the_animation() {
    assert_eq!(SEQUENCE_FORMAT, 1);
    let base = PathBuf::from(env!("CARGO_TARGET_TMPDIR"));
    let first = play(&base.join("sequence-first"));
    let second = play(&base.join("sequence-second"));
    // ANIM-18: a picture every 3 ticks, and always the last.
    let ticks: Vec<u32> = first.iter().map(|(tick, _)| *tick).collect();
    assert_eq!(ticks, vec![0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39]);
    assert!(first == second, "the pictures of a run are the same on every run");
    let picture = |tick: u32| &first.iter().find(|(of, _)| *of == tick).unwrap().1;
    assert!(first.iter().all(|(_, bytes)| bytes.len() == HEADER + WIDTH * HEIGHT * 3));
    // The default colour map's entries, read from where nothing else draws.
    let black = colour(picture(0), 639, 0);
    let entry = |number: u8| {
        // The stream's rectangle of entry 1 and, after the WAIT, of entry 2; the sprite's
        // frames are entries 3 to 6 and the region's cover is entry 9.
        match number {
            2 => colour(picture(39), 330, 470),
            other => panic!("entry {other} is not read by this test"),
        }
    };
    // ANIM-20, WAIT: 2 tenths are 12 ticks, so the second rectangle appears at tick 12.
    assert_eq!(colour(picture(9), 330, 470), black, "tick 9: the WAIT is still played");
    assert_ne!(colour(picture(12), 330, 470), black, "tick 12: what follows the WAIT is drawn");
    assert_eq!(colour(picture(12), 330, 470), entry(2));
    // ANIM-20, BLINK: 5 tenths on and 5 off from tick 0, so the colour changes at tick 30.
    let blinking = |tick: u32| colour(picture(tick), 100, 470);
    assert_eq!(blinking(0), blinking(27));
    assert_ne!(blinking(27), blinking(30));
    assert_eq!(blinking(30), blinking(39));
    // ANIM-14: the cycle starts at tick 1 with a period of 2: frame ((t - 1) / 2) mod 4.
    let sprite = |tick: u32, x: usize| colour(picture(tick), x, 120);
    let frames: Vec<[u8; 3]> = [0, 3, 6, 9].iter().map(|&tick| sprite(tick, 310)).collect();
    assert_eq!(frames[0], frames[3], "ticks 0 and 9 both show frame 0");
    assert_ne!(frames[0], frames[1], "tick 3 shows frame 1");
    assert_ne!(frames[1], frames[2], "tick 6 shows frame 2");
    // ANIM-6: the relative move at tick 10 takes the sprite 20 pixels right, leaving nothing.
    assert_eq!(sprite(12, 305), black, "the sprite has left its old place");
    assert_ne!(sprite(12, 350), black, "and is drawn 20 pixels to the right");
    assert_eq!(sprite(9, 350), black);
    // `frame` at tick 14 stops the cycle on frame 3.
    assert_eq!(sprite(15, 350), sprite(39, 350));
    assert_ne!(sprite(15, 350), frames[0]);
    // ANIM-11: the region hidden at tick 12 is its cover over the stream's rectangle.
    assert_eq!(colour(picture(9), 20, 460), blinking(9), "shown, the region is the stream's picture");
    assert_ne!(colour(picture(12), 20, 460), blinking(12), "hidden, it is its cover");
}

#[test]
fn options_that_do_not_go_together_are_refused() {
    let run = |arguments: &[&str]| {
        let output = Command::new(env!("CARGO_BIN_EXE_naplps-render")).args(arguments).output().unwrap();
        (output.status.code(), String::from_utf8_lossy(&output.stderr).into_owned())
    };
    let manifest = concat!(env!("CARGO_MANIFEST_DIR"), "/Cargo.toml");
    let out = concat!(env!("CARGO_TARGET_TMPDIR"), "/refused.ppm");
    for arguments in [
        ["--frames", "0", manifest, out].as_slice(),
        ["--frames", "36001", manifest, out].as_slice(),
        ["--frames", "5", "--frame-step", "0", manifest, out].as_slice(),
        ["--frames", "5", "--tenths", "3", manifest, out].as_slice(),
        ["--frames", "5", "--stage", "1", manifest, out].as_slice(),
        ["--script", manifest, manifest, out].as_slice(),
        ["--frame-step", "2", manifest, out].as_slice(),
    ] {
        let (code, message) = run(arguments);
        assert_eq!(code, Some(2), "{arguments:?}: {message}");
    }
}
