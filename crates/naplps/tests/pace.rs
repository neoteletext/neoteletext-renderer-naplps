//! A stream given to the terminal at a serial line's pace by [`Player::set_pace`] (DEC-7031
//! item 3; REQ-7024; DEC-6524 item 12 for WAIT on the presentation clock). Each test names what
//! it proves. The streams are the repository's own sample pages (`docs/examples/pages/`,
//! `samples/`) and small ones built here.
//!
//! The reference for "the picture at a tick" is a fresh terminal given the first N bytes by
//! [`Terminal::feed`], without [`Terminal::finish`]: the player runs `finish` only once the
//! hold is empty after [`Player::end`], so a truncated page drawn whole is not the picture a
//! line shows part way.
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::cast_possible_truncation,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::limits::{
    MAX_WAIT_HELD_BYTES, RECEIVER_CANVAS_HEIGHT, RECEIVER_CANVAS_WIDTH, TENTH_TICKS, WAIT_BUDGET_TICKS,
};
use naplps::{Canvas, Event, Pace, Player, Rgb, StrokeFont, Terminal};

const SO: u8 = 0x0E;
/// SELECT COLOR (ANSI X3.110-1983 section 5.3.2.6).
const SELECT_COLOUR: u8 = 0x3E;
/// RECTANGLE, filled, from the drawing point (section 5.3.3.4).
const RECT_FILLED: u8 = 0x31;
/// POINT SET, absolute (section 5.3.3.1).
const POINT_SET: u8 = 0x24;
/// BLINK (section 5.3.2.7).
const BLINK: u8 = 0x3F;
/// The colour-map bits the sample pages are drawn with: 16 entries, PP3's VGA mode.
const PALETTE_BITS: u32 = 4;

/// 1,200 bits a second at ten bits a byte and 60 ticks a second (DEC-7031 item 1,
/// `LINE_PACE_TICKS` 600): 1,200 bytes in 600 ticks.
const LINE_1200: Pace = Pace { bytes: 1200, ticks: 600 };
/// A fast pace whose bytes a tick are not whole, 71 3/7, so that a WAIT falls inside a tick.
const FAST: Pace = Pace { bytes: 500, ticks: 7 };
/// A slow pace: one byte every four ticks.
const SLOW: Pace = Pace { bytes: 1, ticks: 4 };
/// A pace of one and a half bytes a tick, whose credit is left over between bytes.
const HALVES: Pace = Pace { bytes: 3, ticks: 2 };

/// Sample pages with no WAIT, and with WAITs, read from the repository.
const PAGES_WITHOUT_WAIT: [&str; 4] = [
    "docs/examples/pages/02-shapes.nap",
    "docs/examples/pages/12-postcard.nap",
    "docs/examples/pages/14-supplementary.nap",
    "samples/set-4/out/108-festival-poster.nap",
];
/// See [`PAGES_WITHOUT_WAIT`].
const PAGES_WITH_WAITS: [&str; 3] = [
    "samples/set-6/out/122-the-lure.nap",
    "samples/signal/out/01-tide-clock.nap",
    "samples/set-4/out/104-lottery-results.nap",
];
/// A sample page that blinks and has no WAIT.
const BLINKING_PAGE: &str = "docs/examples/pages/11-animation.nap";

fn page(path: &str) -> Vec<u8> {
    let full = format!("{}/../../{path}", env!("CARGO_MANIFEST_DIR"));
    std::fs::read(&full).unwrap_or_else(|error| panic!("{full}: {error}"))
}

/// A terminal as the sample pages are drawn: the repository's stroke font, so text is drawn.
fn terminal() -> Terminal {
    let mut terminal = Terminal::new(PALETTE_BITS);
    terminal.set_font(StrokeFont::parse(include_str!("../../../fonts/neoteletext.strokes")).unwrap());
    terminal
}

fn canvas() -> Canvas {
    Canvas::new(RECEIVER_CANVAS_WIDTH, RECEIVER_CANVAS_HEIGHT).unwrap()
}

/// A terminal, its canvas and a player at tick 0 with `pace`.
struct Run {
    terminal: Terminal,
    canvas: Canvas,
    player: Player,
}

impl Run {
    fn new(pace: Option<Pace>) -> Self {
        let mut player = Player::new();
        player.set_pace(pace);
        Self { terminal: terminal(), canvas: canvas(), player }
    }

    fn push(&mut self, bytes: &[u8]) -> Vec<Event> {
        self.player.push(&mut self.terminal, &mut self.canvas, bytes)
    }

    fn end(&mut self) -> Vec<Event> {
        self.player.end(&mut self.terminal, &mut self.canvas)
    }

    fn advance(&mut self, ticks: u32) -> Vec<Event> {
        self.player.advance(&mut self.terminal, &mut self.canvas, ticks)
    }

    fn ticks_to_next(&self) -> Option<u32> {
        self.player.ticks_to_next(&self.terminal)
    }

    fn colours(&self) -> Vec<Rgb> {
        self.player.colours(&self.terminal)
    }

    /// A paced run of `stream`, pushed whole and ended at tick 0, as `naplps-render` plays it.
    fn of(stream: &[u8], pace: Pace) -> Self {
        let mut run = Self::new(Some(pace));
        let _ = run.push(stream);
        let _ = run.end();
        run
    }

