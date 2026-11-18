//! `naplps-render`: renders a NAPLPS page file to a binary PPM picture, or plays it into a
//! sequence of them.
//!
//! ```text
//! naplps-render [--width N] [--height N] [--palette-bits N] [--font FILE] [--tenths N]
//!               [--stage N] [--border N] [--dac-bits N] [--preamble] [--objects FILE]
//!               [--frames TICKS [--frame-step K] [--script FILE]] PAGE OUT.ppm
//! ```
//!
//! `--font` loads a stroke font in the library's text form (without one, text moves the cursor
//! but draws no glyphs). `--tenths` shows the colour map that many tenths of a second into BLINK
//! animation. `--stage N` stops after the page's Nth WAIT, showing the page as it stands during
//! that pause (0, the default, draws the whole page). `--border N` surrounds the picture with N
//! pixels of the page's border colour (RESET, Table 15). `--dac-bits 6` shows colours as a VGA card's 6-bit colour registers do, as PP3's
//! screen does (each primary rounded to 6 bits, then widened by repeating its top bits, as DOSBox
//! shows them). `--preamble` first sends the oracle's page preamble, so a frame compares with the
//! PP3 reference of the same page.
//!
//! `--objects FILE` gives the page its numbered objects (neoteletext-common `docs/animation.md`,
//! ANIM-11; the file's form is in [`play::objects`]), drawn over the stream's picture.
//!
//! `--frames TICKS` plays the page for that many ticks of one sixtieth of a second from tick 0
//! (ANIM-18): WAIT holds the stream back and BLINK changes the colour map on the ticks they are
//! due (ANIM-20), and `--script FILE` (`-` for standard input) applies ANIM-6's operations to the
//! objects at their ticks. A picture is written every `--frame-step` ticks (default 1) and
//! always for the last tick, each named with `-NNNNN`, its tick, before the extension. The
//! pictures of a run are the same on every machine and every run.
#![deny(
    clippy::indexing_slicing,
    clippy::string_slice,
    clippy::unwrap_used,
    clippy::expect_used,
    clippy::panic,
    clippy::arithmetic_side_effects,
    clippy::unreachable,
    clippy::todo,
    clippy::unimplemented
)]

use std::fs;
use std::io::Write as _;
use std::process::ExitCode;

use naplps::{Canvas, Event, Player, Rgb, StrokeFont, Terminal};

mod play;

/// The largest page file read: a megabyte, far beyond the largest page known (40,876 bytes).
const MAX_PAGE_BYTES: u64 = 1024 * 1024;
/// PP3's VGA screen.
const DEFAULT_WIDTH: u32 = 640;
/// See [`DEFAULT_WIDTH`].
const DEFAULT_HEIGHT: u32 = 480;
/// A 16-entry colour map, as PP3's VGA mode.
const DEFAULT_PALETTE_BITS: u32 = 4;
/// The widest border drawn: as wide as the largest canvas.
const MAX_BORDER: u32 = 4096;
/// The oracle's page preamble (neoteletext-renderer-naplps `naplps-oracle`, `PAGE_PREAMBLE`): ESC % A,
/// CAN, ESC 2/2 4/6, ESC 4/5 (END), NSR to row 0 column 0, SO, RESET 7F 7F.
const ORACLE_PREAMBLE: [u8; 16] =
    [0x1B, 0x25, 0x41, 0x18, 0x1B, 0x22, 0x46, 0x1B, 0x45, 0x1F, 0x40, 0x40, 0x0E, 0x20, 0x7F, 0x7F];

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(message) => {
            eprintln!("naplps-render: {message}");
            ExitCode::from(2)
        }
    }
}

/// The usage line.
const USAGE: &str = "usage: naplps-render [--width N] [--height N] [--palette-bits N] [--font FILE] [--tenths N] [--stage N] [--border N] [--dac-bits N] [--preamble] [--objects FILE] [--frames TICKS [--frame-step K] [--script FILE]] PAGE OUT.ppm";

/// How a picture is written: the border's width and the display's colour registers.
#[derive(Clone, Copy)]
struct Display {
    border: u32,
    dac_bits: u32,
}

