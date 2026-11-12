# Twenty-five NAPLPS designs / 061–085

These pages follow the purposes and visual styles in CONCEPTS.txt. Each has its own composition, palette and typography. All are complete stills: no WAIT and no BLINK. Native Microstar strokes supply every letter. Every stream explicitly designates its character sets, sends `SO 20 7F 7F`, sets four-byte coordinates and defines all sixteen palette entries. The stream ends with END and SO, leaving the drawing set active.

[Contact sheet](out/contact-sheet.png) · [Exact 256 × 200 contact sheet](out/contact-sheet-small.png) · [Manifest](out/manifest.json) · [Validation report](out/validation.json)

All 25 final 640 × 480 renders and their actual 256 × 200 renders were visually inspected. Additional previews are supplied at 320 × 200 and 512 × 400. Changes after review included the arcade title's position, the girih macro's relative origin, the festival caption, the seaside label, the map's closed loop, the tarot numeral and title, the planet ring's occlusion, and the noir title's clear ground. The console texture was revised and rechecked at both sizes. The contact sheets were inspected after these changes.

Twenty-four streams are below 3,000 bytes; every stream is below 6,000 bytes. `validate.py` checks deterministic regeneration, all four image sizes, 7-bit encoding, the RESET, sixteen explicit colour definitions, byte sizes and at most sixteen visible colours. Fifty additional renders compare each page after all 25 predecessors and deliberately altered character-set designations with its standalone pixels, at both 640 × 480 and 256 × 200. All comparisons pass. These are supplied-renderer checks, not PP3 screen captures.

## Renderer observations and workarounds

No confirmed renderer defect or processing-limit warning was found. The definition bitmap records colour index zero as an erased bit (`surface.rs`, `MaskSurface::put`, `entry != 0`). The initial scan-line definition was consequently blank. Page 077 now sends `3E 44` (select entry 1) before `1B 44 41` (DEF TEXTURE A), then defines a broad horizontal band and uses pattern A with `23 60`. This produces visible scan lines at both resolutions. It is documented as an implementation observation, not a claimed standards violation.

The renderer checks full character-field fit at the top of the viewport. An initial 78-pixel field at a 66-pixel baseline caused the arcade title to wrap; its final baseline and field fit. Fine line and mask coverage vary with pixel rounding, so the console uses a filled mask band rather than a hairline. Curved contours in these designs are sampled polylines, not unsupported multi-point ARC splines. Native circles use two-operand ARC instructions. As documented by the project, display-size text may differ from PP3 in placement or thickness; large type is confined to the intentional titles. No renderer source was changed.

## Page notes

**061 — Glenbrae** · [Preview](out/061-glenbrae.png) · [256 × 200](out/061-glenbrae-256x200.png) · [NAPLPS](out/061-glenbrae.nap) · 848 bytes

A full-width green sett is crossed by navy and wine bands, opposing native hatch directions and narrow brass threads. An unframed wool label anchors the lower edge; the fictional clan and large lettering read at terminal size. Techniques: hatching, overlapping textures, palette.

**062 — Eightfold** · [Preview](out/062-eightfold.png) · [256 × 200](out/062-eightfold-256x200.png) · [NAPLPS](out/062-eightfold.nap) · 1,090 bytes

A reusable eight-point girih star tessellates across deep turquoise, joined by small diamonds. The double gold frame encloses a quiet centered atelier cartouche. Geometry is deliberately large enough to survive the smallest preview. Techniques: macro, relative polygons, eightfold symmetry.

**063 — Pressure** · [Preview](out/063-pressure.png) · [256 × 200](out/063-pressure-256x200.png) · [NAPLPS](out/063-pressure.nap) · 5,429 bytes

A mathematically expanded mesh creates a convex lens without shading or colour. Its displaced centre makes the tension asymmetric, while a reversed black title strip gives the eye a stable baseline. Every grid line uses a two-pixel logical pel. Techniques: polylines, nonlinear grid.

**064 — Balance** · [Preview](out/064-counterweight.png) · [256 × 200](out/064-counterweight-256x200.png) · [NAPLPS](out/064-counterweight.nap) · 420 bytes

A heavy black structural grid holds unequal planes of vermilion, cobalt and yellow. The seminar copy occupies the open central white field; the offset blue and yellow weights prevent a symmetric poster. No decorative footer or shared collection furniture is used. Techniques: rectangles, negative space, stroke typography.

**065 — Blue Tide** · [Preview](out/065-blue-tide.png) · [256 × 200](out/065-blue-tide-256x200.png) · [NAPLPS](out/065-blue-tide.nap) · 1,012 bytes

A clawed cream wave curls toward a distant snow-capped mountain. Indigo ribbons sweep across the foreground, leaving warm paper in the sky; a small vermilion publisher seal supplies the only hot colour. The title sits on the paper instead of a common page band. Techniques: layered polygons, polylines, native arc.