    /// Advances one tick at a time until the player is idle, at most `limit` ticks; returns the
    /// tick reached.
    fn drain(&mut self, limit: u64) -> u64 {
        while !self.player.idle() {
            assert!(self.player.tick() < limit, "not idle by tick {limit}");
            let _ = self.advance(1);
        }
        self.player.tick()
    }
}

/// The picture of a fresh terminal given the first `n` bytes of `stream`, not finished.
fn first_bytes(stream: &[u8], n: usize) -> Canvas {
    let mut canvas = canvas();
    let _ = terminal().feed(&mut canvas, &stream[..n]);
    canvas
}

/// The picture, the colour map at rest and the border of `stream` drawn at once and finished.
fn at_once(stream: &[u8]) -> (Canvas, Vec<Rgb>, u8) {
    let mut canvas = canvas();
    let mut terminal = terminal();
    let _ = terminal.feed(&mut canvas, stream);
    let _ = terminal.finish(&mut canvas);
    (canvas, terminal.palette().at(0), terminal.border())
}

/// What a run has left, comparable with [`at_once`].
fn left(run: &Run) -> (Canvas, Vec<Rgb>, u8) {
    (run.canvas.clone(), run.terminal.palette().at(0), run.terminal.border())
}

/// The bytes a line of `pace` has delivered after `ticks` paced ticks: floor(ticks x bytes /
/// ticks of the pace), 0 in either part taken as 1 (DEC-7031 item 3).
fn delivered(pace: Pace, ticks: u64) -> u64 {
    ticks * u64::from(pace.bytes.max(1)) / u64::from(pace.ticks.max(1))
}

/// The paced ticks a line of `pace` takes to deliver `bytes` bytes: ceil(bytes x ticks / bytes
/// of the pace).
fn line_ticks(pace: Pace, bytes: usize) -> u64 {
    (bytes as u64 * u64::from(pace.ticks.max(1))).div_ceil(u64::from(pace.bytes.max(1)))
}

/// The bytes of `stream` the player has given to its terminal.
fn given(run: &Run, stream_length: usize) -> usize {
    stream_length - run.player.held_bytes()
}

/// The WAITs a stream's terminal reports while it is fed (without finish), in tenths each.
fn waits_of(stream: &[u8]) -> Vec<u32> {
    let mut canvas = canvas();
    terminal()
        .feed(&mut canvas, stream)
        .into_iter()
        .filter_map(|event| if let Event::Wait(tenths) = event { Some(tenths) } else { None })
        .collect()
}

/// The WAITs a stream's terminal reports at finish, after being fed it all.
fn finish_waits(stream: &[u8]) -> Vec<u32> {
    let mut canvas = canvas();
    let mut terminal = terminal();
    let _ = terminal.feed(&mut canvas, stream);
    terminal
        .finish(&mut canvas)
        .into_iter()
        .filter_map(|event| if let Event::Wait(tenths) = event { Some(tenths) } else { None })
        .collect()
}

/// The ticks a player plays the WAITs of `tenths`, within the budget (ANIM-20).
fn wait_ticks(tenths: &[u32]) -> u64 {
    u64::from(tenths.iter().map(|tenths| tenths * TENTH_TICKS).sum::<u32>().min(WAIT_BUDGET_TICKS))
}

/// A three-byte coordinate pair in the default domain: (`x`/256, `y`/256) of the unit screen
/// (section 5.3.2.2.3).
fn pair(x: u8, y: u8) -> [u8; 3] {
    let (x, y) = (u16::from(x), u16::from(y));
    let byte = |shift: u16| 0x40 | ((((x >> shift) & 7) as u8) << 3) | (((y >> shift) & 7) as u8);
    [byte(6), byte(3), byte(0)]
}

/// PDI bytes drawing a filled rectangle of `entry` from (`x`, `y`) of size (`width`, `height`).
fn rectangle(entry: u8, x: u8, y: u8, width: u8, height: u8) -> Vec<u8> {
    let mut bytes = vec![SO, SELECT_COLOUR, 0x40 | (entry << 2), POINT_SET];
    bytes.extend(pair(x, y));
    bytes.push(RECT_FILLED);
    bytes.extend(pair(width, height));
    bytes
}

/// WAIT of `tenths` tenths, 0 to 63 (section 5.3.2.8).
fn wait(tenths: u8) -> [u8; 3] {
    [0x3D, 0x5C, 0x40 | tenths]
}

/// Rectangles of entries 1 to 6 with a WAIT of each of `tenths` between them.
fn staged(tenths: &[u8]) -> Vec<u8> {
    let mut stream = rectangle(1, 0, 0, 40, 30);
    for (stage, &tenths) in tenths.iter().enumerate() {
        stream.extend(wait(tenths));
        let stage = stage as u8 + 1;
        stream.extend(rectangle(stage % 6 + 1, (stage % 8) * 30, 60, 30, 40));
    }
    stream
}

// ----- 1. At a tick the picture is a terminal given the bytes the line has delivered ---------

