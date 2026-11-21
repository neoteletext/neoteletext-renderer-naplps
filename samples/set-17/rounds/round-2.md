# Round 2

Renders looked at: `rounds/round-1/`, every page at 640 × 480 and 480 × 460 (and 220 at several BLINK phases).

## Critique

**217 Chess by Wire.** Now reads as a game between two households. What it does not yet use is time: the opponent's move simply *is* there, when the medium could show it arriving. The score panel tells who is playing but not how the game stands; a correspondence player's first question is what has been taken. Changes: animate the move arriving (the bishop on d3, a pause, the envelope on the wire, then the bishop lifted to c4); add a tray of captured pieces drawn with the same programmable characters at a small size.

**218 The Maze.** The turnings now read and the key gives the game an object. The hatched light spill in front of the door still looks like a ladder lying on the floor. The side passages are empty darkness, which is a missed chance for the one thing a maze game needs: a reason to hesitate. The "FACING NORTH" line has no picture. Changes: replace the hatched spill with a programmed dot texture (DEF TEXTURE), a dithered pool of light; put a pair of eyes in the left passage that blink with the key's glint; draw a small compass rose in the panel.

**219 Quiz Night.** Clear and bright. The reveal is still modest: the banner and the colour change happen, but nothing celebrates, and the score changes without saying by how much. Changes: burst a ring of coloured sparks round the right answer after the reveal; show "+10" beside the redrawn score.

**220 Gallery Page: Harbour at Dusk.** The best page. The lighthouse's rock is a single dark blob, and the boats are bare (no rigging, no flags), which is where the period painters spent their extra shapes. Changes: facet the rock in two tones; give the lighthouse a gallery rail; add forestays and pennants to the boats and a rowing boat with a figure near the pier.

**221 The Lace Picture.** The medallion is now properly lace. The ground round it is flat navy, the one large area of the page doing nothing, and the caption sits in a plain bar. Changes: fill the ground with a programmed weave texture (DEF TEXTURE), so the lace lies on cloth; set the caption in a cartouche.

**222 Story Time: The Garden.** Much better with the new Wren and the bee. The left half of the picture has no story context: where does Wren live? Changes: a picket fence along the hills and a small cottage with a red roof on the far hill; turn "PAGE 3 OF 5" into five page dots with the third lit, which a child can read.

**223 The Chat Line.** Believable and legible. It still lacks the sense of live time: lines have no times, the member list no count. Changes: a time beside each speaker's name, so the conversation reads as minutes passing; the member count in the column heading.

**224 The Face Maker.** Fun, but the eyebrows slope inward and make the face look cross, which a face kit's default should not; the backdrop is plain. Changes: arch the eyebrows; hang a pleated photo-booth curtain at each side of the backdrop using hatched fill; add an envelope to the "SEND AS A CARD" band.

**225 Download Tonight's Program.** A good period scene, but the stream of digits appears all at once and the area under it is empty, so the signal crosses nothing. Changes: put a row of small houses with rooftop aerials under the arc, so the signal crosses town; draw the digits one at a time with WAIT, so the stream is seen to flow.

**226 New Year's Eve 1990.** The greeting now reads. The foreground is still only river; the city has no people to celebrate. Changes: a bridge in arches across the river with lamps; a crowd of heads and raised arms on the near bank.

## Changes made

- **217:** the opponent's move now arrives in time: the board first shows the bishop on d3; after the pieces, the panel and a ten-tenths WAIT, the two squares light, the bishop is set down on c4 and the arrow is drawn. Each player's captures (bishop, knight, pawn) are shown beside their town as the same programmable-character pieces at 20 units, outlined.
- **218:** the hatched spill became a dithered pool of light, a two-dot pattern programmed with DEF TEXTURE and used as fill pattern 4; two eyes glint in the left passage on the key's BLINK; the panel has a compass rose (red north needle) before "NORTH".
- **219:** eight four-pointed sparks in yellow, cyan and white burst round the right answer after the reveal; "+10" appears beside the redrawn score.
- **220:** the lighthouse rock is faceted in two tones; the tower has a gallery and rail; each sailing boat has forestay, backstay and a red pennant; a rower in a red boat pulls past the pier, oars out, with his own glints.
- **221:** a basket weave, programmed as fill pattern 4 on a 10-unit mask, covers the ground in a tone just above it, so the lace lies on cloth; the caption sits in a gold-ruled cartouche with round ends.
- **222:** a white picket fence runs behind the garden and Wren's red-roofed cottage stands on the far hill; "PAGE 3 OF 5" became five page dots with the third lit in yellow.
- **223:** every line carries its time (11:36 to 11:41) at the right of the speaker's name; the column heading says "6 IN THE ROOM".
- **224:** the eyebrows are arched and the curls trimmed so they no longer cover the brows' outer ends (the face no longer looks cross); red curtains with pleat lines and a scalloped valance frame the booth; an envelope sits on the band beside "SEND AS A CARD".
- **225:** five houses with rooftop aerials (mast, boom and three elements pointing at the transmitter) stand under the arc, so the signal crosses a town; the digits are sent one at a time with a WAIT between each (a first try drew the aerials as crosses, which read as a churchyard; they were redrawn).
- **226:** a bridge of five filled-arc arches with lamp posts crosses the left half of the river; a crowd of silhouettes, some with arms raised, stands on the near bank.

`validate.py --build` then `validate.py`: all ten pages pass (deliverables up to date).