**066 — Pantry Pop** · [Preview](out/066-pantry-pop.png) · [256 × 200](out/066-pantry-pop-256x200.png) · [NAPLPS](out/066-pantry-pop.nap) · 1,716 bytes

Four identical Lark soup cans are printed in separate three-entry colour families. Acid yellow, turquoise, pink and violet grounds clash with flat can inks. Palette entries are explicitly redefined at the end, demonstrating indexed recolouring without an animated reveal. Techniques: palette redefinition, indexed colour variations, ellipses.

**067 — Make Tomorrow** · [Preview](out/067-make-tomorrow.png) · [256 × 200](out/067-make-tomorrow-256x200.png) · [NAPLPS](out/067-make-tomorrow.nap) · 548 bytes

An upward thrust of vermilion cuts behind a worker raising a hammer. Stacked headlines, a cream event ticket and a black counter-wedge create three directional forces. The festival details are fictional and sized for the low-resolution display. Techniques: diagonal polygons, silhouette, display typography.

**068 — Odd Room** · [Preview](out/068-odd-room.png) · [256 × 200](out/068-odd-room-256x200.png) · [NAPLPS](out/068-odd-room.nap) · 788 bytes

A lemon-seat chair with a mint-white back floats between pink and lilac diagonals. Native downloadable triangular chips and heavy black squiggles supply the terrazzo setting. A small cream address card balances the oversized off-axis furniture. Techniques: DRCS, squiggle polylines, axonometric polygons.

**069 — Vespera** · [Preview](out/069-vespera.png) · [256 × 200](out/069-vespera-256x200.png) · [NAPLPS](out/069-vespera.nap) · 1,139 bytes

A single ivory lily grows above an angular perfume bottle. Mirrored whiplash stems form an organic frame, with sage leaves and dull gold outlines on a deep green ground. Open space around the large name keeps the advertisement poised at small size. Techniques: curved polylines, botanical polygons, proportional text.

**070 — Void Patrol** · [Preview](out/070-void-patrol.png) · [256 × 200](out/070-void-patrol-256x200.png) · [NAPLPS](out/070-void-patrol.nap) · 626 bytes

Three chunky six-cell-mosaic invaders face a gold player ship beneath a cyan and magenta title. Sparse stars and one laser leave generous dark space. The title screen is complete as a still; no essential instruction blinks. Techniques: mosaics, large text fields, points.

**071 — Astor River Bridge** · [Preview](out/071-astor-bridge.png) · [256 × 200](out/071-astor-bridge-256x200.png) · [NAPLPS](out/071-astor-bridge.nap) · 1,290 bytes

A white Warren-truss footbridge spans a faint cyan construction grid. Piers, deck and a single dimension are distinguished by line weight. A conventional bottom-right revision block and measured title make this a technical sheet rather than a decorative landscape. Techniques: polylines, dimension lines, logical pel.

**072 — The Crow and the Pitcher** · [Preview](out/072-crow-pitcher.png) · [256 × 200](out/072-crow-pitcher-256x200.png) · [NAPLPS](out/072-crow-pitcher.nap) · 1,213 bytes

A black crow drops a stone into a heavy jug. White cuts through its wing and cross-hatching in the pitcher evoke carved wood; scattered stones and a rough ground link the two silhouettes. The moral forms a single legible line below the illustration. Techniques: hatching, silhouette polygons, engraved lines.

**073 — Lumen** · [Preview](out/073-lumen-window.png) · [256 × 200](out/073-lumen-window-256x200.png) · [NAPLPS](out/073-lumen-window.nap) · 1,447 bytes

Twelve lancet petals surround an eight-point central star. Dark gaps act as lead came between ruby, teal, amber, sapphire and violet glass. A gold perimeter and repeated pale lozenges produce a bright outer ring without relying on hairline detail. Techniques: radial polygons, native circles, eight-point star.

**074 — Orbit Diner** · [Preview](out/074-orbit-diner.png) · [256 × 200](out/074-orbit-diner-256x200.png) · [NAPLPS](out/074-orbit-diner.nap) · 2,942 bytes

A freestanding pink and mint tube sign hangs against subdued charcoal brick. Four offset dark impressions suggest a neon halo, while an orbital badge crowns the sign. The open-all-night line remains fully lit in the final still; no cycling obscures the diner name. Techniques: stroke overprinting, brick line texture, native arc.

**075 — One Cat** · [Preview](out/075-one-cat.png) · [256 × 200](out/075-one-cat-256x200.png) · [NAPLPS](out/075-one-cat.nap) · 602 bytes

One uninterrupted incremental-line instruction traces a seated cat from the tail through the ears, paws, eyes and whiskers. A two-pixel step keeps the drawing compact and the mark visible at terminal resolution. Large paper margins and an understated copper caption preserve its restraint. Techniques: incremental lines, single continuous path, proportional text.

