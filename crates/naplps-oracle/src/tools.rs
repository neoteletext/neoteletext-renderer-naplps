//! The external programs the oracle drives, and reading and writing pictures through ffmpeg.

use std::ffi::OsStr;
use std::io::{BufRead, BufReader, Read, Write};
use std::path::Path;
use std::process::{Child, Command, Stdio};
use std::sync::mpsc;
use std::thread;
use std::time::{Duration, Instant};

use crate::error::{Error, io_error};
use crate::frame::Frame;

/// The most standard output kept from a tool: a 4096 x 4096 RGB frame and some to spare.
const MAX_OUTPUT_BYTES: u64 = 64 * 1024 * 1024;
/// The most error output quoted back from a failed tool.
const MAX_ERROR_QUOTE_BYTES: usize = 2000;

/// Runs `program` to completion, feeding it `input`, and returns its standard output.
///
/// # Errors
///
/// [`Error::Tool`] if it cannot be started, exits unsuccessfully or writes more than the bound.
pub fn run<I, S>(program: &str, args: I, environment: &[(&str, &str)], input: Option<&[u8]>) -> Result<Vec<u8>, Error>
where
    I: IntoIterator<Item = S>,
    S: AsRef<OsStr>,
{
    let mut command = Command::new(program);
    command
        .args(args)
        .stdin(if input.is_some() { Stdio::piped() } else { Stdio::null() })
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    for (key, value) in environment {
        command.env(key, value);
    }
    let mut child = command.spawn().map_err(|source| missing(program, &source))?;
    // Input is written from its own thread so a program that writes output before it has read all
    // its input cannot deadlock against us.
    let writer = match (input, child.stdin.take()) {
        (Some(bytes), Some(mut stdin)) => {
            let bytes = bytes.to_vec();
            Some(thread::spawn(move || stdin.write_all(&bytes)))
        }
        _ => None,
    };
    // Error output is drained on its own thread too, so a full error pipe cannot stall the program
    // while we read its standard output.
    let error_reader = child.stderr.take().map(|stderr| {
        thread::spawn(move || {
            let mut errors = Vec::new();
            let _ = stderr.take(MAX_OUTPUT_BYTES).read_to_end(&mut errors);
            errors
        })
    });
    let mut output = Vec::new();
    if let Some(stdout) = child.stdout.take() {
        stdout
            .take(MAX_OUTPUT_BYTES.saturating_add(1))
            .read_to_end(&mut output)
            .map_err(io_error(format!("reading {program}'s output")))?;
    }
    let errors = error_reader.and_then(|reader| reader.join().ok()).unwrap_or_default();
    let status = child.wait().map_err(io_error(format!("waiting for {program}")))?;
    if let Some(writer) = writer {
        match writer.join() {
            Ok(Ok(())) => {}
            Ok(Err(source)) => return Err(io_error(format!("writing {program}'s input"))(source)),
            Err(_) => return Err(tool(program, "the thread writing its input failed")),
        }
    }
    if !status.success() {
        return Err(tool(program, &format!("{status}: {}", quote(&errors))));
    }
    if u64::try_from(output.len()).unwrap_or(u64::MAX) > MAX_OUTPUT_BYTES {
        return Err(tool(program, &format!("wrote more than {MAX_OUTPUT_BYTES} bytes")));
    }
    Ok(output)
}

/// Starts `program` in the background with the given standard input, output and error.
///
/// # Errors
///
/// [`Error::Tool`] if it cannot be started.
pub fn spawn<I, S>(
    program: &str,
    args: I,
    environment: &[(&str, &str)],
    stdin: Stdio,
    stdout: Stdio,
    stderr: Stdio,
) -> Result<Child, Error>
where
    I: IntoIterator<Item = S>,
    S: AsRef<OsStr>,
{
    let mut command = Command::new(program);
    command.args(args).stdin(stdin).stdout(stdout).stderr(stderr);
    for (key, value) in environment {
        command.env(key, value);
    }
    command.spawn().map_err(|source| missing(program, &source))
}

/// Reads lines from `reader` until one satisfies `wanted`, and returns it; fails at the ceiling.
/// The reading happens on its own thread, and this waits on a channel, so nothing polls.
///
/// # Errors
///
/// [`Error::Timeout`] at the ceiling, or [`Error::Tool`] if the stream ends first.
pub fn wait_for_line<R, F>(reader: R, what: &str, ceiling: Duration, wanted: F) -> Result<String, Error>
where
    R: Read + Send + 'static,
    F: Fn(&str) -> bool,
{
    let (sender, receiver) = mpsc::channel();
    thread::spawn(move || {
        for line in BufReader::new(reader).lines() {
            let Ok(line) = line else { break };
            if sender.send(line).is_err() {
                break;
            }
        }
    });
    let deadline =
        Instant::now().checked_add(ceiling).ok_or_else(|| Error::Timeout(format!("{what}: ceiling too large")))?;
    loop {
        let remaining = deadline.saturating_duration_since(Instant::now());
        match receiver.recv_timeout(remaining) {
            Ok(line) if wanted(&line) => return Ok(line),
            Ok(_) => {}
            Err(mpsc::RecvTimeoutError::Timeout) => {
                return Err(Error::Timeout(format!("{what}: nothing within {} seconds", ceiling.as_secs())));
            }
            Err(mpsc::RecvTimeoutError::Disconnected) => {
                return Err(Error::Tool { program: what.to_owned(), detail: "its output ended first".to_owned() });
            }
        }
    }
}

