//! `naplps-oracle`: capture reference frames from PP3, and compare frames with references.
//!
//! ```text
//! naplps-oracle capture --out DIR [--pp3 DIR] [--work DIR] [--bits-per-second N]
//!                       [--quiet-ms N] [--ceiling-s N] [--fresh] FILE...
//! naplps-oracle compare [--channel N] [--displacement N] [--place] [--trim N] REFERENCE CANDIDATE
//! ```
//!
//! `compare` takes two pictures, or two directories, in which case each picture in REFERENCE is
//! compared with the picture of the same name (any extension) in CANDIDATE. `--place` is for a
//! reference cropped from a larger screen: it is first placed where it fits the candidate best.
//! `--trim N` drops N pixels from each edge of the reference first, for a crop whose edges caught
//! something beside the screen.
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

use std::collections::BTreeMap;
use std::ffi::OsString;
use std::fmt::Write as _;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use std::time::{Duration, Instant};

use naplps_oracle::compare::{self, Tolerance};
use naplps_oracle::error::Error;
use naplps_oracle::session::{self, DOSBOX_CYCLES, PAGE_PREAMBLE, PINNED_FILES, Session, Settling};
use naplps_oracle::tools;

/// Where PP3 is found when `--pp3` and `NAPLPS_PP3_DIR` are not given, under the home directory:
/// the reference collection every NeoTeletext repository draws its sources from.
const DEFAULT_PP3: &str = "devel/teletext-reference/NAPLPS/Telidon-master/archives/prodigy-slack/pp3217a";
/// The repository's ignored scratch directory.
const DEFAULT_WORK: &str = "tmp/oracle";
/// 9600 bits a second: the fastest modems PP3's service profiles offer, and fast enough that the
/// largest corpus page (40,876 bytes) arrives in under a minute.
const DEFAULT_BITS_PER_SECOND: u64 = 9600;
/// A page counts as drawn after this long unchanged. Longer than any pause between drawing
/// commands seen in the sample pages; a page with a longer WAIT is cut short.
const DEFAULT_QUIET_MS: u64 = 3000;
/// A page still changing after this long, counted from its first byte, is reported as never
/// settled (blink or animation). The largest corpus page (40,876 bytes) takes 43 seconds to send
/// at 9600 bits a second, so the ceiling must exceed that; a larger page needs --ceiling-s.
const DEFAULT_CEILING_S: u64 = 60;
/// The largest page file accepted: the corpus's largest is 40,876 bytes.
const MAX_PAGE_BYTES: u64 = 1024 * 1024;
/// The largest picture file `compare` reads.
const MAX_PICTURE_BYTES: u64 = 64 * 1024 * 1024;

fn main() -> ExitCode {
    let arguments: Vec<OsString> = std::env::args_os().skip(1).collect();
    match run(&arguments) {
        Ok(true) => ExitCode::SUCCESS,
        Ok(false) => ExitCode::FAILURE,
        Err(error) => {
            eprintln!("naplps-oracle: {error}");
            ExitCode::from(2)
        }
    }
}

/// Runs the command; `Ok(false)` means it ran and something did not pass.
fn run(arguments: &[OsString]) -> Result<bool, Error> {
    let (command, rest) = arguments.split_first().ok_or_else(|| usage("no command"))?;
    let options = Options::parse(rest)?;
    match command.to_str() {
        Some("capture") => capture(&options),
        Some("compare") => compare_command(&options),
        _ => Err(usage(&format!("unknown command {}", command.to_string_lossy()))),
    }
}

/// The parsed options and the remaining operands.
struct Options {
    values: BTreeMap<String, String>,
    flags: Vec<String>,
    operands: Vec<PathBuf>,
}

