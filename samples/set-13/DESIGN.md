# Set 13: design

Ten pictures, 177 to 186, made in one pass of creation and five rounds of improvement. The critiques are in `rounds/round-1.md` to `rounds/round-5.md`; the renders of each round are in `rounds/round-0/` to `rounds/round-5/`. The concepts are in `CONCEPTS.md`.

## 177 Good Morning, Hartley Avenue

A sunrise is built from bands of discs, the outer ring first, so the sun is revealed band by band as the page draws, with a pale halo behind it. The house stands in front, with a lit window, a mailbox at the gate and stepping stones to the door, and the bus is on the road for the menu's last entry. The menu panel is paper under a teal header, with a small mark for each service and a blinking "2 NEW" badge beside MAIL. The date is in the title band. The page's strongest choice is the colour: warm oranges and yellows over a blue sky and green grass, which is what the period's posters promised for a household's morning.

## 178 A Card for Grandma

The card is cream on a plum ground, with a raspberry frame, a row of rosettes in raspberry and gold round the inside, and a dot pattern of blush discs over the paper. The greeting, "HAPPY 70TH," is set one character at a time along an arc, the letters alternating rose and raspberry, with a three-unit pen so the strokes stand out. Three tulips open in turn: a bud, then a rounded cup with three tips and a pale facet, on a stem with slim leaves behind them. A teal bow holds the stems. The price line is a band of plum at the foot. NAPLPS rotates text only in quarter turns, so the arc of single characters stands in for the "rotated italic" the concept names.

## 179 The Family Message Board

The board is a warm cork ground with a dot pattern of darker discs, under a navy header that reads THE FAMILY BOARD. Five notes are tilted by small angles, each with a drop shadow, a pin and its text; MUM's pin is teal and DOUG's is navy, the others red, and JEN's pin is orange and blinks to red. A strip of masking tape holds the top of DAD's note, a red heart is pinned at the top right, and a polaroid of a sky and a hill is pinned under DAD. The text of each note starts below its pin, so no pin touches a word; the notes are set in the stroke font at 12 by 18, the smallest size the page uses and still legible at 480 by 460.

## 180 Supper Tonight

A recipe card on cream under a tomato header, with the title in navy and "SERVES 4 - COOK 25 MIN" beside it. The cutaway casserole is a rounded bowl of blue, with layers from its base upward: a green parsley band, a red sauce, a noodle layer, and a cheese layer with a browned edge and bubbles. Above it three grey steam lines rise to the title's foot without touching it. The timer is a ring of twelve segments, eight of them lit in green and four unlit, with tick marks outside; its hub is cream and carries "25" in navy and "MIN LEFT" beneath. The ingredients have a tick box each, and method step 3 is the current one, on a band of the cheese colour. The timer does not blink, because a blink turns the lit segments red in the still, and the still should read as cooking.

## 181 The Wired Living Room

A flat-colour poster of a sitting room in 1983: a window with curtains and tie-backs, a wall clock and a framed picture, a wooden cabinet television whose screen shows a menu of four services in full, and a rabbit-ear aerial. A green sofa sits behind four people, two adults and two children, each with arms resting on the sofa arm. Three thin pale stripes of window light fall across the wood floor, and a floor lamp with a warm shade stands at the front left. A striped rug lies under a sleeping violet cat with closed eyes and a curled tail, beside a coffee table with a set-top terminal and its infrared keyboard, and a potted plant stands at the far right. The sofa is shorter than the television so that the menu stays whole.

## 182 Neighbourhood Calendar, Maple Ridge Estates

A navy month grid for June, under a teal header that names the estate. Each cell is drawn a week at a time, with the weekend columns tinted pale teal. Coloured event blocks carry a short label on each day (BAKE, LG GAME, PARTY, GARAGE), and a legend in full words sits at the foot, with a swatch for BIN DAY. The weather is marked on three days: a sun with rays on the 3rd, a grey cloud on the 8th and rain on the 16th. Grey bins sit in each Thursday cell, three balloons sit above the block party, and a small orange garage-sale board stands on the 27th. Today's box, the 14th, is outlined in coral, which blinks to red, and reads TODAY. A "COMING UP" panel lists three dated events in full words beneath the grid.

