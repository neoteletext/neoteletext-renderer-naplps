# Round 3

Renders looked at: `rounds/round-2/`, every page at 640 × 480 and 480 × 460.

## Critique

**217 Chess by Wire.** Complete as a screen: the move arrives, the captures show, the turn is clear. The title band is now the weakest part, a row of type with no mark of its own, where every period service put a logo built of shapes. Changes: a knight's head mark in the band, drawn with the same programmable character as the board's knights at a large size; a second rule under the band in the board's green so the band, board and panel share one palette.

**218 The Maze.** Atmospheric. Two weaknesses: the mosaic map in the panel is a jumble of blocks that does not read as corridors, and the torch lights nothing, so the near wall is as evenly lit as the far one. Changes: redraw the map as clear mosaic corridors with the walker's position marked; pool the torch's light on the near wall with the dithered pattern already programmed for the door.

**219 Quiz Night.** The reveal now celebrates. The page does not say that the city is playing together, which was the point of a quiz on a network, and the question card has no number on it. Changes: a round "Q7" badge on the card's edge; the foot band says how many households are playing tonight.

**220 Gallery Page: Harbour at Dusk.** Rich. The town's roofs are bare and its quay is dark, so the left third has less incident than the right. Changes: chimneys with curls of smoke, and three quay lamps on posts in the windows' entry, so they light with the town at dusk.

**221 The Lace Picture.** The rosette is a single layer of petals and reads flatter than the rings round it; the picot edge has no accents. Changes: a second, smaller layer of petals in cream over the gold, turned half a petal; gold beads on the outer thread at each of the twelve axes.

**222 Story Time: The Garden.** The fence added in round 2 runs the full width and hides the hills, so the picture has lost its depth. The sky is empty. Changes: the fence only on the right, round the cottage, so the left hill shows behind Wren; two soft clouds.

**223 The Chat Line.** Still the most text-bound page. The badges are only in the member list, so the conversation does not show who is talking at a glance, and the title has no mark. Changes: each speaker's badge before their name in the conversation; a speech-balloon mark in the title band built from a filled arc and a tail.

**224 The Face Maker.** Bright and friendly. The face is meant to be sent as a card but says nothing; the backdrop is a flat colour. Changes: a speech balloon "HI GRAN!" so the face is visibly a card in the making; a polka-dot wallpaper on the booth backdrop, programmed as a fill pattern.

**225 Download Tonight's Program.** The computer floats in space beside the cassette. Changes: a desk under the computer with a lamp and a mug, so the receiving end is a room in a home.

**226 New Year's Eve 1990.** The bridge and crowd are drawn in the darkest entry on a nearly black river and barely show at 480 × 460. Changes: draw the bridge in the lighter tower colour; light the water behind the crowd with a band of reflected glow so the heads stand out as silhouettes.

## Changes made

- **217:** a large ivory knight, the board's own programmable character outlined in ebony, is the service mark at the left of the band; the title text moved right to make room; a felt-green rule under the yellow one ties band and board together.
- **218:** the map is generated from a 12 × 9 grid of corridor cells, turned into mosaic codes two cells across and three down, drawn in wall colour on a black plate with the walker as a red dot, so it reads as a maze; the torch pools dithered light (the door's pattern 4) on the near wall, kept clear of the side passage.
- **219:** a pink "Q7" badge sits on the question card's left edge, the question moved right of it; the foot band reads "1,204 HOMES PLAYING · # NEXT".
- **220:** three chimneys with curls of smoke drawn as stacked arcs; three quay lamps on posts drawn in the windows' entry, so they light with the town in the last dusk step.
- **221:** a second layer of twelve smaller cream petals, turned half a petal, sits over the rosette in an entry that does not blink; twelve gold beads mark the axes on the picot thread.
- **222:** the fence now runs only from the cottage to the right edge, so the green hill shows again behind Wren; two clouds of an ellipse and two discs each.
- **223:** each line of the conversation begins with its speaker's badge in their colour; a pink speech balloon with three dots is the service mark in the band; the room name is set at 12 × 18 so it clears the clock.
- **224:** a polka-dot wallpaper (a disc programmed as fill pattern 4 on a 20-unit mask) behind the sitter; a speech balloon "HI GRAN!" with a tail toward the face.
- **225:** a desk under the keyboard (top and front edge) and a red mug of cocoa at its left end.
- **226:** the bridge is drawn in the lighter tower entry; three bands of reflected glow (gold, magenta, cyan, the bursts' own entries, so they cycle) lie on the water behind the crowd, which now stands out in silhouette.

`validate.py --build` then `validate.py`: all ten pages pass (deliverables up to date).
