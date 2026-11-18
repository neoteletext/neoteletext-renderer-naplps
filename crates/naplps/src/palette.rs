//! The colour map (ANSI X3.110-1983 sections 5.3.2.5 to 5.3.2.7).
//!
//! Every pixel holds a colour-map address; the map turns it into a colour at display time. The
//! map has 2^N entries; nominal black is entry 0 and nominal white is entry 011...1, the top of
//! the grey scale that fills the first half (section 5.3.2.5.2).

use alloc::vec;
use alloc::vec::Vec;

use crate::limits::MAX_BLINKS;

/// Smallest and largest number of colour-map address bits accepted.
pub const MIN_BITS: u32 = 2;
/// See [`MIN_BITS`]; 8 bits is a 256-entry map.
pub const MAX_BITS: u32 = 8;
/// An intensity of one primary.
const FULL: u32 = 255;
/// Degrees in a circle.
const CIRCLE: u32 = 360;
/// The hue-circle positions of the primaries (section 5.3.2.5.2: blue 0, red 120, green 240).
const BLUE_ANGLE: u32 = 0;
/// See [`BLUE_ANGLE`].
const RED_ANGLE: u32 = 120;
/// See [`BLUE_ANGLE`].
const GREEN_ANGLE: u32 = 240;
/// The mixing scale of the second primary: |angle(h) - angle(P1)| / 60 degrees.
const MIX_DEGREES: u32 = 60;

/// An RGB colour, 8 bits per primary.
pub type Rgb = [u8; 3];

/// One BLINK process (section 5.3.2.7): `from` alternates with `to`'s colour.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Blink {
    /// The entry that changes.
    pub from: u8,
    /// The entry whose colour it takes during the ON interval.
    pub to: u8,
    /// Tenths of a second showing `to`'s colour.
    pub on: u32,
    /// Tenths of a second showing its own colour.
    pub off: u32,
    /// When its first ON interval starts, in tenths of a second from the first process's.
    pub start: u32,
}

/// The colour map.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Palette {
    bits: u32,
    entries: Vec<Rgb>,
    used: Vec<bool>,
    blinks: Vec<Blink>,
}

impl Palette {
    /// The default colour map of 2^`bits` entries, `bits` clamped to 2 to 8.
    #[must_use]
    pub fn new(bits: u32) -> Self {
        let bits = bits.clamp(MIN_BITS, MAX_BITS);
        let size = 1usize << bits;
        let mut palette = Self { bits, entries: vec![[0; 3]; size], used: vec![false; size], blinks: Vec::new() };
        palette.reset();
        palette
    }

    /// Colour-map address bits.
    #[must_use]
    pub fn bits(&self) -> u32 {
        self.bits
    }

    /// Number of entries.
    #[must_use]
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    /// Never true: a map always has entries.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    /// Nominal black's entry.
    #[must_use]
    pub fn black(&self) -> u8 {
        0
    }

    /// Nominal white's entry: 011...1.
    #[must_use]
    pub fn white(&self) -> u8 {
        u8::try_from((self.len() / 2).saturating_sub(1)).unwrap_or(u8::MAX)
    }

    /// The colour of an entry (black for an entry out of range).
    #[must_use]
    pub fn colour(&self, entry: u8) -> Rgb {
        self.entries.get(usize::from(entry)).copied().unwrap_or([0; 3])
    }

    /// Every entry's colour.
    #[must_use]
    pub fn colours(&self) -> &[Rgb] {
        &self.entries
    }

    /// Restores the default colour map and forgets which entries mode 0 has used (section
    /// 5.3.2.5.2).
    pub fn reset(&mut self) {
        let size = self.entries.len();
        let half = size / 2;
        for (index, entry) in self.entries.iter_mut().enumerate() {
            *entry = if index < half { grey(index, half) } else { hue(index.saturating_sub(half), half) };
        }
        self.used.fill(false);
    }

    /// The entry an operand of `width` bits names: its most significant bits, padded with zero
    /// bits when it has fewer than the map's address bits (section 5.3.2.6.1).
    #[must_use]
    pub fn entry_from_operand(&self, value: u32, width: u32) -> u8 {
        let entry = if width >= self.bits {
            value.wrapping_shr(width.saturating_sub(self.bits))
        } else {
            value.wrapping_shl(self.bits.saturating_sub(width))
        };
        u8::try_from(entry & ((1u32 << self.bits).saturating_sub(1))).unwrap_or(0)
    }

