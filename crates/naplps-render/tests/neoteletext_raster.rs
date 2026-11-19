//! REQ-5819 version 2, DEC-6857 and `docs/naplps-raster.md` RAS-11 in `naplps-render`: by
//! default the page is drawn on the 480 by 500 teletext raster, its display area 480 by 460 on
//! lines 20 to 479 and rows 0 and 24 in the page's background colour; `--double` at twice the
//! size; `--width`, `--height` and `--border` a bare canvas.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

mod common;

use std::fs;
use std::path::PathBuf;
use std::process::Command;

use common::{SO, rectangle};

/// Renders `bytes` with `options` and returns the picture's bytes.
fn render(name: &str, bytes: &[u8], options: &[&str]) -> Vec<u8> {
    let base = PathBuf::from(env!("CARGO_TARGET_TMPDIR")).join(format!("raster-{name}"));
    fs::create_dir_all(&base).unwrap();
    let page = base.join("page.nap");
    let out = base.join("page.ppm");
    fs::write(&page, bytes).unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_naplps-render")).args(options).arg(&page).arg(&out).output().unwrap();
    assert!(output.status.success(), "{}", String::from_utf8_lossy(&output.stderr));
    fs::read(out).unwrap()
}

#[test]
fn the_raster_holds_480_by_460_on_lines_20_to_479_between_rows_0_and_24_of_the_pages_background() {
    // RESET (opcode 2/0) with 010 in bits 4 to 6 (Table 15) clears the display to the drawing
    // colour, then a rectangle in another entry from the display's bottom left corner.
    let mut bytes = vec![SO, 0x20, 0x50, 0x40];
    bytes.extend(rectangle(2, 0, 0, 64, 16));
    for (options, width, height, lines) in [(&[][..], 480, 500, 20), (&["--double"][..], 960, 1000, 40)] {
        let picture = render(&format!("raster-{width}"), &bytes, options);
        let header = format!("P6\n{width} {height}\n255\n");
        assert!(picture.starts_with(header.as_bytes()), "{options:?}: a picture of {width} by {height}");
        let at =
            |x: usize, y: usize| -> [u8; 3] { picture[header.len() + (y * width + x) * 3..][..3].try_into().unwrap() };
        let background = at(width - 1, lines);
        for y in (0..lines).chain(height - lines..height) {
            for x in [0, width / 2, width - 1] {
                assert_eq!(at(x, y), background, "{options:?}: line {y} of rows 0 and 24 is the page's background");
            }
        }
        // The display area's last line is the raster's line `height - lines - 1`.
        assert_ne!(at(0, height - lines - 1), background, "{options:?}: the rectangle reaches the display's bottom");
        assert_eq!(at(0, height - lines), background, "{options:?}: below it, row 24");
        assert_eq!(picture.len(), header.len() + width * height * 3);
    }
}

#[test]
fn a_size_or_a_border_draws_a_bare_canvas() {
    // RAS-11: --width and --height draw a bare canvas, the oracle's 640 by 480 among them; a
    // border alone surrounds the receiver's canvas.
    let bytes = [SO];
    for (options, header) in [
        (&["--width", "640", "--height", "480"][..], "P6\n640 480\n255\n"),
        (&["--width", "320"][..], "P6\n320 460\n255\n"),
        (&["--border", "4"][..], "P6\n488 468\n255\n"),
    ] {
        let picture = render("bare", &bytes, options);
        assert!(picture.starts_with(header.as_bytes()), "{options:?}: {header:?}");
    }
}

#[test]
fn double_takes_no_size_or_border_and_neoteletext_is_gone() {
    let base = PathBuf::from(env!("CARGO_TARGET_TMPDIR")).join("raster-refused");
    fs::create_dir_all(&base).unwrap();
    let page = base.join("page.nap");
    fs::write(&page, [SO]).unwrap();
    for options in [&["--double", "--width", "640"][..], &["--double", "--border", "4"], &["--neoteletext"]] {
        let output = Command::new(env!("CARGO_BIN_EXE_naplps-render"))
            .args(options)
            .arg(&page)
            .arg(base.join("out.ppm"))
            .output()
            .unwrap();
        assert!(!output.status.success(), "{options:?} is refused");
    }
}