#[allow(clippy::too_many_lines, reason = "one arm an option, then the two modes; splitting hides the option table")]
fn run() -> Result<(), String> {
    let mut width = DEFAULT_WIDTH;
    let mut height = DEFAULT_HEIGHT;
    let mut palette_bits = DEFAULT_PALETTE_BITS;
    let mut font_path = None;
    let mut tenths = None;
    let mut preamble = false;
    let mut display = Display { border: 0, dac_bits: 8 };
    let mut stage = None;
    let mut objects_path = None;
    let mut script_path = None;
    let mut frames = None;
    let mut frame_step = None;
    let mut operands = Vec::new();
    let mut arguments = std::env::args().skip(1);
    while let Some(argument) = arguments.next() {
        let mut value = |name: &str| arguments.next().ok_or_else(|| format!("{name} needs a value"));
        match argument.as_str() {
            "--width" => width = number(&value("--width")?)?,
            "--height" => height = number(&value("--height")?)?,
            "--palette-bits" => palette_bits = number(&value("--palette-bits")?)?,
            "--font" => font_path = Some(value("--font")?),
            "--tenths" => tenths = Some(number(&value("--tenths")?)?),
            "--preamble" => preamble = true,
            "--stage" => stage = Some(number(&value("--stage")?)?),
            "--border" => display.border = number(&value("--border")?)?.min(MAX_BORDER),
            "--dac-bits" => display.dac_bits = number(&value("--dac-bits")?)?.clamp(1, 8),
            "--objects" => objects_path = Some(value("--objects")?),
            "--script" => script_path = Some(value("--script")?),
            "--frames" => frames = Some(number(&value("--frames")?)?),
            "--frame-step" => frame_step = Some(number(&value("--frame-step")?)?),
            other if other.starts_with("--") => return Err(format!("unknown option {other}")),
            other => operands.push(other.to_owned()),
        }
    }
    let [page_path, out_path] = operands.as_slice() else {
        return Err(USAGE.to_owned());
    };
    let length = fs::metadata(page_path).map_err(|error| format!("{page_path}: {error}"))?.len();
    if length > MAX_PAGE_BYTES {
        return Err(format!("{page_path} is {length} bytes, more than {MAX_PAGE_BYTES}"));
    }
    let page = fs::read(page_path).map_err(|error| format!("{page_path}: {error}"))?;
    let mut canvas = Canvas::new(width, height).map_err(|error| error.to_string())?;
    let mut terminal = Terminal::new(palette_bits);
    if let Some(path) = font_path {
        let text = fs::read_to_string(&path).map_err(|error| format!("{path}: {error}"))?;
        terminal.set_font(StrokeFont::parse(&text).map_err(|error| format!("{path}: {error}"))?);
    }
    if let Some(path) = &objects_path {
        let objects = play::objects(&play::read_text(path)?).map_err(|error| format!("{path}: {error}"))?;
        terminal.set_objects(&objects).map_err(|error| format!("{path}: {error}"))?;
    }
    let mut events = Vec::new();
    if preamble {
        events.extend(terminal.feed(&mut canvas, &ORACLE_PREAMBLE));
    }
    if let Some(frames) = frames {
        if tenths.is_some() || stage.is_some() {
            return Err("--frames plays WAIT and BLINK itself; --tenths and --stage do not go with it".to_owned());
        }
        if !(1..=play::MAX_FRAMES).contains(&frames) {
            return Err(format!("--frames is 1 to {} ticks", play::MAX_FRAMES));
        }
        let frame_step = frame_step.unwrap_or(1);
        if frame_step == 0 {
            return Err("--frame-step is at least 1".to_owned());
        }
        let steps = match &script_path {
            Some(path) => play::script(&play::read_text(path)?).map_err(|error| format!("{path}: {error}"))?,
            None => Vec::new(),
        };
        events.extend(play_page(&mut terminal, &mut canvas, &page, &steps, (frames, frame_step), out_path, display)?);
    } else {
        if script_path.is_some() || frame_step.is_some() {
            return Err("--script and --frame-step need --frames".to_owned());
        }
        events.extend(draw_page(&mut terminal, &mut canvas, &page, stage.unwrap_or(0), page_path));
        let colours = terminal.palette().at(tenths.unwrap_or(0));
        if objects_path.is_some() {
            let mut presented = Canvas::new(width, height).map_err(|error| error.to_string())?;
            terminal.compose(&canvas, &mut presented).map_err(|error| error.to_string())?;
            write_picture(out_path, &presented, &colours, terminal.border(), display)?;
        } else {
            write_picture(out_path, &canvas, &colours, terminal.border(), display)?;
        }
    }
    if events.contains(&Event::LimitReached) {
        eprintln!("naplps-render: {page_path}: processing stopped at the limit on bytes processed");
    }
    Ok(())
}

