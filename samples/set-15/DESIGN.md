# NAPLPS pictures · videotex as its makers dreamed it · 197–206

[Contact sheet](out/contact-sheet.png) · [Concepts](CONCEPTS.md) · [Manifest](out/manifest.json) · Rounds: [1](rounds/round-1.md) · [2](rounds/round-2.md) · [3](rounds/round-3.md) · [4](rounds/round-4.md) · [5](rounds/round-5.md)

Ten pages of news, weather and information as Telidon and NAPLPS were meant to deliver them, most of them from one invented city, Calder Bay, and its region, the Westmark. Each page begins with a full RESET, designates macros into G2 and programmable characters into G3, defines all sixteen colour-map entries, and is 7-bit. Every page is animated: WAITs make its build tell a story, BLINK and later SET COLORs change the colour map. The contact sheet shows pages 197 to 201 above 202 to 206; in each group the 640 × 480 renders sit above the 480 × 460 renders, both at half size. Renders are drawn with the repository's stroke font, `fonts/neoteletext.strokes`. No text is smaller than a 12 × 18 field (in 640 × 480 units), the smallest size found to be cleanly legible at 480 × 460; body text is 13 × 20 or larger.

Run `python3 -B set-15/validate.py` from `samples/` to regenerate every stream, check it is deterministic, 7-bit, begins with a full RESET and defines its colour map, run the renderer's check, render both sizes, check that each animated page's WAIT or BLINK changes the picture, and compare everything with the saved outputs. Add `--build` to write the streams, PNGs, contact sheet and manifest. Set `TMPDIR` to keep its scratch files out of `/tmp`. A single page can be rebuilt with `python3 -B set-15/pages/197-the-electronic-front-page.py`. Everything is Python's standard library. The writer in `encoder/` is the set 11 encoder (itself the MIT-licensed set 6 writer), extended with a `Plate` class: framing, cached colour and pel, native circles and rings, outlined frames, defined textures, DRCS characters, measured proportional text (from the font file's glyph widths), macros, BLINK and WAIT. `rounds/` keeps the renders after each round and a critique and change list for rounds 1 to 5.

## 197 · The Electronic Front Page

The *Calder Bay Courier*'s videotext edition. A red nameplate with a gull device and a weather ear, a dateline, and a lead story whose picture shows city hall above the harbour; after a pause the bridge the council has just approved is drawn across the water in dashed red, captioned THE PLAN, and the headline follows. Two smaller stories come in turn, then a LATE item whose tag blinks and a row of keycaps giving the page numbers of the paper's other departments, which are the other pages of this set. Last, after another pause, the satellite story's panel is painted again with the rocket climbing off its pad: a two-frame animation made by repainting, the period's "story that draws itself". The nameplate is drawn three times (a dark shadow and the cream letters twice, one pel apart) for a heavier face than the stroke font gives.

## 198 · Weather Map of the Westmark

An invented prairie region in two provinces on a dark blue sea. The sun, cloud, rain and storm symbols are five programmable characters, overlaid in two colours where one symbol needs two (sun behind cloud, rain under cloud), and reused at a smaller field in the three-day outlook at the foot. Each town has a cream chip with its name and a temperature end, blue below 25 and red-orange above. The highway is a dotted line and the provincial border a dashed one. Where it is raining is a defined texture of drops in the rain entry, which blinks against the cloud colour so the rain area shimmers and the drops under the rain symbol fall; the storm's bolt has its own blinking entry. After a WAIT the low, the cold front with its teeth to the south-east, the warm front with its semicircles on its south side and the wind arrow appear.

## 199 · Storm Warning