    /// The next entry for an implicit SET COLOR or BLINK: the address's bit-reversed increment
    /// ("change the most significant zero to a one, then all ones to its left to zeroes"); `None`
    /// once the entry is all ones (section 5.3.2.5.1; Dillon, SET COLOR).
    #[must_use]
    pub fn next_entry(&self, entry: u8) -> Option<u8> {
        let all_ones = (1u32 << self.bits).saturating_sub(1);
        if u32::from(entry) >= all_ones {
            return None;
        }
        let reversed = reverse(u32::from(entry), self.bits);
        let next = reverse(reversed.saturating_add(1) & all_ones, self.bits);
        u8::try_from(next).ok()
    }

    /// Sets an entry's colour, and marks it used (modes 1 and 2).
    pub fn set(&mut self, entry: u8, colour: Rgb) {
        if let Some(slot) = self.entries.get_mut(usize::from(entry)) {
            *slot = colour;
        }
        if let Some(used) = self.used.get_mut(usize::from(entry)) {
            *used = true;
        }
    }

    /// Marks an entry used (SELECT COLOR names it).
    pub fn mark_used(&mut self, entry: u8) {
        if let Some(used) = self.used.get_mut(usize::from(entry)) {
            *used = true;
        }
    }

    /// The entry mode 0 draws `colour` with: the lowest entry already holding it, else the
    /// lowest entry not used since the last reset (never nominal black or white), defined to it;
    /// with none left, the nearest colour (section 5.3.2.5.1 leaves that case to the
    /// implementation).
    pub fn allocate(&mut self, colour: Rgb) -> u8 {
        if let Some(index) = self.entries.iter().position(|entry| *entry == colour) {
            return u8::try_from(index).unwrap_or(0);
        }
        let black = usize::from(self.black());
        let white = usize::from(self.white());
        let free = self.used.iter().enumerate().position(|(index, used)| !used && index != black && index != white);
        if let Some(index) = free {
            let entry = u8::try_from(index).unwrap_or(0);
            self.set(entry, colour);
            return entry;
        }
        self.nearest(colour)
    }

    /// The lowest entry holding the colour nearest `colour`, changing nothing: what colour mode
    /// 0 draws with when no entry is left, and what an object's macro always draws with
    /// (animation.md ANIM-11: it redefines no entry).
    #[must_use]
    pub fn nearest(&self, colour: Rgb) -> u8 {
        let nearest = self
            .entries
            .iter()
            .enumerate()
            .min_by_key(|(_, entry)| distance(**entry, colour))
            .map_or(0, |(index, _)| index);
        u8::try_from(nearest).unwrap_or(0)
    }

    /// The first time after `tenths` (tenths of a second after the first blink process started)
    /// at which some process changes phase, so the colour map [`Palette::at`] gives changes;
    /// `None` when nothing blinks. A caller with a clock sleeps until then (animation.md ANIM-1,
    /// ANIM-20).
    #[must_use]
    pub fn next_change(&self, tenths: u32) -> Option<u32> {
        self.blinks
            .iter()
            .map(|blink| {
                if tenths < blink.start {
                    return blink.start;
                }
                let period = blink.on.saturating_add(blink.off).max(1);
                let phase = tenths.saturating_sub(blink.start).checked_rem(period).unwrap_or(0);
                let remaining =
                    if phase < blink.on { blink.on.saturating_sub(phase) } else { period.saturating_sub(phase) };
                tenths.saturating_add(remaining)
            })
            .min()
    }

    /// A colour-map entry not used since the last reset (never nominal black or white), given
    /// `colour`; `None` when every entry is in use. BLINK START in colour mode 0 needs an entry of
    /// its own (section 6.2.8.1).
    pub fn allocate_unused(&mut self, colour: Rgb) -> Option<u8> {
        let black = usize::from(self.black());
        let white = usize::from(self.white());
        let index = self.used.iter().enumerate().position(|(index, used)| !used && index != black && index != white)?;
        let entry = u8::try_from(index).ok()?;
        self.set(entry, colour);
        Some(entry)
    }

    /// Starts a blink process, replacing any for the same pair; zero intervals end it instead
    /// (section 5.3.2.7.4). The start is relative to the most recently defined process.
    pub fn blink(&mut self, from: u8, to: u8, on: u32, off: u32, delay: u32) {
        self.blinks.retain(|blink| !(blink.from == from && blink.to == to));
        if on == 0 || off == 0 {
            return;
        }
        let start = self.blinks.last().map_or(0, |last| last.start.saturating_add(delay));
        if self.blinks.len() < MAX_BLINKS {
            self.blinks.push(Blink { from, to, on, off, start });
        }
    }

