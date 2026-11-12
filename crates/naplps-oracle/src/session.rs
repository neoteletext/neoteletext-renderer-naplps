//! A running PP3 (Personality+III 2.18A, Microstar Software, 1991), the period NAPLPS terminal
//! the references are captured from.
//!
//! PP3 runs in DOSBox on a private Xvfb display. Its COM1 is a pseudo-terminal made by socat, so
//! the page bytes go in the way a 1990 bulletin board sent them, down a serial line, and nothing
//! listens on the network. PP3 is started as `PP3 /NC 1`, its "use from inside other program"
//! mode, which goes straight to the online terminal with no menu to drive. DOSBox's own window is
//! the frame buffer at one to one (surface output, no scaler), so a grab of it is the picture PP3
//! drew.

use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStdin, Stdio};
use std::thread;
use std::time::{Duration, Instant};

use crate::error::{Error, io_error};
use crate::frame::Frame;
use crate::screen::{self, Screen};
use crate::tools;

/// The PP3 files the oracle runs, each pinned by SHA-256: a reference is only as good as knowing
/// exactly which decoder made it. They are the copy in
/// `teletext-reference/NAPLPS/Telidon-master/archives/prodigy-slack/pp3217a/` (identical to the
/// Simtel copy except for `PP3.BAT`, which the oracle does not use).
pub const PINNED_FILES: [(&str, &str); 5] = [
    ("MVDIAPP.COM", "ed0800f9c4427a8847c2f53d3b2b65a9b533f10f902cb309a9a9d4ba2055a9ce"),
    ("PP3SCOMM.EXE", "ed133e309a415d770e141471d2cd4bdcf1a44d9c0db840244b8bbe8200aa9aeb"),
    ("VGA640.SCR", "f0bd2cc3bd8cb7f46d2b19e0efa039d44b3eec4e8b8aa5326625b2cb31dd3778"),
    ("PP3S.DAT", "f989f2a40436bf43fa694c0c3266d6fedba7e7380f529c26c61a2ca639b32ac8"),
    ("PP3SE.MSG", "330c01aada54aff4ebee92824642bc45a96bee91056159e4fd37fe8b90238536"),
];

/// How PP3 is started: the command line of the package's own `PP3.BAT` (MVDI loader, VGA 640
/// driver, English messages) with `/NC 1`, which README.1ST describes for running from another
/// program: online at once, with service directory entry 1's settings.
const PP3_COMMAND: &str = "MVDIAPP PP3SCOMM.EXE +Z +2 VGA640.SCR PP3SCOMM.EXE /FMPP3SE.MSG /NC 1";

/// The emulated processor speed. Fixed, so that drawing takes the same time on every run; 20000
/// cycles a millisecond is roughly a 386 of 1991, the machine class PP3 was written for.
pub const DOSBOX_CYCLES: u32 = 20_000;

/// Sent before every page so each starts from the same state, whatever the page before left.
pub const PAGE_PREAMBLE: [u8; 16] = [
    // ESC % A: switch PP3's presentation to NAPLPS (PP3 README.PP3 section 9.0, an ISO 2375
    // registered sequence).
    0x1B, 0x25, 0x41,
    // The opening every MGE-authored page in the rosetta_stone set and PP3's own samples begin
    // with: CAN, ESC 2/2 4/6 (designate the C1 set), ESC 4/5, then NSR with a cursor position of
    // row 0, column 0 (ANSI X3.110-1983 section 6.1.6.5: designations, DOMAIN, TEXT and TEXTURE
    // back to their defaults), and SO, invoking G1 (the PDI set by default).
    0x18, 0x1B, 0x22, 0x46, 0x1B, 0x45, 0x1F, 0x40, 0x40, 0x0E,
    // RESET with every bit of both operand bytes set (section 5.3.2.9.1): DOMAIN, colour, screen
    // and border, TEXT, blink, unprotected fields, texture, macros and DRCS. MGE writes 0x4F as
    // the second byte, which keeps macros and DRCS; the oracle clears them so no page sees
    // another's definitions.
    0x20, 0x7F, 0x7F,
];