/// Draws the whole page, or the page as it stands at its `stage`th WAIT.
fn draw_page(terminal: &mut Terminal, canvas: &mut Canvas, page: &[u8], stage: u32, page_path: &str) -> Vec<Event> {
    let mut events = Vec::new();
    if stage == 0 {
        events.extend(terminal.feed(canvas, page));
        events.extend(terminal.finish(canvas));
        return events;
    }
    let mut waits = 0u32;
    let mut rest = page;
    while waits < stage && !rest.is_empty() {
        let (taken, more) = terminal.feed_until_wait(canvas, rest);
        rest = rest.get(taken..).unwrap_or(&[]);
        waits = waits.saturating_add(
            u32::try_from(more.iter().filter(|event| matches!(event, Event::Wait(_))).count()).unwrap_or(u32::MAX),
        );
        events.extend(more);
    }
    if waits < stage {
        events.extend(terminal.finish(canvas));
        eprintln!("naplps-render: {page_path}: the page has {waits} WAITs, fewer than --stage {stage}; drawn whole");
    }
    events
}

/// Plays the page for `frames` ticks from tick 0, writing a picture every `frame_step` ticks
/// and for the last tick (ANIM-18). The picture of a tick shows the stream as far as its WAITs
/// let it come by that tick, the script's operations of that tick and of every tick before, the
/// cycles' frames at that tick, and the colour map BLINK gives at that tick.
fn play_page(
    terminal: &mut Terminal,
    canvas: &mut Canvas,
    page: &[u8],
    steps: &[play::Step],
    (frames, frame_step): (u32, u32),
    out_path: &str,
    display: Display,
) -> Result<Vec<Event>, String> {
    let mut presented = Canvas::new(canvas.width(), canvas.height()).map_err(|error| error.to_string())?;
    let mut player = Player::new();
    let mut animator = play::Animator::default();
    let mut events = player.push(terminal, canvas, page);
    events.extend(player.end(terminal, canvas));
    let mut steps = steps.iter().peekable();
    for tick in 0..frames {
        if tick > 0 {
            events.extend(player.advance(terminal, canvas, 1));
        }
        while let Some(step) = steps.next_if(|step| step.tick <= tick) {
            animator.apply(terminal, tick, step);
        }
        animator.tick(terminal, tick);
        terminal.compose(canvas, &mut presented).map_err(|error| error.to_string())?;
        if tick.checked_rem(frame_step) == Some(0) || tick.saturating_add(1) == frames {
            let colours = player.colours(terminal);
            write_picture(&play::numbered(out_path, tick), &presented, &colours, terminal.border(), display)?;
        }
    }
    let late = steps.count();
    if late > 0 {
        eprintln!("naplps-render: {late} script lines are at or after tick {frames} and were not played");
    }
    if animator.ignored > 0 {
        eprintln!(
            "naplps-render: {} operations did nothing: no such object, or more cycles than the limit",
            animator.ignored
        );
    }
    Ok(events)
}

/// Writes `canvas` as a binary PPM with the colour map `colours`, inside its border.
fn write_picture(
    path: &str,
    canvas: &Canvas,
    colours: &[Rgb],
    border_entry: u8,
    display: Display,
) -> Result<(), String> {
    let Display { border, dac_bits } = display;
    let rgb = |entry: u8| {
        naplps::palette::through_register(colours.get(usize::from(entry)).copied().unwrap_or([0, 0, 0]), dac_bits)
    };
    let (width, height) = (canvas.width(), canvas.height());
    let (outer_width, outer_height) =
        (width.saturating_add(border.saturating_mul(2)), height.saturating_add(border.saturating_mul(2)));
    let border_rgb = rgb(border_entry);
    let mut ppm = format!("P6\n{outer_width} {outer_height}\n255\n").into_bytes();
    for y in 0..outer_height {
        for x in 0..outer_width {
            let inside = (border..border.saturating_add(width)).contains(&x)
                && (border..border.saturating_add(height)).contains(&y);
            let colour = if inside {
                canvas.pixel(x.saturating_sub(border), y.saturating_sub(border)).map_or([0, 0, 0], rgb)
            } else {
                border_rgb
            };
            ppm.extend_from_slice(&colour);
        }
    }
    let mut file = fs::File::create(path).map_err(|error| format!("{path}: {error}"))?;
    file.write_all(&ppm).map_err(|error| format!("{path}: {error}"))?;
    Ok(())
}

fn number(text: &str) -> Result<u32, String> {
    text.parse().map_err(|_| format!("{text:?} is not a whole number"))
}
