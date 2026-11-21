# Round 4

Renders looked at: `rounds/round-3/`, every page at 640 × 480 and 480 × 460. This round also asked of each page which of the medium's strengths it still leaves unused: so far no page used a macro or rotated text, and only two used programmed fill patterns.

## Critique

**217 Chess by Wire.** Finished as a screen, but its foot line still says the deadline in words ("REPLY BY FRIDAY") where a picture would say it faster, and the envelope, the page's own symbol of a move by wire, appears once. The board frame is plain wood. Changes: define the envelope once as a macro and play it on the wire and again in the prompt band beside "ENTER MOVE"; show the reply time as five day pips with three used; inlay the frame with a gold line.

**218 The Maze.** The prompt is the one place the page asks the player to act, and it is words only. Changes: a programmable arrow character, defined once and set with TEXT rotation at 0, 90 and 270 degrees, before each choice (left, ahead, right), so the keypad prompt reads as directions at a glance.

**219 Quiz Night.** "QUESTION 7 OF 10" is the one line of the strip that could be a picture, and it hides how the player has done so far. Changes: replace it with ten pips: six answered (green right, red wrong), the current one pink, three still to come.

**220 Gallery Page: Harbour at Dusk.** The foreground water is a flat navy with scattered glints; the period painters would have drawn the swell. Changes: long swell lines across the near water drawn as incremental lines (two bits a step), in the hills' entry, so they darken with the dusk.

**221 The Lace Picture.** All the threads are solid lines; real lace has running stitches. Changes: two running-stitch circles drawn with the dotted line texture and a two-unit pel, between the lozenges and the scallops and inside the teardrops.

**222 Story Time: The Garden.** The story's text panel is plain type. Changes: a drop capital "E" in a coloured square, as a picture book sets its first line; a ladybird on the upper leaf.

**223 The Chat Line.** Skye's message says the card "plays a tune", but nothing sings. Changes: a programmable musical-note character, drawn three times in rising sizes beside the private panel, blinking in turn.

**224 The Face Maker.** The parts menu is words and numbers; a child cannot read "NOSE" faster than they can see one. Changes: six small programmable icons (head, hair, eye, nose, mouth, hat) at the right of the menu rows.

**225 Download Tonight's Program.** The screen shows a rocket, which says *game* but not *program arriving*. Changes: the screen shows the start of the program's listing as it arrives, in phosphor green, with a block cursor.

**226 New Year's Eve 1990.** The year is flat on the sky; the tower that dominates the right half tells no time. Changes: a drop shadow under "1990"; a clock face on the tower with both hands at twelve.

## Changes made

- **217:** the envelope is now a macro (DEF MACRO, relative RECT and LINE so it draws wherever the point is), played on the wire and again in the prompt band; "REPLY BY FRIDAY" became "DAYS TO REPLY" with five day pips, three used in grey and two left in yellow; a gold inlay line runs inside the wooden frame.
- **218:** one arrow programmable character, set with TEXT rotation 90, 0 and 270 degrees (each shifted back into its cell, since a turned character pivots on its lower left corner), stands between each key and its word: "4 ← LEFT  8 ↑ AHEAD  6 → RIGHT".
- **219:** "QUESTION 7 OF 10" became ten pips: five lime (right), one grey and crossed (wrong), the current one pink and larger, three empty rings to come; the scores became 50 and 60 to agree with one wrong answer.
- **220:** five long lines of swell, each an INCREMENTAL LINE of two-bit moves (across, across and down, and a reverse of dy each half crest), drawn in the town's shadow colour across the near water. A first try in the hills' entry was invisible on the dusk sea and was changed.
- **221:** two running-stitch circles, drawn with the dotted line texture and a two-unit pel, one in ice between the lozenges and the scallops and one in gold just inside the picot thread.
- **222:** a blue drop capital square with a cream "E" begins the story's first line; a ladybird sits on the upper leaf.
- **223:** a programmable musical-note character, set three times in rising sizes so the notes climb out of the private panel; they blink between blush and lilac (one entry, so they blink together, not in turn as the critique proposed: the palette has no three spare entries).
- **224:** six programmable icons (head, hair, eye with a cleared iris ring, nose, mouth, hat) at the right of the menu rows; the choice numbers moved left to make room.
- **225:** the screen shows the listing arriving ("LOADING 14/30", then four numbered lines of the program) in phosphor green, with a block cursor, in place of the rocket.
- **226:** the year has a drop shadow in the darkest tower colour; the tower has a lit clock face with twelve hour dots and both hands at twelve.

`validate.py --build` then `validate.py`: all ten pages pass (deliverables up to date).
