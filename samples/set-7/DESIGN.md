# NAPLPS game screens / 126–135

[Contact sheet](out/contact-sheet.png) · [Manifest](out/manifest.json) · [Concepts](CONCEPTS.md)

The sheet shows pages 126–130 in the upper group and 131–135 in the lower group. Each group has 640 × 480 previews above 480 × 460 previews at half size. The individual PNGs are direct renders at their named dimensions using the repository stroke font. Each page begins with a full RESET and programs all 16 colour entries.

From this directory, run `python3 -B validate.py --build` to regenerate the streams, previews, sheet and manifest. Run `python3 -B validate.py` to check the saved files against fresh builds, confirm deterministic generation and stream framing, check renderer diagnostics, and render both sizes and the alternate timing states. An individual stream can be rebuilt with `python3 -B pages/126-hem-of-the-sky.py`. The generators and image packaging use Python’s standard library. The base writer is the MIT-licensed encoder from set 6, copyright 2026 Andrew Stuart.

## 126 · Hem of the Sky

The stretched title sits opposite a large needle kite, whose four angular faces read in silhouette against a striped sun. Cross stitches bridge a jagged seam behind the kite, and a spool feeds the thread into its needle, with a pennant line dipping across the foothills. BLINK alternates the arrow beside PRESS START between cream and vermilion while the prompt stays cream and blue.

## 127 · Spore Switch

Fungus caps climb from the lower left in a sequence of four jumps. Each cap has a broad edge and three gill marks, so it reads as both a fungus and a landing surface. A relative macro places the same lamp on every cap. Two take a lime ink over a dim green halo, and the muted pair ahead match the two hollow positions in the HUD. A native arc marks the beetle’s jump, and a barred exit sits in the growth rings of the log.

## 128 · Siltfold

Ink-blue pools sit inside the exposed basin. A defined texture repeats a single horizontal mark across the silt, while a broad cream stroke separates the dashed footpath from both water and texture. Three circular stops give the route a clear reading order. A pointer ties the parchment ford sign to the middle stop. Recession contours and shallow shelves show how the route fits the basin. A masonry ford crosses the remaining stream between two pools.

## 129 · Tessera Vault

A cut-open gravity relic floats above a recessed gravity field, surrounded by rising chips of stone. Separate mint, amber and ivory faces give the hollow a visible edge. A thick amber border identifies the selected WEIGHT slot. The two other slots use concentric arcs and a notched heat shard so that every entry has a recognisable silhouette alongside its label.

## 130 · Brine Dash

A skewed banner and four slanted bands give the finish board the direction of the race. The fastest sled gets a persimmon lane, and each lane has a sail-sled silhouette. Large fixed-pitch times keep the decimal points aligned. The inset record tab sits beside the units for the signed gaps in the results.

## 131 · Hillwalk Oath

At the first WAIT a walker approaches the hill on a narrow path beneath a subdued sun. After 1.4 seconds, the same sun brightens through a palette update, the hill lifts above the broken crossing, and a single bright disc becomes its eye. The walker recoils. The caption changes with the reveal. Use the renderer’s `--stage 1` to see the opening tableau.

## 132 · Dayglass Relay

Inset sea-glass tiles hold ringed mirror discs. The selected mirror sends the beam upward and out of the board. Four coral corners mark the selection, and a dashed channel traces the route a turn would open to the dormant lens.

## 133 · Drum of Moths

Each winged beat cue uses two native six-cell mosaics. The lanes share the same motif but have distinct inks, matched to their keys. Five strike pads line the bottom of the playfield. The moth at the timing line and the ripples on the struck drum pulse together using BLINK, with steady key lettering below.

## 134 · Terrace Kin

Nine plots rise from a single clay base, with a raised cistern and spillway at the center. The generator paints the distant plots first so the nearer terraces cover their edges. Different polygon colours distinguish the two exposed walls, and wide pel strokes describe irrigation furrows. A sluice feeds the selected plot, where cream shoots preview the next planting.

## 135 · Keel of Thunder

Mirrored facets give the storm machine a steep swept shape, with chartreuse along its main structural edges and a central keel suspended above the player. Each side has an orange charge node inside a dark collar, and both node centres pulse together through a shared BLINK entry. The charge arcs land in collectors held open by the player ship. Floor cables carry the intercepted charge to the arena edges. Nine individually visible health segments sit above the machine.
