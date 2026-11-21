# Set 15 · Improvement round 2

## Critique of the round-1 renders

Each page was looked at again at 640 × 480 and 480 × 460.

### 197 · The Electronic Front Page · 1,970 bytes

Now a front page: the lead story dominates, the masthead has a device and a weather ear, and every line is legible at 480 × 460. The bottom band spends 62 pixels on one late item, and nothing on the page says the paper is a whole service of other pages, which was the videotex promise. The lead picture's harbour is empty, so the bridge story has nothing crossing the water. The rocket's porthole sat in the LATE tag's blinking entry.

- Turn the bottom band into a compact late item plus a keycap index of the other departments with their page numbers (weather 300, markets 400, city 230, encyclopedia 711, the other pages of this set).
- Put a ferry on the harbour where the bridge will go; move the porthole off the blinking entry.

### 198 · Weather Map of the Westmark · 1,904 bytes

Clear and correct now: chips, symbols and fronts with their marks on the leading side. The two provinces are one undifferentiated green; the sea is empty; the weather symbols are still pictures, though a storm and rain could move.

- Shade the eastern province a deeper green and name the bay on the sea.
- Give the storm's bolt its own entry (rivers now share the lake's) and BLINK it, and BLINK the rain so it falls.

### 199 · Storm Warning · 1,360 bytes

The flashing sky works, but in its lit state the sky is one flat pale green; the funnel ends in a small grey wedge rather than a debris cloud.

- Drift dark scud across the middle of the sky so it has depth in both states of the flash.
- Give the funnel a debris cloud of circles and flung fragments.

### 200 · Market Close · 2,572 bytes

Strong. The headline figure is fixed while the chart builds hour by hour, so the build does not tell the day as it happens; the header has no device.

- Repaint the headline index and change at every hour of the reveal, so the figure ticks as the line climbs: painting over is how a terminal updates.
- Draw the broker's device, a Q of ring and tail.

### 201 · Last Night's Scores · 1,728 bytes

The crowd and pennants work. The tenth-inning column's yellow figures are weak on orange; the winning run, the point of the story, is two dots; the other results are a plain list.

- White figures in the lit column.
- The winning run sliding home past the catcher, with the umpire behind.
- Each result with team colour chips and the winner in white.

### 202 · The Community Almanac · 1,975 bytes

The isotype rows are the right idea but the figures are small at 480 × 460 and rounded to whole thousands; the pie is crowded against them; the grain wedge is plain.

- Larger figures, with the last figure cut to the fraction it stands for, as isotype charts did.
- A smaller pie moved right, with a sheaf of wheat drawn on the grain wedge.

### 203 · Ask the Encyclopedia: Volcanoes · 1,509 bytes

Reads as a textbook plate now. The eruption arrives all at once after one WAIT; the crust is unlabelled; nothing says this is one page of a longer article.

- Magma climbs the vent in five WAIT steps before the eruption.
- Label the solid crust and add a six-dot article indicator with page two lit.

### 204 · City Directory: Hotels · 1,944 bytes

The sign is thin and its letters faint at 480 × 460; the directory has no sense of the visitor's choice, though choosing by key was the whole point.

- A wider sign with larger letters.
- The visitor's current choice boxed in the band colour with a wide-pel outline.

### 205 · Your Own Newspaper · 2,132 bytes

Charming and legible. The folders are flat on the desk and every line of text has the same weight, so no item has a headline.

- Shadows under folders and tabs (the desk lightened so the ink entry serves as shadow).
- Each folder's first line as a headline in the folder's colour.
- A clipped cutting on the curling folder.

### 206 · The Night Sky Tonight · 2,509 bytes

The most finished page. The dome is still four plain bands with scattered stars; the sky has no structure.

- A Milky Way across the dome from two defined speckle textures, a broad haze and a denser core.

## What changed

- **197**: bottom band rebuilt as a LATE line and a row of four keycaps (WEATHER 300, MARKETS 400, CITY 230, ASK 711); a ferry on the harbour; the rocket's porthole moved to the water entry. 2,230 bytes.
- **198**: eastern province in the deeper green; "Kestrel Bay" on the sea; the bolt has its own entry and blinks against the cloud, and the rain blinks so it falls; the southern hatching stops at the provincial line. 1,982 bytes.
- **199**: two bands of dark scud across the sky; a debris cloud of four circles with flung fragments at the funnel's foot. 1,486 bytes.
- **200**: the headline figure, arrow and change are repainted at each hour as the chart draws (painted over with a black rectangle, then rewritten); the Q device in the header. 3,027 bytes.
- **201**: white figures in the lit column; a sliding runner, catcher and umpire at home plate; results with colour chips, winners in white and losers in grey. 1,897 bytes.
- **202**: figures 17 × 34; the last figure of each row cut to its fraction by painting paper over it; pie moved right and made smaller; a sheaf of wheat on the grain wedge with its percentage beside it. 2,227 bytes.
- **203**: the main vent fills in five steps with a WAIT after each; "Solid crust" label; six article dots with the second lit. 1,691 bytes.
- **204**: sign widened to 30 and its letters to a 20 × 16 field; Grand Calder boxed with a 3-pel outline (a new `frame` method in the encoder); a pointer was tried and removed because it covered the row number at 480 × 460. 1,965 bytes.
- **205**: folder and tab shadows; headlines in the folder colour at 15 × 24; a clipped cutting on the curling folder. 2,284 bytes.
- **206**: Milky Way haze and core in two defined textures of square specks. 2,778 bytes.

`validate.py` passed on all ten pages after these changes.
