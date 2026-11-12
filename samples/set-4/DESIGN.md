# Twenty-five independent NAPLPS services / 086–110

[640-pixel contact sheet](out/contact-sheet.png) · [Native 256-pixel contact sheet](out/contact-sheet-256.png) · [Manifest](out/manifest.json) · [Validation report](out/validation.json)

These are separate fictional services, not a branded collection. Their colour families, geometry, density, borders and composition follow the individual purposes in CONCEPTS.txt. Each numbered Python generator is independently runnable from any directory and writes its matching stream into `out/`. The encoder and page generators use only the Python standard library; Pillow is used solely by the preview and checking scripts. All artwork is native NAPLPS geometry, characters, patterns or macros, with Microstar as the only stroke font. No external artwork, assets or brands are used.

Reproduce from this directory:

```sh
python3 render.py      # generate 25 streams, 100 still previews and two contact sheets
python3 finish.py      # manifest, these notes, summary and two protocol-derived GIFs
python3 validate.py    # deterministic output, sizes, reset independence and content checks
```

For a single page, use `python3 pages/093-ski-report.py`, then `python3 render.py 093`. Full-size images have the same stem as the stream. Smaller previews have `-256x200`, `-320x200` and `-512x400` suffixes. The 5 × 5 main contact sheet uses 320 × 240 thumbnails of the 640 × 480 renders; the small contact sheet pastes actual 256 × 200 renders without resampling.

## Encoding and review

Every stream first designates G1 as PDI (`1B 29 57`) so even a predecessor that reassigned G1 cannot intercept its reset, then immediately sends `SO RESET 7F 7F` (`0E 20 7F 7F`). G0 primary, G2 macros and G3 mosaics are explicitly designated after reset. Every page defines all sixteen colour-map entries, uses one-byte single operands and four-byte coordinate/colour operands (`DOMAIN 21 4C`), and sets a nonzero logical pel. The extended local `pages/lib.py` reuses the supplied encoder but suppresses redundant state commands, measures proportional stroke extents, and enforces the stricter 6,144-byte ceiling. All streams are 7-bit and all are below 3 KB. No word-wrap, cursor, input-field or transmit-macro facility is used.

Every final page was inspected at 640 × 480 and at native 256 × 200. The 320 × 200 and 512 × 400 previews were also generated. The visual iterations included heavier crossword rules, thicker branched DRCS snowflakes, a shorter ticket seat line, a corrected tide ordinate and an accurately sized dinosaur/human comparison. Main copy generally uses fields of at least 20 design pixels (1/32 screen width); smaller diagram indices and nonessential security detail are secondary. Static pictures remain complete with either phase of the mission LED.

`validate.py` regenerates every stream to check determinism, checks manifest counts, seven-bit data, reset and all sixteen palette definitions, dimensions and palette counts at all four sizes. It compares each page after a different predecessor at both 640 and 256 widths, then repeats at 256 after deliberately hostile character-set assignments. It also verifies the actual mate-in-two, crossword interlock, 60-seat allocation, WAIT budget and LED phases. The machine-readable report includes SHA-256 hashes and exact byte sizes.

## Timing and renderer observations

Only **098** and **104** are animated. Kestrel blinks a small LED using `3F 5C 42 4E 40` on selected entry 8: entry 7 for two tenths, entry 8 for fourteen. Lucky Comet has seven `3D 5C 43` WAITs, totalling 21 tenths (2.1 seconds), and settles on a complete result screen. Its final `SELECT COLOR 7; SET COLOR` redefines already drawn confetti. All other pages have neither WAIT nor BLINK. Both are below the brief’s eight-page animation allowance.

The known **WAIT preview limitation** is present: `naplps-render` feeds the entire stream and does not stop at WAIT. Thus the seven `3D 5C 43` commands in 104 do not delay the CLI’s final PNG. `finish.py` renders stream prefixes at the exact WAIT boundaries for the numbered stage PNGs and GIF; the GIF adds a final viewing hold and loops for review, whereas NAPLPS plays once and holds. The mission GIF samples the native BLINK states with `--tenths 0` and `--tenths 2`. [Mission GIF](out/098-orbit-status.gif) · [Lottery GIF](out/104-lottery-results.gif).

