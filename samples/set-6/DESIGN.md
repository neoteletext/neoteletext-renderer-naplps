# NAPLPS pictures / 121–125

[Contact sheet](out/contact-sheet.png) · [Manifest](out/manifest.json) · [Concepts](CONCEPTS.md) · [Round 1](rounds/round-1.md) · [Round 2](rounds/round-2.md) · [Round 3](rounds/round-3.md) · [Round 4](rounds/round-4.md)

The contact sheet shows 640 × 480 renders across the top and 480 × 460 renders below, in page order. Each full-size PNG is rendered directly at its named size using the repository's stroke font. Each stream begins with the full reset and defines all 16 colour-map entries.

Run `python3 render.py` to rebuild the streams, previews, manifest and contact sheet. Run `python3 validate.py` to confirm deterministic generation, the reset, the colour map, the 7-bit restriction, clean renderer diagnostics, both preview sizes and the animated states. An individual page can also be generated with `python3 -B pages/121-afterimage.py`. All Python code uses the standard library.

## 121 · Afterimage

Nested native circles form the instrument housing and hub. Polygon faces, bevels and milled channels give the blades depth. Opposite blade insets share an index, so six BLINK commands move two lime highlights around the ring every 1.2 seconds and drive the recessed phase lamps with the same entries. Concentric rings and offset reflections form the central lens. Each index also lights a narrow trailing channel on the preceding blade. The renderer adds each blink delay to the preceding blink's start. A delay of two tenths on each successive definition produces six evenly spaced steps. The iris reads as a taller oval at 480 × 460 because the renderer maps unit-screen coordinates to the full viewport.

## 122 · The Lure

Layered water and suspended particles establish a dive beam. WAIT holds that opening for one second. The next group draws the silhouette, fins and jaws, then holds for seven tenths. The filament, concentric lure, eye and teeth arrive with a SET COLOR update that brightens the fish's back. Lit baitfish gather around the lure. The renderer's ordinary still passes through both waits. Inspect the opening and silhouette using `--stage 1` and `--stage 2`.

## 123 · Fault Line

The five display letters are filled polygons clipped to both sides of a diagonal and displaced. The upper arms of the U are clipped independently. Offset impressions and ink flecks give the letters a printed surface, and overpainted bands of variable depth, cast shadows and loose fibres expose layers along the paper tear. A triangular overpaint opens the counter in the A. The lower margin carries an ink control strip and registration target.

## 124 · Breathing Earth

Faceted clay walls overlay sediment bands. A three-fleck DEF TEXTURE mask stipples the cutaway across both clay tones. Layered strokes connect irregular chamber cavities occupied by tiny termites. Chevrons trace airflow out of two shafts. A magnified worker is indexed to a chamber, and the garden and brood chamber are distinguished by green clusters and pale brood shapes.

## 125 · Selvedge Moth

A reflected tile map builds the moth from one square and four triangular DRCS masks. Paired DRCS masks stamp reflected running stitches, satin stitches and diagonal edge stitches. Vector satin stitching forms eyespots across the tiles, while running stitches trace the veins. A threaded body, woven ground, diamond motifs and knotted fringe complete the cloth. The character fields rasterize at the terminal's field size, giving the occasional single-pixel seam between tiles.
