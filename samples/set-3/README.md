# NAPLPS sample pages 061–085

Start with [the 5 × 5 contact sheet](out/contact-sheet.png), [the exact-size 256 × 200 sheet](out/contact-sheet-small.png), or [the design notes](DESIGN.md).

- `pages/`: 25 independent page generators, numbered to match `CONCEPTS.txt`.
- `out/*.nap`: final 7-bit NAPLPS streams.
- `out/*.png`: final 640 × 480 previews, plus `-256x200`, `-320x200`, and `-512x400` previews rendered directly from each stream.
- `out/manifest.json`: requested machine-readable catalogue.
- `out/validation.json`: hashes, sizes, colour counts and verification results.
- `out/summary.txt`: one-line summary for every page.
- `atelier.py` and `encoder/`: shared encoding/geometry utilities; no shared page layout.

Regenerate and verify from this directory:

```sh
python3 render.py --generate
python3 validate.py
```

Generators use Python's standard library. Preview assembly uses Pillow and the existing `naplps-render` binary and Microstar stroke font at the paths given in `render.py`. Validation also regenerates `DESIGN.md`, the manifest, report and summaries. All 25 pages are stills and settle to the complete composition immediately after drawing.
