# Set 16: videotex as its makers dreamed it, at work and in public life · pages 207 to 216

[Contact sheet](out/contact-sheet.png) · [Manifest](out/manifest.json) · [Concepts](CONCEPTS.md) ·
rounds of critique and change in [rounds/](rounds/)

Ten pictures of what Telidon, NAPLPS and videotex were meant to be outside the living room: the farm, the
airfield, the school, the travel agent, the town hall, the home office and the clinic. Seven are screens of
invented services; three (209, 212, 215) are scenes of the people they were for. Every service, place and
person is invented.

Each page begins with a full RESET, designates its sets, and defines all sixteen colour-map entries before it
draws. Every page is animated: it is ordered to be watched as it paints, with WAITs between its stages, and at
least one entry of its colour map blinks.

## Making and checking

- `pages/NNN-<slug>.py` each hold one page: a `META` record and a `build()` that returns the page.
- `pages/_kit.py` is the set's drawing kit over its own copy of the encoder (`encoder/`, copied from set 11
  and unchanged): cached colour and pel, shapes, measured and aligned text, DRCS characters, fill patterns,
  macros, WAIT, BLINK, and the foot band's key tops.
- `python3 validate.py` regenerates every stream, checks that two runs agree, that the stream is 7-bit, begins
  with the full reset and defines sixteen entries, runs the renderer's own `check`, renders at 640 × 480 and
  480 × 460, and compares everything with `out/`. `--build` writes `out/` instead; `--snapshot R` also copies
  the renders into `rounds/round-R/`.
- The renderer is `../../target/release/naplps-render` with `../../fonts/neoteletext.strokes`. Scratch files go
  in `~/.cache/cft`.

## Text sizes

All text is in five named sizes, chosen from a test chart rendered at 480 × 460 before any page was drawn. The
stroke font's pen is a twelfth of the character field's height, rounded to whole pixels: at 480 × 460 a field
under 20 design units high gets a one-pixel pen, which reads thin, and a field narrower than 16 units closes
the counters of small letters under the two-pixel pen. So the smallest size anywhere is 16 × 20; body text is
18 × 24; a service's name in its title band is 26 × 30, wide so that an overstruck W stays open. `say()`
measures every caption by the renderer's proportional-spacing rule and refuses one that leaves the screen or
the room given it, which caught two captions during the rounds.

## The pages

### 207 · Grain Prices at the Elevator

The farm service Furrowline's closing prices at Halven. The picture is drawn first in late-afternoon light: a
banded sky, a cribbed-timber elevator with its loading spout out, a train of hopper cars (one macro, called
three times) with its engine against the sun, a field in a defined stubble pattern, a wire fence. Then the
board: for each grain a DRCS head of grain, its name, an eight-day trend line, the close with its decimal
point drawn as a square so it cannot be lost, an arrow and the change. With each row the colour map takes the
sky one step toward sunset; at the end the yard light comes on and the evening star comes out. The lamp in the
cupola blinks.

### 208 · Spraying Weather

Furrowline's answer to one question: when can I spray? A sprayer works a field whose crop rows are one fill
pattern defined at two scales, fine in the distance and coarse close to. Below, five hours of Tuesday as
cards headed in the colour of their verdict: an arrow for the wind, its compass point and speed, the drift
risk in a word, and a rain gauge that fills after a WAIT. When the forecast reaches noon the afternoon is
drawn into the picture: a storm cloud, the windsock painted out and redrawn streaming, every fan of spray
trailing downwind. The two good hours are bracketed and the verdict is one line. The poor hours blink.

### 209 · The Farm Kitchen

A scene at twenty to six: a farmer in a feed cap and braces, keypad in one hand and mug in the other, before
a television whose screen is page 207 in miniature. A speckled coffee pot steams on the range, eggs are in the
pan, the dog is asleep, the co-operative's calendar hangs by the window, and a red lead runs from the wall
telephone's jack to the box on the set. The window's sky is drawn dark; two WAITs later the colour map has
brought up the dawn behind the yard fence and its rooster. The rising arrows on the small screen wink.

### 210 · Flight Briefing

The pilots' terminal at Corbel Lake airfield. A chart with shorelines, a dotted graticule (a line texture
with a real pel), uplands with a spot height, a cross-hatched danger area, wind barbs and a scale; five
airfields, each a disc in the colour of its state with its runway on its own heading and a plate giving its
ident and its ceiling in feet; a deck of low cloud drawn as a fill pattern with a scalloped edge. The route
asked for is then drawn leg by leg with its distances; its destination is below limits and blinks; after a
pause the terminal draws an amber leg to the alternate and adds a line saying so under the notices to airmen.

