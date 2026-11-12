# How NAPLPS rendering is verified

This explains how a NAPLPS renderer in this repository is checked, and how each part of that checking was itself checked. The records behind it are in rdm:
- the decision to verify against PP3: DEC-5747;
- the repository's shape: DEC-5748;
- the requirements: REQ-5749 to REQ-5752;
- the work still owed: TODO-5753 to TODO-5763.

## 1. Why a period decoder is the reference

ANSI X3.110-1983 section 8.3.4 lets a conforming decoder approximate. Line widths, the edges of fills, fonts, and how the unit screen maps onto pixels can all differ between two decoders that both conform. Section 5.3.2.3.9 leaves the text font entirely to the implementation. So there is no single correct frame that could be computed from the standard and compared exactly.

A renderer is judged instead against what a period decoder drew: PP3 (Personality+III 2.18A, Microstar Software, 1991). The standard remains the source of truth for behaviour. PP3 is the evidence for what the standard's approximations looked like in practice. Where the two disagree, the choice is recorded as a decision in rdm, never settled silently in code.

## 2. The oracle: `naplps-oracle capture`

### 2.1 What runs

1. **Pinned PP3 files.** Five PP3 files are read from `~/devel/teletext-reference/NAPLPS/Telidon-master/archives/prodigy-slack/pp3217a/`, or from `--pp3` or `NAPLPS_PP3_DIR`. Each is checked against its SHA-256 in `PINNED_FILES` (`crates/naplps-oracle/src/session.rs`), and the run stops if any differs. They are copied to a scratch drive under `tmp/oracle/run-<pid>/`.
2. **The display.** Xvfb starts with `-displayfd`, so it picks a free display itself, and with `-nolisten tcp`.
3. **The serial line.** socat makes a pseudo-terminal (`socat -d -d -u STDIN PTY,raw,echo=0`) and reports its path on its error output. That pseudo-terminal becomes PP3's COM1.
4. **DOSBox 0.74-3** runs with:
   - `serial1=directserial realport:pts/N`;
   - a fixed 20,000 cycles;
   - surface output with no scaler and no aspect correction, so its window is PP3's screen pixel for pixel.

   It starts PP3 as `MVDIAPP PP3SCOMM.EXE +Z +2 VGA640.SCR PP3SCOMM.EXE /FMPP3SE.MSG /NC 1`. That is the package's own command line plus `/NC 1`, the "use from inside other program" mode, which is online at once with no menu to drive.
5. **The screen.** One ffmpeg x11grab stream reads the whole 1024 × 768 display at 10 frames a second into a thread. Waiting happens on a condition variable, never on a sleep loop.

### 2.2 Start-up, and how its order was found

1. **The shareware notice.** Wait for it to appear (the first frame that is not black), then press space.
2. **The terminal.** Wait for the screen to change.
3. **Readiness.** Send the page preamble (section 2.3), and resend it every 2 seconds within a 30-second ceiling, until PP3's window becomes 640 × 480. PP3 opens COM1 a little after its terminal appears, and bytes sent before then are lost. The 640 × 480 screen is the only sure sign it is reading the line: entering NAPLPS mode switches the VGA 640 driver from the 640 × 400 text screen to VGA's 640 × 480 sixteen-colour screen.

What was tried and replaced:
- **Waiting for the screen to stop changing.** It cost the full ceiling twice, because the shareware notice and the empty terminal both blink a text cursor and never settle. The first capture run took 5 minutes for 18 small pages.
- **Waiting only for the screen to change.** That lost the first page: `arc` came back as the 640 × 400 text screen, never settled.
- **Driving PP3's menus with keystrokes.** xdotool delivers plain keys to DOSBox under Xvfb, but not Ctrl or Alt combinations: Ctrl-F2 (file display) and Ctrl-F5 (DOSBox's screenshot) both failed.
- **DOSBox's `nullmodem` serial mode.** It works, but listens on TCP on every network interface. A private network namespace (`unshare -rn`) is refused on chunko by Ubuntu's `kernel.apparmor_restrict_unprivileged_userns = 1`. The pseudo-terminal opens no port at all.

