# Videotex as its makers dreamed it: entertainment, games, arts and messaging · 217–226

[Contact sheet](out/contact-sheet.png) · [Manifest](out/manifest.json) · [Concepts](CONCEPTS.md) · [Rounds](rounds/)

Group E of the videotex research: what the period promised the terminal in the living room would be for once the news and the bank had been read. Every page begins with a full RESET, designates G0 ASCII, G1 PDI, G2 macros and G3 programmable characters (DRCS), sets DOMAIN to four-byte coordinates, and defines all sixteen colour-map entries before drawing. Every service, brand, place and person is invented. Pages are drawn on a 640 × 480 design canvas by `pages/_screen.py` over the encoder in `encoder/` (copied from set 11 and extended in `_screen.py` with programmable characters, rotated characters, fill patterns, macros and mosaics). Text is at least 12 × 18 canvas units almost everywhere (11 × 16 nowhere), checked at 480 × 460.

Run `python3 set-17/validate.py --build` from `samples/` to regenerate the streams, PNGs, contact sheet and manifest, and `python3 set-17/validate.py` to check that they are up to date. It generates each page twice and requires identical bytes, checks 7-bit, the reset and designations and the sixteen colour-map definitions, runs the renderer's `check`, renders at 640 × 480 and 480 × 460, and requires a page that WAITs to differ between its first stage and its end and a page that BLINKs to change with time. `rounds/round-0` to `round-5` hold the renders after creation and after each of five improvement rounds; `round-N.md` holds each round's critique and changes.

## 217 · Chess by Wire

A correspondence game between households in two invented towns. The board is two rows of rectangles per rank in parchment and felt green inside a wooden frame with a gold inlay; the pieces are six programmable characters, each drawn five times (four offset passes in the opposite colour, then the piece) so they hold a hard edge on either square. The board arrives rank by rank, the pieces after a WAIT, and after a longer WAIT the opponent's move lands: d3 and c4 light, the bishop is set down on c4 and an arrow is drawn with a head computed from the move's direction. The panel shows the two households joined by a telephone line with an envelope on it, and each side's captures as the same pieces at a fifth of the size. The envelope is a macro of relative RECT and LINE commands, played on the wire and again by "# SEND". The last move and the reply cursor blink; the reply deadline is five day pips.

## 218 · The Maze

A first-person dungeon of the invented Questline service. The corridor is four cross-sections joined by ceiling, floor and wall polygons in three graded wall entries, with converging mortar courses and staggered joints, ribs vaulting the ceiling, a side passage on each side (a shadowed facing wall and a corner pillar), and a glowing door at the end. Light is a dot pattern programmed once with DEF TEXTURE and used as fill pattern 4, both for the pool before the door and the torch's light on the wall; the flame flickers by two BLINKs; a key's glint and a pair of eyes in the left passage share a third. The panel has a compass rose, a mosaic map generated from a 12 × 9 grid of corridor cells, and one arrow character set with TEXT rotation at 90, 0 and 270 degrees for "4 LEFT · 8 AHEAD · 6 RIGHT" (a turned character pivots on its lower left corner, so each is shifted back into its cell).

## 219 · Quiz Night

The evening quiz of the invented Brainwave service. A yellow question card with a Q7 badge and a drawn globe, four answers in their own colour-map entries on drop-shadowed buttons, ten progress pips (right, wrong, current, to come). A dial of ten sectors drains by WAIT, one overdrawn sector a second; then the reveal is done by the colour map alone: the three wrong answers' entries are redefined to grey and the right answer blinks pink against green, a banner names it, sparks burst round it and the score is redrawn with "+10". The foot band says how many homes are playing.

## 220 · Gallery Page: Harbour at Dusk

A gallery picture after the period videotex painters, built from several hundred flat shapes in the order a viewer would watch them arrive: sky bands (ellipses 1.8 times wider than high round the sun) and lit cloud strata, the sun, hills, a sea with a glitter road whose first rows are in the sun's own entry, a steamer on the horizon, long swell drawn as INCREMENTAL LINEs (two bits a step), the gabled town with chimneys and smoke curls, quay lamps, the pier and reflections, the faceted rock and lighthouse with gallery rail, three sailing boats with stays and pennants, a rower, gulls. Then dusk falls in three WAIT steps of SET COLOR, gold to violet; on the last the windows, stars, quay lamps and portholes (all one entry) light together. Two lighthouse beams in their own entries blink into the sky's colour in turn, so the light sweeps.

