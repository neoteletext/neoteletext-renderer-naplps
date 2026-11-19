//! What a stream's bytes did that its author may not have meant: bytes the renderer passed over
//! and work it refused at a bound (DEC-6638 item 7, row 9.3: an authoring check for NAPLPS like
//! `regis-minify`'s render check). Drawing does not depend on any of it.

/// Why the renderer refused part of a stream: each a bound of [`crate::limits`].
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Refusal {
    /// A macro definition's bytes beyond [`crate::limits::MAX_MACRO_BYTES`] were dropped.
    MacroTooLong,
    /// A macro definition was dropped whole: with it the macros would hold more than
    /// [`crate::limits::MAX_ALL_MACRO_BYTES`].
    MacrosFull,
    /// A PDI's operand bytes beyond [`crate::limits::MAX_PDI_BYTES`] were dropped.
    PdiTooLong,
    /// A polygon's, arc's or incremental figure's points beyond [`crate::limits::MAX_VERTICES`]
    /// were dropped.
    TooManyVertices,
    /// A macro call was not expanded: [`crate::limits::MAX_MACRO_DEPTH`] macros were already
    /// expanding inside one another.
    MacroTooDeep,
    /// Processing stopped at [`crate::limits::MAX_PROCESSED_BYTES`] in one call.
    ProcessingLimit,
    /// Drawing stopped because its pixel work could not be paid for from the stream's
    /// allowance ([`crate::limits::WORK_CAP`], earning [`crate::limits::WORK_PER_BYTE`] a byte),
    /// and the rest of the call was passed over (TODO-6844).
    WorkLimit,
}

impl Refusal {
    /// Every kind, in the order [`Diagnostics::refusals`] counts them.
    pub const ALL: [Self; REFUSAL_KINDS] = [
        Self::MacroTooLong,
        Self::MacrosFull,
        Self::PdiTooLong,
        Self::TooManyVertices,
        Self::MacroTooDeep,
        Self::ProcessingLimit,
        Self::WorkLimit,
    ];

    /// A short name, for a report.
    #[must_use]
    pub fn name(self) -> &'static str {
        match self {
            Self::MacroTooLong => "a macro definition longer than the limit",
            Self::MacrosFull => "a macro definition beyond the macros' total limit",
            Self::PdiTooLong => "PDI operands beyond the limit",
            Self::TooManyVertices => "points beyond the vertex limit",
            Self::MacroTooDeep => "a macro call nested beyond the depth limit",
            Self::ProcessingLimit => "bytes left unprocessed at the processing limit",
            Self::WorkLimit => "bytes left unprocessed at the pixel work limit",
        }
    }

    fn index(self) -> usize {
        match self {
            Self::MacroTooLong => 0,
            Self::MacrosFull => 1,
            Self::PdiTooLong => 2,
            Self::TooManyVertices => 3,
            Self::MacroTooDeep => 4,
            Self::ProcessingLimit => 5,
            Self::WorkLimit => 6,
        }
    }
}

/// How many kinds of [`Refusal`] there are.
pub const REFUSAL_KINDS: usize = 7;

/// What the renderer passed over and refused in a stream since the terminal was made. Bytes
/// that an object's macro runs are not counted: they are the stream's macros run again.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Diagnostics {
    /// Bytes that had no effect by the standard's rules: C0 codes that belong to other layers
    /// (ANSI X3.110-1983 section 6.1: 0/0 to 0/6 and 1/0 to 1/7), bytes of a null G-set
    /// (section 4.3.2: an unknown designation makes one), and PDI operand bytes with no PDI
    /// command before them.
    pub passed_over: u32,
    /// The stream offset of the first byte passed over: the count of the stream's bytes before
    /// it, over every call; a byte a macro runs is counted at the byte that called the macro.
    pub first_passed_over: Option<usize>,
    /// For each kind of [`Refusal`], in the order of [`Refusal::ALL`], how many times it
    /// happened; for [`Refusal::ProcessingLimit`], [`Refusal::WorkLimit`] and the dropped bytes of
    /// [`Refusal::MacroTooLong`], [`Refusal::MacrosFull`] and [`Refusal::PdiTooLong`], how many
    /// bytes.
    pub refusals: [u32; REFUSAL_KINDS],
    /// The stream offset at which the first refusal happened, counted as for
    /// [`Diagnostics::first_passed_over`]; a PDI's refusal is found when it runs, at the byte
    /// after its operands.
    pub first_refused: Option<usize>,
    /// Characters written back over the character before them, after ACTIVE POSITION BACKWARD
    /// (0/8, section 6.1.2.1) with nothing drawn between, while colour mode 2 is in force: in
    /// that mode a character's field is filled with the background colour (section 5.3.2.6.3), so
    /// such a character erases the one beneath it. This is how a text part writes a diacritical
    /// mark over its letter (renderer parity PAR-5), and the server logs it (PAR-23). Neither a
    /// refusal nor a byte passed over: the character is drawn as the standard says.
    pub overwritten_in_mode_two: u32,
    /// The stream offset of the first such character, counted as for
    /// [`Diagnostics::first_passed_over`].
    pub first_overwritten_in_mode_two: Option<usize>,
}

impl Diagnostics {
    /// How many times a refusal of `kind` happened.
    #[must_use]
    pub fn count(&self, kind: Refusal) -> u32 {
        self.refusals.get(kind.index()).copied().unwrap_or(0)
    }

    /// All refusals together.
    #[must_use]
    pub fn refused(&self) -> u32 {
        self.refusals.iter().fold(0u32, |sum, count| sum.saturating_add(*count))
    }

    pub(super) fn pass_over(&mut self, offset: usize) {
        self.passed_over = self.passed_over.saturating_add(1);
        self.first_passed_over.get_or_insert(offset);
    }

    pub(super) fn overwrite_in_mode_two(&mut self, offset: usize) {
        self.overwritten_in_mode_two = self.overwritten_in_mode_two.saturating_add(1);
        self.first_overwritten_in_mode_two.get_or_insert(offset);
    }

    pub(super) fn refuse(&mut self, kind: Refusal, count: usize, offset: usize) {
        if let Some(slot) = self.refusals.get_mut(kind.index()) {
            *slot = slot.saturating_add(u32::try_from(count).unwrap_or(u32::MAX));
        }
        self.first_refused.get_or_insert(offset);
    }
}