### 2.3 Before every page: the preamble

`PAGE_PREAMBLE`, 16 bytes, puts every page in the same starting state whatever the page before it left:

| Bytes | Meaning |
|---|---|
| `1B 25 41` | ESC % A, PP3's switch to NAPLPS mode (README.PP3 section 9.0, an ISO 2375 registered sequence) |
| `18 1B 22 46 1B 45 1F 40 40 0E` | the opening of every MGE-authored page in the collection: CAN, designate the C1 set, ESC 4/5, NSR to row 0 column 0 (section 6.1.6.5), SO |
| `20 7F 7F` | RESET with every bit of both operand bytes (section 5.3.2.9.1), clearing macros and DRCS as well; MGE's own RESET is `20 7F 4F` |

The meaning of CAN and ESC 4/5 in this position has not yet been checked against the standard (TODO-5758).

### 2.4 Sending and settling

- **Line rate.** Pages are sent at 9,600 bits a second, 8N1, by default (`--bits-per-second`; 0 sends unpaced). Whether faster sending loses bytes is not yet measured (TODO-5756).
- **When a page is drawn.** A page counts as drawn when the frame has not changed for 3 seconds (`--quiet-ms`).
- **"Drawn in".** This is the time from the page's first byte to the first frame showing the final picture, accurate to one frame (100 ms).
- **Pages that never settle.** A page still changing 60 seconds after its first byte (`--ceiling-s`), from blinking or animation, is reported as never settled, and its last frame is kept. Capturing blink phases and drawing over time is TODO-5762.

### 2.5 What a run records

Each run writes one PNG per page (lossless) and `manifest.tsv`.
- **The manifest header** records everything that decides the picture:
  - the five pinned PP3 files and their SHA-256;
  - the DOSBox version and cycles;
  - the preamble;
  - the line rate;
  - the settling rule.
- **Each row** gives the page name, the page's SHA-256 and size, the drawing time (or `never`), the frame size, and the PNG's SHA-256.

### 2.6 Isolation

Nothing the oracle starts listens on a network (REQ-5750). This was checked by hand on 12 November 2026 during a live run: `ss -ltnup` showed no listening TCP or UDP socket belonging to Xvfb, socat, DOSBox or ffmpeg. A test that checks this in the full gate is TODO-5759.

## 3. The comparison: `naplps-oracle compare`

A frame and a reference of the same size are compared pixel by pixel (REQ-5751):

- **Differing:** a pixel whose colour differs from the other frame's at the same place by more than the channel tolerance (`--channel`) in any channel.
- **Unexplained in the candidate:** a differing pixel whose colour the reference has nowhere within the displacement (`--displacement`, Chebyshev distance in pixels). **Unexplained in the reference** is the same check the other way round.
- **Agreement:** the frames agree when no pixel is unexplained in either direction.

So a line one pixel wider, or a shape shifted by one pixel, passes at displacement 1. A missing shape, a wrong colour, or a shape displaced further does not. Results are always reported with the tolerances used.

- `--place` is for a reference cropped from a larger screen. It finds the offset where the reference best fits the candidate (least mean absolute difference) and compares there.
- `--trim N` first drops N pixels from each edge of the reference.

Either argument may be a directory. Each picture in the reference directory is then compared with the picture of the same name, of any extension, in the candidate directory.

**Unit tests (15, in `src/compare.rs`, `src/frame.rs` and `src/tools.rs`)** cover:
- identical frames;
- a shape shifted one pixel, which fails exactly and passes at displacement 1;
- a shape shifted two pixels, which fails at displacement 1;
- a wrong colour, which fails at any displacement;
- a missing shape, which is unexplained in the reference only;
- channel tolerance at and just past its bound;
- frames of different sizes;
- placement of a crop;
- frame bounds and cropping;
- digest parsing;
- error-message shortening.

