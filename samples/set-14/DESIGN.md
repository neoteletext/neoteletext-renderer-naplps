# Videotex as its makers dreamed it, group B · pages 187 to 196

[Contact sheet](out/contact-sheet.png) · [Manifest](out/manifest.json) · [Concepts](CONCEPTS.md) · [Round notes](rounds/)

Ten pictures of commerce, banking and shopping as the videotex services promised them. Every service, shop, bank, place and person is invented. Each page is 7-bit, begins with a full reset and defines all sixteen colour-map entries. Text is the repository stroke font, proportional, in cells of at least 12 by 18 design pixels (about 9 by 17 at 480 by 460), the size found by rendering a ladder of sizes at 480 by 460 and choosing those where the strokes hold. There is no size limit on a picture and none is checked.

Run `python3 set-14/validate.py --build` from `samples/` to regenerate the streams, PNGs, contact sheet and manifest, and `python3 set-14/validate.py` to verify them: each page is regenerated twice and compared, checked for 7-bit framing and all sixteen palette entries, passed through the renderer's `check`, rendered at 640 by 480 and 480 by 460, and every page that claims BLINK or WAIT must render differently across blink phases or at its first stage. The contact sheet groups 187 to 191 and 192 to 196, 640 by 480 above 480 by 460, at half size. `pages/_kit.py` holds the shared helpers: text with measured proportional advances, a scaling proxy, a DRCS definer, a user-defined fill pattern, a polygon clipper and the wedge `rays`. `rounds/` holds the renders after each of the five improvement rounds and the notes of each.

## 187 · The Electronic Catalogue

A department store's page of three goods, each in its own panel: a toaster before kitchen tiles (a fill pattern defined in the stream), a pocket radio against stripes with a blinking NEW star, a running shoe over track lanes. Each panel draws in turn with a pause. The store's mark is drawn in the band, the foot shows the viewer's own keypad with keys 1 to 3 lit, and a last stage shows key 2 pressed: the radio panel is framed and the order confirmed. The key rings blink.

## 188 · Your Balance, Mrs Okafor

A prairie bank's vault door sits closed, then opens in six foreshortened steps while a clipped sunburst of rays spreads behind it, revealing shelves of gold, money bags and boxes. The statement prints beside it: balances, four bills with blinking PAID stamps, a six-month savings chart and a DRCS warning triangle by a reminder. After a pause the chequing balance changes with a green arrow as a deposit lands.

## 189 · Build Your Credit

A savings and loan advertisement that builds itself. Coins stack step by step into an eight-step staircase over a pale town skyline; a figure climbs every step, alternating strides, the sky and skyline repainted behind him, and plants a flag that unfurls in two frames. Confetti falls, sparkles blink on the stair, and the slogan comes last.

## 190 · The Showhome on Cedar Crescent

A realty listing in four stages: the house elevation, the floor plan with its rooms, furniture and door swings, the labels and a dotted walk-through, then the spec line with bed, bath and house icons, the price star and the monthly payment. At the end the windows light up by a colour-map change.

## 191 · Classifieds: Bicycles

A drawn ten-speed over rays tops a neighbourhood classified column. Six ads each carry a small bicycle that is a DRCS character defined in the stream; one ad is framed in blinking cyan with a DRCS telephone. A dashed coupon invites the reader to place an ad.

## 192 · Going Once, Going Twice

A live auction of a walnut mantel clock under a hatched spotlight. The bid counter is three seven-segment digits whose segments belong to six shared colour-map entries; each WAIT rewrites those entries so the counter reads 98, 105 and 112, the bid ladder lights its lines with the same entries and the clock's hands and pendulum move with each bid. A DRCS eye marks the viewer count and the lamps count the sale.

## 193 · Grocery Order, Week of June 3

A grocer's order. Six packages drop into a wire cart one at a time; the cart's front mesh is a macro redrawn over each, and each item is ticked with a DRCS check mark as the running total grows. At the end the SEND key goes down and a DRCS delivery van marks the confirmation.

## 194 · Theatre Tickets

A box office opens its pleated curtain (a hatch fill) on a railway-platform set; the engine rolls in over three frames and the marquee beads twinkle. The hall below fans around the stage in curved rows of seats drawn with a seat macro, sold seats red and free ones green, the reader's pair held by a blinking frame, with seat numbers under the last row.

## 195 · The Mall Directory

A shopping-centre kiosk: two floor plans in pastel with a fountain, planters, entrance gaps and an escalator, ten numbered touch keys each with a DRCS shop icon, key 5 shown pressed and a dotted route to it from a blinking YOU ARE HERE.

## 196 · Today's Special at the Hardware Store

A Saturday project page (a birdhouse in four steps with dimension lines, its steps painted one at a time) whose foot is an advertising band with a DRCS drill and a blinking LOOK key. The band rises in steps until it fills the page: a large cordless drill on radiating wedges and a three-layer starburst whose colours chase through the colour map. The old price is struck through after a pause.
