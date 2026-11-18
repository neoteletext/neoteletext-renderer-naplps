//! REQ-5819 and DEC-6667 in `naplps-render`: `--neoteletext` draws the page on 480 by 462
//! pixels centred in the 480 by 500 teletext raster, the 19 lines above and below in the page's
//! background colour, and `--double` at twice the size.
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
fn the_neoteletext_raster_holds_480_by_462_between_19_lines_of_the_pages_background() {
    // RESET (opcode 2/0) with 010 in bits 4 to 6 (Table 15) clears the display to the drawing
    // colour, then a rectangle in another entry from the display's bottom left corner.
    let mut bytes = vec![SO, 0x20, 0x50, 0x40];
    bytes.extend(rectangle(2, 0, 0, 64, 16));
    for (options, width, height, lines) in
        [(&["--neoteletext"][..], 480, 500, 19), (&["--neoteletext", "--double"][..], 960, 1000, 38)]
    {
        let picture = render(&format!("raster-{width}"), &bytes, options);
        let header = format!("P6\n{width} {height}\n255\n");
        assert!(picture.starts_with(header.as_bytes()), "{options:?}: a picture of {width} by {height}");
        let at =
            |x: usize, y: usize| -> [u8; 3] { picture[header.len() + (y * width + x) * 3..][..3].try_into().unwrap() };
        let background = at(width - 1, lines);
        for y in (0..lines).chain(height - lines..height) {
            for x in [0, width / 2, width - 1] {
                assert_eq!(at(x, y), background, "{options:?}: border line {y} is the page's background");
            }
        }
        // The display area's last line is the raster's line `height - lines - 1`.
        assert_ne!(at(0, height - lines - 1), background, "{options:?}: the rectangle reaches the display's bottom");
        assert_eq!(at(0, height - lines), background, "{options:?}: below it, the border");
        assert_eq!(picture.len(), header.len() + width * height * 3);
    }
}

#[test]
fn neoteletext_takes_no_size_or_border_of_its_own() {
    let base = PathBuf::from(env!("CARGO_TARGET_TMPDIR")).join("raster-refused");
    fs::create_dir_all(&base).unwrap();
    let page = base.join("page.nap");
    fs::write(&page, [SO]).unwrap();
    for options in [&["--neoteletext", "--width", "640"][..], &["--neoteletext", "--border", "4"], &["--double"]] {
        let output = Command::new(env!("CARGO_BIN_EXE_naplps-render"))
            .args(options)
            .arg(&page)
            .arg(base.join("out.ppm"))
            .output()
            .unwrap();
        assert!(!output.status.success(), "{options:?} is refused");
    }
}
