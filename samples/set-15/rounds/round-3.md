# Set 15 · Improvement round 3

## Critique of the round-2 renders

### 197 · The Electronic Front Page · 2,230 bytes

A convincing front page with its index of departments. The nameplate is set in the thin stroke face and looks light for a newspaper's name. The lead picture shows the bridge from the first byte, so the page's build does nothing for the story; a planned bridge should arrive as the plan. The keycap index at 12 × 18 is the smallest text on the page but reads at 480 × 460.

- A heavier nameplate: a dark offset shadow and the cream letters drawn twice, one pel apart.
- The bridge drawn after a WAIT, captioned THE PLAN.
- MORNING EDITION in the dateline.

### 198 · Weather Map of the Westmark · 1,982 bytes

Complete as a map. The footer's second line of prose is the weakest part, and a forecast page of the period gave the days ahead.

- Replace it with a three-day outlook that reuses the map's programmable symbols at a smaller field.

### 199 · Storm Warning · 1,486 bytes

The rain shafts are thin vertical lines that do not lean with the wind; the farm is empty of life; the bulletin does not say when it was issued.

- Rain curtains filled with a defined texture of slanting streaks.
- One lit window in the farmhouse.
- The issue time in the header.

### 200 · Market Close · 3,027 bytes

The ticking headline makes the build tell the day. The table gives no reason to look at one share more than another; the footer gives volume only.

- The most active share's row gets an entry of its own whose panel pulses amber by BLINK.
- The footer gives the day's breadth: volume, seven up, three down.

### 201 · Last Night's Scores · 1,897 bytes

The board is plain green; the slide at home plate is still small at 480 × 460.

- A third defined texture fills the board with unlit bulbs, the look of a stadium board.
- Larger runner, catcher and umpire.

### 202 · The Community Almanac · 2,227 bytes

Good statistics; nothing places it in a community, and the legend's "Dairy 7%" is inconsistent with the other legend entries.

- A small prairie town on the skyline beside the title: an elevator, a water tower, houses.
- The 7 % labelled outside the pie on a leader, and the legend names only.

### 203 · Ask the Encyclopedia: Volcanoes · 1,691 bytes

The background is two flat bands, so the cone floats; the ash column has no drama.

- Distant ranges behind the volcano.
- Lightning inside the ash column, a real feature of eruptions.
- A few conifers at the foot of the right flank.

### 204 · City Directory: Hotels · 1,965 bytes

The directory gives no prices, though "rooms and rates" was the promise; the header has no sign that this is visitor information.

- A nightly price on every hotel's second line.
- A gold information emblem in the header.

### 205 · Your Own Newspaper · 2,284 bytes

The orange headline on peach is faint at 480 × 460; the gardening folder's frost warning has no picture of frost.

- Darker orange, green, blue and pink so every headline has contrast.
- A frost crystal drawn once as a programmable character and placed at two sizes by the tomatoes.

### 206 · The Night Sky Tonight · 2,778 bytes

Jupiter is a plain dot, the Moon has no glow, and the horizon has only three points.

- Jupiter's four moons in a line, as binoculars show them.
- A halo ring round the Moon.
- SE and SW between the gold E, S and W.

## What changed

- **197**: offset-shadow nameplate; MORNING EDITION; the planned bridge drawn after a WAIT with a THE PLAN caption (first tried at 10 × 15 over the sun and moved to the water at 12 × 19). 2,363 bytes.
- **198**: footer now one line of news and an outlook of three days with the sun, cloud and rain characters drawn at a 30-unit field. 2,124 bytes.
- **199**: defined texture of slanting streaks fills two rain curtains; a lit window; "6:40 PM p 9" in the header. 1,440 bytes.
- **200**: Ninefield Oil's row panel in its own entry, pulsing to dark amber; footer "Vol 14.2M 7 up 3 down". 3,039 bytes.
- **201**: board filled with a texture of square bulbs in a lighter green (the unused entry reassigned); bigger figures at home plate. 1,965 bytes.
- **202**: elevator, water tower and houses beside the title; the pie lowered to clear them; 7 % on a leader; legend names only. 2,479 bytes.
- **203**: distant ranges in the band colour; two white strokes of lightning in the ash; three conifers. 1,827 bytes.
- **204**: prices ($24 to $68 a night) on each hotel's second line; gold "i" emblem. 2,131 bytes.
- **205**: darker folder colours; a frost-crystal DRCS at 24 and 16 units by the tomato plant. 2,588 bytes.
- **206**: four moons beside Jupiter; a one-pel halo round the Moon (first drawn at two pels and 46 units, over the label); SE and SW in dim blue. 2,865 bytes.

`validate.py` passed on all ten pages after these changes.
