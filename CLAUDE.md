# neoteletext-renderer-naplps

NAPLPS (ANSI X3.110-1983, CSA T500-1983, CCITT T.101 Annex D) for NeoTeletext: the renderer (`naplps`, a `no_std` library, and `naplps-render`) and the verification it is judged by: `naplps-oracle`, which captures reference frames from PP3 (Personality+III, 1991) running in DOSBox, and the comparison that judges a frame against them.

## How we work

@~/devel/neoteletext-common/DEVELOPMENT.md

That is the one document of how we work, for every NeoTeletext repository, with rdm as the record of all work (DEC-2162). This file says only what is particular to this repository; where the two differ, that document holds.

## Rules particular to this repository

- **Developed on chunko** (Ubuntu). The oracle needs `dosbox`, `Xvfb`, `socat`, `xdotool`, `ffmpeg` and `ffprobe` (`sudo apt-get install dosbox xvfb socat xdotool ffmpeg`); the full gate fails without them.
- **No period software, page data or screenshots in this repository.** PP3, the corpus pages and the reference screenshots are read from `~/devel/teletext-reference/NAPLPS/` (or `NAPLPS_PP3_DIR`, `NAPLPS_ROSETTA_DIR`) and pinned by SHA-256: PP3's files in `session.rs` (`PINNED_FILES`), the rosetta_stone testbed in `crates/naplps-oracle/tests/rosetta.sha256`. Captured frames go to the ignored `tmp/`.
- **The oracle never listens on the network.** PP3's COM1 is a pseudo-terminal made by socat (DOSBox's `nullmodem` would listen on every interface); Xvfb runs with `-nolisten tcp`.
- **The standard is the source of truth for behaviour; PP3 is the evidence for what the standard's approximations look like** (section 8.3.4). A difference between the two is recorded as a decision in rdm, never settled silently in code.
- **The renderer library is sans-IO, `no_std` and integer-only** (DEC-5764, DEC-5765): no file, clock or floating point; it draws colour-map addresses into the caller's canvas. Fonts are data passed in (DEC-5768); no font is compiled in.
- **Behaviour PP3 shows is measured, then recorded**: each rule taken from PP3's frames (pixel rounding, fill edges, hatching, circle radii, glyph placement) cites its measurement in the code and is a decision in rdm.
- **No library without the owner's approval by name** (DEVELOPMENT.md section 7), or under the owner's standing approval of pure-Rust libraries (DEC-6579). The renderer library `naplps` has no dependencies and must keep none; the oracle has none either, since it drives external programs. The one library in the workspace is `proptest`, a development dependency of the test-only crate `naplps-fuzz` alone (DEC-6607), which drives the renderer with generated input and keeps every input that found a fault.

## Commands

- `cargo build --release`, then `target/release/naplps-oracle capture --out tmp/ref/NAME FILE...` captures PP3's frame of each page; `target/release/naplps-oracle compare [--place] [--trim N] [--channel N] [--displacement N] REFERENCE CANDIDATE` judges pictures or directories of them.
- Gates: `scripts/check.sh commit | push | full`; the full gate runs the oracle self-check (`cargo test --release -- --ignored`), which captures the 18 rosetta_stone pages and compares them with the independent PP3 screenshots.
