# Set 15 · Improvement round 1

## Critique of the round-0 renders

Every page was looked at rendered at 640 × 480 and at 480 × 460. Byte counts are the round-0 streams.

### 197 · The Electronic Front Page · 1,386 bytes

Clean and legible at both sizes, but it reads as a menu, not a newspaper: three equal rows give no story more weight than another, and the 120 × 84 icons are small. The masthead is type alone, and "THE" sits as a small orphan in the corner at 480 × 460. Of NAPLPS it uses rectangles and polygons and one BLINK; the build order (story by story) is the best idea on the page. Nothing is broken.

- Give the lead story the top half with a large drawing and display headline; set the other two stories side by side below it.
- Give the masthead a drawn device and a weather "ear", as a paper's front page has.

### 198 · Weather Map of the Westmark · 1,838 bytes

The map reads at once as a forecast map and the programmable weather symbols are the right technique, but the symbols are small, the town names sit loose on the hatched farmland where the hatching crosses the letters at 480 × 460, and Pellham's name runs into the cold front. The warm front's semicircles sit on the north side; a front's marks belong on the side it moves toward. The provincial line cut through Tasker's temperature tag.

- Put each town's name and temperature together on a solid chip, with its symbol above the dot.
- Move the fronts clear of the towns and put their teeth and semicircles on the leading side.

### 199 · Storm Warning · 1,134 bytes

The strongest bulletin of the set: TORNADO WATCH in alarm red, the time in amber, the instruction in white, all clean at 480 × 460. The sky is one flat green with a row of lighter discs that read as balloons, not cloud, and the bolt simply blinks on a static sky. The lower landscape is empty.

- Build a real storm sky: a ragged cloud deck, a shelf cloud with a lit underside, mammatus pouches.
- Make the lightning a colour-map event: the bolt's own colour is the sky's, so it is invisible until BLINK strikes it, and the whole sky flashes on the same beat.
- Put a car with its headlights on the road for scale.

### 200 · Market Close · 2,228 bytes

Convincing and the densest information page: the index line, the hour-by-hour reveal and ten shares in two columns are all legible. The axis figures are thin grey at 480 × 460. The chart's fill is a single hatch over black and looks thin; nothing on the chart tells the story of the day.

- Larger, brighter axis figures.
- Hatching over a solid fill, for a two-tone area under the line.
- Flag the day's low and the high close on the line.

### 201 · Last Night's Scores · 1,561 bytes

The pennants and the wooden line-score board are strong period images, and the figures are clean. The ballpark has no crowd and the score itself is only in the table. The blinking highlight of the tenth inning was invisible in the still because BLINK starts by showing the other entry's colour. (Round 0 corrected the innings so they add to the totals.)

- Fill the stands with a crowd made of two defined dot textures.
- Put the final score on the pennants, with FINAL and the innings.
- Light the whole tenth-inning column with an entry that keeps the board's colour and blinks to orange.

### 202 · The Community Almanac · 1,942 bytes

Clear statistics, credible as a government page; horizontal bars (round 0 replaced vertical bars whose rotated names did not fit) read well. It is plain: nothing in it is particular to NAPLPS except the pie's hatching, and nothing says "community".

- Replace the bars with isotype rows: one programmable figure for every thousand people, repeated with REPEAT.
- Explode the largest wedge of the pie.

### 203 · Ask the Encyclopedia: Volcanoes · 1,517 bytes

The layered cone and labelled leader lines are the textbook look wanted, and the eruption after a WAIT is good use of time. But the lava flow floats above the flank as a separate slab, the magma chamber is a flat ring, and the ash column is a small cluster of discs.

- Lay the lava flow along the surface of the flank, down to the plain.
- Give the magma chamber an irregular shape, a hot heart and feeders.
- Raise a bigger ash column with falling ash drawn as hatching.

### 204 · City Directory: Hotels · 1,912 bytes

A good directory: the dusk skyline whose windows all light at once by a colour-map change is a perfect videotex moment, and the table is orderly. The addresses are thin grey and just legible at 480 × 460; the stars are tiny; the skyline and the table do not connect.

- Darker, larger address text and larger stars.
- A vertical HOTEL sign on one tower, written on a downward text path and flashing with the last-room dot.

### 205 · Your Own Newspaper · 2,006 bytes

The idea comes through: one reader's chosen topics as coloured folders. Round 0 gave the NEW marker its own entry after the first version blinked every tomato and roof. The masthead is type only, and the curling icon is a confusing set of rings.

- Add a rose and the reader's monogram to the masthead.
- Redraw the curling icon as a stone at rest on the house, seen from the side.
- Put the NEW tag on the stock-club folder itself.

### 206 · The Night Sky Tonight · 2,374 bytes

The domed sky in concentric bands over a roofline is the most atmospheric page; twinkling by three staggered BLINKs works. The Moon's craters are odd blobs, "9 days" and the compass points are in a dim blue that is hard to read at 480 × 460, and the scene has no one in it.

- Put a neighbour at a telescope in the garden.
- Leader lines to the planets, brighter and larger labels and compass points; remove the craters.

## What changed

- **197**: lead story redrawn as a 300 × 160 picture of city hall on its hill with the approved bridge drawn dashed across the harbour (a planned structure), a three-line display headline and a kicker; two secondary stories side by side; masthead device (gull over waves) and a weather ear with a drawn sun. The harbour water got its own entry after the first try blinked it red with the LATE tag. 1,970 bytes.
- **198**: towns carry cream chips with the name and a coloured temperature end (red-orange at 25 and over, blue below); symbols enlarged to 64 and centred above each dot; Orrin moved east; the cold front moved west of Orrin with its teeth turned to the south-east; the warm front's semicircles moved to its south side. 1,904 bytes.
- **199**: cloud deck with lumpy base, a shelf cloud with a lit underside, mammatus pouches; the bolt's entry now holds the sky colour and BLINK lights it cream while the sky entry flashes to the horizon green on the same beat; a road and a car with headlights. 1,360 bytes.
- **200**: axis figures 13 × 20 in cyan (a first try used the blinking close-marker entry and the figures vanished); the area under the line is a solid dark green with green hatching over it; orange LOW and green HIGH CLOSE flags with leaders. 2,572 bytes.
- **201**: stands filled with fans by two defined dot textures in cream and blue over dark terraces; the field redrawn below them; pennants carry 5 and 3 with FINAL 10 INN beneath; the tenth-inning column is a board-coloured entry that BLINK turns orange. 1,728 bytes.
- **202**: isotype rows of a DRCS figure, one per thousand people, drawn with REPEAT, Brackwater's in red; key "= 1,000 people, 1981"; the grain wedge pulled out of the pie. 1,975 bytes.
- **203**: lava flow lies along the right flank from the rim to the plain, with a bright core; irregular magma chamber with a hot heart and two feeders; ash column of ten discs with ash falling as vertical hatching. 1,509 bytes.
- **204**: address text 13 × 20 in a darker grey; stars enlarged to a 20-unit field; a vertical HOTEL sign on a downward text path in the flashing beacon entry. 1,944 bytes.
- **205**: rose drawn at the left of the masthead and an EP monogram ring at the right; curling icon redrawn as a stone on the house; NEW tag moved inside the stock-club folder. 2,132 bytes.
- **206**: a neighbour at a telescope in the garden; leader lines to Jupiter and Mars; labels 15 × 24; "9 days old" in white; compass points in gold; craters removed; a meteor streak. 2,509 bytes.

`validate.py` passed on all ten pages after these changes.
