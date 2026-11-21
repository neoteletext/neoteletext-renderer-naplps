# Round 5: critique of the round-4 renders

The critique below is of the renders in `rounds/round-4/`, looked at in both sizes. It is the last round. Each page is judged as a finished picture; the changes name what would still improve it.

## 177 Good Morning, Hartley Avenue

Complete: sunrise, house, mailbox with its flag, the menu with its marks and the bus on the road. The path from the gate to the door is missing, so the mailbox stands alone on the grass, and the house has no way in.

Changes: stepping stones of paper colour from the mailbox to the door.

## 178 A Card for Grandma

Complete as a card. The rosettes are all one colour, and the greeting is one colour, so the page is evenly toned; a card of its kind would vary its colour a little.

Changes: the rosettes alternate raspberry and gold; the greeting's letters alternate rose and raspberry.

## 179 The Family Message Board

Complete. Every pin is red, so the board reads as one kind of pin, and the pins have no differences in the way real pins do.

Changes: MUM's pin is teal and DOUG's pin is navy; the other pins stay red.

## 180 Supper Tonight

Complete as a recipe. The bowl beside INGREDIENTS floats between the heading and the list and does not earn its place, so it is removed.

Changes: the bowl is removed; the rest of the page is unchanged.

## 181 The Wired Living Room

Complete. The room has no window treatment beyond the curtains, and the television has no aerial, so it is a box.

Changes: rabbit-ear aerial on top of the television cabinet; a tie-back for each curtain.

## 182 Neighbourhood Calendar, Maple Ridge Estates

Complete. The legend names the four events but not the bin day or the weather, so the new marks have no key.

Changes: a legend entry for BIN DAY with a bin swatch, in the legend band.

## 183 The House That Orders Its Own Paper Towels

The LOW flag and the x4 count tag touch on the second shelf, which is cramped. The rest is complete.

Changes: the LOW flag moves up to clear the count tag.

## 184 Home Watch

Complete. The status panel has no date or time, so the page does not say when it was last read.

Changes: a line in the status panel's header reading the time of the last check, "CHECKED 7:40 PM"; the lamp rings are unchanged.

## 185 Tonight's Horoscope

Two sparkles sit on text in the round-4 render: one on "QUIET" and one on the rule under LEO. The moon has no glow.

Changes: the sparkles move to clear places; a glow ring is set round the moon.

## 186 School Bus Is Late

Complete. The bus's windows are empty, so the bus looks empty while it waits for a parent to see it.

Changes: two windows are lit from inside with yellow discs, as if passengers are aboard.

## Summary of the round

Every page is complete. The changes are of small detail: the path on 177, the colour variation on 178 and 179, the aerial on 181, the legend on 182, the flag on 183, the time on 184, the sparkles on 185 and the lit windows on 186.

---

## Changes made in round 5

- **177 Good Morning, Hartley Avenue:** three stepping stones of paper colour lead from the mailbox toward the door. [`pages/177-good-morning-hartley-avenue.py`]
- **178 A Card for Grandma:** the rosettes alternate raspberry and gold, round the frame; the greeting's letters alternate rose and raspberry. [`pages/178-a-card-for-grandma.py`]
- **179 The Family Message Board:** MUM's pin is teal and DOUG's pin is navy; the other pins stay red. [`pages/179-the-family-message-board.py`]
- **180 Supper Tonight:** the bowl beside INGREDIENTS is removed, as it floated between the heading and the list. [`pages/180-supper-tonight.py`]
- **181 The Wired Living Room:** a rabbit-ear aerial stands on the television cabinet; each curtain is held back by a mustard tie. [`pages/181-the-wired-living-room.py`]
- **182 Neighbourhood Calendar, Maple Ridge Estates:** the legend gains a BIN DAY entry with a grey swatch; its spacing is `LEGEND_SPACING`, and its text is 9 by 13 so five entries fit. [`pages/182-neighbourhood-calendar.py`]
- **183 The House That Orders Its Own Paper Towels:** the LOW flag moves up to y 246, clear of the x4 count tag. [`pages/183-the-house-that-orders-its-own-paper-towels.py`]
- **184 Home Watch:** the status panel's header carries "CHECKED 7:40 PM". [`pages/184-home-watch.py`]
- **185 Tonight's Horoscope:** the sparkles are moved off the text: they are now at (14, 60), (340, 28), (372, 30), (560, 52), (12, 330), (40, 420) and (300, 424); the moon has a glow ring. [`pages/185-tonights-horoscope.py`]
- **186 School Bus Is Late:** two windows are lit from inside with cream discs. [`pages/186-school-bus-is-late.py`]

The round-5 pass also corrected a mistake in the round-5 edit script, which stopped part-way; the failed patches were re-run and each change was checked in the file before the renders were made.