/// Ceilings: each is the most a step may take before the session is declared broken.
const START_CEILING: Duration = Duration::from_secs(30);
/// PP3's screen in NAPLPS mode with the VGA 640 driver: VGA's 640 x 480 sixteen-colour mode.
pub const NAPLPS_SCREEN: (u32, u32) = (640, 480);
/// How long start-up waits for NAPLPS mode before sending the preamble again.
const READY_RETRY: Duration = Duration::from_secs(2);
/// One serial character: a start bit, 8 data bits and a stop bit (8N1).
const BITS_PER_CHARACTER: u64 = 10;
/// Bytes written to the line at a time when pacing.
const PACING_CHUNK: usize = 16;

/// How long a frame must stay unchanged to count as drawn, and the most a page may take.
#[derive(Clone, Copy, Debug)]
pub struct Settling {
    /// Unchanged this long counts as finished. A page with a WAIT longer than this is cut short.
    pub quiet: Duration,
    /// A page still changing after this long (blinking, or animating) is reported as never settled.
    pub ceiling: Duration,
}

/// A frame after drawing stopped.
#[derive(Debug)]
pub struct Settled {
    /// The picture.
    pub frame: Frame,
    /// From the first byte sent to the first frame showing the final picture, to within one frame
    /// of the screen stream; `None` if the picture never stopped changing.
    pub drawn_in: Option<Duration>,
}

/// A running PP3.
pub struct Session {
    display: String,
    window: String,
    line: ChildStdin,
    screen: Screen,
    // Last, so the line is closed before the programs are stopped.
    #[allow(dead_code, reason = "held only so its Drop stops the programs when the session ends")]
    children: Children,
}

/// The programs a session started, stopped when it ends, including when starting fails part way.
#[derive(Default)]
struct Children(Vec<Child>);

