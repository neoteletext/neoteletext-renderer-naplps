# neoteletext-renderer-naplps

NAPLPS for NeoTeletext. NAPLPS is the North American Presentation Level Protocol Syntax: ANSI X3.110-1983, CSA T500-1983, CCITT T.101 Annex D.

## Making pages

- [docs/guide.html](docs/guide.html): a tutorial from an empty file to a finished, animated page, every example a real page with its picture.
- [docs/reference.html](docs/reference.html): every byte, control and drawing command, the operand encodings, the limits, and where this renderer departs from the standard.

## What is here

**`naplps`** is the renderer: a `no_std` library with no input or output that turns a page's bytes into colour-map addresses on a canvas the caller owns (ANSI X3.110-1983 throughout: code extension, every PDI, colour modes 0 to 2 and the default colour map, text, mosaics, macros, DRCS, fill masks, WAIT and BLINK as events and colour maps over time). It contains no font: a stroke font is passed in as data. Everything a page can make it hold or do is bounded (`naplps::limits`). `naplps::Validator` reads a stream as the renderer does without a canvas and draws nothing, so that a server can check what it sends with the receiver's own reading (renderer parity PAR-15).

For animation (neoteletext-common `docs/animation.md`) it reports the rectangle of pixels that changed (`Terminal::take_damage`), draws numbered objects over the page's picture (macros placed, moved, hidden, layered and stepped through frames by the receiver, composed into a second canvas by `Terminal::compose`), and plays WAIT and BLINK on ticks of one sixtieth of a second it is told have passed (`Player`). It still keeps no clock.

**`naplps-render`** renders one page to a PPM picture, or plays it into a sequence of them:

```
naplps-render [--width N] [--height N] [--palette-bits N] [--font FILE] [--tenths N] [--stage N] [--border N] [--dac-bits N] [--preamble] [--objects FILE] [--frames TICKS [--frame-step K] [--script FILE]] [--teletext ENGINE] [--neoteletext [--double]] PAGE OUT.ppm
```

`--teletext ENGINE` loads NeoTeletext's 55 character sets from the teletext engine's checkout (its `required.txt` and Noto Teletext BDF files, and for the plain Arabic-script sets 44 to 51 its joining table and `forms.txt`, so that their letters join as on teletext pages), which a page designates by their ISO 2022 private designations (docs/reference.html, "Sets and shifts"; REQ-6668). `--neoteletext` draws the page as NeoTeletext shows it, on 480 by 462 pixels centred in the 480 by 500 teletext raster with the lines above and below in the page's background colour (REQ-5819, DEC-6667); `--double` at twice the size.

`--frames` plays the page for that many ticks, WAIT and BLINK on their ticks, and writes `OUT-NNNNN.ppm` every `--frame-step` ticks; `--objects` gives the page numbered objects and `--script` moves, hides and cycles them at stated ticks (docs/reference.html, "Objects and animation").

`naplps-render check [--font FILE] [--objects FILE] [--title TEXT] PAGE` checks a page for its author with the receiver's renderer: the rectangle it draws on, its objects and title, and every byte passed over or refused; it exits 1 on a refusal (docs/reference.html, "naplps-render check").

`--font` takes a stroke font in the library's text form, such as NeoTeletext's own (`fonts/neoteletext.strokes`, both sets) or the Microstar font recovered from PP3 (`~/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes`). `--preamble` and `--dac-bits 6` render a page as the oracle shows it to PP3, for comparison.


`naplps-oracle` makes the reference frames a NAPLPS renderer is judged by, and judges frames against them.

The standard alone cannot say whether a renderer is right, because section 8.3.4 lets decoders approximate line widths, fill edges, fonts and the mapping of the unit screen onto pixels. So the references come from a period decoder.

`capture` runs PP3 (Personality+III 2.18A, Microstar Software, 1991) in DOSBox on a private X display, sends each page down an emulated serial line at 9600 bits a second, and saves the frame once drawing has stopped. A manifest records:
- the pinned PP3 files;
- the DOSBox version and speed;
- the reset sent before each page;
- each page's SHA-256 and how long it took to draw.

`compare` checks a frame against a reference. A pixel fails only if its colour appears nowhere within a given distance in the other frame. A line one pixel wider passes; a missing shape, a wrong colour or a shape in the wrong place does not.

How all of this is checked, and how each check was itself checked, is in `docs/verification.md`.

The oracle is checked against independent evidence. The `rosetta_stone` testbed of the Telidon project has 18 PP3 screenshots, and the oracle's captures of the same 18 pages match them.

## Requirements

Linux with `dosbox`, `Xvfb`, `socat`, `xdotool`, `ffmpeg` and `ffprobe`:

```
sudo apt-get install dosbox xvfb socat xdotool ffmpeg
```

PP3 and the testbed are read from `~/devel/teletext-reference/NAPLPS/`. Point `NAPLPS_PP3_DIR` and `NAPLPS_ROSETTA_DIR` elsewhere if needed. Each file must match its pinned SHA-256.

## Use

```
cargo build --release
target/release/naplps-oracle capture --out tmp/ref/samples PAGE.nap ...
target/release/naplps-oracle compare --displacement 1 tmp/ref/samples my-renderer-output/
```

## Licence

MIT.
