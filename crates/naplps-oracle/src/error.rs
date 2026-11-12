//! The one error type of the oracle.

use std::fmt;
use std::io;
use std::path::PathBuf;

/// What went wrong, with enough context to act on it.
#[derive(Debug)]
pub enum Error {
    /// A file or process operation failed.
    Io {
        /// What was being done.
        context: String,
        /// The operating system's error.
        source: io::Error,
    },
    /// An external program the oracle drives is missing, failed or said something unexpected.
    Tool {
        /// The program.
        program: String,
        /// What went wrong, with the program's own error output where there was any.
        detail: String,
    },
    /// A file of the period software differs from the copy the references were made with.
    Pin {
        /// The file.
        path: PathBuf,
        /// The SHA-256 the oracle is pinned to.
        expected: &'static str,
        /// The SHA-256 found.
        found: String,
    },
    /// A frame's size or data is not what it must be.
    Frame(String),
    /// Something did not happen within its ceiling.
    Timeout(String),
    /// The command line is wrong.
    Usage(String),
}

impl fmt::Display for Error {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io { context, source } => write!(formatter, "{context}: {source}"),
            Self::Tool { program, detail } => write!(formatter, "{program}: {detail}"),
            Self::Pin { path, expected, found } => write!(
                formatter,
                "{} has SHA-256 {found}, but the references were made with {expected}; the oracle runs only the pinned copy",
                path.display()
            ),
            Self::Frame(detail) | Self::Timeout(detail) | Self::Usage(detail) => formatter.write_str(detail),
        }
    }
}

impl std::error::Error for Error {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Io { source, .. } => Some(source),
            _ => None,
        }
    }
}

/// Wraps an I/O error with what was being done.
pub(crate) fn io_error(context: impl Into<String>) -> impl FnOnce(io::Error) -> Error {
    let context = context.into();
    move |source| Error::Io { context, source }
}
