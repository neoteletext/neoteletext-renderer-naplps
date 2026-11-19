//! Playing a page into a sequence of pictures (neoteletext-common `docs/animation.md`,
//! ANIM-18): the script of timed operations, the objects file, and the loop over ticks.
//!
//! The renderer keeps no clock and no cycle, so this is where they are: a tick is one step of
//! the loop, a cycle's frame is computed here by ANIM-14's formula and given to the renderer.

use std::io::Read as _;

use naplps::limits::{MAX_CYCLING_OBJECTS, MAX_FRAME_NUMBER, MAX_OBJECT_FRAMES, MAX_OBJECTS};
use naplps::{Animation, Look, Object, ObjectKind, Terminal};

/// The most ticks `--frames` plays (ANIM-18: 1 to 36,000, ten minutes).
pub const MAX_FRAMES: u32 = 36_000;
/// The largest script or objects file read.
pub const MAX_TEXT_BYTES: u64 = 1024 * 1024;
/// The longest period of a cycle, in ticks (ANIM-6: 1 to 3,600).
const MAX_PERIOD: u32 = 3_600;
/// The highest layer (ANIM-12: 0 to 3).
const MAX_LAYER: u8 = naplps::limits::LAYERS - 1;
/// The word for "leave the layer as it is" in an `order` operation (ANIM-18).
const KEEP: &str = "keep";

/// One of ANIM-6's operations, as a script line names it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Operation {
    /// `show <n>`.
    Show,
    /// `hide <n>`.
    Hide,
    /// `look <n> <0-3>`.
    Look(Look),
    /// `move <n> <x> <y> [relative]`.
    Move { x: i16, y: i16, relative: bool },
    /// `order <n> <layer|keep> <order>`.
    Order { layer: Option<u8>, order: i8 },
    /// `frame <n> <f>`; also stops a cycle.
    Frame(u8),
    /// `cycle <n> <first> <last> <period> [once]`.
    Cycle { first: u8, last: u8, period: u32, once: bool },
    /// `stop_cycle <n>`.
    StopCycle,
    /// `reset <n>`.
    Reset,
}

/// A script line: at `tick`, `operation` on object `number`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Step {
    /// The tick at which it is applied.
    pub tick: u32,
    /// The object.
    pub number: u16,
    /// What is done to it.
    pub operation: Operation,
}

/// Reads a file of text, or standard input for `-`, refusing more than [`MAX_TEXT_BYTES`].
///
/// # Errors
///
/// The file cannot be read, is too long or is not UTF-8.
pub fn read_text(path: &str) -> Result<String, String> {
    let mut text = String::new();
    let limit = MAX_TEXT_BYTES.saturating_add(1);
    let read = if path == "-" {
        std::io::stdin().take(limit).read_to_string(&mut text)
    } else {
        std::fs::File::open(path).and_then(|file| file.take(limit).read_to_string(&mut text))
    };
    let length = read.map_err(|error| format!("{path}: {error}"))?;
    if u64::try_from(length).unwrap_or(u64::MAX) > MAX_TEXT_BYTES {
        return Err(format!("{path} is longer than {MAX_TEXT_BYTES} bytes"));
    }
    Ok(text)
}

fn field<T: std::str::FromStr>(fields: &[&str], index: usize, what: &str) -> Result<T, String> {
    let text = fields.get(index).ok_or_else(|| format!("{what} is missing"))?;
    text.parse().map_err(|_| format!("{what} {text:?} is not a number in range"))
}

fn at_most<T: PartialOrd + std::fmt::Display + Copy>(value: T, most: T, what: &str) -> Result<T, String> {
    if value > most { Err(format!("{what} {value} is above {most}")) } else { Ok(value) }
}

/// Whether the optional last word of an operation is `word`; anything else there is refused.
fn flag(fields: &[&str], index: usize, word: &str) -> Result<bool, String> {
    if fields.len() > index.saturating_add(1) {
        return Err("too many fields".to_owned());
    }
    match fields.get(index) {
        None => Ok(false),
        Some(found) if *found == word => Ok(true),
        Some(found) => Err(format!("{found:?} is not {word:?}")),
    }
}