#[test]
fn at_chosen_ticks_the_paced_picture_is_a_terminal_fed_the_bytes_the_line_delivered() {
    for path in PAGES_WITHOUT_WAIT {
        let stream = page(path);
        assert!(waits_of(&stream).is_empty(), "{path} has no WAIT");
        for pace in [LINE_1200, FAST, HALVES, Pace { bytes: 7, ticks: 3 }] {
            let total = line_ticks(pace, stream.len());
            let mut chosen: Vec<u64> = vec![1, 2, 3, 7, total / 3, total / 2, total - 1];
            chosen.retain(|&tick| tick > 0 && tick < total);
            chosen.sort_unstable();
            chosen.dedup();
            let mut run = Run::of(&stream, pace);
            assert_eq!(run.player.held_bytes(), stream.len(), "{path}: nothing is given at tick 0");
            for tick in chosen {
                let _ = run.advance((tick - run.player.tick()) as u32);
                let n = delivered(pace, tick) as usize;
                assert!(n < stream.len());
                assert_eq!(given(&run, stream.len()), n, "{path} at {pace:?}, tick {tick}: N");
                assert!(
                    run.canvas == first_bytes(&stream, n),
                    "{path} at {pace:?}, tick {tick}: the picture of {n} bytes"
                );
            }
        }
    }
}

#[test]
fn at_every_tick_the_paced_picture_is_a_terminal_fed_the_bytes_the_line_delivered() {
    for path in &PAGES_WITHOUT_WAIT[..2] {
        let stream = page(path);
        for pace in [LINE_1200, HALVES, SLOW] {
            let mut run = Run::of(&stream, pace);
            // The reference is fed the newly delivered bytes each tick; fed in pieces, a stream
            // draws what it draws fed whole (the fuzz target naplps_stream).
            let mut reference = canvas();
            let mut reference_terminal = terminal();
            let mut fed = 0;
            for tick in 1..line_ticks(pace, stream.len()) {
                let _ = run.advance(1);
                let n = delivered(pace, tick) as usize;
                let _ = reference_terminal.feed(&mut reference, &stream[fed..n]);
                fed = n;
                assert_eq!(given(&run, stream.len()), n, "{path} at {pace:?}, tick {tick}");
                assert!(run.canvas == reference, "{path} at {pace:?}, tick {tick}");
            }
        }
    }
}

// ----- 2. The last frame is the picture painted at once --------------------------------------

#[test]
fn the_last_frame_is_the_picture_painted_at_once_and_finish_runs_once_when_the_hold_empties() {
    let mut pages: Vec<Vec<u8>> = PAGES_WITHOUT_WAIT.iter().chain(&PAGES_WITH_WAITS).map(|path| page(path)).collect();
    pages.push(page(BLINKING_PAGE));
    // A stream whose last rectangle only finish draws: its operands could go on.
    let mut open = rectangle(2, 0, 0, 64, 64);
    open.extend(rectangle(5, 100, 100, 64, 64));
    pages.push(open.clone());
    for stream in &pages {
        let whole = at_once(stream);
        // One byte every four ticks only for the small streams: each tick's call costs a
        // pass over the canvas, and the large pages would take ten thousand.
        let chosen_paces: &[Pace] = if stream.len() < 300 { &[LINE_1200, FAST, SLOW] } else { &[LINE_1200, FAST] };
        for &pace in chosen_paces {
            let mut run = Run::of(stream, pace);
            let mut events = Vec::new();
            let end = line_ticks(pace, stream.len()) + wait_ticks(&waits_of(stream));
            while !run.player.idle() {
                if run.player.held_bytes() > 0 && run.player.tick().is_multiple_of((end / 8).max(1)) {
                    // Before the hold empties, the picture is never finished early.
                    assert!(
                        run.canvas == first_bytes(stream, given(&run, stream.len())),
                        "tick {}: drawn beyond the bytes given",
                        run.player.tick()
                    );
                }
                events.extend(run.advance(1));
            }
            assert_eq!(run.player.tick(), end, "{pace:?}");
            assert!(left(&run) == whole, "{pace:?}: the last frame is the picture painted at once");
            // Nothing more is drawn or reported, however the player is called again.
            let mut after = run.end();
            after.extend(run.advance(1000));
            after.extend(run.push(&[]));
            after.extend(run.end());
            assert_eq!(after, Vec::new(), "{pace:?}: no second finish");
            assert!(left(&run) == whole, "{pace:?}: still the picture painted at once");
        }
    }
    // The open rectangle shows finish ran: fed without it, the last rectangle is missing.
    assert!(first_bytes(&open, open.len()) != at_once(&open).0, "the stream needs finish to be whole");
}

#[test]
fn a_stream_not_ended_is_not_finished_when_its_hold_empties() {
    let mut open = rectangle(2, 0, 0, 64, 64);
    open.extend(rectangle(5, 100, 100, 64, 64));
    let mut run = Run::new(Some(HALVES));
    let _ = run.push(&open);
    let _ = run.drain(1000);
    assert!(run.canvas == first_bytes(&open, open.len()), "not ended: no finish");
    let _ = run.end();
    assert!(run.canvas == at_once(&open).0, "ended: finish runs at once, nothing being held");
}

// ----- 3. A WAIT adds its time ---------------------------------------------------------------