/// Options that take a value.
const VALUE_OPTIONS: [&str; 9] = [
    "--out",
    "--pp3",
    "--work",
    "--bits-per-second",
    "--quiet-ms",
    "--ceiling-s",
    "--channel",
    "--displacement",
    "--trim",
];
/// Options that stand alone.
const FLAG_OPTIONS: [&str; 2] = ["--place", "--fresh"];

impl Options {
    fn parse(arguments: &[OsString]) -> Result<Self, Error> {
        let mut options = Self { values: BTreeMap::new(), flags: Vec::new(), operands: Vec::new() };
        let mut iterator = arguments.iter();
        while let Some(argument) = iterator.next() {
            let text = argument.to_string_lossy();
            if VALUE_OPTIONS.contains(&text.as_ref()) {
                let value = iterator.next().ok_or_else(|| usage(&format!("{text} needs a value")))?;
                options.values.insert(text.into_owned(), value.to_string_lossy().into_owned());
            } else if FLAG_OPTIONS.contains(&text.as_ref()) {
                options.flags.push(text.into_owned());
            } else if text.starts_with("--") {
                return Err(usage(&format!("unknown option {text}")));
            } else {
                options.operands.push(PathBuf::from(argument));
            }
        }
        Ok(options)
    }

    fn number(&self, name: &str, default: u64) -> Result<u64, Error> {
        self.values.get(name).map_or(Ok(default), |value| {
            value.parse().map_err(|_| usage(&format!("{name} takes a whole number, not {value:?}")))
        })
    }

    fn path(&self, name: &str) -> Option<PathBuf> {
        self.values.get(name).map(PathBuf::from)
    }
}

fn capture(options: &Options) -> Result<bool, Error> {
    let out = options.path("--out").ok_or_else(|| usage("capture needs --out DIR"))?;
    if options.operands.is_empty() {
        return Err(usage("capture needs at least one page file"));
    }
    let pp3 = match options.path("--pp3").or_else(|| std::env::var_os("NAPLPS_PP3_DIR").map(PathBuf::from)) {
        Some(path) => path,
        None => {
            std::env::var_os("HOME").map(PathBuf::from).ok_or_else(|| usage("no HOME; give --pp3"))?.join(DEFAULT_PP3)
        }
    };
    let work_root = options.path("--work").unwrap_or_else(|| PathBuf::from(DEFAULT_WORK));
    let bits_per_second = options.number("--bits-per-second", DEFAULT_BITS_PER_SECOND)?;
    let settling = Settling {
        quiet: Duration::from_millis(options.number("--quiet-ms", DEFAULT_QUIET_MS)?),
        ceiling: Duration::from_secs(options.number("--ceiling-s", DEFAULT_CEILING_S)?),
    };

    // Names must not collide, since each page's picture is named after its file.
    let mut names = BTreeMap::new();
    for path in &options.operands {
        let name = path
            .file_stem()
            .map(|stem| stem.to_string_lossy().into_owned())
            .ok_or_else(|| usage(&format!("{} has no file name", path.display())))?;
        if let Some(earlier) = names.insert(name.clone(), path.clone()) {
            return Err(usage(&format!("{} and {} would both be {name}.png", earlier.display(), path.display())));
        }
    }

    fs::create_dir_all(&out).map_err(|source| Error::Io { context: format!("creating {}", out.display()), source })?;
    let work = session::fresh_work_directory(&work_root)?;
    let fresh = options.flags.iter().any(|flag| flag == "--fresh");
    let mut session = Session::start(&pp3, &work)?;

    let mut manifest = manifest_header(bits_per_second, settling)?;
    let mut all_settled = true;
    for (index, (name, path)) in names.iter().enumerate() {
        let page = read_bounded(path, MAX_PAGE_BYTES)?;
        let mut bytes = PAGE_PREAMBLE.to_vec();
        bytes.extend_from_slice(&page);
        let sent_at = Instant::now();
        if fresh && index > 0 {
            // A new PP3 for every page: one session can carry state a reset does not clear
            // (pages captured after others came out blank in the corpus run of 12 November 2026).
            drop(session);
            session = Session::start(&pp3, &work)?;
        }
        session.send(&bytes, bits_per_second)?;
        let settled = session.settle(sent_at, settling)?;
        let picture = out.join(format!("{name}.png"));
        tools::save_png(&settled.frame, &picture)?;
        let drawn = settled.drawn_in.map_or_else(|| "never".to_owned(), |time| time.as_millis().to_string());
        all_settled &= settled.drawn_in.is_some();
        let _ = writeln!(
            manifest,
            "{name}\t{}\t{}\t{drawn}\t{}\t{}\t{}",
            tools::sha256_bytes(&page)?,
            page.len(),
            settled.frame.width(),
            settled.frame.height(),
            tools::sha256_file(&picture)?
        );
        println!("{name}: {} bytes, drawn in {drawn} ms, {}", page.len(), picture.display());
    }
    let manifest_path = out.join("manifest.tsv");
    fs::write(&manifest_path, manifest)
        .map_err(|source| Error::Io { context: format!("writing {}", manifest_path.display()), source })?;
    drop(session);
    let _ = fs::remove_dir_all(&work);
    Ok(all_settled)
}