impl Drop for Children {
    fn drop(&mut self) {
        // DOSBox first, then the line and the display it uses.
        for child in self.0.iter_mut().rev() {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

impl Session {
    /// Starts Xvfb, the serial line and DOSBox running PP3 from a copy of `pp3_directory` under
    /// `work`, and waits until PP3 is online.
    ///
    /// # Errors
    ///
    /// [`Error::Pin`] if a PP3 file differs from the pinned copy, [`Error::Tool`] or
    /// [`Error::Timeout`] if a program fails to start, [`Error::Io`] for the work directory.
    pub fn start(pp3_directory: &Path, work: &Path) -> Result<Self, Error> {
        let drive = work.join("c");
        fs::create_dir_all(&drive).map_err(io_error(format!("creating {}", drive.display())))?;
        for (name, expected) in PINNED_FILES {
            let source = pp3_directory.join(name);
            let found = tools::sha256_file(&source)?;
            if found != expected {
                return Err(Error::Pin { path: source, expected, found });
            }
            fs::copy(&source, drive.join(name)).map_err(io_error(format!("copying {}", source.display())))?;
        }
        let mut children = Children::default();

        // Xvfb picks a free display itself and prints its number once it accepts clients.
        let screen_size = format!("{}x{}x24", screen::WIDTH, screen::HEIGHT);
        let mut xvfb = tools::spawn(
            "Xvfb",
            ["-displayfd", "1", "-screen", "0", screen_size.as_str(), "-nolisten", "tcp"],
            &[],
            Stdio::null(),
            Stdio::piped(),
            Stdio::null(),
        )?;
        let xvfb_out = xvfb.stdout.take();
        children.0.push(xvfb);
        let number = tools::wait_for_line(
            xvfb_out.ok_or_else(|| Error::Tool { program: "Xvfb".to_owned(), detail: "no output".to_owned() })?,
            "Xvfb",
            START_CEILING,
            |line| !line.trim().is_empty(),
        )?;
        let display = format!(":{}", number.trim());

        // socat makes the pseudo-terminal and copies our writes into it.
        let mut socat = tools::spawn(
            "socat",
            ["-d", "-d", "-u", "STDIN", "PTY,raw,echo=0"],
            &[],
            Stdio::piped(),
            Stdio::null(),
            Stdio::piped(),
        )?;
        let socat_err = socat.stderr.take();
        let line = socat
            .stdin
            .take()
            .ok_or_else(|| Error::Tool { program: "socat".to_owned(), detail: "no input".to_owned() })?;
        children.0.push(socat);
        let announced = tools::wait_for_line(
            socat_err.ok_or_else(|| Error::Tool { program: "socat".to_owned(), detail: "no output".to_owned() })?,
            "socat",
            START_CEILING,
            |line| line.contains("PTY is "),
        )?;
        let pty = announced
            .split("PTY is ")
            .nth(1)
            .map(str::trim)
            .and_then(|path| path.strip_prefix("/dev/"))
            .ok_or_else(|| Error::Tool { program: "socat".to_owned(), detail: format!("unexpected: {announced}") })?
            .to_owned();

        let configuration = work.join("dosbox.conf");
        fs::write(&configuration, dosbox_configuration(&drive, &pty))
            .map_err(io_error(format!("writing {}", configuration.display())))?;
        let log_path = work.join("dosbox.log");
        let log = File::create(&log_path).map_err(io_error(format!("creating {}", log_path.display())))?;
        let log_err = log.try_clone().map_err(io_error("sharing the DOSBox log"))?;
        let environment = [("DISPLAY", display.as_str()), ("SDL_AUDIODRIVER", "dummy")];
        let configuration_arg = configuration.as_os_str().to_owned();
        let dosbox = tools::spawn(
            "dosbox",
            [std::ffi::OsString::from("-conf"), configuration_arg],
            &environment,
            Stdio::null(),
            Stdio::from(log),
            Stdio::from(log_err),
        )?;
        children.0.push(dosbox);

        let mut finder = tools::spawn(
            "xdotool",
            ["search", "--sync", "--name", "DOSBox"],
            &environment,
            Stdio::null(),
            Stdio::piped(),
            Stdio::null(),
        )?;
        let found = finder
            .stdout
            .take()
            .map(|out| tools::wait_for_line(out, "the DOSBox window", START_CEILING, |line| !line.trim().is_empty()));
        let _ = finder.kill();
        let _ = finder.wait();
        let window = found
            .ok_or_else(|| Error::Tool { program: "xdotool".to_owned(), detail: "no output".to_owned() })??
            .trim()
            .to_owned();
        tools::run("xdotool", ["mousemove", "--screen", "0", "0", "0"], &environment, None)?;
        let screen = Screen::start(&display)?;
        let session = Self { display, window, line, screen, children };

        // PP3 shows its shareware notice and waits for a key; after it, the online terminal. Both
        // show a blinking text cursor, so neither ever settles: start-up waits for the notice to
        // appear and then for the screen to change, rather than for stillness.
        let notice = session.wait_for(|frame| frame.iter().any(|&byte| byte != 0))?;
        session.press("space")?;
        session.wait_for(|frame| *frame != *notice)?;
        // PP3 opens COM1 some time after its terminal appears, and bytes sent before then are
        // lost. Its NAPLPS mode is the only sure sign it is listening: entering it switches the
        // VGA 640 driver from the 640 x 400 text screen to the 640 x 480 graphics screen. So the
        // preamble is sent, and sent again, until the screen is the graphics screen.
        session.wait_until_listening()
    }

    /// Sends the preamble until PP3 shows its NAPLPS screen, which means it is reading COM1.
    fn wait_until_listening(mut self) -> Result<Self, Error> {
        let start = Instant::now();
        loop {
            self.send(&PAGE_PREAMBLE, 0)?;
            let sent_at = Instant::now();
            while sent_at.elapsed() < READY_RETRY {
                self.wait_for(|_| true)?;
                if self.window_size()? == NAPLPS_SCREEN {
                    return Ok(self);
                }
            }
            if start.elapsed() >= START_CEILING {
                return Err(Error::Timeout(format!(
                    "PP3 did not enter NAPLPS mode within {} seconds",
                    START_CEILING.as_secs()
                )));
            }
        }
    }

    /// Writes bytes down the serial line, at `bits_per_second` (8N1), or as fast as the line takes
    /// them when it is zero.
    ///
    /// # Errors
    ///
    /// [`Error::Io`] if the line is closed.
    pub fn send(&mut self, bytes: &[u8], bits_per_second: u64) -> Result<(), Error> {
        if bits_per_second == 0 {
            self.line.write_all(bytes).map_err(io_error("writing to the serial line"))?;
            return self.line.flush().map_err(io_error("writing to the serial line"));
        }
        let start = Instant::now();
        let mut sent: u64 = 0;
        for chunk in bytes.chunks(PACING_CHUNK) {
            self.line.write_all(chunk).map_err(io_error("writing to the serial line"))?;
            self.line.flush().map_err(io_error("writing to the serial line"))?;
            sent = sent.saturating_add(u64::try_from(chunk.len()).unwrap_or(u64::MAX));
            // The line rate is the behaviour being reproduced, so here waiting is the point.
            let due = Duration::from_micros(
                sent.saturating_mul(BITS_PER_CHARACTER)
                    .saturating_mul(1_000_000)
                    .checked_div(bits_per_second)
                    .unwrap_or(0),
            );
            thread::sleep(due.saturating_sub(start.elapsed()));
        }
        Ok(())
    }

    /// Waits until the picture has not changed for `settling.quiet`, and returns it. `from` is
    /// when the bytes being drawn started to be sent.
    ///
    /// # Errors
    ///
    /// [`Error::Tool`] or [`Error::Timeout`] if the screen stream fails.
    pub fn settle(&self, from: Instant, settling: Settling) -> Result<Settled, Error> {
        let (mut seen, mut changed_at, mut last) = self.screen.next_after(self.screen.sequence()?, START_CEILING)?;
        loop {
            if from.elapsed() >= settling.ceiling {
                return Ok(Settled { frame: self.window_of(&last)?, drawn_in: None });
            }
            let (sequence, time, frame) = self.screen.next_after(seen, START_CEILING)?;
            seen = sequence;
            if frame != last {
                last = frame;
                changed_at = time;
            } else if time.saturating_duration_since(changed_at) >= settling.quiet {
                return Ok(Settled {
                    frame: self.window_of(&last)?,
                    drawn_in: Some(changed_at.saturating_duration_since(from)),
                });
            }
        }
    }

    /// Waits for a display frame that satisfies `wanted`, up to the start-up ceiling.
    fn wait_for(&self, wanted: impl Fn(&[u8]) -> bool) -> Result<std::sync::Arc<Vec<u8>>, Error> {
        let start = Instant::now();
        let mut seen = self.screen.sequence()?;
        loop {
            let remaining = START_CEILING.saturating_sub(start.elapsed());
            if remaining.is_zero() {
                return Err(Error::Timeout(format!("PP3 did not start within {} seconds", START_CEILING.as_secs())));
            }
            let (sequence, _, frame) = self.screen.next_after(seen, remaining)?;
            if wanted(&frame) {
                return Ok(frame);
            }
            seen = sequence;
        }
    }

    /// PP3's window as it is now.
    ///
    /// # Errors
    ///
    /// [`Error::Tool`] or [`Error::Timeout`] if the screen stream or xdotool fail.
    pub fn grab(&self) -> Result<Frame, Error> {
        let (_, _, frame) = self.screen.next_after(self.screen.sequence()?, START_CEILING)?;
        self.window_of(&frame)
    }

    /// The part of a display frame that is PP3's window, which is PP3's screen at one to one.
    fn window_of(&self, display_frame: &[u8]) -> Result<Frame, Error> {
        let (left, top, width, height) = self.window_geometry()?;
        Screen::crop(display_frame, left, top, width, height)
    }

    /// The size of PP3's window, which is the size of its screen.
    fn window_size(&self) -> Result<(u32, u32), Error> {
        let (_, _, width, height) = self.window_geometry()?;
        Ok((width, height))
    }

    /// PP3's window on the display: left, top, width and height.
    fn window_geometry(&self) -> Result<(u32, u32, u32, u32), Error> {
        let environment = [("DISPLAY", self.display.as_str())];
        let shell = tools::run("xdotool", ["getwindowgeometry", "--shell", self.window.as_str()], &environment, None)?;
        let shell = String::from_utf8_lossy(&shell);
        let value = |key: &str| -> Result<u32, Error> {
            shell
                .lines()
                .find_map(|line| line.strip_prefix(key).and_then(|rest| rest.strip_prefix('=')))
                .and_then(|value| value.trim().parse().ok())
                .ok_or_else(|| Error::Tool { program: "xdotool".to_owned(), detail: format!("no {key} in {shell:?}") })
        };
        Ok((value("X")?, value("Y")?, value("WIDTH")?, value("HEIGHT")?))
    }

    /// Presses one key in PP3's window (an xdotool key name).
    ///
    /// # Errors
    ///
    /// [`Error::Tool`] if xdotool fails.
    pub fn press(&self, key: &str) -> Result<(), Error> {
        let environment = [("DISPLAY", self.display.as_str())];
        tools::run("xdotool", ["windowfocus", "--sync", self.window.as_str(), "key", key], &environment, None)?;
        Ok(())
    }
}

/// The DOSBox configuration: PP3's drive, COM1 on the pseudo-terminal, a fixed speed, and a
/// window that is the frame buffer at one to one.
fn dosbox_configuration(drive: &Path, pty: &str) -> String {
    format!(
        "[sdl]\noutput=surface\nfullscreen=false\n\
         [dosbox]\nmachine=svga_s3\n\
         [cpu]\ncore=normal\ncycles=fixed {DOSBOX_CYCLES}\n\
         [render]\nframeskip=0\naspect=false\nscaler=none\n\
         [mixer]\nnosound=true\n\
         [serial]\nserial1=directserial realport:{pty}\nserial2=disabled\n\
         [autoexec]\nmount c \"{}\"\nc:\n{PP3_COMMAND}\n",
        drive.display()
    )
}

/// The work directory a run uses: `root/run-<process id>`, removed and made afresh.
///
/// # Errors
///
/// [`Error::Io`] if it cannot be made.
pub fn fresh_work_directory(root: &Path) -> Result<PathBuf, Error> {
    let work = root.join(format!("run-{}", std::process::id()));
    if work.exists() {
        fs::remove_dir_all(&work).map_err(io_error(format!("clearing {}", work.display())))?;
    }
    fs::create_dir_all(&work).map_err(io_error(format!("creating {}", work.display())))?;
    Ok(work)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dosbox_configuration_names_the_drive_line_and_command() {
        let text = dosbox_configuration(Path::new("/work/c"), "pts/7");
        assert!(text.contains("serial1=directserial realport:pts/7\n"));
        assert!(text.contains("mount c \"/work/c\"\n"));
        assert!(text.contains(&format!("cycles=fixed {DOSBOX_CYCLES}\n")));
        assert!(text.ends_with(&format!("{PP3_COMMAND}\n")));
    }

    #[test]
    fn the_preamble_ends_with_a_full_reset() {
        assert_eq!(PAGE_PREAMBLE[..3], [0x1B, 0x25, 0x41]);
        assert_eq!(PAGE_PREAMBLE[PAGE_PREAMBLE.len() - 3..], [0x20, 0x7F, 0x7F]);
    }
}