/// Plays `stream` at `pace` one tick at a time and checks the time and the pictures: the player
/// is idle at the line's ticks plus every WAIT's, the ticks spent waiting are the WAITs', the
/// picture is a terminal fed the bytes given so far (every `every` ticks, a fresh terminal each
/// time being slow), and at the end it is the picture painted at once.
fn wait_adds_its_time(name: &str, stream: &[u8], pace: Pace, every: u64) {
    let tenths = waits_of(stream);
    assert!(!tenths.is_empty(), "{name} has WAITs");
    let mut run = Run::of(stream, pace);
    let mut ticks_waiting = 0u64;
    let mut previous = 0;
    let mut waits_seen = Vec::new();
    while !run.player.idle() {
        assert!(run.player.tick() < 100_000, "{name}: never idle");
        if run.player.waiting_ticks() > 0 {
            ticks_waiting += 1;
        }
        for event in run.advance(1) {
            if let Event::Wait(tenths) = event {
                waits_seen.push(tenths);
            }
        }
        let n = given(&run, stream.len());
        assert!(n >= previous, "{name}: bytes given never go back");
        previous = n;
        if run.player.held_bytes() > 0 && run.player.tick().is_multiple_of(every) {
            assert!(run.canvas == first_bytes(stream, n), "{name} at {pace:?}, tick {}", run.player.tick());
        }
    }
    let expected = line_ticks(pace, stream.len()) + wait_ticks(&tenths);
    assert_eq!(run.player.tick(), expected, "{name} at {pace:?}: the line's ticks and every WAIT's");
    assert_eq!(ticks_waiting, wait_ticks(&tenths), "{name} at {pace:?}: the ticks spent in WAITs");
    assert_eq!(u64::from(run.player.waited_ticks()), wait_ticks(&tenths), "{name}");
    // A WAIT at the very end, with no byte after it, is run by finish: reported, and with
    // nothing after it to delay, not played.
    let mut all = tenths.clone();
    all.extend(finish_waits(stream));
    assert_eq!(waits_seen, all, "{name}: every WAIT is reported, in order");
    assert!(left(&run) == at_once(stream), "{name} at {pace:?}: the picture painted at once");
}

#[test]
fn several_waits_each_add_their_time_to_the_line_at_1200_bits_a_second() {
    wait_adds_its_time("three stages", &staged(&[3, 2, 4]), LINE_1200, 1);
}

#[test]
fn a_wait_met_inside_a_tick_at_a_fast_pace_adds_its_time() {
    // 71 3/7 bytes a tick: each WAIT here falls inside a tick's bytes.
    let stream = staged(&[1, 5, 2, 7, 1, 3, 1, 2, 4, 1]);
    assert!(stream.len() > 71 * 2);
    wait_adds_its_time("five stages", &stream, FAST, 1);
    wait_adds_its_time("five stages", &stream, Pace { bytes: 13, ticks: 1 }, 1);
}

#[test]
fn the_sample_pages_waits_add_their_time_at_several_paces() {
    for path in PAGES_WITH_WAITS {
        for pace in [LINE_1200, FAST] {
            wait_adds_its_time(path, &page(path), pace, 89);
        }
    }
}

// ----- 4. The budget of waiting --------------------------------------------------------------

#[test]
fn the_budget_of_waiting_still_caps_the_waits_under_a_pace() {
    // Twelve WAITs of 63 tenths, 4,536 ticks, past WAIT_BUDGET_TICKS (3,600).
    let stream = staged(&[63; 12]);
    let tenths = waits_of(&stream);
    assert_eq!(tenths.iter().sum::<u32>() * TENTH_TICKS, 4536);
    for pace in [LINE_1200, FAST] {
        let mut run = Run::of(&stream, pace);
        let idle = run.drain(20_000);
        assert_eq!(idle, line_ticks(pace, stream.len()) + u64::from(WAIT_BUDGET_TICKS), "{pace:?}");
        assert_eq!(run.player.waited_ticks(), WAIT_BUDGET_TICKS);
        assert!(left(&run) == at_once(&stream), "the picture painted at once");
    }
}

// ----- 5. The viewer's setting off -----------------------------------------------------------

#[test]
fn a_pace_set_while_delays_are_off_is_not_taken_and_the_stream_is_drawn_at_once() {
    let stream = page(PAGES_WITH_WAITS[0]);
    let mut run = Run::new(None);
    run.player.set_delays(false);
    run.player.set_pace(Some(LINE_1200));
    assert_eq!(run.player.pace(), None);
    let _ = run.push(&stream);
    let _ = run.end();
    assert_eq!((run.player.held_bytes(), run.player.waiting_ticks(), run.player.tick()), (0, 0, 0));
    assert!(run.player.idle());
    assert!(left(&run) == at_once(&stream), "the picture painted at once");
    // Delays on again bring no pace back.
    run.player.set_delays(true);
    assert_eq!(run.player.pace(), None);
}

#[test]
fn delays_turned_off_during_a_paced_run_draw_what_is_held_at_the_next_call() {
    let stream = page(PAGES_WITH_WAITS[0]);
    let whole = at_once(&stream);
    // Turned off while bytes are paced, and while a WAIT is played.
    for (when, ticks) in [("paced", 20u32), ("in a WAIT", 0)] {
        let mut run = Run::of(&stream, LINE_1200);
        if ticks == 0 {
            while run.player.waiting_ticks() == 0 {
                let _ = run.advance(1);
            }
        } else {
            let _ = run.advance(ticks);
        }
        assert!(run.player.held_bytes() > 0, "{when}");
        let tick = run.player.tick();
        run.player.set_delays(false);
        assert_eq!(run.player.pace(), None, "{when}");
        assert_eq!(run.player.waiting_ticks(), 0, "{when}");
        let _ = run.advance(0);
        assert_eq!((run.player.held_bytes(), run.player.tick()), (0, tick), "{when}: drawn at once, no tick passing");
        assert!(run.player.idle());
        assert!(left(&run) == whole, "{when}");
        run.player.set_pace(Some(SLOW));
        assert_eq!(run.player.pace(), None, "{when}: a pace is not taken while delays are off");
    }
}

// ----- 6. idle ------------------------------------------------------------------------------

