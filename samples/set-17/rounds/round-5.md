# Round 5

Renders looked at: `rounds/round-4/`, every page at 640 × 480 and 480 × 460. The last round: what still looks crude or unfinished at the channel's size.

## Critique

**217 Chess by Wire.** The move arrow is a short red stub with a head pointing the wrong way at 480 × 460; it is the crudest mark on an otherwise careful page. The prompt band still shows an example ("E.G. E6-E5") rather than the player's reply. Changes: draw the arrow from the centre of d3 to the centre of c4 with a head computed from its direction, over the pieces as a chess diagram would; turn the prompt into an entry field with the reply being typed and "# SEND" beside the envelope.

**218 The Maze.** The right-hand near wall, the largest flat area on the page, has nothing on it, so the composition leans left. Changes: hang a shield with a chevron on the right wall; string a cobweb across the top left corner of the vault.

**219 Quiz Night.** The answer boxes are flat rectangles; a keypad game's answers should look pressable. Changes: give each box a drop shadow so the four read as buttons; ring the empty clock dial so it does not read as a hole.

**220 Gallery Page: Harbour at Dusk.** The horizon between the hills is empty and the glitter road is the same pink everywhere. Changes: a steamer on the horizon with a row of portholes in the windows' entry, lit at dusk; the glitter nearest the sun in the sun's own entry, so the road is brightest where it begins.

**221 The Lace Picture.** The bead ring round the rosette is a plain row of cream dots, and the medallion's rim is a single line. Changes: beads alternating gold and cream; a double rim with a gold inner line.

**222 Story Time: The Garden.** The edge between grass and soil is a ruler-straight line, and the right half of the soil has only a worm. Changes: tufts of grass along the edge; a snail on the soil by the fence.

**223 The Chat Line.** The band is crowded: "NIGHT OWLS ROOM" had to be shrunk to fit and reads small. The night window is a four-pane box that could be a picture frame. Changes: shorten the band to "NIGHT OWLS" at full size; give the window a sill and curtains.

**224 The Face Maker.** The nose is a bare triangle, the one part that looks unfinished beside the rounded eyes, cheeks and mouth; the ears are plain discs. Changes: a rounded nose with nostrils; inner-ear curves.

**225 Download Tonight's Program.** The transmitter mast stands on nothing. Changes: a transmitter hut at its foot and a ground line, with the hut's window lit and a small red lamp.

**226 New Year's Eve 1990.** The stars are fixed points while everything else moves, and the back row of towers is unlit. Changes: the stars twinkle by BLINK; the back towers get scattered lit windows.

## Changes made

- **217:** the arrow runs from the centre of d3 to the centre of c4, six units wide, with a head built on the line's own direction (a triangle whose base is perpendicular to the move) and a disc at its tail, drawn over the bishop; the prompt became "YOUR REPLY:" with an entry field showing "E6-E5" and the blinking cursor, and "# SEND" beside the envelope macro.
- **218:** a red shield with a gold chevron and boss, shadowed, hangs in the near right wall's perspective; a cobweb of four spokes and three threads fills the top left corner of the vault.
- **219:** each answer box has a dark drop shadow, so the four read as buttons; the empty clock dial has a dark face and a pink inner ring round its 0.
- **220:** a steamer with funnel and a row of portholes (in the windows' entry, so they light at dusk) sits on the horizon against the sun; the first five rows of the glitter road are in the sun's entry, so the road is brightest where it starts and follows the sun's dusk colours.
- **221:** the bead ring alternates gold and cream; the medallion's rim is a double line, blue outside and gold inside.
- **222:** tufts of grass in leaf green along the soil's edge (clear of the stem); a snail with a spiral shell and eye stalks crosses the soil by the fence.
- **223:** the band reads "NIGHT OWLS" at 14 × 22, no longer crowding the clock; the night window has pink curtains drawn back, a pelmet and a sill.
- **224:** the triangle nose became a soft bridge, a round tip and two nostrils; each ear has an inner curve.
- **225:** a transmitter hut with a lit window and a red lamp stands at the mast's foot on a line of ground.
- **226:** the stars twinkle (their entry blinks to the mid sky's colour on its own beat); the back row of towers has scattered lit windows in the windows' entry, which blink with the front row.

`validate.py --build` then `validate.py`: all ten pages pass (deliverables up to date).

After the round, four names were found to be in real use and were coined afresh: the story service *Storyline* became *Bedtime*, *Facekit* became *Phizkit*, *Citynet* became *Citylamp* and the game *Starhopper* became *Moonskip* (the earlier rounds' notes keep the names as they then were). `validate.py --build` and `validate.py` were run again: all ten pages pass.
