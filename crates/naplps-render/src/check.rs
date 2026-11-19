//! `naplps-render check`: an authoring check of a NAPLPS page, as `regis-minify` checks a `ReGIS`
//! picture by rendering it (DEC-6638 item 7, row 9.3). It draws the page with the renderer the
//! receiver uses, on the receiver's canvas of 480 by 460 (REQ-6646, `docs/naplps-raster.md`
//! RAS-11), and reports what an author needs to know: how much of the picture the page
//! draws on, its objects and title, and every byte the renderer passed over or refused.
//!
//! ```text
//! naplps-render check [--font FILE] [--objects FILE] [--title TEXT] PAGE
//! ```
//!
//! The exit status is 0 when nothing was refused (bytes passed over are reported, not failed:
//! the standard gives them no effect), 1 when the renderer refused part of the page, the
//! objects or the title, and 2 when the check could not run (a file could not be read, a
//! malformed option).

use std::fmt::Write as _;
use std::fs;

use naplps::limits::{DISPLAY_FIRST_LINE, RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_PIXELS, RECEIVER_CANVAS_WIDTH};
use naplps::{Canvas, Event, ObjectKind, Refusal, StrokeFont, Terminal};

use crate::play;

/// The usage line.
pub const USAGE: &str = "usage: naplps-render check [--font FILE] [--objects FILE] [--title TEXT] PAGE";

/// What the check found: the report's text, and whether anything was refused.
pub struct Outcome {
    /// The report, one finding a line.
    pub report: String,
    /// Whether the renderer refused part of the page, its objects or its title.
    pub refused: bool,
}

/// Runs the check on the command line's arguments after `check`.
///
/// # Errors
///
/// A message when the check cannot run: an unknown option, a missing operand, or a file that
/// cannot be read.
pub fn run(arguments: impl Iterator<Item = String>) -> Result<Outcome, String> {
    let mut font_path = None;
    let mut objects_path = None;
    let mut title = None;
    let mut operands = Vec::new();
    let mut arguments = arguments;
    while let Some(argument) = arguments.next() {
        let mut value = |name: &str| arguments.next().ok_or_else(|| format!("{name} needs a value"));
        match argument.as_str() {
            "--font" => font_path = Some(value("--font")?),
            "--objects" => objects_path = Some(value("--objects")?),
            "--title" => title = Some(value("--title")?),
            other if other.starts_with("--") => return Err(format!("unknown option {other}")),
            other => operands.push(other.to_owned()),
        }
    }
    let [page_path] = operands.as_slice() else {
        return Err(USAGE.to_owned());
    };
    let page = crate::read_page(page_path)?;
    let mut terminal = Terminal::new(crate::DEFAULT_PALETTE_BITS);
    if let Some(path) = font_path {
        let text = fs::read_to_string(&path).map_err(|error| format!("{path}: {error}"))?;
        terminal.set_font(StrokeFont::parse(&text).map_err(|error| format!("{path}: {error}"))?);
    }
    let objects = match &objects_path {
        Some(path) => Some(play::objects(&play::read_text(path)?).map_err(|error| format!("{path}: {error}"))?),
        None => None,
    };
    Ok(check(&mut terminal, &page, objects.as_deref(), title.as_deref()))
}

/// Checks `page` on `terminal`, with its objects and title if it has them.
fn check(terminal: &mut Terminal, page: &[u8], objects: Option<&[naplps::Object]>, title: Option<&str>) -> Outcome {
    let mut report = String::new();
    let mut refused = false;
    let mut line = |text: String| {
        report.push_str(&text);
        report.push('\n');
    };
    let Ok(mut canvas) = Canvas::new(RECEIVER_CANVAS_WIDTH, RECEIVER_CANVAS_HEIGHT) else {
        return Outcome { report: "the picture could not be made\n".to_owned(), refused: true };
    };
    let mut events = terminal.feed(&mut canvas, page);
    events.extend(terminal.finish(&mut canvas));
    line(format!("page: {} bytes", page.len()));

    // How much of the picture the page draws on: the rectangle of every pixel it wrote, in
    // raster dots (DEC-6853), the canvas's row 0 being raster line 20 (DEC-6857).
    match terminal.take_damage() {
        Some(rect) => {
            let percent = rect.area().saturating_mul(100).checked_div(RECEIVER_CANVAS_PIXELS).unwrap_or(0);
            let line_of = |row: u32| row.saturating_add(DISPLAY_FIRST_LINE);
            line(format!(
                "drawn: x {} to {}, y {} to {} of the display area, {RECEIVER_CANVAS_WIDTH} by {RECEIVER_CANVAS_HEIGHT} dots from line {DISPLAY_FIRST_LINE} ({percent} % of it)",
                rect.x,
                rect.right().saturating_sub(1),
                line_of(rect.y),
                line_of(rect.bottom().saturating_sub(1)),
            ));
        }
        None => line("drawn: nothing".to_owned()),
    }
    let waits = events.iter().filter(|event| matches!(event, Event::Wait(_))).count();
    let tenths: u64 = events
        .iter()
        .map(|event| if let Event::Wait(tenths) = event { u64::from(*tenths) } else { 0 })
        .fold(0, u64::saturating_add);
    if waits > 0 {
        line(format!("waits: {waits}, {tenths} tenths of a second in all"));
    }

    match title {
        Some(title) => match terminal.set_title(title) {
            Ok(()) => line(format!("title: {title:?}")),
            Err(error) => {
                refused = true;
                line(format!("REFUSED title: {error}"));
            }
        },
        None => line("title: none".to_owned()),
    }

    if let Some(objects) = objects {
        match terminal.set_objects(objects) {
            Ok(()) => {
                line(format!("objects: {}", objects.len()));
                for object in terminal.objects() {
                    line(describe(terminal, object));
                }
            }
            Err(error) => {
                refused = true;
                line(format!("REFUSED objects: {error}"));
            }
        }
    }

    let diagnostics = terminal.diagnostics();
    if diagnostics.passed_over > 0 {
        line(format!(
            "passed over: {} bytes with no effect, the first at offset {}",
            diagnostics.passed_over,
            diagnostics.first_passed_over.unwrap_or(0),
        ));
    }
    for kind in Refusal::ALL {
        let count = diagnostics.count(kind);
        if count > 0 {
            refused = true;
            line(format!("REFUSED {}: {count}", kind.name()));
        }
    }
    if let Some(first) = diagnostics.first_refused {
        line(format!("the first refusal at offset {first}"));
    }
    line(if refused { "result: refused".to_owned() } else { "result: clean".to_owned() });
    Outcome { report, refused }
}

/// One line describing an object as the renderer took it.
fn describe(terminal: &Terminal, object: &naplps::Object) -> String {
    let mut text = format!(
        "  object {}: {}, layer {}, order {}, at ({}, {}) {} by {}",
        object.number,
        if object.kind == ObjectKind::Macro { "macro" } else { "region" },
        object.layer,
        object.order,
        object.x,
        object.y,
        object.width,
        object.height,
    );
    if !object.frames.is_empty() {
        let frames: Vec<String> = object.frames.iter().map(|code| format!("{code:02X}")).collect();
        let _ = write!(text, ", frames {}", frames.join(","));
    }
    if object.detectable {
        text.push_str(", detectable");
    }
    if !object.label.is_empty() {
        let _ = write!(text, ", label {:?}", object.label);
    }
    if object.shown && terminal.bounds(object.number).is_none() {
        text.push_str(", WHOLLY OFF THE PICTURE");
    }
    text
}