A tornado watch, issued at 6:40 pm. The sky is a ragged deck, a shelf cloud with a lit underside, mammatus pouches, scud and rain curtains filled with a defined texture of slanting streaks. The lightning bolt's own colour is the sky's, so it is invisible until BLINK strikes it cream; on the same beat the sky and the fields flash to a paler green (each BLINK's delay counts from the one before, so all start together). The funnel turns: a second set of its bands lies in an entry that BLINK shows and hides. An inset map shows the two counties under the watch in red cross-hatching. The bulletin's TORNADO WATCH blinks between alarm red and dark red. The page draws in three stages: sky, then funnel and farm, then bulletin.

## 200 · Market Close

A broker's quotation page in the green-screen manner. The index line is drawn half-hour by half-hour, with a WAIT each hour, and at every hour the headline figure, arrow and change are painted over and rewritten, so the number ticks as the line climbs. The area under the line is green hatching over a solid dark green; yesterday's close is a dotted reference line; orange and green flags mark the day's low and the high close. Ten invented shares follow in two columns, with up and down arrows as programmable characters; the most active share's row has an entry of its own that pulses amber. The closing bell in the header shares its sound lines with the blinking close marker, so it rings.

## 201 · Last Night's Scores

A night ballpark from behind home plate. The crowd is two defined dot textures in cream and blue over dark terraces; advertising boards in team colours line the wall, with yellow foul poles; the winning run slides home past the catcher in a cloud of dust. Pennants carry the final score. The line score is on a board whose face is a third defined texture of unlit bulbs, and it is replayed inning by inning with a WAIT before each, a longer one before the tenth; the tenth-inning column is an entry that holds the board's colour and BLINK lights it orange. Results around the league follow with team chips, winners in white.

## 202 · The Community Almanac

The Westmark Bureau of Statistics' census page on cream paper. Towns are isotype rows of a programmable figure, one per thousand people, drawn with REPEAT; the last figure of each row is cut to its fraction by painting paper over it, and rules at five and ten thousand let the rows be read off. Each row is drawn after a WAIT. Farms by type are a pie of polygon wedges filled solid or with native vertical and cross hatching over a base colour, the grain wedge pulled out and drawn with a sheaf of wheat. A small prairie town stands beside the title, and a teal foot gives the next pages.

## 203 · Ask the Encyclopedia: Volcanoes

The *Quarto Home Encyclopedia*'s plate, page two of six. A cut-away volcano of eight uneven strata stands before distant ranges, over a crust speckled with a defined texture and an irregular magma chamber. After a WAIT the magma climbs the main vent in five steps, then the eruption: lava fountaining from the crater and flowing down the flank, a side vent fed by a dike, an ash column with lightning in it and ash falling as hatching, and volcanic bombs on dotted arcs. The lava's bright core blinks. Every part is named on a leader line; a scale bar gives 5 km.

## 204 · City Directory: Hotels

The Calder Bay city guide's hotel page. A dusk skyline of two depths stands on the bay; every window and every broken reflection streak on the water is drawn in one entry that holds a dark colour, and after the directory has been listed row by row a single SET COLOR lights the whole city at once. A vertical HOTEL sign, written on a downward text path, flashes with the last free room. The directory gives each hotel's name, address, telephone number, stars (a programmable character), nightly price, and a programmable bed in green, red or flashing for tonight's rooms; the visitor's current choice is boxed with a wide-pel outline.

## 205 · Your Own Newspaper

*The Pellow Post*, edited for one reader. A masthead with a rose and her monogram, then four topic folders filed one after another on a plum desk, each with a coloured tab, a shadow, a drawing on a white plate, a headline in the folder's colour and the page number to read more. The gardening folder warns of frost with a crystal drawn once as a programmable character and placed at two sizes; a clipping is pinned to the curling folder; the stock club's NEW tag blinks.

## 206 · The Night Sky Tonight

An almanac page for a hobby club. It opens at dusk: the dome's four entries hold twilight colours and the houses and a neighbour at a telescope stand against them; after a WAIT four SET COLORs turn the same entries to night, and only then do the Milky Way (two defined speckle textures), the stars (two programmable characters in three entries that blink to a dim blue with staggered delays, so they twinkle), the Moon with its halo, Jupiter with its four moons and Mars appear; the roofline is drawn again over them. Everything outside the dome is painted in the roof's near-black, which frees entry 0 for a meteor that BLINK flashes white for two tenths of a second in every three.

## What the renderer showed

- Proportional stroke text narrows at 480 × 460 (three quarters of the width) and its pen width rounds unevenly: a 12 × 18 field is thin but clean, a 10 × 15 field is not. Every page keeps text at 12 × 18 or larger.
- Native circles are worked out on the unit screen, so they are round at 640 × 480 and slightly tall at 480 × 460; the pie in 202 and the plates in 205 show it.
- BLINK starts in its ON interval, showing the other entry's colour. An entry that should look normal in a still and change briefly (the tenth-inning column, the bolt, the meteor) holds the background colour itself and blinks to the colour it flashes.
- Native hatching at one pel nearly fills at 480 × 460; a sparse defined texture keeps an area visibly patterned at both sizes (the rain area in 198).
- A three-point arc's points must be chosen as a shallow arc; through steep points it closes into a near-circle (seen in round 5 on 203).