### 211 · Lesson Four: Fractions

A programmed-learning lesson on a blackboard in a wooden frame. A pie with a crimped crust, cut in eighths,
three slices orange; the question, with the word "orange" written in orange; four answers as fractions on
numbered keys; five pips showing where the pupil is in the lesson; an owl in a mortarboard in chalk outline.
After four seconds the lesson marks the answer: the right key turns green by a change of the colour map, the
orange slices are counted 1, 2, 3, the same fraction is drawn as a bar of eight parts, the score gains a
star, and the three slices blink.

### 212 · The Classroom Terminal

A scene from the back of a class: five children, each different, crowd a terminal on a cart; the teacher, in
profile with glasses and a lesson book, holds a pointer; the blackboard says "TODAY: THE WORLD"; the alphabet
runs along the wall on cards; there are a globe, a bookcase, coats on pegs and a tree in the window. The room
is drawn first. After a WAIT the map draws itself on the screen, one land at a time, then the dotted equator;
only then does the pointer come up, and a marker of its own blinks where it rests.

### 213 · Book Your Holiday

Sundrift Holidays sells a week on Isla Corvanta. A travel-poster beach in bands: two palms with cut fronds,
a sea in a defined wave pattern whose entry shimmers by BLINK, the sun's path on the water, a sail, a hut on
stilts, a parasol and deck chair, a sandcastle. The panel names the island and the inn, gives the flights out
and back and the seats left; while it is read the morning flight crosses the sky, its trail growing. The
price arrives last and pops: a small starburst, then the full sticker, then the pink key that books it, which
blinks.

### 214 · Vote on the New Library

The Township of Elderwick puts a question to its households. The proposed library in elevation (portico,
fluted columns, an open book in the pediment), labelled as the proposal, with the closing time and an inset
street plan marking the lot. The question in plain words, its cost, and two keys. After a WAIT the household's
key is ringed and ticked; then the count arrives and fills a bar with a tick at every tenth and a mark at the
half that carries it. The ring and the lot on the plan blink together, in an entry of their own.

### 215 · Working from Home

A scene in a spare bedroom at a quarter past nine: a parent in office clothes and slippers at a desk
terminal, the telephone in a modem's cradle, a briefcase that has not moved, a wastebasket and its misses;
on the rug a toddler with blocks, a toy telephone and a bear; a crayon drawing taped low on the striped wall;
the cat on the sill watching the street. The terminal's chart is drawn last with WAITs, five bars and then
the trend across them. The cursor, the set's lamp and one modem lamp share an entry, which blinks.

### 216 · The Community Health Page

Tamarack Creek Clinic. The clinic with a nurse at the door and the town bus at its stop; a card of hours
headed "OPEN NOW" with a green lamp; then "Anna's shots": a timeline from two months to five years, doses
given as solid discs and doses to come as rings, drawn vaccine by vaccine. The column for her age is ringed
and blinks. After three seconds key 1 is taken as pressed: "DUE NOW" becomes "BOOKED: THU 2:30" and the foot
band offers to change the time. Below, the nurse line in a red band with a nurse in a headset. The telephone
number is in the range kept for fiction.

## What the designer noticed about the renderer

- **A still shows a blinking entry in the other colour.** BLINK begins in its ON interval, and a start delay
  counts from the blink defined before it, so a single blink's delay has nothing to count from. The kit sends
  a blink of the background to itself before a page's first real blink and starts every real blink at least a
  tenth later; a still then shows every entry in its own colour, and `--tenths 1` shows the other state.
- **A blink belongs to an entry, not to a shape.** Three pages first blinked an entry that also coloured
  something that should stay still (a child's suit, a title, the clock). Each now gives the blinking thing an
  entry of its own.
- **A DRCS character is one colour, but it can be cut.** Drawing in entry 0 inside a definition clears pels,
  which is how the furrows in the Furrowline mark and the tree in the Elderwick crest are made.
- **Hatching and line textures need a pel.** The dotted graticule and the cross-hatched danger area on 210 set
  a pel of two and three design units; with the default pel they are solid.
- **A defined fill pattern tiles from the screen's origin** at its mask size in screen units, so its texture
  is finer at 480 × 460 than at 640 × 480 but always lines up across shapes.
- **Circles are round on the unit screen, not in pixels,** so at 480 × 460, which is not 4:3, the pie on 211
  and the discs elsewhere are slightly tall. That is the display's shape, not a fault of the page.
- **A filled polygon is finer than it looks.** A pie wedge of thirty-degree steps left a sliver of the disc
  under it showing; two-degree steps closed it.