A suspected **rotated-glyph edge clipping/rounding issue** was observed on the queen’s lower Q: at x=496 a glyph stroke on its rotated field boundary disappeared, while x=490 retained it at all four output sizes. The failing TEXT/POINT/character bytes were `22 42 40 40 4A 6A 56 24 58 44 72 5D 0F 51 0E`; the workaround aligns the origin to a common pixel boundary, using POINT `24 58 44 62 45` instead. These operands are derived from the generator’s four-byte encoding; no renderer code was changed. Apart from this visual observation, no malformed-stream errors or processing-limit warnings were observed. Known period differences in very large/rotated stroke type, downloadable character rasterisation and separated-mosaic spacing still apply; these previews are not PP3 oracle certifications. The queen’s lower Q deliberately uses a half-turn; ellipse shapes that are not circular are explicitly faceted polygons rather than unsupported multi-point spline arcs. Fine decorative banknote engraving is allowed to merge at low resolution while its labels stay legible. Nothing outside this working directory was changed in the project.

## Pages

### 086 — The Velvet Satellites

[Preview](out/086-admission.png) · [256 × 200](out/086-admission-256x200.png) · [Stream](out/086-admission.nap) · **881 bytes**

A landscape concert ticket for the Velvet Satellites at the Glasshouse, with price, door time, floor, row and seat. Coral stock gives the service its own print identity; the long perforation, end notches and narrow barcode stub make the object recognisable before any text is read. I shortened the seat line after the small render showed it touching the perforation. The serial bars are illustrative rather than a claim of a standard barcode symbology.

### 087 — Isles Reserve / 25 Crowns

[Preview](out/087-banknote.png) · [256 × 200](out/087-banknote-256x200.png) · [Stream](out/087-banknote.nap) · **1,023 bytes**

A clearly marked specimen from the fictional Isles Reserve, honouring the invented naturalist Mira Vale. Native three-point arcs make guilloche-like fans around a faceted oval portrait; opposing large numerals and a double border recall intaglio composition. The restrained sage, cream and dark green inks are deliberately unlike the vivid ticket. Fine engraving is decorative: the value and specimen wording remain the primary readings at 256 pixels.

### 088 — Queen of Hearts

[Preview](out/088-queen.png) · [256 × 200](out/088-queen-256x200.png) · [Stream](out/088-queen.nap) · **953 bytes**

An ivory card on a bottle-green table, with a red, gold and navy queen repeated under a 180-degree geometric transform. Crowns, roses, a sceptre and diamond embroidery identify the court figure without tiny face details. Opposing hearts and a rotated lower Q complete the traditional two-ended card. The design uses only the Microstar font, including the corner indices.

### 089 — The King’s Turn

[Preview](out/089-mate-in-two.png) · [256 × 200](out/089-mate-in-two-256x200.png) · [Stream](out/089-mate-in-two.nap) · **1,396 bytes**

A three-piece problem framed as a chess journal, with an oversized title column beside a properly oriented a1-dark board. Each piece is a polygon silhouette; the white pieces keep an ink contour on both square colours. Position: White Ka5, Qa1; Black Ka8. The unique key is 1.Kb6+! Kb8 2.Qh8#. The local validator checks the legal king/queen moves, excludes any immediate mate, and verifies both the unique key and forced reply.

### 090 — The Morning Fold / Mini 218

[Preview](out/090-crossword.png) · [256 × 200](out/090-crossword-256x200.png) · [Stream](out/090-crossword.nap) · **906 bytes**