## 4. How the oracle was itself checked

The oracle is only useful if it reproduces PP3 as PP3 really behaved. That was checked against independent evidence.

**The evidence.** The Telidon project's `rosetta_stone` testbed (Nick Fox-Gieg, 2018) has 18 small pages and 18 JPEG screenshots (634 × 476, one 633 × 476). Before this work nobody knew what had rendered them.

**The check.** The oracle captured the same 18 pages. Each JPEG was placed inside the 640 × 480 capture and compared:
- **Placement:** every JPEG sits at an offset of 0 to 4 pixels, consistent with hand-cropped screenshots.
- **Difference:** the mean absolute difference was 0.00 to 0.78 levels.
- **JPEG noise:** 11 of the 18 had no pixel differing by more than 24 levels; the others differed on at most 0.28 % of pixels.

**The tolerance, measured rather than chosen:**

| Channel tolerance | Displacement | Pass |
|---|---|---|
| 0 | 0 | 0 of 18 |
| 24 | 0 | 11 of 18 |
| 48 | 0 | 12 of 18 |
| 48 | 1 | 13 of 18; the 5 failing had 2 to 16 unexplained pixels |
| 64 | 1 | 17 of 18 |
| 64 | 1, trim 1 | 18 of 18 |

**The residual differences**, each examined:
- **JPEG chroma smear** on saturated colour edges, in the green, purple, cyan, red and orange pages.
- **One-pixel steps** on the left and right of the circle.
- **`arc.jpg`'s crop artifact:** two blue pixels at its top-right corner, (631,0) and (632,0), caught from whatever was beside PP3's window.

**The conclusion.** The JPEGs are PP3 screenshots, and the oracle reproduces what someone else independently got from PP3.

**The permanent test.** This check is the ignored test `the_oracle_reproduces_the_rosetta_stone_screenshots` (`crates/naplps-oracle/tests/rosetta.rs`), run by the full gate (REQ-5752).
- **Inputs:** its 36 input files are pinned by SHA-256 in `tests/rosetta.sha256`, and the test fails if any differs.
- **What it checks:** that the set of passing pictures is exactly the 18 page names.
- **Result:** it passed on 12 November 2026 in 66 seconds.

## 5. Reference frames of the collection

All 141 distinct NAPLPS pages under `~/devel/teletext-reference/NAPLPS/` were captured on 12 November 2026. The collection holds 309 page files with 141 distinct contents. The frames, the manifest, the page-hash list (`pages.sha256`, page hash to original paths) and the gallery are kept in `~/devel/teletext-reference/NAPLPS/pp3-reference-frames/`, never in this repository.

- **Never settled:** 18 pages, most likely from blink or animation (TODO-5762). The first reviewed were `mge201a/HALLEYS.NAP` and `images/ny2001.nap`.
- **Explained so far:** `COMSANTA.NAP` draws a white screen because the file is only 28 bytes.
- **Not yet explained:**
  - a small "<!q>" at the top left of `canada1`, `efini` and `caski1`;
  - vertical stripes at the edges of `canada1`.
- **Timing:** the run took about 40 minutes, sequentially. 53 % of that was the pages that never settled waiting out the 60-second ceiling, 30 % was sending at 9,600 bits a second, and 16 % was the 3-second quiet wait.
- **Faster runs:** stopping early on a blink cycle and running several PP3 sessions in parallel should bring a full run to a few minutes. Neither is built yet.

The review of these frames, tagging each page as Telidon 699 or NAPLPS, and committing the pinned page list are TODO-5761 and TODO-5753.

## 6. The period fonts and how they were validated

