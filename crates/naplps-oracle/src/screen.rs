//! The whole X display as a stream of frames, from one long-running ffmpeg.
//!
//! Starting a grabber for every sample cost most of a second each; one stream costs nothing per
//! frame, and a waiter is woken by each new frame rather than looking again on a timer.

use std::io::Read;
use std::process::{Child, Stdio};
use std::sync::{Arc, Condvar, Mutex, MutexGuard};
use std::thread;
use std::time::{Duration, Instant};

use crate::error::Error;
use crate::frame::{CHANNELS, Frame};
use crate::tools;

/// The display's size: larger than PP3's largest mode (640 x 480), so its window always fits.
pub const WIDTH: u32 = 1024;
/// See [`WIDTH`].
pub const HEIGHT: u32 = 768;
/// Frames a second taken from the display; the resolution of every drawing time measured.
pub const FRAMES_PER_SECOND: u32 = 10;

/// A frame of the stream: its number, when it arrived and its RGB data.
pub type Sample = (u64, Instant, Arc<Vec<u8>>);

/// The stream of frames of one display.
pub struct Screen {
    latest: Arc<Latest>,
    child: Child,
}

#[derive(Default)]
struct Latest {
    state: Mutex<State>,
    arrived: Condvar,
}

#[derive(Default)]
struct State {
    sequence: u64,
    frame: Option<(Instant, Arc<Vec<u8>>)>,
    ended: bool,
}

impl Screen {
    /// Starts streaming `display`.
    ///
    /// # Errors
    ///
    /// [`Error::Tool`] if ffmpeg cannot be started.
    pub fn start(display: &str) -> Result<Self, Error> {
        let size = format!("{WIDTH}x{HEIGHT}");
        let rate = FRAMES_PER_SECOND.to_string();
        let mut child = tools::spawn(
            "ffmpeg",
            [
                "-loglevel",
                "error",
                "-f",
                "x11grab",
                "-draw_mouse",
                "0",
                "-framerate",
                &rate,
                "-video_size",
                &size,
                "-i",
                display,
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-",
            ],
            &[],
            Stdio::null(),
            Stdio::piped(),
            Stdio::null(),
        )?;
        let mut stdout = child
            .stdout
            .take()
            .ok_or_else(|| Error::Tool { program: "ffmpeg".to_owned(), detail: "no output".to_owned() })?;
        let frame_bytes = usize::try_from(u64::from(WIDTH).saturating_mul(u64::from(HEIGHT)))
            .ok()
            .and_then(|pixels| pixels.checked_mul(CHANNELS))
            .ok_or_else(|| Error::Frame("the display's frame does not fit this machine's addresses".to_owned()))?;
        let latest = Arc::new(Latest::default());
        let writer = Arc::clone(&latest);
        thread::spawn(move || {
            let mut buffer = vec![0; frame_bytes];
            loop {
                let read = stdout.read_exact(&mut buffer);
                let Ok(mut state) = writer.state.lock() else { return };
                if read.is_err() {
                    state.ended = true;
                    writer.arrived.notify_all();
                    return;
                }
                state.sequence = state.sequence.saturating_add(1);
                state.frame = Some((Instant::now(), Arc::new(buffer.clone())));
                writer.arrived.notify_all();
            }
        });
        Ok(Self { latest, child })
    }

    /// The number of the newest frame so far (0 before the first).
    ///
    /// # Errors
    ///
    /// [`Error::Tool`] if the stream's lock was poisoned.
    pub fn sequence(&self) -> Result<u64, Error> {
        Ok(self.lock()?.sequence)
    }

    /// Waits for a frame newer than `seen`, up to `ceiling`.
    ///
    /// # Errors
    ///
    /// [`Error::Timeout`] at the ceiling, [`Error::Tool`] if ffmpeg stopped.
    pub fn next_after(&self, seen: u64, ceiling: Duration) -> Result<Sample, Error> {
        let deadline = Instant::now()
            .checked_add(ceiling)
            .ok_or_else(|| Error::Timeout("waiting for a frame: ceiling too large".to_owned()))?;
        let mut state = self.lock()?;
        loop {
            if state.sequence > seen
                && let Some((time, frame)) = &state.frame
            {
                return Ok((state.sequence, *time, Arc::clone(frame)));
            }
            if state.ended {
                return Err(Error::Tool { program: "ffmpeg".to_owned(), detail: "the screen stream ended".to_owned() });
            }
            let remaining = deadline.saturating_duration_since(Instant::now());
            if remaining.is_zero() {
                return Err(Error::Timeout(format!("no frame of the display within {} seconds", ceiling.as_secs())));
            }
            state = self.latest.arrived.wait_timeout(state, remaining).map_err(|_| poisoned())?.0;
        }
    }

    /// The `width` x `height` rectangle at (`left`, `top`) of a frame of this stream.
    ///
    /// # Errors
    ///
    /// [`Error::Frame`] if the rectangle reaches outside the display.
    pub fn crop(rgb: &[u8], left: u32, top: u32, width: u32, height: u32) -> Result<Frame, Error> {
        Frame::new(WIDTH, HEIGHT, rgb.to_vec())?.crop(left, top, width, height)
    }

    fn lock(&self) -> Result<MutexGuard<'_, State>, Error> {
        self.latest.state.lock().map_err(|_| poisoned())
    }
}

impl Drop for Screen {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

fn poisoned() -> Error {
    Error::Tool { program: "ffmpeg".to_owned(), detail: "the screen stream's reader failed".to_owned() }
}