## 221 · The Lace Picture

A decorative piece: a twelvefold medallion of lace on a basket-weave cloth (a fill pattern programmed with DEF TEXTURE). Rings are revealed one per WAIT: a two-layer rosette, a threaded bead ring in gold and cream, lozenges with cut-outs and gold diamonds, scallops of filled arcs, teardrops with holes and ice picots, and a picot edge of forty-eight loops with gold beads on the axes. Radial thread bars join the rings and two running-stitch circles use the dotted line texture with a two-unit pel. Each ring has its own colour-map entry, and six BLINKs with staggered delays send gold light running outward ring by ring. Lace corners and a gold-ruled cartouche frame it.

## 222 · Story Time: The Garden

A children's story page of the invented Bedtime service whose picture grows as it draws: soil in cross-section with stones and a worm, then the seed and roots, the shoot, the stem and leaves, the bud; the petals are drawn while their entries still hold the sky's colour, so one pair of SET COLORs opens the flower; then a bee arrives along a dotted path. Wren kneels with her watering can, a cottage and picket fence stand on the far hill, the sun has a face, grass tufts edge the soil and a snail crosses it. The text panel has a drop capital and two lines of proportional text; page dots show page 3 of 5.

## 223 · The Chat Line

A late-night room of the invented Parlour chat service, the use the period's users wanted most. Seven programmable badges (moon, cedar, cat, owl, pipe, star, heart) mark each member in the list and each speaker in the conversation; lines arrive one per WAIT, each with its time. A private message from one member sits in its own lilac panel with a heart and three rising musical notes (a programmable note at three sizes), which blink. A night window with curtains closes the member column, and the reply being typed ends in a blinking cursor whose entry is the input line's colour until BLINK lends it white.

## 224 · The Face Maker

A face kit of the invented Phizkit service, played by number and sent on as a card. In a photo booth with pleated curtains, a scalloped valance and polka-dot wallpaper (a programmed fill pattern), the face is drawn part by part, a WAIT between each: shoulders and collar, head and ears, curls, eyes and brows, nose and freckles and cheeks, the smile, a party hat, and a speech balloon "HI GRAN!". The menu lists the six parts with their current numbers and a programmable icon each; the part being changed flashes; three numbered mouth thumbnails show the choice framed in gold.

## 225 · Download Tonight's Program

Telesoftware from the invented Homebyte service: a broadcast mast with its hut sends a program across a town of houses with rooftop aerials, as a stream of digits drawn one per WAIT along an arc, to a home computer on a desk with a mug of cocoa, whose screen shows the listing arriving. A floppy disk and a cassette, tonight's program card, and a progress bar of mosaic blocks filled one frame per WAIT to 14 of 30, with a blinking receiving lamp.

## 226 · New Year's Eve 1990

The service's makers imagining their own future: the invented Citylamp service greets a new decade. A countdown of 3, 2, 1 is drawn and erased in the empty sky; then the skyline in two rows of lit towers, a clock tower at midnight, a bridge of filled-arc arches, a crowd in silhouette against the water's glow; five bursts of lines, each in its own entry; a greeting on a ribbon and the year with a drop shadow. Five BLINKs with different partners and beats cycle the bursts (and their reflections in the river) through each other's colours, the windows flicker and the stars twinkle.

## What the renderer showed

- A BLINK begins in its ON interval, showing the partner entry, so a still render shows the partner's colour: blink partners were chosen so the still reads correctly (the cursor in 223 is defined dark and blinks to white).
- A programmable character turned by TEXT rotation pivots on its lower left corner (90 degrees moves it one cell left, 270 one cell down); 218 shifts each arrow back.
- Proportional text overlaps a doubled "!!"; the pages use a single "!".
