# Sample pages

110 designed NAPLPS pages, each different in visual style and application purpose: news, weather, timetables, lessons, games, maps, charts, advertisements, posters and more.

| Directory | Pages | What |
|---|---|---|
| `signal/` | 01 to 10 | The SIGNAL collection: ten studies with a shared house style. |
| `set-1/` | 011 to 035 | News, forecasts, timetables, lessons, games, listings, maps. |
| `set-2/` | 036 to 060 | Plans, calendars, music, stories, advertisements, service screens, charts, science. |
| `set-3/` | 061 to 085 | Patterns and art styles: tartan, De Stijl, woodcut, stained glass, posters. |
| `set-4/` | 086 to 110 | Tickets, cards, puzzles, reports, guides, results boards, signs. |

In each directory:

- `out/*.nap` are the pages: 7-bit streams of 438 to 5,083 bytes that begin with a full RESET and use a 16-entry colour map.
- `out/manifest.json` (`manifest.tsv` in `signal/`) lists each page's title, purpose, style and size; `CONCEPTS.txt` is the list the set was designed from.
- `pages/*.py` generate the pages with the set's own `encoder/` (Python 3, standard library only). Each set was made independently and extended its own copy of the encoder, so the copies differ (DEC-5828). The helper scripts beside them (`render.py`, `validate.py`) name the renderer and font by the absolute paths of the machine they were written on.
- `DESIGN.md` has a paragraph on each page and what its designer noticed about the renderer.

`samples/pipeline.sh` renders every page at 256 x 200, 320 x 200, 512 x 400, 480 x 500 and 480 x 462, captures each in PP3 and compares the renderer with PP3; see its header. The results of 13 November 2026 are in `docs/verification.md`.

`samples/gallery/build_gallery.py` then builds one HTML page of every rendering and each page's PP3 comparison (REQ-5821).