    /// Ends every blink process changing `from` (BLINK with no data, BLINK STOP).
    pub fn stop_blinks_from(&mut self, from: u8) {
        self.blinks.retain(|blink| blink.from != from);
    }

    /// Ends every blink process (RESET).
    pub fn stop_blinks(&mut self) {
        self.blinks.clear();
    }

    /// The blink processes, in the order they were defined.
    #[must_use]
    pub fn blinks(&self) -> &[Blink] {
        &self.blinks
    }

    /// The colour map as it shows `tenths` tenths of a second after the first blink process
    /// started: each process, in order, gives its `from` entry `to`'s current colour during its
    /// ON interval (section 5.3.2.7.3: later processes see earlier ones' results).
    #[must_use]
    pub fn at(&self, tenths: u32) -> Vec<Rgb> {
        let mut entries = self.entries.clone();
        // Section 5.3.2.7: processes acting at once run from the most recently defined to the
        // least, each taking the colour map the one before it left.
        for blink in self.blinks.iter().rev() {
            if tenths < blink.start {
                continue;
            }
            let period = blink.on.saturating_add(blink.off).max(1);
            let phase = tenths.saturating_sub(blink.start).checked_rem(period).unwrap_or(0);
            if phase < blink.on {
                let colour = entries.get(usize::from(blink.to)).copied().unwrap_or([0; 3]);
                if let Some(slot) = entries.get_mut(usize::from(blink.from)) {
                    *slot = colour;
                }
            }
        }
        entries
    }
}

/// A colour as a display with `bits`-bit colour registers shows it: each primary rounded to
/// `bits` bits, then widened back to 8 by repeating its top bits. VGA has 6-bit registers, and
/// PP3 runs on VGA: its screen shows the standard's 63 as 65 and 191 as 190, exactly this with
/// `bits` = 6. Eight or more leaves the colour unchanged.
#[must_use]
pub fn through_register(colour: Rgb, bits: u32) -> Rgb {
    colour.map(|primary| widen(primary, bits))
}

#[allow(clippy::arithmetic_side_effects, reason = "bits is 1 to 7 here and values stay below 2^16")]
fn widen(primary: u8, bits: u32) -> u8 {
    if bits >= 8 || bits == 0 {
        return primary;
    }
    let top = (1u32 << bits) - 1;
    let register = (u32::from(primary) * top + 127) / 255;
    let mut widened = 0u32;
    let mut filled = 0u32;
    while filled < 8 {
        widened = (widened << bits) | register;
        filled += bits;
    }
    u8::try_from(widened >> (filled - 8)).unwrap_or(u8::MAX)
}

/// Grey `index` of `count` uniformly spaced greys from black to white.
#[allow(clippy::arithmetic_side_effects, reason = "colour arithmetic on entries below 256 and intensities below 256")]
fn grey(index: usize, count: usize) -> Rgb {
    let steps = u32::try_from(count.saturating_sub(1)).unwrap_or(1).max(1);
    // Rounded to the nearest level, as section 5.3.2.5.2 rounds the hues' second primary.
    let level = u32::try_from(index).unwrap_or(0).saturating_mul(FULL).saturating_add(steps / 2) / steps;
    let level = u8::try_from(level).unwrap_or(u8::MAX);
    [level, level, level]
}