**076 — Salt Afternoon** · [Preview](out/076-salt-afternoon.png) · [256 × 200](out/076-salt-afternoon-256x200.png) · [NAPLPS](out/076-salt-afternoon.nap) · 2,808 bytes

More than five hundred native POINT marks scatter cool and warm pigment across sea, sand and a tree canopy. A tiny cream sail and striped parasol give the loose dots a readable scene. A pale upper-right card carries the title clear of the stippling. Techniques: POINT, large logical pel, deterministic stippling.

**077 — Morrow System Console** · [Preview](out/077-morrow-console.png) · [256 × 200](out/077-morrow-console-256x200.png) · [NAPLPS](out/077-morrow-console.nap) · 869 bytes

A fictional node reports uptime, link speed and free memory in large fixed-pitch fields. A native defined texture lays faint phosphor scan lines over the black-green ground. Explicit colour-mode-2 fields reverse the all-systems-nominal message, and a segmented receive meter provides a single compact graphic. Techniques: defined fill pattern, colour mode 2, fixed-pitch text.

**078 — The Amber Road** · [Preview](out/078-amber-road.png) · [256 × 200](out/078-amber-road-256x200.png) · [NAPLPS](out/078-amber-road.nap) · 1,089 bytes

Four camel riders cross rose and terracotta dunes beneath an oversized pale sun. Each silhouette is a single cut shape, with connecting reins and varied scale forming the caravan. The dark foreground absorbs the travel caption, leaving the warm sky open. Techniques: layered polygons, silhouette, native circles.

**079 — Fox Ridge Loop** · [Preview](out/079-fox-ridge.png) · [256 × 200](out/079-fox-ridge-256x200.png) · [NAPLPS](out/079-fox-ridge.nap) · 2,240 bytes

Warm brown contours surround a crooked red hiking loop beside a blue-green creek. Large trail endpoints, summit elevation and a simple north arrow carry the practical information. Paper label patches keep names legible above the contour field; the native dashed path uses an explicit logical pel. Techniques: contour polylines, dashed line texture, native points.

**080 — The Star** · [Preview](out/080-the-star.png) · [256 × 200](out/080-the-star-256x200.png) · [NAPLPS](out/080-the-star.nap) · 1,467 bytes

An ivory card floats on midnight blue. Eight celestial emblems surround a kneeling figure pouring two gold vessels toward water and earth. Corner diamonds, an inset rule and Roman numeral complete the card without making its symbolic scene depend on small ornament. Techniques: star polygons, figurative silhouette, border ornaments.

**081 — Elin Vale** · [Preview](out/081-elin-vale.png) · [256 × 200](out/081-elin-vale-256x200.png) · [NAPLPS](out/081-elin-vale.nap) · 2,338 bytes

A sage profile portrait of the invented field naturalist Elin Vale is engraved with coarse coat and hair cuts. Circular edge perforations, an oversized 80 denomination and a double keyline make the composition unmistakably postal. The name, dates and Aurelia Post service are fictional. Techniques: perforated native circles, portrait polygons, engraved lines.

**082 — Side Street** · [Preview](out/082-side-street.png) · [256 × 200](out/082-side-street-256x200.png) · [NAPLPS](out/082-side-street.nap) · 629 bytes

An ink-blue saxophonist is tightly cropped against a darker blue ground, while a cream left column holds the sleeve typography. The bell and bent arm give the music a diagonal movement. A native supplementary acute accent prints the fictional venue name Café Sable. Techniques: supplementary accented letter, duotone silhouette, display typography.

**083 — Orbits of Glass** · [Preview](out/083-orbits-of-glass.png) · [256 × 200](out/083-orbits-of-glass-256x200.png) · [NAPLPS](out/083-orbits-of-glass.nap) · 943 bytes

A huge ringed planet cuts through seven horizontal bands of muted sunset ink. The tiny traveller supplies scale beneath an oversized two-line title. A dark author strip closes the paperback cover; the stepped colours are palette bands, not a raster gradient. Techniques: palette stripe gradient, native circles, elliptical polylines.

**084 — Last Tram at Midnight** · [Preview](out/084-last-tram.png) · [256 × 200](out/084-last-tram-256x200.png) · [NAPLPS](out/084-last-tram.nap) · 787 bytes

Cream shafts of blind-filtered light cut across a faceless detective in a wide-brimmed hat. Grey lapels describe the coat without illuminating the face. A red title accent and Friday release label punctuate the otherwise monochrome cinema poster; all credits are invented. Techniques: high-contrast polygons, silhouette, red accent.

**085 — Valenne** · [Preview](out/085-valenne.png) · [256 × 200](out/085-valenne-256x200.png) · [NAPLPS](out/085-valenne.nap) · 631 bytes

A red skier descends a broad cream snowfield beneath two sharply faceted peaks and a pale sun. Glacial blue layers describe distance, while the large resort name sits in a deep-blue station-style base. The fictional rail destination and winter date give the poster a period travel purpose. Techniques: flat mountain polygons, skier silhouette, display typography.
