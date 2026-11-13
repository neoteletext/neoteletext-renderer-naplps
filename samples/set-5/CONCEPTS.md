# Brief: ten NAPLPS pages that exercise everything text can do

You are the designer. Earlier runs made 110 NAPLPS sample pages that the owner liked; see `reference/` for contact sheets, design notes and generators. Now make **ten pages, numbered 111 to 120, that between them exercise every text facility NAPLPS has**. Each page is both a real, good-looking page with a believable purpose and a demonstration: a reader of the gallery should be able to see from the set what NAPLPS text can do.

## Sources

- **Read `~/devel/neoteletext-naplps/docs/guide.html` (section 8 especially) and `~/devel/neoteletext-naplps/docs/reference.html` (C0 controls, C1 controls, TEXT, FIELD, Text, the supplementary set, Mosaics, DRCS) first.** They list every text facility, its bytes, and what this renderer does not do.
- The renderer's source is the ground truth: `~/devel/neoteletext-naplps/crates/naplps/src/terminal.rs` (text_command, character, advance_step, row_step, carriage_return, line_feed, scroll, active_position_set, nsr, the C0 and C1 dispatch) and `text.rs`.
- `encoder/` is a working encoder (Python 3, standard library only) from an earlier set; the earlier generators in `reference/*/pages/` show its use. Extend it freely.

## What the ten pages must cover between them

Every item below appears on at least one page, used where it suits that page's purpose, and each page's design notes say which items it covers:

1. **The five C1 sizes**: SMALL, MEDIUM, NORMAL, DOUBLE HEIGHT, DOUBLE SIZE.
2. **TEXT field sizes** beyond the presets, from small print to display type a quarter of the screen high.
3. **Character spacing**: 1, 5/4, 3/2 and proportional.
4. **Row spacing**: 1, 5/4, 3/2 and 2.
5. **Path**: right, left, up and down.
6. **Rotation**: 0, 90, 180 and 270 degrees, and rotation combined with path (vertical text that reads upward or downward, text that runs upside down).
7. **Cursor and drawing point motion** (TEXT second byte b4 b3): together, cursor leads, point leads, independent, used so that the difference is visible.
8. **Underline, reverse video, and colour mode 2** text on a background colour.
9. **The supplementary set**: accented letters (non-spacing accents before letters) in at least three languages, currency signs, fractions, arrows, typographic symbols.
10. **Positioning controls**: APS (row and column), APH (home), NSR with a position, BS, HT, LF, VT, CR, and POINT SET for exact placement.
11. **REPEAT and REPEAT TO EOL** for rules, leaders (dot leaders in a table of contents or price list) and fills.
12. **An active FIELD**: text wrapping and CR/LF behaviour inside a field smaller than the screen, and **scroll mode** (SCROLL ON) scrolling text up inside that field.
13. **BLINK START** on text (sparingly), and BLINK on a colour-map entry used for text.
14. **DRCS characters** used as text: a custom glyph or logotype set in a line of ordinary text.
15. **Mosaic characters** mixed with text (a mosaic border, bar or banner).
16. **The full primary set**: every printable ASCII character appears somewhere in the ten.

## Ideas for purposes (choose your own if better)

A multilingual travel phrasebook page; a typographic specimen sheet; a restaurant price list with dot leaders; a news ticker or chat screen that scrolls in a field; a crossword or word-search with vertical words; a book spine and cover with rotated titles; a mirror-writing or upside-down puzzle page; an airline boarding pass; a currency exchange board; a poetry page with generous row spacing; a typewriter letter using BS and HT; a cinema marquee.

## Your working directory

This directory is yours; write only here.
- `pages/NNN-name.py` (NNN from 111 to 120) writing `out/NNN-name.nap`.
- `out/manifest.json`: a JSON array, one object per page: `{"number": 111, "file": "111-name.nap", "title": "...", "purpose": "...", "style": "...", "bytes": 1234, "techniques": [...], "covers": [1, 3, 5], "animated": false}` where `covers` lists the numbered items above that the page exercises.
- `DESIGN.md`: a paragraph per page, and at the end a table of the sixteen items and which pages cover each.

## Rendering

```
~/devel/neoteletext-naplps/target/release/naplps-render --width 640 --height 480 --font ~/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes out/111-x.nap out/111-x.ppm
ffmpeg -loglevel error -y -i out/111-x.ppm out/111-x.png
```

Look at every render, at 640 x 480 and at 512 x 400, and iterate until each page is good. `--tenths N` shows BLINK state only; WAIT is not honoured (the whole stream is drawn).

## Hard requirements

1. The final picture is the finished design, complete as a still: pages are compared with the period terminal program PP3 by capturing its screen once the page settles. At most 3 of the 10 pages may blink or use WAIT, and nothing the composition depends on may blink.
2. 7-bit stream, beginning with SO and a RESET of `20 7F 7F`; a 16-entry colour map; each page under 6 KB.
3. Stroke font only (`microstar.strokes`). Word wrap is not implemented and the cursor is never drawn: do not rely on either.
4. Believable fictional content; no real brands or people.
5. **Report renderer behaviour you believe is wrong.** These pages exercise text far more than earlier ones did, so expect to find things. For each, note in DESIGN.md under "Renderer observations" the bytes that show it, what you expected from the standard or the reference, and what the renderer did; then design around it. Do not change anything outside this directory.

## Finish

Render all ten at 640 x 480, make `out/contact-sheet.png` (5 x 2), write the manifest and DESIGN.md, and print a one-line summary per page, the coverage table, and the renderer observations.
