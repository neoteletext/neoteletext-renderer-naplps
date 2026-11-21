# NAPLPS pictures / 121–125

[Contact sheet](out/contact-sheet.png) · [Manifest](out/manifest.json) · [Concepts](CONCEPTS.md)

The contact sheet shows 640 × 480 renders across the top and 480 × 460 renders below, in page order. Each full-size PNG is rendered directly at its named size using the repository's stroke font. Each stream begins with the full reset and defines all 16 colour-map entries.

Run `python3 render.py` to rebuild the streams, previews, manifest and contact sheet. Run `python3 validate.py` to confirm deterministic generation, the reset, the colour map, the 7-bit and byte-size limits, clean renderer diagnostics, both preview sizes and the animated states. An individual page can also be generated with `python3 -B pages/121-afterimage.py`. All Python code uses the standard library.

## 121 · Afterimage

Nested native circles give the iris a machined rim, and stepped polygon vertices describe the taper of each blade. Opposite blades share an index, so six BLINK commands move two lime highlights around the ring every 1.2 seconds and drive the phase strip with the same entries. The renderer adds each blink delay to the preceding blink's start. A delay of two tenths on each successive definition produces six evenly spaced steps. The enlarged title and mint PHASE / 06 caption sit below the iris, with a wider phase strip under the caption. The circle reads as a taller oval on the 480 × 460 raster because the renderer maps the unit-screen coordinates to the full viewport.

## 122 · The Lure

Two wide polygons establish the dive beam, with a few small particles giving the empty water scale. WAIT holds that opening for one second. The next group draws the silhouette and jaws, then holds for seven tenths. The lure, eye and teeth follow. A SET COLOR update brightens the fish's already-painted back at the same moment. The larger depth caption sits below the beam and stays visible through the reveal. The renderer's ordinary still passes straight through both waits. Inspect the opening and silhouette using `--stage 1` and `--stage 2`.

## 123 · Fault Line

The five display letters are filled polygons, each clipped in the generator to both sides of a diagonal and displaced before encoding. The triangular counter in the A is painted back in with the paper colour. Larger horizontal lettering frames the display word. SHEAR appears once, in the INK / PAPER / SHEAR footer.

## 124 · Breathing Earth

Faceted walls frame the branching tunnels and chambers, which read as dark shapes against the ochre. A three-fleck DEF TEXTURE mask stipples both the outer clay and the brighter cut face in a single pass. The renderer leaves the previous fill visible through the gaps in the mask, so the stipple crosses the two clay tones without needing separate shapes. Stout connected lines link the cavities. Heavier leaders underline the enlarged AIR SHAFT, GARDEN and BROOD CHAMBER labels and point to their features. The TERMITE MOUND / SECTION subtitle identifies the cutaway.

## 125 · Selvedge Moth

A reflected tile map builds the moth from one square and four triangular DRCS masks. The same masks take different palette entries across the forewing eyespots and the cool hindwings. The body and aerials use simple vector strokes and fills. An enlarged SELVEDGE MOTH title is the only caption inside the stitched border. DRCS fields rasterize at the terminal's field size. At both preview sizes the occasional single-pixel seam between tiles reads as part of the weave, while the mirrored diagonal tiles retain their sharp silhouette.