## 183 The House That Orders Its Own Paper Towels

A cutaway house in flat colour: a gabled roof with eaves and a chimney, a sky with a sun of eight rays, and a cut-away section whose edges are shadowed and whose ceiling carries a beam. The pantry has three shelves: tins, paper towel rolls and cereal boxes, each row with a white count tag (x6, x4, x12). A low-stock flag on the paper towel shelf is red and blinks to green once it is delivered, and the terminal on the counter reads STOCK and "1 LOW" in the same colour, so both change together. Three arcs beside the terminal show the order being sent; a window with a blind looks onto the kitchen; a delivery van stands on the lawn at the left, revealed last with WAIT, and a standing order on paper sits under the counter with a green tick drawn last, to confirm it.

## 184 Home Watch

A home-control page for a bungalow, WARDWELL HOME WATCH. The floor plan has five rooms, each a flat fill with its name: living room, kitchen, bedroom, bath and study. Doors are drawn as quarter-circle swings, and windows as blue strips in the outer walls. The thermostat is a half-circle dial from 50 to 80 F, with its needle at 68 F and the figure below. The kitchen has three ceiling lamps, a green ring marks the smoke detector, and the study has a lamp. The porch lamp is a disc with a glow ring, whose entry blinks between yellow and navy to show it switched on and off, and the panel on the right lists five devices with a coloured dot for each, under a line that reads when the house was last checked.

## 185 Tonight's Horoscope

A deep violet ground with sparkles and a crescent moon, and ORRERY DAILY in yellow at the top. The wheel has twelve segments, each in its own palette entry, with the three-letter sign codes at their centres and TODAY in a cream hub, ringed in navy. Twelve planet marks sit on a ring outside it. The reader's sign, LEO, is the segment that blinks to white. The reading panel gives LEO, its dates, a six-line reading in 12 by 18, four lucky-colour chips, and TOMORROW: A QUIET DAY. Sparkles are placed clear of every word.

## 186 School Bus Is Late

A winter bulletin for CROSSRIDGE SCHOOLS. A red band carries ROUTE 14 IS LATE in large type, and "20 MIN LATE" sits beneath it on the sky. The bus stands on a grey road in profile, with a yellow body, a windscreen and door at the front, two of its windows lit from inside, and a red stop arm folded out from its side. A white snowbank lies at the road's edge across its wheels' level. A red octagon stop sign and three children in red, teal and orange coats wait at the roadside. Snowflakes are programmable characters: each is one character in the text stream, drawn from one of two six-armed stars (a large one and a small one), each defined once in the stream, so the page has fourteen of them.

## Notes on the renderer

- **Text needs a font.** The renderer draws no letters without a stroke font; every render here passes `fonts/neoteletext.strokes`, as set 11 does. The validator passes it in both the check and the renders.
- **Programmable characters need their own designation.** A snowflake did not draw until the G3 designation was `ESC + {` (`\x1b+{`), which set 10 uses; the `ESC + }` that the earlier sets use draws nothing for them. Every definition's ink is selected again after its `ESC C ... ESC E` block, and so is each text run's ink, or the renderer takes the background colour.
- **Blink shows one state in a still.** A BLINK changes an entry in the colour map over time, so the still shows its starting state. The pages choose the starting state deliberately, and where a feature must read in the still (the porch lamp, the kitchen lamps), it has a glow ring, so it reads in either state.
- **Rotation is by the quarter turn.** Text can be rotated only in quarter turns, so the arc of single characters on the card stands in for a slanted greeting.
- **Stroke weight is the pen's.** Stroke text takes its weight from the pen width, so the greeting and the name are set with a three-unit pen, and the body text with the default.