/// Hue `index` of `count` hues equally spaced counterclockwise from 0 degrees (section
/// 5.3.2.5.2). Angles are kept multiplied by `count` so they stay whole numbers.
#[allow(clippy::arithmetic_side_effects, reason = "colour arithmetic on entries below 256 and intensities below 256")]
fn hue(index: usize, count: usize) -> Rgb {
    let count = u32::try_from(count).unwrap_or(1).max(1);
    let angle = u32::try_from(index).unwrap_or(0).saturating_mul(CIRCLE); // degrees x count
    let primaries = [(BLUE_ANGLE, 2usize), (RED_ANGLE, 0usize), (GREEN_ANGLE, 1usize)]; // RGB slot
    let distance = |primary: u32| {
        let primary = primary.saturating_mul(count);
        let full = CIRCLE.saturating_mul(count);
        let difference = angle.abs_diff(primary);
        difference.min(full.saturating_sub(difference))
    };
    let mut order = primaries;
    order.sort_by_key(|(primary, _)| distance(*primary));
    let mut rgb = [0u32; 3];
    let [(first, first_slot), (_, second_slot), _] = order;
    if let Some(slot) = rgb.get_mut(first_slot) {
        *slot = FULL;
    }
    // The second primary: the distance from the closest primary over 60 degrees.
    // Section 5.3.2.5.2: P2 is normalised by the largest value the primary can hold "and then
    // rounded".
    let denominator = MIX_DEGREES.saturating_mul(count).max(1);
    let mix = distance(first).saturating_mul(FULL).saturating_add(denominator / 2) / denominator;
    if let Some(slot) = rgb.get_mut(second_slot) {
        *slot = mix.min(FULL);
    }
    rgb.map(|value| u8::try_from(value).unwrap_or(u8::MAX))
}

/// `value` with its lowest `bits` bits in reverse order.
fn reverse(value: u32, bits: u32) -> u32 {
    let mut out = 0;
    for bit in 0..bits {
        if value & (1u32 << bit) != 0 {
            out |= 1u32 << (bits.saturating_sub(1).saturating_sub(bit));
        }
    }
    out
}

/// Squared distance between two colours.
fn distance(a: Rgb, b: Rgb) -> u32 {
    a.iter().zip(b).map(|(x, y)| u32::from(x.abs_diff(y)).pow(2)).sum()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_map_of_16() {
        let palette = Palette::new(4);
        assert_eq!(palette.colour(0), [0, 0, 0]);
        assert_eq!(palette.white(), 7);
        assert_eq!(palette.colour(7), [255, 255, 255]);
        assert_eq!(palette.colour(8), [0, 0, 255]); // 0 degrees: blue
        // 90 degrees: red is closest (30 degrees away), blue second: blue = 30/60 of full.
        assert_eq!(palette.colour(10), [255, 0, 128]);
        // 135 degrees: red closest (15 away), green second: green = 15/60 of full, rounded.
        assert_eq!(palette.colour(11), [255, 64, 0]);
        // Greys rounded to the nearest level: 255 x 3 / 7 = 109.3, 255 x 4 / 7 = 145.7.
        assert_eq!(palette.colour(3), [109, 109, 109]);
        assert_eq!(palette.colour(4), [146, 146, 146]);
    }

    #[test]
    fn entries_from_operands_and_increments() {
        let palette = Palette::new(4);
        assert_eq!(palette.entry_from_operand(0b01_1111, 6), 7);
        assert_eq!(palette.entry_from_operand(0b01, 2), 4);
        assert_eq!(palette.next_entry(0b0101), Some(0b1101));
        assert_eq!(palette.next_entry(0b1101), Some(0b0011));
        assert_eq!(palette.next_entry(0b1111), None);
    }

    #[test]
    fn mode_zero_allocates_lowest_free_entry() {
        let mut palette = Palette::new(4);
        assert_eq!(palette.allocate([255, 255, 255]), 7);
        assert_eq!(palette.allocate([1, 2, 3]), 1);
        assert_eq!(palette.allocate([1, 2, 3]), 1);
        assert_eq!(palette.allocate([4, 5, 6]), 2);
    }

    #[test]
    fn vga_registers_show_colours_as_pp3_does() {
        assert_eq!(through_register([63, 191, 255], 6), [65, 190, 255]);
        assert_eq!(through_register([63, 191, 255], 8), [63, 191, 255]);
    }

    #[test]
    fn blink_alternates() {
        let mut palette = Palette::new(4);
        palette.blink(1, 7, 3, 2, 0);
        assert_eq!(palette.at(0)[1], [255, 255, 255]);
        assert_eq!(palette.at(3)[1], palette.colour(1));
        assert_eq!(palette.at(5)[1], [255, 255, 255]);
    }
    #[test]
    fn simultaneous_blinks_run_from_the_most_recent() {
        // Entry 1 blinks to entry 2, then entry 2 blinks to entry 3, both on at time 0: the most
        // recent runs first, so entry 1 takes entry 2's new colour, which is entry 3's.
        let mut palette = Palette::new(4);
        palette.blink(1, 2, 5, 5, 0);
        palette.blink(2, 3, 5, 5, 0);
        let colours = palette.at(0);
        assert_eq!(colours.get(1).copied(), Some(palette.colour(3)));
    }
}