/// The manifest's header: everything that decides what the pictures look like.
fn manifest_header(bits_per_second: u64, settling: Settling) -> Result<String, Error> {
    let mut header = String::new();
    let _ = writeln!(header, "# NAPLPS reference frames captured by naplps-oracle from PP3 under DOSBox.");
    for (file, digest) in PINNED_FILES {
        let _ = writeln!(header, "# pp3 {file} sha256 {digest}");
    }
    let version = tools::run("dosbox", ["-version"], &[], None)?;
    let version = String::from_utf8_lossy(&version);
    let _ = writeln!(header, "# dosbox {}", version.lines().find(|line| !line.trim().is_empty()).unwrap_or("").trim());
    let _ = writeln!(header, "# dosbox cycles fixed {DOSBOX_CYCLES}");
    let preamble: Vec<String> = PAGE_PREAMBLE.iter().map(|byte| format!("{byte:02X}")).collect();
    let _ = writeln!(header, "# preamble before each page {}", preamble.join(" "));
    let _ = writeln!(header, "# line {bits_per_second} bits per second 8N1 (0: unpaced)");
    let _ = writeln!(
        header,
        "# settled after {} ms unchanged, ceiling {} s",
        settling.quiet.as_millis(),
        settling.ceiling.as_secs()
    );
    let _ = writeln!(header, "name\tpage_sha256\tpage_bytes\tdrawn_ms\twidth\theight\tpicture_sha256");
    Ok(header)
}

fn compare_command(options: &Options) -> Result<bool, Error> {
    let [reference, candidate] = options.operands.as_slice() else {
        return Err(usage("compare needs REFERENCE and CANDIDATE"));
    };
    let tolerance = Tolerance {
        channel: u8::try_from(options.number("--channel", 0)?).map_err(|_| usage("--channel is at most 255"))?,
        displacement: u32::try_from(options.number("--displacement", 0)?)
            .map_err(|_| usage("--displacement is too large"))?,
    };
    let place = options.flags.iter().any(|flag| flag == "--place");
    let trim = u32::try_from(options.number("--trim", 0)?).map_err(|_| usage("--trim is too large"))?;
    if reference.is_dir() && candidate.is_dir() {
        let mut all = true;
        let candidates = pictures_by_name(candidate)?;
        for (name, reference_path) in pictures_by_name(reference)? {
            let Some(candidate_path) = candidates.get(&name) else {
                println!("{name}: FAIL no candidate picture");
                all = false;
                continue;
            };
            all &= compare_one(&name, &reference_path, candidate_path, tolerance, place, trim)?;
        }
        Ok(all)
    } else {
        compare_one(&reference.display().to_string(), reference, candidate, tolerance, place, trim)
    }
}

