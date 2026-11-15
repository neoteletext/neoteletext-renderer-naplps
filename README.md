# neoteletext-renderer-naplps

NAPLPS for NeoTeletext. NAPLPS is the North American Presentation Level Protocol Syntax: ANSI X3.110-1983, CSA T500-1983, CCITT T.101 Annex D.

## Making pages

- [docs/guide.html](docs/guide.html): a tutorial from an empty file to a finished, animated page, every example a real page with its picture.
- [docs/reference.html](docs/reference.html): every byte, control and drawing command, the operand encodings, the limits, and where this renderer departs from the standard.

## What is here

**`naplps`** is the renderer: a `no_std` library with no input or output that turns a page's bytes into colour-map addresses on a canvas the caller owns (ANSI X3.110-1983 throughout: code extension, every PDI, colour modes 0 to 2 and the default colour map, text, mosaics, macros, DRCS, fill masks, WAIT and BLINK as events and colour maps over time). It contains no font: a stroke font is passed in as data. Everything a page can make it hold or do is bounded (`naplps::limits`).

**`naplps-render`** renders one page to a PPM picture:

```
naplps-render [--width N] [--height N] [--palette-bits N] [--font FILE] [--tenths N] [--dac-bits N] [--preamble] PAGE OUT.ppm
```

`--font` takes a stroke font in the library's text form, such as the Microstar font recovered from PP3 (`~/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes`). `--preamble` and `--dac-bits 6` render a page as the oracle shows it to PP3, for comparison.


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
