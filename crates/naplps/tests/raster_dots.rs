//! `docs/naplps-raster.md` RAS-2 on the renderer itself (DEC-6853, DEC-6857): every one of the
//! raster's 240,000 dots, written by `dot_steps` rounded to nearest at four-byte and at six-byte
//! operands and read back as the renderer reads an operand, lands on exactly that dot; drawn
//! after DOMAIN on the receiver's 480 by 460 canvas it lights pixel (X, Y − 20) for lines 20 to
//! 479 and nothing for rows 0 and 24; and on 960 by 920 it lights pixel (2X, 2(Y − 20) + 1).
#![allow(
    clippy::arithmetic_side_effects,
    clippy::indexing_slicing,
    clippy::cast_possible_truncation,
    clippy::cast_possible_wrap,
    clippy::cast_sign_loss,
    reason = "a test: fixed inputs within range, and failure is a panic"
)]

use naplps::fixed::{FRACTION_BITS, Unit};
use naplps::limits::{DISPLAY_FIRST_LINE, DISPLAY_LINES, RASTER_HEIGHT, RASTER_WIDTH};
use naplps::operand::{Domain, Reader};
use naplps::{Canvas, Rounding, Terminal, dot_of_point, dot_steps, multi_value_operand};

const SO: u8 = 0x0E;
/// DOMAIN (section 5.3.2.2).
const DOMAIN: u8 = 0x21;
/// POINT ABSOLUTE (section 5.3.3.1, 2/6): moves the drawing point and draws the logical pel
/// there, a single pixel while the pel is (0, 0).
const POINT: u8 = 0x26;
/// SELECT COLOR (section 5.3.2.6) of entry 7, nominal white in the default colour map.
const WHITE: [u8; 2] = [0x3E, 0x40 | (7 << 2)];
/// The operand lengths RAS-2 computes for: DEC-6849's four bytes and RAS-6's six.
const OPERAND_BYTES: [u8; 2] = [4, 6];

/// DOMAIN's fixed-format byte for one-byte single values, `bytes`-byte multi-value operands and
/// two dimensions (Figure 14: b5 b4 b3 the length less one), and the logical pel (0, 0).
fn domain(bytes: u8) -> Vec<u8> {
    let mut out = vec![DOMAIN, 0x40 | ((bytes - 1) << 2)];
    multi_value_operand(0, 0, bytes, &mut out);
    out
}

/// The operand of dot (`x`, `y`) at `bytes` bytes, rounded to nearest.
fn operand(x: u32, y: u32, bytes: u8) -> Vec<u8> {
    let (across, up) = dot_steps(i64::from(x), i64::from(y), 1, bytes, Rounding::Nearest);
    let mut out = Vec::new();
    multi_value_operand(across, up, bytes, &mut out);
    out
}

/// An axis value of a `bytes`-byte operand as a [`Unit`]: 3 `bytes` − 1 fractional bits.
fn as_unit(value: i64, bytes: u8) -> Unit {
    (value << (FRACTION_BITS - (3 * u32::from(bytes) - 1))) as Unit
}

#[test]
fn every_dot_written_and_read_back_is_that_dot() {
    // RAS-2's verification: dot_of_point of dot_steps(X, Y, 1, 6, Nearest), and the same with
    // the bytes read as the renderer reads a PDI's operand.
    for bytes in OPERAND_BYTES {
        let domain = Domain { single_bytes: 1, multi_bytes: usize::from(bytes), three_d: false };
        for y in 0..RASTER_HEIGHT {
            for x in 0..RASTER_WIDTH {
                let (across, up) = dot_steps(i64::from(x), i64::from(y), 1, bytes, Rounding::Nearest);
                let want = (x as i32, y as i32);
                assert_eq!(dot_of_point(as_unit(across, bytes), as_unit(up, bytes)), want, "{bytes} bytes");
                let written = operand(x, y, bytes);
                let point = Reader::new(&written).point(domain).unwrap();
                assert_eq!(dot_of_point(point.x, point.y), want, "{bytes} bytes, read back");
            }
        }
    }
}

#[test]
fn every_dot_drawn_lights_its_pixel_on_the_receivers_canvas_and_twice_it() {
    // RAS-2: a point written at each dot, line by line, lights exactly the pixels of that line
    // on the receiver's canvas, the dot's pixel (X, Y − 20), and none for the lines of rows 0
    // and 24; on twice the canvas it lights (2X, 2(Y − 20) + 1).
    for bytes in OPERAND_BYTES {
        for scale in [1, 2] {
            let (width, height) = (RASTER_WIDTH * scale, DISPLAY_LINES * scale);
            for y in 0..RASTER_HEIGHT {
                let mut stream = vec![SO];
                stream.extend(domain(bytes));
                stream.extend(WHITE);
                stream.push(POINT);
                for x in 0..RASTER_WIDTH {
                    stream.extend(operand(x, y, bytes));
                }
                let mut canvas = Canvas::new(width, height).unwrap();
                let mut terminal = Terminal::new(4);
                let _ = terminal.feed(&mut canvas, &stream);
                let _ = terminal.finish(&mut canvas);
                let white = terminal.palette().white();
                // The damage holds every pixel written (ANIM-4), so the lit pixels are sought
                // only inside it, and the canvas outside it is the black it was made.
                let damage = terminal.take_damage();
                let lit: Vec<(u32, u32)> = damage.map_or_else(Vec::new, |rect| {
                    (rect.y..rect.bottom())
                        .flat_map(|row| (rect.x..rect.right()).map(move |column| (column, row)))
                        .filter(|&(column, row)| canvas.pixel(column, row) == Some(white))
                        .collect()
                });
                let on_display = (DISPLAY_FIRST_LINE..DISPLAY_FIRST_LINE + DISPLAY_LINES).contains(&y);
                let expected: Vec<(u32, u32)> = if on_display {
                    let row = scale * (y - DISPLAY_FIRST_LINE) + (scale - 1);
                    (0..RASTER_WIDTH).map(|x| (scale * x, row)).collect()
                } else {
                    Vec::new()
                };
                let written = damage.map_or(0, |rect| rect.area());
                assert_eq!(written, if on_display { u64::from(scale * (RASTER_WIDTH - 1) + 1) } else { 0 });
                assert_eq!(lit, expected, "{bytes} bytes, {width} by {height}, line {y}");
            }
        }
    }
}