fn compare_one(
    name: &str,
    reference: &Path,
    candidate: &Path,
    tolerance: Tolerance,
    place: bool,
    trim: u32,
) -> Result<bool, Error> {
    check_size(reference)?;
    check_size(candidate)?;
    let mut reference_frame = tools::load_picture(reference)?;
    if trim > 0 {
        let both_sides = trim.saturating_mul(2);
        let (Some(width), Some(height)) =
            (reference_frame.width().checked_sub(both_sides), reference_frame.height().checked_sub(both_sides))
        else {
            return Err(usage(&format!("--trim {trim} leaves nothing of {}", reference.display())));
        };
        reference_frame = reference_frame.crop(trim, trim, width, height)?;
    }
    let mut candidate_frame = tools::load_picture(candidate)?;
    let mut placed = String::new();
    if place {
        let placement = compare::place(&candidate_frame, &reference_frame)?;
        candidate_frame =
            candidate_frame.crop(placement.left, placement.top, reference_frame.width(), reference_frame.height())?;
        placed = format!(" placed at ({}, {})", placement.left, placement.top);
    }
    let result = compare::compare(&reference_frame, &candidate_frame, tolerance)?;
    println!(
        "{name}: {}{placed} {} of {} pixels differ; unexplained {} in the candidate, {} in the reference",
        if result.passes() { "pass" } else { "FAIL" },
        result.differing,
        result.pixels,
        result.unexplained_in_candidate,
        result.unexplained_in_reference
    );
    Ok(result.passes())
}

/// The pictures in a directory by file stem, refusing two with one stem.
fn pictures_by_name(directory: &Path) -> Result<BTreeMap<String, PathBuf>, Error> {
    let mut pictures = BTreeMap::new();
    let entries = fs::read_dir(directory)
        .map_err(|source| Error::Io { context: format!("listing {}", directory.display()), source })?;
    for entry in entries {
        let path =
            entry.map_err(|source| Error::Io { context: format!("listing {}", directory.display()), source })?.path();
        let is_picture = path.extension().and_then(|extension| extension.to_str()).is_some_and(|extension| {
            ["png", "jpg", "jpeg", "gif", "bmp", "ppm"].contains(&extension.to_ascii_lowercase().as_str())
        });
        if !is_picture {
            continue;
        }
        let Some(name) = path.file_stem().map(|stem| stem.to_string_lossy().into_owned()) else { continue };
        if let Some(earlier) = pictures.insert(name.clone(), path.clone()) {
            return Err(usage(&format!("{} and {} have the same name", earlier.display(), path.display())));
        }
    }
    Ok(pictures)
}

fn check_size(path: &Path) -> Result<(), Error> {
    let length = fs::metadata(path)
        .map_err(|source| Error::Io { context: format!("reading {}", path.display()), source })?
        .len();
    if length > MAX_PICTURE_BYTES {
        return Err(Error::Frame(format!("{} is {length} bytes, more than {MAX_PICTURE_BYTES}", path.display())));
    }
    Ok(())
}

fn read_bounded(path: &Path, limit: u64) -> Result<Vec<u8>, Error> {
    let length = fs::metadata(path)
        .map_err(|source| Error::Io { context: format!("reading {}", path.display()), source })?
        .len();
    if length > limit {
        return Err(Error::Frame(format!("{} is {length} bytes, more than the {limit} a page may be", path.display())));
    }
    fs::read(path).map_err(|source| Error::Io { context: format!("reading {}", path.display()), source })
}

fn usage(detail: &str) -> Error {
    Error::Usage(format!(
        "{detail}\nusage: naplps-oracle capture --out DIR [--pp3 DIR] [--work DIR] [--bits-per-second N] [--quiet-ms N] [--ceiling-s N] FILE...\n       naplps-oracle compare [--channel N] [--displacement N] [--place] [--trim N] REFERENCE CANDIDATE"
    ))
}
