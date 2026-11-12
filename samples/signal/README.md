# SIGNAL

Ten original NAPLPS pages, designed for the supplied 640 x 480 renderer and a 16-entry colour map.

Start with [the contact sheet](out/contact-sheet.png) or [the design notes](DESIGN.md). The five animated review copies are [harbour](out/01-tide-clock.gif), [constellation](out/03-constellation.gif), [city](out/04-city-block.gif), [bird](out/06-two-languages.gif) and [kaleidoscope](out/08-kaleidoscope.gif).

```sh
python3 render.py
python3 validate.py
python3 finish.py
```

- `encoder/`: original Python 3 standard-library-only encoder.
- `pages/`: one standalone generator per page.
- `out/`: ten `.nap` streams, final PNGs, key-moment PNGs, GIF review copies, palette/timing JSON and a verification manifest.
- `DESIGN.md`: concepts, complete palettes, techniques, revisions, timing, byte sizes, future improvements and renderer observations.

Each stream is self-contained and under 8 KB. `validate.py` also confirms clean rendering, no inherited state from another page, deterministic generation and different animation phases.

The renderer consumes WAITs immediately; `--tenths` only controls BLINK. The PNG checkpoints and GIFs use exact stream prefixes to show WAIT timing. The `.nap` files retain their native WAITs. See `DESIGN.md` for details.
