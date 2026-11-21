# Set 15 · Improvement round 5

## Critique of the round-4 renders

### 197 · The Electronic Front Page · 2,482 bytes

Every piece of text is clean at 480 × 460 and the page reads as a newspaper front. Of the period's favourite trick, a picture that draws itself as a story, it has only the bridge; the satellite story's rocket sits on its pad though the headline says it is up.

- After a WAIT the rocket panel is painted again with the rocket climbing on a column of smoke: a two-frame animation made by repainting, as a terminal would.

### 198 · Weather Map of the Westmark · 2,265 bytes

Complete and legible. Where it is raining is shown only by two symbols, though the period's maps shaded the rain area.

- The rain area west of the front in a defined texture of drops, drawn in the rain entry so it shimmers as that entry blinks. (A first version in native hatching filled solid at 480 × 460 and read as a lake.)

### 199 · Storm Warning · 1,650 bytes

The funnel is static, and the flash lights the sky but leaves the ground dark.

- A second set of bands on the funnel in an entry of their own (the bulletin panel moved to entry 0 to free it), shown and hidden by BLINK so the funnel turns.
- The fields flash with the sky on the same beat.

### 200 · Market Close · 3,097 bytes

The closing bell, the moment the page is named for, is not on the page. The most active row rests in navy between pulses, not in the panel colour the other rows use: the round-3 palette change had not been applied.

- A bell in the header whose sound lines are in the closing marker's blinking entry, so it rings.
- The row's resting entry corrected to the panel colour, so it pulses amber against matching rows.

### 201 · Last Night's Scores · 1,991 bytes

The ballpark wall is a bare brown band; the slide at home has no dust.

- Advertising boards in team colours along the wall and yellow foul poles at its ends.
- A cloud of infield dust behind the sliding runner.

### 202 · The Community Almanac · 2,596 bytes

The isotype rows cannot be read off against a scale; the pie gives shares but not how many farms.

- Rules at five and ten thousand with their numbers (first drawn in the grid colour, too faint at 480 × 460, then in ink).
- "2,840 farms" under the legend.

### 203 · Ask the Encyclopedia: Volcanoes · 1,942 bytes

An encyclopedia plate has a scale; the eruption throws nothing.

- Dotted arcs for the paths of volcanic bombs (first drawn through badly chosen points as near-circles, then flattened).
- A 5 km scale bar on the crust.

### 204 · City Directory: Hotels · 2,600 bytes

The availability column is three coloured dots whose meaning a visitor must guess; the bay has the city's lights but not the Moon's.

- A programmable bed character in place of each dot, in green, red or the flashing last-room entry.
- The Moon's path on the water in broken cream streaks.

### 205 · Your Own Newspaper · 2,723 bytes

The icons sit directly on pastel folders and lose their edges; the NEW tag blinks to the desk colour, which is not the folder it sits on.

- A white plate behind each picture, like a clipping pasted in.
- NEW blinks between red and the stock folder's orange.

### 206 · The Night Sky Tonight · 3,172 bytes

The meteor is a fixed streak, which is the one thing in the sky that should not stay.

- Everything outside the dome is painted in the roof's near-black, which frees entry 0; entry 0 is given the outer sky's colour and the meteor is drawn in it, and BLINK flashes it white for two tenths of a second every three seconds.

## What changed

- **197**: `rocket_climbing` repaints the satellite panel after a 1.5-second WAIT. 2,706 bytes.
- **198**: defined drop texture over the rain area, in the blinking rain entry. 2,357 bytes.
- **199**: turning funnel bands in entry 12 (BLINK 2 on, 2 off); bulletin panel and inset in black; the ground entry flashes with the sky. 1,699 bytes.
- **200**: ringing bell; most-active row's resting entry corrected. 3,229 bytes.
- **201**: five wall boards, two foul poles, slide dust. 2,095 bytes.
- **202**: reading rules at 5 and 10 with ink numbers; farm total. 2,678 bytes.
- **203**: two dotted bomb arcs; scale bar. 2,044 bytes.
- **204**: bed DRCS at a 38-unit field; the Moon's path on the water; prices moved left to clear the beds. 2,715 bytes.
- **205**: white plates behind the icons; NEW blinks to orange. 2,769 bytes.
- **206**: flashing meteor in entry 0. 3,186 bytes.

`validate.py` passed on all ten pages after these changes.