/// Reads a picture file of any format ffmpeg reads, as RGB.
///
/// # Errors
///
/// [`Error::Tool`] if ffprobe or ffmpeg fail, or [`Error::Frame`] if the result is malformed.
pub fn load_picture(path: &Path) -> Result<Frame, Error> {
    let size = run(
        "ffprobe",
        [
            OsStr::new("-v"),
            OsStr::new("error"),
            OsStr::new("-select_streams"),
            OsStr::new("v:0"),
            OsStr::new("-show_entries"),
            OsStr::new("stream=width,height"),
            OsStr::new("-of"),
            OsStr::new("csv=p=0:s=x"),
            path.as_os_str(),
        ],
        &[],
        None,
    )?;
    let size = String::from_utf8_lossy(&size);
    let (width, height) = size
        .trim()
        .split_once('x')
        .and_then(|(width, height)| Some((width.parse::<u32>().ok()?, height.parse::<u32>().ok()?)))
        .ok_or_else(|| Error::Frame(format!("ffprobe gave no size for {}: {size:?}", path.display())))?;
    let rgb = run(
        "ffmpeg",
        [
            OsStr::new("-loglevel"),
            OsStr::new("error"),
            OsStr::new("-i"),
            path.as_os_str(),
            OsStr::new("-frames:v"),
            OsStr::new("1"),
            OsStr::new("-f"),
            OsStr::new("rawvideo"),
            OsStr::new("-pix_fmt"),
            OsStr::new("rgb24"),
            OsStr::new("-"),
        ],
        &[],
        None,
    )?;
    Frame::new(width, height, rgb)
}

/// Writes a frame as a PNG file, which is lossless.
///
/// # Errors
///
/// [`Error::Tool`] if ffmpeg fails.
pub fn save_png(frame: &Frame, path: &Path) -> Result<(), Error> {
    let size = format!("{}x{}", frame.width(), frame.height());
    run(
        "ffmpeg",
        [
            OsStr::new("-loglevel"),
            OsStr::new("error"),
            OsStr::new("-y"),
            OsStr::new("-f"),
            OsStr::new("rawvideo"),
            OsStr::new("-pix_fmt"),
            OsStr::new("rgb24"),
            OsStr::new("-video_size"),
            OsStr::new(&size),
            OsStr::new("-i"),
            OsStr::new("-"),
            OsStr::new("-frames:v"),
            OsStr::new("1"),
            path.as_os_str(),
        ],
        &[],
        Some(frame.rgb()),
    )?;
    Ok(())
}

/// The SHA-256 of a file, by `sha256sum`, as lower-case hexadecimal.
///
/// # Errors
///
/// [`Error::Tool`] if `sha256sum` fails or prints something unexpected.
pub fn sha256_file(path: &Path) -> Result<String, Error> {
    let output = run("sha256sum", [OsStr::new("--"), path.as_os_str()], &[], None)?;
    first_hex_word(&output).ok_or_else(|| tool("sha256sum", "printed no digest"))
}

/// The SHA-256 of bytes, by `sha256sum`, as lower-case hexadecimal.
///
/// # Errors
///
/// [`Error::Tool`] if `sha256sum` fails or prints something unexpected.
pub fn sha256_bytes(bytes: &[u8]) -> Result<String, Error> {
    let output = run("sha256sum", ["-"], &[], Some(bytes))?;
    first_hex_word(&output).ok_or_else(|| tool("sha256sum", "printed no digest"))
}

/// A SHA-256 digest in hexadecimal is this many characters.
const SHA256_HEX_LENGTH: usize = 64;

fn first_hex_word(output: &[u8]) -> Option<String> {
    let text = String::from_utf8_lossy(output);
    let word = text.split_whitespace().next()?;
    (word.len() == SHA256_HEX_LENGTH && word.bytes().all(|byte| byte.is_ascii_hexdigit())).then(|| word.to_owned())
}

fn missing(program: &str, source: &std::io::Error) -> Error {
    tool(program, &format!("cannot be started ({source}); the oracle needs it installed"))
}

fn tool(program: &str, detail: &str) -> Error {
    Error::Tool { program: program.to_owned(), detail: detail.to_owned() }
}

fn quote(errors: &[u8]) -> String {
    let text = String::from_utf8_lossy(errors);
    let text = text.trim();
    match text.char_indices().nth(MAX_ERROR_QUOTE_BYTES) {
        Some((cut, _)) => format!("{}...", text.get(..cut).unwrap_or_default()),
        None => text.to_owned(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn first_hex_word_accepts_a_digest_and_refuses_anything_else() {
        let digest = "a".repeat(64);
        assert_eq!(first_hex_word(format!("{digest}  -\n").as_bytes()), Some(digest));
        assert_eq!(first_hex_word(b"abc  -\n"), None);
        assert_eq!(first_hex_word(format!("{}  -", "g".repeat(64)).as_bytes()), None);
        assert_eq!(first_hex_word(b""), None);
    }

    #[test]
    fn quote_shortens_long_error_output() {
        let long = "x".repeat(MAX_ERROR_QUOTE_BYTES + 10);
        assert_eq!(quote(long.as_bytes()).len(), MAX_ERROR_QUOTE_BYTES + 3);
        assert_eq!(quote(b"  short \n"), "short");
    }
}