fn exactly(fields: &[&str], count: usize) -> Result<(), String> {
    if fields.len() == count { Ok(()) } else { Err(format!("expected {count} fields, found {}", fields.len())) }
}

fn step(line: &str) -> Result<Step, String> {
    let fields: Vec<&str> = line.split_whitespace().collect();
    let tick = at_most(field::<u32>(&fields, 0, "the tick")?, MAX_FRAMES, "the tick")?;
    let name = fields.get(1).copied().ok_or("the operation is missing")?;
    if name == "record" {
        return Err("record lines are for neottx; a NAPLPS page's objects are given with --objects".to_owned());
    }
    let number: u16 = field(&fields, 2, "the object's number")?;
    if number == 0 {
        return Err("an object's number is 1 to 65,535".to_owned());
    }
    let operation = match name {
        "show" => exactly(&fields, 3).map(|()| Operation::Show)?,
        "hide" => exactly(&fields, 3).map(|()| Operation::Hide)?,
        "stop_cycle" => exactly(&fields, 3).map(|()| Operation::StopCycle)?,
        "reset" => exactly(&fields, 3).map(|()| Operation::Reset)?,
        "look" => {
            exactly(&fields, 4)?;
            Operation::Look(Look::from_code(field(&fields, 3, "the look")?).ok_or("the look is 0 to 3")?)
        }
        "move" => Operation::Move {
            x: field(&fields, 3, "x")?,
            y: field(&fields, 4, "y")?,
            relative: flag(&fields, 5, "relative")?,
        },
        "order" => {
            exactly(&fields, 5)?;
            let layer = if fields.get(3) == Some(&KEEP) {
                None
            } else {
                Some(at_most(field::<u8>(&fields, 3, "the layer")?, MAX_LAYER, "the layer")?)
            };
            Operation::Order { layer, order: field(&fields, 4, "the order")? }
        }
        "frame" => {
            exactly(&fields, 4)?;
            Operation::Frame(at_most(field::<u8>(&fields, 3, "the frame")?, MAX_FRAME_NUMBER, "the frame")?)
        }
        "cycle" => {
            let first: u8 = field(&fields, 3, "the first frame")?;
            let last = at_most(field::<u8>(&fields, 4, "the last frame")?, MAX_FRAME_NUMBER, "the last frame")?;
            let period = at_most(field::<u32>(&fields, 5, "the period")?, MAX_PERIOD, "the period")?;
            if first > last || period == 0 {
                return Err("a cycle needs first <= last and a period of 1 to 3,600 ticks".to_owned());
            }
            Operation::Cycle { first, last, period, once: flag(&fields, 6, "once")? }
        }
        other => return Err(format!("unknown operation {other:?}")),
    };
    Ok(Step { tick, number, operation })
}

/// Reads a script: `<tick> <operation>` a line, in ascending tick; blank lines and lines
/// beginning `#` are skipped (`neottx rules-run` writes its reports as such comments).
///
/// # Errors
///
/// A line is malformed or its tick is below the line before; the message names the line.
pub fn script(text: &str) -> Result<Vec<Step>, String> {
    let mut steps: Vec<Step> = Vec::new();
    for (index, line) in text.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let number = index.saturating_add(1);
        let step = step(line).map_err(|error| format!("script line {number}: {error}"))?;
        if steps.last().is_some_and(|last| last.tick > step.tick) {
            return Err(format!("script line {number}: its tick is below the line before"));
        }
        steps.push(step);
    }
    Ok(steps)
}

/// A macro code written in hexadecimal, `20` to `7F`.
fn code(text: &str) -> Result<u8, String> {
    u8::from_str_radix(text, 16).map_err(|_| format!("{text:?} is not a hexadecimal macro code"))
}

