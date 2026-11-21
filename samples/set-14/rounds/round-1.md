# Round 1

Critique of the round-0 renders (`rounds/round-0/`), looked at at 640 x 480 and 480 x 460.

## Critique

**187 The Electronic Catalogue.** Composition is clear (three equal panels, price star, key, prompts) and the red, yellow and navy feel like a 1983 shopping page. The sneaker is the weak panel: a tangle of blue shapes with no readable silhouette. The band under the panels is wasted space with one centred line. The order keys are the only blinking element and the period object that makes the promise, the viewer's keypad, is missing. Text is legible at 480 x 460.

**188 Your Balance, Mrs Okafor.** The statement reads well and the vault door's four-step opening is a good use of WAIT. The vault interior is a grid of drawers that looks like a spreadsheet and runs outside the circle; the left half has nothing to say beyond the door. The statement has dead space under the bills.

**189 Build Your Credit.** The strongest composition of the set: sequential build, climbing figure, slogan last. Weaknesses: the figure is tiny and appears at only four steps, the coins are flat repeats, and nothing sparkles when the climb ends.

**190 The Showhome on Cedar Crescent.** The elevation is charming. The floor plan is an empty diagram: rooms are coloured boxes with centred labels and no furniture, so it does not look like a plan someone could use. The spec lines are three plain text rows and the price star's blink makes the page number and sun go dark in the still.

**191 Classifieds: Bicycles.** The drawn ten-speed is convincing; the list is legible. The ads have nothing visual beside the lettered key, so the page is a bike and a table of text. The highlighted ad's blink made its letter disc and marker vanish in the still (fixed during round 0, but the disc is still a plain circle).

**192 Going Once, Going Twice.** The colour-map seven-segment counter is the best idea in the set and works at all three stages. The right column below it has a single bidder line that never changes, the clock is a flat disc with no glass or depth, and the gavel is a floating shape.

**193 Grocery Order.** The cart is nearly empty above its rim: items are hidden behind the front mesh and the picture does not read as groceries. The list and the running total work.

**194 Theatre Tickets.** The seat plan is accurate and the blink pair is clear. The stage is a dark smudge: the "NOW PLAYING" text sits on a pale beam and cannot be read, and the opening curtain reveals nothing worth opening for. The row letters were misaligned in round 0 (fixed).

**195 The Mall Directory.** A clear kiosk page; the touch keys read well. Legend names run to the screen edge at 640 and are cut at 480; the YOU ARE HERE label turns dark-on-red in the still. The plan is blocks only: no fountain, no route, no sign of what touching a key does.

**196 Today's Special.** The expanding ad band and the SALE starburst chase are good. The first stage (the article) is plain. The band has no picture of the thing it advertises.

## Changes planned, two or three per page

- 187: redraw the sneaker as one readable high-top; add the viewer's keypad with keys 1 to 3 lit; use the band for the account line.
- 188: redraw the vault interior as shelves of gold bars, money bags and boxes clipped to the circle; add a six-month savings chart to the statement.
- 189: climb every step with a figure half as large again; stamp the coins; add sparkles that blink along the stair.
- 190: furnish the plan (beds, tub, sofa, table, counter); add icons to the spec line; move the labels to the foot of each room.
- 191: define six small bicycles as DRCS characters and set one beside each ad.
- 192: turn the single bidder line into a bid ladder whose lines light with the same colour-map entries as the counter; add glass reflection and plinth ornament to the clock.
- 193: scale the items 1.3 times, lift the rim, move the cart down so the load shows above the mesh.
- 194: draw a railway platform set with an engine, lamp and clock; put the title on a gold plaque; halo the chosen pair.
- 195: shorten legend names to fit; add a fountain, planters and a dotted route to the touched store; show key 5 pressed.
- 196: add a DRCS drill icon to the band, numbered discs to the article steps, a spiral bit.

## Done in round 1

All the planned changes were made; `validate.py` passes at both sizes.

- 187: sneaker redrawn as a single scaled high-top; keypad drawn in the band with keys 1 to 3 lit.
- 188: vault interior rebuilt (three shelves, bars, bags, boxes, all clipped to the chamber); savings bar chart in the statement.
- 189: the figure, scaled 1.5 times, climbs all seven steps; coins carry a thistle mark; blinking white sparkles on the upper coins.
- 190: plan furnished, door swings drawn with arcs, labels at the foot of each room; bed, tub and house icons in the spec line.
- 191: six DRCS bicycle characters, one per ad. This also taught the encoder that DRCS needs `ESC + {` into G3 (the plate writer's default `}` is a mosaic-like set) and that a definition leaves the pel and colour changed.
- 192: bid ladder lit with the counter's colour-map entries; reflection arc, column highlights and plinth scrolls on the clock.
- 193: items drawn through a scaling proxy at 1.3 times, cart geometry lowered.
- 194: platform set (engine, smoke, lamp, clock), gold title plaque, blinking halo round the chosen pair.
- 195: legend shortened, fountain and planters on the upper floor, dotted route to store 5 with its key shown pressed, YOU ARE HERE blinking white and butter.
- 196: DRCS drill icon in the band, numbered discs, spiral-flute bit.