#[test]
fn idle_is_true_on_a_new_player_false_while_bytes_are_held_or_a_wait_plays_and_true_once_drained() {
    assert!(Player::new().idle());
    let mut run = Run::new(Some(SLOW));
    assert!(run.player.idle(), "a pace and nothing held");
    let _ = run.push(&rectangle(1, 0, 0, 10, 10));
    assert!(!run.player.idle(), "bytes held");
    let _ = run.drain(1000);
    assert!(run.player.idle());
    // A WAIT as the stream's last bytes: the byte after its operands runs it, and with that
    // byte taken nothing is held while it plays.
    let mut stream = rectangle(1, 0, 0, 10, 10);
    stream.extend(wait(5));
    stream.push(POINT_SET);
    let mut run = Run::of(&stream, HALVES);
    while run.player.held_bytes() > 0 {
        assert!(!run.player.idle());
        let _ = run.advance(1);
    }
    assert!(run.player.waiting_ticks() > 0, "the WAIT plays after the last byte");
    let mut played = 0;
    while run.player.waiting_ticks() > 0 {
        assert!(!run.player.idle(), "a WAIT plays with nothing held");
        assert_eq!(run.player.held_bytes(), 0);
        let _ = run.advance(1);
        played += 1;
    }
    assert_eq!(played, 5 * TENTH_TICKS);
    assert!(run.player.idle());
    // Without a pace, a WAIT holding bytes back.
    let mut run = Run::new(None);
    let _ = run.push(&staged(&[2]));
    assert!(!run.player.idle());
    let _ = run.advance(2 * TENTH_TICKS);
    assert!(run.player.idle());
}

// ----- 8. advance(n) is n calls of advance(1) -------------------------------------------------

#[test]
fn advancing_n_ticks_at_once_is_advancing_one_tick_n_times() {
    let mut streams: Vec<(String, Vec<u8>, Pace)> = Vec::new();
    streams.push(("stages".into(), staged(&[1, 3, 2]), HALVES));
    streams.push(("stages fast".into(), staged(&[1, 5, 2, 7, 1]), FAST));
    let lure = page(PAGES_WITH_WAITS[0]);
    streams.push((PAGES_WITH_WAITS[0].into(), lure, Pace { bytes: 1200, ticks: 25 }));
    let mut blinking = page(BLINKING_PAGE);
    blinking.extend(wait(2));
    blinking.extend(rectangle(3, 50, 50, 20, 20));
    streams.push(("blinking".into(), blinking, Pace { bytes: 5, ticks: 3 }));
    for (number, (name, stream, pace)) in streams.iter().enumerate() {
        // Every tick for the small streams; every fifth for the sample page, whose drawing
        // again from tick 0 for each is slow.
        let stride = if number == 2 { 5 } else { 1 };
        let mut singly = Run::of(stream, *pace);
        let total = singly.drain(100_000) as u32 + 5;
        let mut singly = Run::of(stream, *pace);
        let mut single_events = Vec::new();
        let mut pictures = vec![(singly.canvas.clone(), singly.colours(), single_events.clone())];
        for _ in 0..total {
            single_events.extend(singly.advance(1));
            pictures.push((singly.canvas.clone(), singly.colours(), single_events.clone()));
        }
        // Every tick reached in one call.
        for n in (0..=total).step_by(stride) {
            let mut once = Run::of(stream, *pace);
            let events = once.advance(n);
            assert_eq!(once.player.tick(), u64::from(n), "{name}");
            let (picture, colours, events_then) = &pictures[n as usize];
            assert!(once.canvas == *picture, "{name}: tick {n}");
            assert_eq!(&once.colours(), colours, "{name}: colours at tick {n}");
            assert_eq!(&events, events_then, "{name}: events by tick {n}");
        }
        // And in calls of mixed sizes.
        let mut mixed = Run::of(stream, *pace);
        let mut step = 1;
        while mixed.player.tick() < u64::from(total) {
            let n = step.min(total - mixed.player.tick() as u32);
            let _ = mixed.advance(n);
            assert!(
                mixed.canvas == pictures[mixed.player.tick() as usize].0,
                "{name}: mixed, tick {}",
                mixed.player.tick()
            );
            step = step % 7 + 2;
        }
    }
}

#[test]
fn advancing_the_most_ticks_at_once_ends() {
    let stream = staged(&[2, 3]);
    for pace in [Some(SLOW), Some(Pace { bytes: 1, ticks: u32::MAX }), Some(Pace { bytes: u32::MAX, ticks: 1 }), None] {
        let mut run = Run::new(pace);
        let _ = run.push(&stream);
        let _ = run.end();
        let _ = run.advance(u32::MAX);
        assert_eq!(run.player.tick(), u64::from(u32::MAX), "{pace:?}");
        let _ = run.advance(u32::MAX);
        assert_eq!(run.player.tick(), 2 * u64::from(u32::MAX), "{pace:?}");
        if pace != Some(Pace { bytes: 1, ticks: u32::MAX }) {
            assert!(run.player.idle(), "{pace:?}");
            assert!(left(&run) == at_once(&stream), "{pace:?}");
        }
    }
}

// ----- 9. ticks_to_next ----------------------------------------------------------------------