fn object(line: &str) -> Result<Object, String> {
    // A label is text with spaces, so it is the last option and takes the rest of the line.
    let (line, label) = line.split_once(" label=").map_or((line, ""), |(head, label)| (head, label));
    let fields: Vec<&str> = line.split_whitespace().collect();
    let kind = match fields.first().copied() {
        Some("macro") => ObjectKind::Macro,
        Some("region") => ObjectKind::Region,
        _ => return Err("a line begins with macro or region".to_owned()),
    };
    let mut object = Object {
        number: field(&fields, 1, "the number")?,
        kind,
        shown: true,
        detectable: false,
        layer: field(&fields, 2, "the layer")?,
        order: field(&fields, 3, "the order")?,
        x: field(&fields, 4, "x")?,
        y: field(&fields, 5, "y")?,
        width: field(&fields, 6, "the width")?,
        height: field(&fields, 7, "the height")?,
        origin_x: 0,
        origin_y: 0,
        cover: 0,
        hover: 0,
        pressed: 0,
        alternative: 0,
        frames: Vec::new(),
        label: label.to_owned(),
    };
    let options = match kind {
        ObjectKind::Macro => {
            object.origin_x = field(&fields, 8, "the origin's x")?;
            object.origin_y = field(&fields, 9, "the origin's y")?;
            let frames = fields.get(10).ok_or("the frames are missing")?;
            object.frames = frames.split(',').map(code).collect::<Result<_, _>>()?;
            if object.frames.len() > MAX_OBJECT_FRAMES {
                return Err(format!("more than {MAX_OBJECT_FRAMES} frames"));
            }
            11
        }
        ObjectKind::Region => {
            object.cover = field(&fields, 8, "the cover")?;
            9
        }
    };
    for option in fields.get(options..).unwrap_or(&[]) {
        match option.split_once('=') {
            None if *option == "hidden" => object.shown = false,
            None if *option == "detectable" => object.detectable = true,
            Some(("hover", value)) => object.hover = code(value)?,
            Some(("pressed", value)) => object.pressed = code(value)?,
            Some(("alternative", value)) => object.alternative = code(value)?,
            _ => return Err(format!("unknown option {option:?}")),
        }
    }
    Ok(object)
}

/// Reads an objects file: one object a line, with the fields of the `NAPLPS_OBJECTS` record
/// (ANIM-11) as text; blank lines and lines beginning `#` are skipped. Places and sizes are
/// raster dots, 480 by 500 (DEC-6853, `docs/naplps-raster.md` RAS-4), on every canvas drawn.
///
/// ```text
/// macro  <number> <layer> <order> <x> <y> <width> <height> <origin x> <origin y> <frames> [options]
/// region <number> <layer> <order> <x> <y> <width> <height> <cover> [options]
/// ```
///
/// `<frames>` is the frames' macro codes in hexadecimal with commas between (`20,21`); the
/// options are `hidden`, `detectable`, `hover=<code>`, `pressed=<code>`,
/// `alternative=<code>` and, last because it takes the rest of the line, `label=<text>`
/// (DEC-6638 item 6: what a screen reader says for the object; never drawn).
///
/// # Errors
///
/// A line is malformed; the message names the line.
pub fn objects(text: &str) -> Result<Vec<Object>, String> {
    let mut objects = Vec::new();
    for (index, line) in text.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if objects.len() >= MAX_OBJECTS {
            return Err(format!("more than {MAX_OBJECTS} objects"));
        }
        objects.push(object(line).map_err(|error| format!("objects line {}: {error}", index.saturating_add(1)))?);
    }
    Ok(objects)
}

/// A cycle in progress (ANIM-14).
#[derive(Clone, Copy, Debug)]
struct Cycle {
    number: u16,
    first: u8,
    last: u8,
    period: u32,
    once: bool,
    /// The tick the cycle started: the tick after its operation ran.
    start: u32,
}

impl Cycle {
    /// The frame at `tick`, and whether a `once` cycle has reached its last frame.
    fn frame(&self, tick: u32) -> (u8, bool) {
        let steps = tick.saturating_sub(self.start).checked_div(self.period).unwrap_or(0);
        let count = u32::from(self.last.saturating_sub(self.first)).saturating_add(1);
        if self.once {
            let frame = u32::from(self.first).saturating_add(steps).min(u32::from(self.last));
            (u8::try_from(frame).unwrap_or(self.last), frame == u32::from(self.last))
        } else {
            let frame = u32::from(self.first).saturating_add(steps.checked_rem(count).unwrap_or(0));
            (u8::try_from(frame).unwrap_or(self.last), false)
        }
    }
}