A legitimate five-by-five open word-square crossword, avoiding an illegibly dense full newspaper puzzle. Each clue is indexed across/down, and all five answers interlock in both directions: HEART, EMBER, ABUSE, RESIN, TREND. Numbering is 1–5 across the top, then 6–9 down the first column. I thickened every grid rule after it disappeared in the first 256-pixel preview.

### 091 — Fern Cowl / Chart 02

[Preview](out/091-knit-chart.png) · [256 × 200](out/091-knit-chart-256x200.png) · [Stream](out/091-knit-chart.nap) · **1,754 bytes**

A ten-stitch, ten-round fair-isle repeat on a cream chart, with moss and rose diamonds climbing diagonally like a small fern motif. A real relative polygon macro supplies all forty coloured stitches; the colour key and instructions sit outside the grid. Large cells and short instructions make this usable as a pattern rather than a texture sample. Round numbering and the lower-right reading instruction agree.

### 092 — Greyhook Harbour / Tides

[Preview](out/092-tide-table.png) · [256 × 200](out/092-tide-table-256x200.png) · [Stream](out/092-tide-table.nap) · **877 bytes**

A fictional harbour almanac combines a 24-hour, metre-labelled tidal plot with high and low water times. The cosine curve has a 12-hour 24-minute period, highs of 3.0 m and lows of 0.5 m; the table agrees with its extrema. Four native circle constructions illustrate moon phases. The chart ordinate was corrected to match the labelled 0–3 m range during review; no navigation accuracy is claimed for the fictional harbour.

### 093 — Rime Ridge / Snow Report

[Preview](out/093-ski-report.png) · [256 × 200](out/093-ski-report-256x200.png) · [Stream](out/093-ski-report.nap) · **756 bytes**

A cold blue mountain panorama gives way to a pale report panel: 124 cm base, 18 cm fresh snow, seven of nine lifts and trail/grooming totals. The five six-armed snowflakes are genuine downloadable DRCS characters, drawn once and reused at text positions. I enlarged their logical pen and added branches because the initial thin character vanished when reduced; the final 256-pixel flakes remain visibly six-armed.

### 094 — Breakwater / Surf

[Preview](out/094-surf-report.png) · [256 × 200](out/094-surf-report-256x200.png) · [Stream](out/094-surf-report.nap) · **586 bytes**

A broad teal sky, apricot sun and oversized foam crest supply a beach-service identity. The 1.8 m southwest swell and 12-second interval occupy the dark water, while a separate north-labelled wind rose shows NW at 12 kt. The wave combines a native filled arc with a cut-out inner arc and an angular foam polygon. Its broad shapes survive at terminal resolution.

### 095 — The Seed Cupboard

[Preview](out/095-planting-calendar.png) · [256 × 200](out/095-planting-calendar-256x200.png) · [Stream](out/095-planting-calendar.nap) · **1,327 bytes**

A practical southern cool-climate sowing planner for peas, kale and radish. Two six-month tables preserve full three-letter month names without shrinking the text; green cells and seed dots denote sowing windows. Warm seed-packet paper, a tiny sprout and a thin green border create a quiet garden-shop identity. Windows are broad fictional editorial guidance, not a forecast for a specific locality.

### 096 — Field Notes / Finches

[Preview](out/096-finches.png) · [256 × 200](out/096-finches-256x200.png) · [Stream](out/096-finches.nap) · **1,232 bytes**

Three invented Alder Isles finches sit on separate ochre perches: Amber, Russet and Sage. Their cap, breast and wing colours provide identification cues, while scaled bodies, stated lengths and an approximate 10 cm bar establish relative size. The plate keeps generous open space around the specimens and avoids boxes. I lengthened the scale bar after comparing it with the illustrated body lengths.

### 097 — Stegosaurus / Armour Up!

[Preview](out/097-stegosaurus.png) · [256 × 200](out/097-stegosaurus-256x200.png) · [Stream](out/097-stegosaurus.nap) · **782 bytes**