/// Plays `stream` at `pace` one tick at a time and checks that bytes are drawn on a tick only
/// when `ticks_to_next` said 1 before it, and, when `exact`, that when it says k, the next
/// thing (bytes drawn or a WAIT's end) happens k ticks later and nothing happens before.
fn ticks_to_next_holds(name: &str, stream: &[u8], pace: Pace, exact: bool) {
    let mut run = Run::of(stream, pace);
    let mut countdown: Option<u32> = None;
    while !run.player.idle() {
        let next = run.ticks_to_next();
        assert!(next.is_some(), "{name}: something is held, so something is due");
        if exact {
            if let Some(left) = countdown {
                assert_eq!(
                    next,
                    Some(left),
                    "{name}, tick {}: the time to the next thing counts down",
                    run.player.tick()
                );
            }
            countdown = next;
        }
        let (held, waiting) = (run.player.held_bytes(), run.player.waiting_ticks());
        let _ = run.advance(1);
        let drawn = run.player.held_bytes() < held;
        if drawn {
            assert_eq!(next, Some(1), "{name}, tick {}: bytes drawn on a tick not said to be due", run.player.tick());
        }
        if exact {
            let happened = drawn || waiting > 0 && run.player.waiting_ticks() == 0;
            let left = countdown.unwrap() - 1;
            assert_eq!(happened, left == 0, "{name}, tick {}: due when said, and not before", run.player.tick());
            countdown = if happened { None } else { Some(left) };
        }
    }
    assert_eq!(run.ticks_to_next(), None, "{name}: nothing is due once idle");
}

#[test]
fn bytes_are_drawn_only_on_a_tick_ticks_to_next_said_was_due() {
    for pace in [LINE_1200, FAST, HALVES, SLOW] {
        ticks_to_next_holds("stages", &staged(&[2, 1, 3]), pace, false);
        ticks_to_next_holds(PAGES_WITH_WAITS[0], &page(PAGES_WITH_WAITS[0]), pace, false);
    }
}

#[test]
fn ticks_to_next_is_exact_at_a_slow_pace() {
    let mut run = Run::of(&rectangle(1, 0, 0, 10, 10), SLOW);
    assert_eq!(run.ticks_to_next(), Some(4), "one byte every four ticks");
    let _ = run.advance(3);
    assert_eq!((run.ticks_to_next(), run.player.held_bytes()), (Some(1), 11));
    let _ = run.advance(1);
    assert_eq!((run.ticks_to_next(), run.player.held_bytes()), (Some(4), 10));
    ticks_to_next_holds("stages", &staged(&[2, 1]), SLOW, true);
    ticks_to_next_holds("stages", &staged(&[2, 1]), Pace { bytes: 2, ticks: 9 }, true);
}

// ----- 10. Runs ------------------------------------------------------------------------------

#[test]
fn bytes_pushed_after_the_hold_emptied_start_a_new_run_with_no_burst_from_idle_ticks() {
    let first = rectangle(1, 0, 0, 10, 10);
    let second = page(PAGES_WITHOUT_WAIT[1]);
    for pace in [HALVES, LINE_1200, Pace { bytes: 7, ticks: 3 }] {
        let mut run = Run::new(Some(pace));
        let _ = run.push(&first);
        let _ = run.drain(1000);
        // Idle ticks earn nothing.
        let _ = run.advance(500);
        let _ = run.push(&second);
        assert_eq!(run.player.held_bytes(), second.len(), "{pace:?}: nothing drawn as the run starts");
        for tick in 1..=20 {
            let _ = run.advance(1);
            assert_eq!(given(&run, second.len()) as u64, delivered(pace, tick), "{pace:?}: tick {tick} of the new run");
        }
    }
    // A new player's ticks before any byte earn nothing either.
    let mut run = Run::new(Some(HALVES));
    let _ = run.advance(1000);
    let _ = run.push(&second);
    assert_eq!(run.player.held_bytes(), second.len());
    let _ = run.advance(1);
    assert_eq!(given(&run, second.len()), 1);
}

#[test]
fn a_run_that_drew_its_last_byte_with_credit_left_forgets_it() {
    // At 7 bytes in 3 ticks a run of 10 bytes ends at tick 5 (11 delivered) with credit left.
    let first: Vec<u8> = rectangle(1, 0, 0, 10, 10)[..10].to_vec();
    let second = page(PAGES_WITHOUT_WAIT[1]);
    let pace = Pace { bytes: 7, ticks: 3 };
    let mut run = Run::new(Some(pace));
    let _ = run.push(&first);
    let _ = run.advance(5);
    assert!(run.player.idle());
    let _ = run.push(&second);
    let _ = run.advance(1);
    assert_eq!(given(&run, second.len()), 2, "floor(7/3), not the last run's leftover as well");
}

#[test]
fn bytes_pushed_mid_run_join_the_run() {
    let stream = page(PAGES_WITHOUT_WAIT[3]);
    let (head, tail) = stream.split_at(40);
    for pace in [HALVES, LINE_1200, Pace { bytes: 7, ticks: 3 }] {
        let mut run = Run::new(Some(pace));
        let _ = run.push(head);
        let _ = run.advance(5);
        assert!(run.player.held_bytes() > 0);
        let _ = run.push(tail);
        for tick in 6..=60 {
            let _ = run.advance(1);
            assert_eq!(given(&run, stream.len()) as u64, delivered(pace, tick), "{pace:?}: tick {tick}");
        }
        assert!(
            run.canvas == first_bytes(&stream, delivered(pace, 60) as usize),
            "{pace:?}: the picture of the bytes delivered"
        );
    }
}

