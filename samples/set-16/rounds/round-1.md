# Round 1

Looked at every page's renders at 640 × 480 and 480 × 460 (round-0). Text sizes had been fixed before the first
page from a test chart: at 480 × 460 a field under 20 units high gets a one-pixel pen and reads thin, and a
field under 16 wide clogs the counters of small letters under the two-pixel pen, so the smallest size used
anywhere is 16 × 20.

## Critique

**207 Grain Prices at the Elevator.** The sunset bands and the elevator read at once and feel like a farm
service's page. But the sun is hidden behind the hopper cars, so the picture's brightest thing is lost; the
decimal point of each price is a single low dot squeezed by proportional spacing, and "4.18" reads as "418" at
480 × 460; and the board is only a list, when a line drawn from a few numbers is what this medium does well.
Changes: (1) a drawn decimal point and larger price figures; (2) an eight-day trend line for each grain;
(3) the sun moved clear of the train, with geese and a waiting grain truck for life.

**208 Spraying Weather.** The striped field made with a defined fill pattern is the best thing here. The board
below is weak: a thin verdict stripe that is easy to miss, a hole between the wind figures and the rain bars,
bars with no scale, and bold type that clogs in the verdict line. The tractor is a toy. Changes: (1) each hour
becomes a card headed in its verdict colour; (2) rain becomes a gauge with a scale to 100 per cent and a half
mark; (3) the sprayer redrawn with wheels, a tank, a driver and mist that leans downwind.

**209 The Farm Kitchen.** The idea carries, and the green screen is the focus. The drawing is crude: the stove
stands in front of the window, the steam crosses the glass, the coffee pot is a red wedge, and the farmer is a
blue block with a head and no arms. Changes: (1) the wall rearranged, stove and calendar left, window centre,
set right, clock above the set; (2) the farmer given braces, a plaid back, an arm and a mug, behind a proper
chair; (3) a speckled pot with spout and handle, a geranium, a yard light, and a dog asleep by the counter.

**210 Flight Briefing.** Legible and plausible, but thin for a chart: no ceilings are given though the legend
is about ceilings, the cloud deck is a hard-edged grid, the north arrow sits in the cloud, and there is no
graticule. Changes: (1) each airfield gets a plate with its ident and its ceiling in feet, edged in its state
colour; (2) the cloud deck gets a bank of solid lumps along its edge; (3) a dotted graticule (line texture with
a real pel) and the north arrow moved to the sea.

**211 Lesson Four: Fractions.** Clear, and the blackboard is a good frame for programmed learning. The pie is
a flat disc with a sliver of cream showing outside the orange wedge (the wedge polygon was coarser than the
circle), and the marking is abrupt: a tick and a line of text. Changes: (1) the wedge drawn finely and the pie
given a crimped crust and a shadow; (2) the marking now counts the slices, 1, 2, 3, one at a time, before it
says "3 of 8".

**212 The Classroom Terminal.** The crowd of backs works, and the raised arm. The teacher is a purple cone
without a face; the window's sky is the map's sea blue and far too dark; one hairstyle draws a skin-coloured
slab across the head; the blink was on the white entry, which would have flashed the clock and the cards too.
Changes: (1) the teacher redrawn in profile with glasses, bun, cardigan, skirt, legs and a lesson book; (2) a
light sky entry for the window, with clouds; (3) alphabet cards along the wall, a child in a cap, and a marker
of its own on the map where the pointer rests, which is what blinks.

**213 Book Your Holiday.** The strongest page: bands, wave pattern, sticker. The palm is four kites on a stick,
and the sky is empty. Changes: (1) palms with curved, cut fronds, and a second, smaller palm; (2) gulls and an
incoming airliner with its trail; (3) the price on a starburst, and small aircraft marking the flights out and
back.

**214 Vote on the New Library.** Reads as a civic notice, and the tally bar is right. "LIBRARY" in bold on the
frieze is clogged at 480 × 460; the voter is told nothing about cost; and nothing shows that a vote was cast.
Changes: (1) the frieze lettering unbolded in a darker ink; (2) a cost line under the question; (3) the pressed
key ringed and ticked before the count arrives, lamps and two townspeople on the steps for scale.

**215 Working from Home.** Charming, but the caption band cuts off the blocks and the child, the parent's legs
vanish into it, and the wall is bare between window and shelf. Changes: (1) the rug, blocks and child moved up
clear of the caption; (2) the parent given collar, cuff, glasses, an ear and a chair that stands on the floor;
(3) a wall clock at 9:15, a framed certificate, the telephone cord into the terminal, papers, a mug, a bear.

**216 The Community Health Page.** Friendly and clear. The handset looks like headphones; the timeline is a
general chart when the promise of the medium was a page about *your* child; the building has no name. Changes:
(1) a real handset; (2) the timeline made personal: "Anna's shots", doses given solid and doses to come as
rings, her age's column ringed and flashing; (3) CLINIC on the fascia, the sign on a post, sun and cloud.

## What changed

- **207:** prices set larger with a drawn square decimal point; an eight-day trend line and end dot per grain;
  sun moved to the right with the furrows' vanishing point; geese; grain truck; time of the close added.
- **208:** hour cards headed in verdict colours; rain gauges with a scale; sprayer redrawn; "TUES" row label;
  bold removed from the hour labels and reduced in the verdict.
- **209:** wall recomposed; farmer redrawn with arm, mug, braces and chair; new coffee pot, pan, geranium, yard
  light, dog; screen given a heading row.
- **210:** ident-and-ceiling plates; lumped cloud edge; dotted graticule; north arrow moved. The kit's
  `pattern()` gained line textures.
- **211:** fine wedge, crimped crust, shadow; counted slices in the reveal.
- **212:** teacher redrawn; sky entry and clouds; alphabet cards; cap; map marker with its own blinking entry.
- **213:** new palms (two), gulls, airliner and trail, starburst price, flight icons.
- **214:** frieze lettering; cost line; ringed and ticked key; lamps and figures; foot line now says the vote
  is in.
- **215:** floor group raised; parent and chair redrawn; clock, certificate, cord, papers, mug, bear.
- **216:** handset; personal timeline with given and to-come doses and a flashing column; fascia name, post
  sign, sun and cloud.

`validate.py` passed: 10 pages, all checks.
