//! A player given no pace behaves as it did before the pace was added (DEC-7031 item 3:
//! pacing is added beside WAIT and BLINK, REQ-6531's ANIM-20, and changes nothing without it).
//!
//! Each stream is played by a fixed script of pushes and advances, and everything the player
//! reports after each call is summed: the events, the picture, the colour map, the ticks to
//! the next thing due and to the next blink, the WAIT's ticks left, the bytes held, the ticks
//! waited and the tick. The sums were taken from the player at livedevelopment 96307fd, the
//! commit before the pace, by running this file there unchanged (it uses only what that player
//! had), on 21 November 2026. The first page's were taken again on 22 November 2026 from the
//! player at d613621, the last commit before the pace was merged, because that page's sample
//! was redrawn in between (3f78114).
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use std::fmt::Write as _;

use naplps::limits::{RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_WIDTH};
use naplps::{Canvas, Player, StrokeFont, Terminal};

/// The 64-bit FNV-1a hash (Fowler, Noll and Vo; the constants are the algorithm's).
fn fnv(bytes: &[u8]) -> u64 {
    const OFFSET_BASIS: u64 = 0xCBF2_9CE4_8422_2325;
    const PRIME: u64 = 0x0000_0100_0000_01B3;
    bytes.iter().fold(OFFSET_BASIS, |hash, &byte| (hash ^ u64::from(byte)).wrapping_mul(PRIME))
}

/// The sample pages played, with WAITs, BLINKs or both, and one with neither.
const PAGES: [&str; 6] = [
    "samples/set-6/out/122-the-lure.nap",
    "samples/signal/out/01-tide-clock.nap",
    "samples/signal/out/03-constellation.nap",
    "samples/signal/out/06-two-languages.nap",
    "docs/examples/pages/11-animation.nap",
    "docs/examples/pages/12-postcard.nap",
];

/// The sums of [`PAGES`] played by [`play`] before the pace; the second of each pair is with
/// delays off.
const BEFORE_THE_PACE: [(u64, u64); 6] = [
    (0x33FF_F044_E36A_218C, 0x1EBA_20F6_5191_3281),
    (0xE173_763F_EE0B_3AA5, 0xD19D_E2AF_5B8A_0084),
    (0xC564_5386_4574_9BB0, 0x5C85_91A4_A9C8_BD43),
    (0xC58D_52AA_EEBC_FDD0, 0x85EE_A592_C9FD_C449),
    (0x13EF_5F75_7DA0_E36D, 0x13EF_5F75_7DA0_E36D),
    (0x31B4_5F62_D212_2D32, 0x31B4_5F62_D212_2D32),
];

/// Plays `stream` in pieces whose sizes and the ticks between them are fixed, then for a
/// minute and a half more, and returns the sum of every report.
fn play(stream: &[u8], delays: bool) -> u64 {
    let mut terminal = Terminal::new(4);
    terminal.set_font(StrokeFont::parse(include_str!("../../../fonts/neoteletext.strokes")).unwrap());
    let mut canvas = Canvas::new(RECEIVER_CANVAS_WIDTH, RECEIVER_CANVAS_HEIGHT).unwrap();
    let mut player = Player::new();
    player.set_delays(delays);
    let mut log = String::new();
    let report = |player: &Player, terminal: &Terminal, canvas: &Canvas, events: &[naplps::Event], log: &mut String| {
        let _ = writeln!(
            log,
            "{events:?} {:016x} {:?} {:?} {:?} {} {} {} {}",
            fnv(canvas.pixels()),
            player.colours(terminal),
            player.ticks_to_next(terminal),
            player.ticks_to_blink(terminal),
            player.waiting_ticks(),
            player.held_bytes(),
            player.waited_ticks(),
            player.tick()
        );
    };
    let mut rest = stream;
    let mut size = 1;
    let mut ticks = 0;
    while !rest.is_empty() {
        let (piece, more) = rest.split_at(size.min(rest.len()));
        rest = more;
        let events = player.push(&mut terminal, &mut canvas, piece);
        report(&player, &terminal, &canvas, &events, &mut log);
        let events = player.advance(&mut terminal, &mut canvas, ticks);
        report(&player, &terminal, &canvas, &events, &mut log);
        size = size * 3 % 97 + 1;
        ticks = (ticks + 7) % 23;
    }
    let events = player.end(&mut terminal, &mut canvas);
    report(&player, &terminal, &canvas, &events, &mut log);
    for step in [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 1] {
        let events = player.advance(&mut terminal, &mut canvas, step);
        report(&player, &terminal, &canvas, &events, &mut log);
    }
    fnv(log.as_bytes())
}

#[test]
fn a_player_with_no_pace_reports_what_the_player_before_the_pace_reported() {
    let mut sums = Vec::new();
    for path in PAGES {
        let full = format!("{}/../../{path}", env!("CARGO_MANIFEST_DIR"));
        let stream = std::fs::read(&full).unwrap_or_else(|error| panic!("{full}: {error}"));
        sums.push((play(&stream, true), play(&stream, false)));
    }
    assert_eq!(sums, BEFORE_THE_PACE);
}