#[test]
fn bytes_pushed_during_a_wait_that_ended_the_previous_run_start_a_new_run() {
    // The previous run's last byte runs a WAIT; bytes pushed while it plays begin a new run.
    let mut first = rectangle(1, 0, 0, 10, 10);
    first.extend(wait(3));
    first.push(POINT_SET);
    let second = page(PAGES_WITHOUT_WAIT[1]);
    for pace in [Pace { bytes: 7, ticks: 3 }, Pace { bytes: 40, ticks: 1 }, HALVES] {
        let mut run = Run::new(Some(pace));
        let _ = run.push(&first);
        while run.player.held_bytes() > 0 {
            let _ = run.advance(1);
        }
        assert!(run.player.waiting_ticks() > 0, "{pace:?}: the WAIT plays");
        let _ = run.advance(2);
        let _ = run.push(&second);
        while run.player.waiting_ticks() > 0 {
            assert_eq!(run.player.held_bytes(), second.len(), "{pace:?}: held through the WAIT");
            let _ = run.advance(1);
        }
        assert_eq!(run.player.held_bytes(), second.len(), "{pace:?}: no credit from the last run");
        for tick in 1..=10 {
            let _ = run.advance(1);
            assert_eq!(
                given(&run, second.len()) as u64,
                delivered(pace, tick).min(second.len() as u64),
                "{pace:?}: tick {tick} after the WAIT"
            );
        }
    }
}

#[test]
fn credit_left_when_a_wait_inside_a_run_begins_is_kept_after_it() {
    // A WAIT inside the run: the ticks before it and after it add up to the line's time.
    let stream = staged(&[2]);
    let pace = Pace { bytes: 7, ticks: 3 };
    let mut run = Run::of(&stream, pace);
    let idle = run.drain(1000);
    assert_eq!(idle, line_ticks(pace, stream.len()) + 2 * u64::from(TENTH_TICKS));
}

// ----- 11. Paces of 0 and of the most ---------------------------------------------------------

/// What a run of `stream` at `pace` shows at each tick: the bytes given and the picture's sum.
fn trace(stream: &[u8], pace: Pace, ticks: u32) -> Vec<(usize, Option<u32>)> {
    let mut run = Run::of(stream, pace);
    let mut trace = Vec::new();
    for _ in 0..ticks {
        let _ = run.advance(1);
        trace.push((given(&run, stream.len()), run.ticks_to_next()));
    }
    trace
}

#[test]
fn a_pace_of_0_bytes_or_0_ticks_is_taken_as_1() {
    let stream = staged(&[1]);
    let ticks = 200;
    assert_eq!(trace(&stream, Pace { bytes: 0, ticks: 0 }, ticks), trace(&stream, Pace { bytes: 1, ticks: 1 }, ticks));
    assert_eq!(trace(&stream, Pace { bytes: 0, ticks: 3 }, ticks), trace(&stream, Pace { bytes: 1, ticks: 3 }, ticks));
    assert_eq!(trace(&stream, Pace { bytes: 4, ticks: 0 }, ticks), trace(&stream, Pace { bytes: 4, ticks: 1 }, ticks));
    // The pace is reported as it was set.
    let mut player = Player::new();
    player.set_pace(Some(Pace { bytes: 0, ticks: 0 }));
    assert_eq!(player.pace(), Some(Pace { bytes: 0, ticks: 0 }));
}

#[test]
fn a_pace_of_the_most_bytes_or_ticks_neither_panics_nor_overflows() {
    let stream = staged(&[1, 2]);
    let whole = at_once(&stream);
    // The most bytes in a tick: everything on the first tick, but for the WAITs.
    for pace in [Pace { bytes: u32::MAX, ticks: 1 }, Pace { bytes: u32::MAX, ticks: 0 }] {
        let mut run = Run::of(&stream, pace);
        assert_eq!(run.ticks_to_next(), Some(1));
        let idle = run.drain(1000);
        assert_eq!(idle, 1 + 3 * u64::from(TENTH_TICKS), "{pace:?}");
        assert!(left(&run) == whole, "the picture painted at once");
    }
    // One byte in the most ticks.
    let mut run = Run::of(&stream, Pace { bytes: 1, ticks: u32::MAX });
    assert_eq!(run.ticks_to_next(), Some(u32::MAX));
    let _ = run.advance(u32::MAX - 1);
    assert_eq!((given(&run, stream.len()), run.ticks_to_next()), (0, Some(1)));
    let _ = run.advance(1);
    assert_eq!(given(&run, stream.len()), 1);
    for _ in 0..3 {
        let _ = run.advance(u32::MAX);
    }
    assert_eq!(given(&run, stream.len()), 4);
    // The most of both: a byte a tick.
    let max = Pace { bytes: u32::MAX, ticks: u32::MAX };
    assert_eq!(trace(&stream, max, 100), trace(&stream, Pace { bytes: 1, ticks: 1 }, 100));
}

// ----- 12. The hold's bound ------------------------------------------------------------------

