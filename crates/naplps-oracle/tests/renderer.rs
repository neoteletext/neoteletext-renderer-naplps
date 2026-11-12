//! The renderer (crate `naplps`) against PP3, and against the whole collection.
//!
//! The `rosetta_stone` pages are rendered by the library exactly as the oracle sends them to PP3
//! (its page preamble first), with the Microstar font recovered from PP3 and PP3's 6-bit VGA
//! colour registers, and compared with PP3's own frames at channel tolerance 0 and displacement 1
//! (REQ-5751). The set of pages that do not yet agree is asserted exactly, so a regression fails
//! and an improvement must be acknowledged here.
#![allow(clippy::unwrap_used, clippy::expect_used, clippy::panic, reason = "a test fails by panicking")]

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::time::Instant;

use naplps::palette::through_register;
use naplps::{Canvas, Event, StrokeFont, Terminal};
use naplps_oracle::compare::{Tolerance, compare};
use naplps_oracle::frame::Frame;
use naplps_oracle::session::PAGE_PREAMBLE;
use naplps_oracle::tools;

/// PP3's screen and its colour registers.
const WIDTH: u32 = 640;
const HEIGHT: u32 = 480;
const PALETTE_BITS: u32 = 4;
const VGA_REGISTER_BITS: u32 = 6;

/// Pages whose frames do not yet agree with PP3, and why:
/// - `circf`: a filled circle's edge differs by about a pixel in places (73 of 17,600 pixels);
/// - `hello`, `text`: text at other sizes and rotations than the default, where PP3 scales its
///   font differently from the default-size fit the renderer uses.
const KNOWN_DIFFERENCES: [&str; 3] = ["circf", "hello", "text"];

fn reference() -> PathBuf {
    std::env::var_os("NAPLPS_REFERENCE_DIR").map_or_else(
        || PathBuf::from(std::env::var_os("HOME").expect("HOME")).join("devel/teletext-reference/NAPLPS"),
        PathBuf::from,
    )
}

fn font(reference: &Path) -> StrokeFont {
    let text = std::fs::read_to_string(reference.join("fonts-extracted/data/microstar.strokes")).unwrap();
    StrokeFont::parse(&text).unwrap()
}

/// Renders a page as the oracle shows it to PP3, as RGB on PP3's screen.
fn render(page: &[u8], font: &StrokeFont) -> (Frame, Vec<Event>) {
    let mut canvas = Canvas::new(WIDTH, HEIGHT).unwrap();
    let mut terminal = Terminal::new(PALETTE_BITS);
    terminal.set_font(font.clone());
    let mut events = terminal.feed(&mut canvas, &PAGE_PREAMBLE);
    events.extend(terminal.feed(&mut canvas, page));
    events.extend(terminal.finish(&mut canvas));
    let colours = terminal.palette().colours();
    let rgb: Vec<u8> = canvas
        .pixels()
        .iter()
        .flat_map(|&entry| {
            through_register(colours.get(usize::from(entry)).copied().unwrap_or([0; 3]), VGA_REGISTER_BITS)
        })
        .collect();
    (Frame::new(WIDTH, HEIGHT, rgb).unwrap(), events)
}

#[test]
#[ignore = "needs ffmpeg and ffprobe, and the rosetta_stone pages, PP3's frames of them and the recovered Microstar font from ~/devel/teletext-reference/NAPLPS (or NAPLPS_REFERENCE_DIR)"]
fn the_renderer_agrees_with_pp3_on_the_rosetta_pages() {
    let reference = reference();
    let font = font(&reference);
    let pages = reference.join("Telidon-master/tools/rosetta_stone/testbed/nap");
    let frames = reference.join("pp3-reference-frames/rosetta");
    let mut names: Vec<String> = std::fs::read_dir(&pages)
        .unwrap()
        .map(|entry| entry.unwrap().path())
        .filter(|path| path.extension().is_some_and(|extension| extension.eq_ignore_ascii_case("nap")))
        .map(|path| path.file_stem().unwrap().to_string_lossy().into_owned())
        .collect();
    names.sort();
    assert_eq!(names.len(), 18);
    let mut differing = Vec::new();
    let mut report = String::new();
    for name in &names {
        let page = std::fs::read(pages.join(format!("{name}.nap"))).unwrap();
        let (ours, _) = render(&page, &font);
        let theirs = tools::load_picture(&frames.join(format!("{name}.png"))).unwrap();
        let result = compare(&theirs, &ours, Tolerance { channel: 0, displacement: 1 }).unwrap();
        let _ = writeln!(
            report,
            "{name}: {} differing, unexplained {} / {}",
            result.differing, result.unexplained_in_candidate, result.unexplained_in_reference
        );
        if !result.passes() {
            differing.push(name.as_str());
        }
    }
    assert_eq!(differing, KNOWN_DIFFERENCES, "pages differing from PP3 changed:\n{report}");
}

#[test]
#[ignore = "needs the NAPLPS pages of ~/devel/teletext-reference/NAPLPS (or NAPLPS_REFERENCE_DIR) and the recovered Microstar font; renders every page"]
fn every_page_of_the_collection_renders_within_its_budget() {
    let reference = reference();
    let font = font(&reference);
    let mut pages = Vec::new();
    let mut directories = vec![reference.clone()];
    while let Some(directory) = directories.pop() {
        for entry in std::fs::read_dir(&directory).unwrap() {
            let path = entry.unwrap().path();
            if path.is_dir() {
                directories.push(path);
            } else {
                let name = path.file_name().unwrap().to_string_lossy().to_ascii_lowercase();
                let is_page = path.extension().is_some_and(|extension| extension.eq_ignore_ascii_case("nap"))
                    || (name.starts_with("naplps.0") && name.len() == 10);
                if is_page {
                    pages.push(path);
                }
            }
        }
    }
    pages.sort();
    assert!(pages.len() > 100, "only {} pages found under {}", pages.len(), reference.display());
    let start = Instant::now();
    let mut limited = Vec::new();
    for path in &pages {
        let page = std::fs::read(path).unwrap();
        let (_, events) = render(&page, &font);
        if events.contains(&Event::LimitReached) {
            limited.push(path.display().to_string());
        }
    }
    println!("{} pages rendered in {} ms", pages.len(), start.elapsed().as_millis());
    assert!(limited.is_empty(), "pages stopped at the processing limit: {limited:?}");
}