/// The receiver's side of ANIM-6 for a played page: applies operations to the renderer's
/// animation state and runs the cycles.
#[derive(Default)]
pub struct Animator {
    cycles: Vec<Cycle>,
    /// Operations that did nothing: a target that does not exist, or a cycle beyond
    /// [`MAX_CYCLING_OBJECTS`] (ANIM-6, ANIM-14: "does nothing and is counted").
    pub ignored: u32,
}

impl Animator {
    /// Applies one operation at `tick`.
    pub fn apply(&mut self, terminal: &mut Terminal, tick: u32, step: &Step) {
        let number = step.number;
        let Some(object) = terminal.object(number) else {
            self.ignored = self.ignored.saturating_add(1);
            return;
        };
        let own = (object.x, object.y);
        let mut animation = terminal.animation(number).unwrap_or_default();
        match step.operation {
            Operation::Show => animation.shown = Some(true),
            Operation::Hide => animation.shown = Some(false),
            Operation::Look(look) => animation.look = look,
            Operation::Move { x, y, relative } => {
                // ANIM-6: a relative move adds to the position in force, saturating.
                let (from_x, from_y) = if relative { animation.position.unwrap_or(own) } else { (0, 0) };
                animation.position = Some((from_x.saturating_add(x), from_y.saturating_add(y)));
            }
            Operation::Order { layer, order } => {
                animation.layer = layer.or(animation.layer);
                animation.order = Some(order);
            }
            Operation::Frame(frame) => {
                self.cycles.retain(|cycle| cycle.number != number);
                animation.frame = Some(frame);
            }
            Operation::Cycle { first, last, period, once } => {
                self.cycles.retain(|cycle| cycle.number != number);
                if self.cycles.len() >= MAX_CYCLING_OBJECTS {
                    self.ignored = self.ignored.saturating_add(1);
                    return;
                }
                self.cycles.push(Cycle { number, first, last, period, once, start: tick.saturating_add(1) });
            }
            Operation::StopCycle => self.cycles.retain(|cycle| cycle.number != number),
            Operation::Reset => {
                self.cycles.retain(|cycle| cycle.number != number);
                let _ = terminal.clear_animation(number);
                return;
            }
        }
        let _ = terminal.set_animation(number, animation);
    }

    /// Gives every cycling object its frame at `tick`, and ends the `once` cycles that have
    /// reached their last frame.
    pub fn tick(&mut self, terminal: &mut Terminal, tick: u32) {
        let mut ended = Vec::new();
        for cycle in &self.cycles {
            if tick < cycle.start {
                continue;
            }
            let (frame, done) = cycle.frame(tick);
            let animation = terminal.animation(cycle.number).unwrap_or_default();
            let _ = terminal.set_animation(cycle.number, Animation { frame: Some(frame), ..animation });
            if done {
                ended.push(cycle.number);
            }
        }
        self.cycles.retain(|cycle| !ended.contains(&cycle.number));
    }
}