A bold museum children’s panel puts a heavy green Stegosaurus against ochre, with rusty plates and pale tail spikes. Native incremental lines encode its short flank marks. A roughly 1.8 m human stands beside the 7 m animal at the corresponding horizontal scale, and the lower strip gives its plant diet and approximate 150-million-year age. The initial token human icon was replaced with a real side-by-side scale comparison.

### 098 — Kestrel / Flight 03

[Preview](out/098-orbit-status.png) · [256 × 200](out/098-orbit-status-256x200.png) · [Stream](out/098-orbit-status.nap) · **776 bytes**

A sparse green phosphor mission display centres on a small Earth, reference circles and an inclined orbital ellipse. A gold spacecraft with two solar panels sits on the track; right-hand telemetry gives altitude, velocity and battery state. Only the tiny link LED blinks (two tenths dim, fourteen tenths bright); the LINK OK words and all mission information stay visible. The diagram is schematic.

### 099 — Vanterra / V-6 GT

[Preview](out/099-car-advert.png) · [256 × 200](out/099-car-advert-256x200.png) · [Stream](out/099-car-advert.nap) · **887 bytes**

A fictional Vanterra V-6 GT appears in low three-quarter view above a violet perspective grid, with a striped peach sunset behind the roofline. Large filled faces, deep glazing, tyre discs and narrow highlights produce an advertising gloss without a raster image. The price and fuel-injection/five-speed copy form a compact sales proposition. The exaggerated wedge and dramatic horizon belong to the car advertisement alone.

### 100 — Velune / Autumn 86

[Preview](out/100-lookbook.png) · [256 × 200](out/100-lookbook-256x200.png) · [Stream](out/100-lookbook.nap) · **832 bytes**

A pale editorial page pairs a quiet seasonal column with a tall, faceted figure in a linen coat and wool skirt. A genuine defined fill pattern A tiles diagonal marks over the skirt, with the mask size chosen to remain distinct at 256 pixels. The limited charcoal, taupe and muted red palette and the open white space are intentionally far from the car’s glossy night scene. No bitmap illustration or second font is embedded.

### 101 — Château Aubrel / Reserve 1983

[Preview](out/101-wine-label.png) · [256 × 200](out/101-wine-label-256x200.png) · [Stream](out/101-wine-label.nap) · **694 bytes**

A clipped-corner cream label on burgundy stock uses nested gold rules, a shield and a simple chateau engraving. Native horizontal hatching gives the vineyard slopes an engraved rhythm; short vector serif terminals embellish the large Microstar AUBREL lettering. The circumflex in CHÂTEAU is a real supplementary-set accent (SS2 43 before A), not an ASCII approximation. Vintage, fictional region, volume and alcohol information complete the bottle label.

### 102 — Alder United / 4-4-2

[Preview](out/102-football-tactics.png) · [256 × 200](out/102-football-tactics-256x200.png) · [Stream](out/102-football-tactics.nap) · **840 bytes**

A horizontal pitch carries exactly eleven numbered discs: one goalkeeper, four defenders, four midfielders and two forwards. Cream markings, alternating grass strips and gold arrows communicate the high press and rightward attack. Passing arrows are drawn beneath player discs so they never obscure the numbers. Penalty boxes, six-yard boxes and the centre circle keep the field recognisable at low resolution.

### 103 — Bracken Park / Race 4

[Preview](out/103-racing-form.png) · [256 × 200](out/103-racing-form-256x200.png) · [Stream](out/103-racing-form.nap) · **945 bytes**

A compact form guide for a fictional 1600 m race lists four runners, their last three finishes and fractional odds. Four distinctive silks—sash, hoop, diamond and shoulder band—supply the coloured shapes the concept calls for. Alternating white and warm paper rows make the entries easy to follow without dense rules; the going, time and purse are included. Odds are deliberately much larger than the supporting form figures.

### 104 — Lucky Comet / Draw 318

[Preview](out/104-lottery-results.png) · [256 × 200](out/104-lottery-results-256x200.png) · [Stream](out/104-lottery-results.nap) · **998 bytes**

