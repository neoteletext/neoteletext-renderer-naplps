//! Every bound on what a page may make the renderer hold or do (the security analysis of NAPLPS
//! input; ANSI X3.110-1983 section 5.5 warns that the application must guard against infinite
//! macro loops).

/// Macros that may be expanding inside one another at once.
pub const MAX_MACRO_DEPTH: usize = 16;
/// Bytes one macro definition may hold.
pub const MAX_MACRO_BYTES: usize = 4096;
/// Bytes all macro definitions together may hold.
pub const MAX_ALL_MACRO_BYTES: usize = 65_536;
/// Bytes processed by one call of `feed` or `finish`, counting macro expansion, before
/// processing stops and the limit is reported.
pub const MAX_PROCESSED_BYTES: usize = 4_000_000;
/// Data bytes one PDI may carry; more are dropped (section 5.3.1: the standard sets no limit,
/// but a polygon of 4096 vertices at 8 bytes each fits).
pub const MAX_PDI_BYTES: usize = 32_768;
/// Vertices of one polygon, scribble or arc spline (the standard asks for at least 256).
pub const MAX_VERTICES: usize = 4096;
/// Pixels on the longer side of the one-bit bitmap a DRCS character or fill mask is drawn into
/// (section 5.6 leaves the resolution to the implementation).
pub const MASK_SIDE: u32 = 128;
/// Blink processes at once (Dillon, BLINK: at least 16).
pub const MAX_BLINKS: usize = 32;
/// Width or height of a canvas.
pub const MAX_CANVAS_SIDE: u32 = 4096;