/// The path of the picture of `tick`: `-NNNNN`, the tick in five digits, before the extension
/// (ANIM-18).
#[must_use]
pub fn numbered(path: &str, tick: u32) -> String {
    let file_starts = path.rfind('/').map_or(0, |slash| slash.saturating_add(1));
    match path.rfind('.').filter(|dot| *dot > file_starts) {
        Some(dot) => {
            let (stem, extension) = path.split_at(dot);
            format!("{stem}-{tick:05}{extension}")
        }
        None => format!("{path}-{tick:05}"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_script_reads_every_operation_of_anim_6() {
        // ANIM-18: the operations as a script writes them.
        let text = "# a comment\n0 show 1\n0 hide 2\n1 look 1 3\n2 move 1 -5 7\n2 move 1 5 7 relative\n\
                    3 order 1 keep -2\n3 order 1 3 2\n4 frame 1 15\n5 cycle 1 0 3 6\n5 cycle 2 1 2 3600 once\n\
                    6 stop_cycle 1\n7 reset 1\n";
        let steps = script(text).unwrap();
        let operations: Vec<Operation> = steps.iter().map(|step| step.operation).collect();
        assert_eq!(
            operations,
            vec![
                Operation::Show,
                Operation::Hide,
                Operation::Look(Look::Alternative),
                Operation::Move { x: -5, y: 7, relative: false },
                Operation::Move { x: 5, y: 7, relative: true },
                Operation::Order { layer: None, order: -2 },
                Operation::Order { layer: Some(3), order: 2 },
                Operation::Frame(15),
                Operation::Cycle { first: 0, last: 3, period: 6, once: false },
                Operation::Cycle { first: 1, last: 2, period: 3600, once: true },
                Operation::StopCycle,
                Operation::Reset,
            ]
        );
        assert_eq!(steps.last().map(|step| (step.tick, step.number)), Some((7, 1)));
    }

    #[test]
    fn a_script_refuses_what_anim_6_does_not_allow() {
        for line in [
            "0 look 1 4",
            "0 frame 1 16",
            "0 order 1 4 0",
            "0 cycle 1 3 2 6",
            "0 cycle 1 0 3 0",
            "0 cycle 1 0 3 3601",
            "0 cycle 1 0 16 6",
            "0 move 1 5",
            "0 move 1 5 5 sideways",
            "0 show 0",
            "0 show",
            "0 show 1 2",
            "0 jump 1",
            "36001 show 1",
            "0 record ANIMATE 00",
            "x show 1",
        ] {
            assert!(script(line).is_err(), "{line:?} must be refused");
        }
        assert!(script("5 show 1\n4 show 1\n").unwrap_err().contains("line 2"), "ticks ascend");
    }

    #[test]
    fn a_cycle_follows_the_formulas_of_anim_14() {
        // first + ((t - s) / p) mod c, and with once min(first + (t - s) / p, last).
        let cycle = Cycle { number: 1, first: 2, last: 4, period: 3, once: false, start: 10 };
        let frames: Vec<u8> = (10..22).map(|tick| cycle.frame(tick).0).collect();
        assert_eq!(frames, vec![2, 2, 2, 3, 3, 3, 4, 4, 4, 2, 2, 2]);
        let once = Cycle { once: true, ..cycle };
        let frames: Vec<(u8, bool)> = (10..20).step_by(3).map(|tick| once.frame(tick)).collect();
        assert_eq!(frames, vec![(2, false), (3, false), (4, true), (4, true)]);
    }

    #[test]
    fn an_objects_file_reads_both_kinds() {
        let text = "macro 1 2 0 300 200 48 64 0 416 20,21 detectable hover=22\n\
                    region 2 1 -1 0 460 480 40 9 hidden\n";
        let objects = objects(text).unwrap();
        assert_eq!(objects.len(), 2);
        let first = objects.first().unwrap();
        assert_eq!((first.number, first.origin_y, first.frames.clone(), first.hover), (1, 416, vec![0x20, 0x21], 0x22));
        assert!(first.shown && first.detectable);
        let second = objects.get(1).unwrap();
        assert_eq!((second.kind, second.cover, second.shown, second.order), (ObjectKind::Region, 9, false, -1));
        assert!(super::objects("sprite 1 2 0 0 0 1 1").is_err());
        assert!(super::objects("macro 1 2 0 0 0 1 1 0 0 zz").is_err());
        assert!(super::objects("region 1 1 0 0 0 1 1 0 blinking").is_err());
    }

    #[test]
    fn pictures_are_numbered_before_the_extension() {
        assert_eq!(numbered("out/page.ppm", 7), "out/page-00007.ppm");
        assert_eq!(numbered("out.dir/page", 36_000), "out.dir/page-36000");
        assert_eq!(numbered(".hidden", 1), ".hidden-00001");
    }
}