#[test]
fn exactly_the_most_bytes_held_keeps_the_pace_and_one_more_ends_it_and_draws_everything() {
    let stream = page(PAGES_WITHOUT_WAIT[3]);
    let mut run = Run::new(Some(LINE_1200));
    let _ = run.push(&stream);
    let _ = run.advance(10);
    let held = run.player.held_bytes();
    assert_eq!(held, stream.len() - 20);
    // NUL is passed over (section 6.1), so the padding draws nothing.
    let padding = vec![0u8; MAX_WAIT_HELD_BYTES - held];
    let _ = run.push(&padding);
    assert_eq!(run.player.held_bytes(), MAX_WAIT_HELD_BYTES, "exactly the most is held");
    assert_eq!(run.player.pace(), Some(LINE_1200), "and the pace goes on");
    let _ = run.advance(1);
    assert_eq!(run.player.held_bytes(), MAX_WAIT_HELD_BYTES - 2, "two bytes a tick still");
    let _ = run.push(&[0, 0, 0]);
    assert_eq!(run.player.pace(), None, "one more than the most ends the pace");
    assert_eq!(run.player.held_bytes(), 0, "and everything is drawn");
    let mut all = stream.clone();
    all.extend(&padding);
    all.extend([0, 0, 0]);
    assert!(run.canvas == first_bytes(&all, all.len()), "everything held is drawn");
    let _ = run.end();
    assert!(left(&run) == at_once(&stream), "the picture painted at once");
    // The pace is not taken up again.
    let _ = run.push(&rectangle(1, 0, 0, 5, 5));
    assert_eq!(run.player.held_bytes(), 0);
}

// ----- 13. Changing the pace mid-run ---------------------------------------------------------

#[test]
fn removing_the_pace_mid_run_draws_the_rest_at_the_next_call() {
    for path in [PAGES_WITHOUT_WAIT[3], PAGES_WITH_WAITS[0]] {
        let stream = page(path);
        for call in ["advance 0", "push", "end"] {
            let mut run = Run::new(Some(LINE_1200));
            let _ = run.push(&stream);
            let _ = run.advance(10);
            run.player.set_pace(None);
            assert_eq!(run.player.pace(), None);
            if run.player.waiting_ticks() == 0 {
                assert_eq!(run.player.held_bytes(), stream.len() - 20, "{path}, {call}: nothing drawn by setting it");
            }
            match call {
                "advance 0" => drop(run.advance(0)),
                "push" => drop(run.push(&[])),
                _ => drop(run.end()),
            }
            if waits_of(&stream).is_empty() {
                assert_eq!(run.player.held_bytes(), 0, "{path}, {call}: the rest is drawn");
            } else {
                // Drawn up to the next WAIT, which still plays.
                assert!(run.player.waiting_ticks() > 0 || run.player.held_bytes() == 0, "{path}, {call}");
                assert!(run.canvas == first_bytes(&stream, given(&run, stream.len())), "{path}, {call}");
            }
            let _ = run.end();
            let _ = run.drain(10_000);
            assert!(left(&run) == at_once(&stream), "{path}, {call}");
        }
    }
}

#[test]
fn changing_the_pace_mid_run_forgets_the_credit() {
    let stream = page(PAGES_WITHOUT_WAIT[1]);
    // At 3 bytes in 2 ticks, one tick gives 1 byte and leaves half a byte's credit.
    let mut run = Run::of(&stream, HALVES);
    let _ = run.advance(1);
    assert_eq!(given(&run, stream.len()), 1);
    run.player.set_pace(Some(HALVES));
    let _ = run.advance(1);
    assert_eq!(given(&run, stream.len()), 2, "the same pace set again: its credit forgotten, 1 more byte, not 2");
    // To a slower pace: its own count from the change.
    run.player.set_pace(Some(SLOW));
    assert_eq!(run.player.pace(), Some(SLOW));
    for tick in 1..=12 {
        let _ = run.advance(1);
        assert_eq!(given(&run, stream.len()) as u64, 2 + delivered(SLOW, tick), "tick {tick} at the new pace");
    }
}

// ----- 14. BLINK under a pace -----------------------------------------------------------------

#[test]
fn a_blink_under_a_pace_is_timed_from_the_tick_its_bytes_were_drawn() {
    // A rectangle, then a BLINK of its entry to entry 7, 5 tenths on and 5 off.
    let mut stream = rectangle(1, 0, 0, 32, 16);
    stream.extend(rectangle(2, 64, 64, 32, 16));
    stream.extend([BLINK, 0x40 | (7 << 2), 0x45, 0x45, 0x40]);
    stream.extend(rectangle(3, 128, 0, 32, 16));
    // The fewest bytes after which a terminal holds the blink.
    let defined = (1..=stream.len())
        .find(|&n| {
            let mut terminal = terminal();
            let _ = terminal.feed(&mut canvas(), &stream[..n]);
            !terminal.palette().blinks().is_empty()
        })
        .unwrap();
    let mut reference = terminal();
    let _ = reference.feed(&mut canvas(), &stream);
    for pace in [HALVES, SLOW, Pace { bytes: 2, ticks: 5 }] {
        let origin = line_ticks(pace, defined);
        assert!(origin > 1, "{pace:?}: the blink is defined after tick 0");
        let mut run = Run::of(&stream, pace);
        for tick in 1..=origin + 130 {
            let _ = run.advance(1);
            assert_eq!(!run.terminal.palette().blinks().is_empty(), tick >= origin, "{pace:?}: tick {tick}");
            if tick >= origin {
                let into = tick - origin;
                let expected = reference.palette().at((into / u64::from(TENTH_TICKS)) as u32);
                assert_eq!(run.colours(), expected, "{pace:?}: tick {tick}, {into} ticks into the blink");
                assert_eq!(
                    run.player.ticks_to_blink(&run.terminal),
                    Some(30 - (into % 30) as u32),
                    "{pace:?}: tick {tick}"
                );
            }
        }
    }
}
