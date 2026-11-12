//! `naplps-render`: renders a NAPLPS page file to a binary PPM picture.
//!
//! ```text
//! naplps-render [--width N] [--height N] [--palette-bits N] [--font FILE] [--tenths N]
//!               [--dac-bits N] [--preamble] PAGE OUT.ppm
//! ```
//!
//! `--font` loads a stroke font in the library's text form (without one, text moves the cursor
//! but draws no glyphs). `--tenths` shows the colour map that many tenths of a second into BLINK
//! animation. `--dac-bits 6` shows colours as a VGA card's 6-bit colour registers do, as PP3's
//! screen does (each primary rounded to 6 bits, then widened by repeating its top bits, as DOSBox
//! shows them). `--preamble` first sends the oracle's page preamble, so a frame compares with the
//! PP3 reference of the same page.
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

use naplps::{Canvas, Event, StrokeFont, Terminal};

/// The largest page file read: a megabyte, far beyond the largest page known (40,876 bytes).
const MAX_PAGE_BYTES: u64 = 1024 * 1024;
/// PP3's VGA screen.
const DEFAULT_WIDTH: u32 = 640;
/// See [`DEFAULT_WIDTH`].
const DEFAULT_HEIGHT: u32 = 480;
/// A 16-entry colour map, as PP3's VGA mode.
const DEFAULT_PALETTE_BITS: u32 = 4;
/// The oracle's page preamble (neoteletext-naplps `naplps-oracle`, `PAGE_PREAMBLE`): ESC % A,
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

fn run() -> Result<(), String> {
    let mut width = DEFAULT_WIDTH;
    let mut height = DEFAULT_HEIGHT;
    let mut palette_bits = DEFAULT_PALETTE_BITS;
    let mut font_path = None;
    let mut tenths = 0u32;
    let mut preamble = false;
    let mut dac_bits = 8u32;
    let mut operands = Vec::new();
    let mut arguments = std::env::args().skip(1);
    while let Some(argument) = arguments.next() {
        let mut value = |name: &str| arguments.next().ok_or_else(|| format!("{name} needs a value"));
        match argument.as_str() {
            "--width" => width = number(&value("--width")?)?,
            "--height" => height = number(&value("--height")?)?,
            "--palette-bits" => palette_bits = number(&value("--palette-bits")?)?,
            "--font" => font_path = Some(value("--font")?),
            "--tenths" => tenths = number(&value("--tenths")?)?,
            "--preamble" => preamble = true,
            "--dac-bits" => dac_bits = number(&value("--dac-bits")?)?.clamp(1, 8),
            other if other.starts_with("--") => return Err(format!("unknown option {other}")),
            other => operands.push(other.to_owned()),
        }
    }
    let [page_path, out_path] = operands.as_slice() else {
        return Err("usage: naplps-render [--width N] [--height N] [--palette-bits N] [--font FILE] [--tenths N] [--preamble] PAGE OUT.ppm".to_owned());
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
    let mut events = Vec::new();
    if preamble {
        events.extend(terminal.feed(&mut canvas, &ORACLE_PREAMBLE));
    }
    events.extend(terminal.feed(&mut canvas, &page));
    events.extend(terminal.finish(&mut canvas));
    if events.contains(&Event::LimitReached) {
        eprintln!("naplps-render: {page_path}: processing stopped at the limit on bytes processed");
    }
    let colours = terminal.palette().at(tenths);
    let mut ppm = format!("P6\n{} {}\n255\n", canvas.width(), canvas.height()).into_bytes();
    for &entry in canvas.pixels() {
        let colour = colours.get(usize::from(entry)).copied().unwrap_or([0, 0, 0]);
        ppm.extend_from_slice(&naplps::palette::through_register(colour, dac_bits));
    }
    let mut file = fs::File::create(out_path).map_err(|error| format!("{out_path}: {error}"))?;
    file.write_all(&ppm).map_err(|error| format!("{out_path}: {error}"))?;
    Ok(())
}

fn number(text: &str) -> Result<u32, String> {
    text.parse().map_err(|_| format!("{text:?} is not a whole number"))
}