Six large result balls alternate gold and turquoise against purple; their staggered heights, offset shadows and arc glints suggest a bounce while remaining a complete still. The results 07, 12, 19, 28, 34, 41 and bonus 03 are unambiguous. Six three-tenth reveals plus a three-tenth final palette change total 2.1 seconds. The final SET COLOR changes already drawn orange confetti to gold; no part of the final design depends on blinking.

### 105 — Vale Votes / Election 1986

[Preview](out/105-election-night.png) · [256 × 200](out/105-election-night-256x200.png) · [Stream](out/105-election-night.nap) · **1,044 bytes**

A broadcast results page reports the fictional Vale’s completed 60-seat election: Civic 33, Union 21 and League 6. The hemicycle contains exactly sixty native filled circles in rows of 9, 13, 17 and 21; sorting by angle assigns contiguous party sectors while preserving those counts. A warm lower band gives declaration progress and the Civic swing. A 31-seat majority threshold makes the Civic majority headline consistent.

### 106 — Merevale Hospital / North Entrance

[Preview](out/106-hospital-wayfinding.png) · [256 × 200](out/106-hospital-wayfinding-256x200.png) · [Stream](out/106-hospital-wayfinding.nap) · **567 bytes**

A large medical cross introduces three full-width destination bands: emergency left, ward 3 ahead and X-ray right. Simple cross, bed and radiograph pictograms reinforce the words, and the arrows are oversized for viewing at terminal resolution. The white hospital heading and north-entrance location make it a believable fixed sign. Calm spacing and very short copy replace the denser information treatment used by the reports.

### 107 — The Linden Quay / Confirmed

[Preview](out/107-hotel-confirmation.png) · [256 × 200](out/107-hotel-confirmation-256x200.png) · [Stream](out/107-hotel-confirmation.nap) · **582 bytes**

A warm reservation card welcomes the fictional Nora Bell for three nights in a quay double, with two guests and a paid total of $216. Arrival and departure occupy two tidy columns, while a native brass key motif balances the guest line. Colour mode 2 paints a distinct paper-tinted field behind the reference number. Breakfast and the 14:00 check-in time make the confirmation useful without introducing an interactive form.

### 108 — Sun Spiral / Music Fair

[Preview](out/108-festival-poster.png) · [256 × 200](out/108-festival-poster-256x200.png) · [Stream](out/108-festival-poster.nap) · **1,310 bytes**

A psychedelic music-fair poster uses full-height plum, pink, orange and green ribbons, two flower rosettes and deliberately undulating letter baselines. A gold field carries five fictional acts, with the Moth Parade highlighted on an orange banner. The dates, Meadow Park location, three-day duration and $24 price are all retained at readable sizes. Its flowing left edge and uneven display lettering break the rectilinear layouts elsewhere in the set.

### 109 — Northline FM / The Night Train

[Preview](out/109-radio-dial.png) · [256 × 200](out/109-radio-dial-256x200.png) · [Stream](out/109-radio-dial.nap) · **1,213 bytes**

A dark hi-fi tuner presents an 88–108 MHz scale, a red 101.7 needle, warm orange frequency readout and green stereo/programme accents. Native separated mosaic characters form the speaker grille at lower left. The Night Train runs 21:00–23:00 with the invented presenter Ivo Marsh. Tick hierarchy and a generous programme panel let the dial feel like equipment while retaining readable radio-service information.

### 110 — The Hollow Below / Chamber 04

[Preview](out/110-cave-room.png) · [256 × 200](out/110-cave-room-256x200.png) · [Stream](out/110-cave-room.nap) · **993 bytes**

Two polygonal passages frame a cold green pool and a small torch inside a faceted cave. A bright north/east compass agrees with the available exits; the lower text describes the draft, lists both exits and names the lamp, rope and brass key inventory. The picture dominates the upper half while the short command-style copy remains large. This is a complete illustrated adventure room, with no cursor or input-field commands.