The fonts PP3, MGE and Prodigy used were recovered exactly from the programs. The data, the format, every offset, the scripts that reproduce each step, and a specimen page are in `~/devel/teletext-reference/NAPLPS/fonts-extracted/`, with `FONTS.md` as the full account. In short, validation came from four independent directions:

1. **Rendering.** PP3 drew each of its three character sets through the oracle.
   - **At the default character field** (1/40 × 5/128, 16 × 24 pixels): every code 2/1 to 7/14 of G0, G2 (through SS2) and G3 (through SS3).
   - **At about five times that size** (dx 78/256, dy 120/256, three glyphs a page, 96 pages).

   The large drawings keep chamfered corners, and the pen thickens with the size. That shows the font is a stroke font, not a bitmap.
2. **Structure in the binary.**
   - **A coordinate-only run:** profiling `PP3SCOMM.EXE` found a 4 KB run of bytes all below 10 that read as connected segments (x1 y1 x2 y2).
   - **The index:** chained 6-byte records (length, offset, two metric bytes) gave exactly 94 records per set.
   - **Every coordinate in range:** all 992 segments fall inside a 7 × 10 grid, asserted by the extractor.
3. **Agreement with the rendering.** The extracted glyphs match the glyphs PP3 drew.
4. **Agreement across programs.** The same bytes are in MGE 2.01, identical for both sets, and in Prodigy's MVDI layer. Prodigy's version differs at 7/12, a broken bar, and in its supplementary set, which has 44 of the same glyphs at the same codes and 8 interface symbols at 7/0 to 7/7.

Two problems found while extracting, and how each was settled:
- **Several blocks of small numbers fit a table's data span.** The data base is taken as the fitting position nearest before the index that follows a byte which is not a coordinate. That rule reproduces the base confirmed by hand for PP3 (0x2FD60) and for Prodigy (0xE5E0).
- **A sparse table whose first codes are unassigned also chains when read one record early,** which shifts every code by one. The reading kept is the one that agrees code for code with PP3's sets, whose alignment PP3's own rendering fixes. For Prodigy's supplementary set, 44 of 52 glyphs agree at shift −1 and none at 0.

**Not yet confirmed:** the meaning of the two metric bytes in each record. Only eight (left, width) pairs occur, and they do not map directly onto the ten width classes in Dillon's NAPLPS notes. Settling it means drawing proportionally spaced text through PP3 and measuring each glyph's advance.

## 7. Running it

```
cargo build --release
target/release/naplps-oracle capture --out tmp/ref/NAME PAGE.nap ...
target/release/naplps-oracle compare --displacement 1 REFERENCE_DIR CANDIDATE_DIR
cargo test --release -- --ignored        # the rosetta self-check, about a minute
scripts/check.sh full                    # every gate, including the self-check
```

The oracle needs `dosbox`, `Xvfb`, `socat`, `xdotool`, `ffmpeg`, `ffprobe` and `sha256sum` (`sudo apt-get install dosbox xvfb socat xdotool ffmpeg`). The full gate fails, naming what is missing, without them.

## 8. Still owed

| To-do | What |
|---|---|
| TODO-5753 | tag each corpus page as Telidon 699 or NAPLPS |
| TODO-5754 | a second period decoder (TurShow, MGE) as an oracle, and its agreement with PP3 |
| TODO-5755 | calibration and conformance pages written from the standard, one per clause |
| TODO-5756 | byte loss on the serial line above 9,600 bits a second |
| TODO-5757 | PP3's service-directory entry 1 settings, recorded in the manifest |
| TODO-5758 | the preamble checked against the standard |
| TODO-5759 | a full-gate test that nothing the oracle starts listens on a network |
| TODO-5760 | a security analysis and fuzz target before the renderer is built |
| TODO-5761 | review of the corpus frames and a committed pinned page list |
| TODO-5762 | drawing over time: WAIT, blink, incremental drawing at period line rates |
| TODO-5763 | modern decoders as differential decode oracles under `tests/oracles/` |
