# Round 2

Critique of the round-1 renders (`rounds/round-1/`), looked at at both sizes.

## Critique

**187.** The sneaker now reads, and the keypad helps the scene feel like a household terminal. But the three illustrations float on flat colour fields: toaster, radio and shoe have no setting, so the three panels feel like clip art. The page still has one blinking element and nothing signals novelty. Text is legible.

**188.** Statement and vault are both good, and the shelves read. The left half is still a dark green slab with a drawn object on it: the opening of the vault does not change the page. The caption is plain text.

**189.** The figure climbs every step and the stair sparkles. The scene has no place: a flat sky and a bare stair. The coins stand on a line with no shadow.

**190.** The furnished plan is a real improvement. The page is still static after the last stage; a house shown "at home" has no sign of life; the mortgage line states a rate but not what it costs a month, which is the figure a buyer wants.

**191.** Icons per ad work. The area to the right of the bike is blank, and the bike floats on flat slate.

**192.** The ladder lights in step with the counter. The page header has no sign of the other bidders, and the gavel is a floating shape and clipped when scaled.

**193.** The cart is full and legible; the list has no visual confirmation that an item was taken (a tick), unlike the cart.

**194.** The platform set works and the plaque is legible. The seat plan is a flat grid: a hall has curved rows, and a flat grid reads as a spreadsheet.

**195.** Clear. The legend has numbers and names only; a kiosk for shoppers would show what each shop sells. At 480 the longest legend name touches the edge ("HEELS & SOLES").

**196.** The best page. The rising band and the chase are good. The background is a plain dark hatch, which does nothing for the starburst.

## Changes planned

- 187: set each product in a setting made with fill patterns, one of them a user-defined tile; a blinking NEW star on the radio.
- 188: a sunburst of rays behind the vault that appears as the door opens; a brass plaque for the caption.
- 189: a pale town skyline behind the stair, repainted when the figure's strip of sky is cleared; ground shadows and grass.
- 190: the monthly payment; the windows light up at the end by a palette change.
- 191: a dashed-edge coupon for placing an ad; faint rays behind the bike.
- 192: an eye DRCS character and "212 WATCHING" in the header; a redrawn, smaller gavel on its block.
- 193: a DRCS tick beside each item, placed as the item arrives.
- 194: rows bowed toward the stage so the hall fans around it.
- 195: ten DRCS shop icons in the touch keys; shorter names.
- 196: radial rays from the starburst across the whole picture.

## Done in round 2

All planned changes made; `validate.py` passes.

- 187: kitchen-tile pattern (a user-defined DEF TEXTURE tile) behind the toaster, stripes behind the radio, track lanes behind the shoe; blinking NEW star; the ring and star blink to red.
- 188: twenty-wedge sunburst clipped to the left half drawn as the door opens (new `rays` and polygon clipper in the kit); brass plaque.
- 189: skyline of twelve buildings with a function that repaints it over cleared sky; shadows and grass tufts.
- 190: 13.25% fixed, about $876 a month; a fifteen-tenth wait, then the window entry changes to lit yellow.
- 191: dashed-edge coupon (line texture) and rays behind the bike; the bike moved right so its wheel is no longer cut.
- 192: DRCS eye and "212 WATCHING"; the gavel rebuilt on a block, scaled 1.1 and moved clear of the prompt band.
- 193: DRCS tick set with each list line.
- 194: rows bow toward the stage by sixteen pixels at the ends; plan lowered to fit.
- 195: ten DRCS shop icons (book, shoe, train, record, sandwich, coin, camera, envelope, flower, cup); names shortened to one word or two.
- 196: radial wedges replace the vertical hatch.
