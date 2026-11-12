# SIGNAL — ten studies in light

Ten original NAPLPS pages for a 640 x 480, 16-entry display. The set pairs the discipline of an art journal with the limited colours and geometric confidence of period videotex. Each page has its own palette; small SIGNAL identifiers and footers tie them together.

[Contact sheet](out/contact-sheet.png). Each page has a same-stem `.nap`, final `.png` and machine-readable `.json` in `out/`. Animated pages also have looping `.gif` review copies. These GIFs are previews; the NAPLPS files themselves contain the protocol animation commands.

## Reproduce

```sh
python3 render.py       # generate all ten streams, final PNGs and key-moment PNGs
python3 validate.py     # constraints, determinism, rendering, resets, stages and BLINK
python3 finish.py       # five GIFs and the contact sheet
```

Individual generators can also be run directly, for example `python3 pages/01-tide-clock.py`; they locate the output directory relative to their source, so they work from any current directory. `python3 render.py 01 04` regenerates selected pages. No Python packages are required. Rendering uses the supplied release renderer, Microstar stroke font and ffmpeg. Every generated or temporary file stays in this directory.

## Encoding decisions and sources

The encoder is original Python 3 standard-library code. Geometry and layouts are original. No third-party encoder code or period picture stream was copied. I read the local BYTE 1983 NAPLPS introduction (opcode and operand tables, DOMAIN/TEXT/TEXTURE and incremental-line sections), the CSA T500-1983 OCR (especially 5.3.1, 5.3.2 and 5.3.3), Dillon's `naplps.txt`, the repository's `docs/verification.md`, and the renderer's operand, terminal, text and raster implementation. A `seaport.nap` hex dump helped check the surrounding control sequences.

- All streams are 7-bit. `ESC % A`, C1 designation and `SO RESET 7F 7F` establish a clean start. G2 is explicitly designated as the macro set. Each stream resets screen, palette, DOMAIN, text, textures, blink, macros and DRCS.
- DOMAIN uses one-byte single values and four-byte 2D coordinates (`21 4C`), giving eleven fractional bits per axis. The drawing API converts a 640 x 480 design canvas to a unit viewport of 1 x 25/32, following the measured PP3 geometry. Relative coordinates have signed two's-complement components.
- Colour indices occupy the most significant four bits of a six-bit single operand: index `i` is `40 | (i << 2)`. Each RGB definition is four GRBGRB operand bytes, giving eight bits per primary. SELECT COLOR / SET COLOR defines every entry explicitly. The tables below give the initial requested RGB values, indexed in decimal; animation overrides are listed separately. Some closely related entries are reserved shades.
- Text stays in the supplied Microstar stroke font, using SI/SO to switch between text and PDIs. No word wrap, forms, cursor styles, or transmit macros are used. Large display type uses non-default character fields; these have been visually checked in the supplied renderer, not certified against PP3 at every size.
- The fern uses actual incremental 2-bit drawing operations. The bird uses actual native mosaic glyphs. The window, weather and wedge patterns use actual DEFINE MACRO / SS2 invocations. Ellipses elsewhere are deliberately faceted polygon shapes; the menu and cover specifically use native ARC commands.

## Timing and renderer observations

**WAIT playback is the material limitation.** The supplied CLI feeds the whole stream before producing its image; its `--tenths` option changes BLINK palette state, but does not stop at WAIT. For example, valid `3D 5C 4C` means WAIT 12 tenths, yet a complete-stream render at `--tenths 0` already includes palette changes and drawing that follow that WAIT. This is a CLI playback limitation: the decoder does emit `Event::Wait`. The renderer was not modified.

The generator records exact command boundaries and wait durations in each `.json`. `render.py` renders a stream prefix at each named key moment, applying `--tenths` as well; `finish.py` plays those same boundaries into GIFs. Thus the stills and GIFs show the intended WAIT sequence without replacing the valid WAIT instructions in the deliverable. The constellation GIF samples at 10 fps to combine sequential drawing with continuous BLINK. The other GIFs preserve their WAIT intervals and add a one-second final hold before looping. NAPLPS playback itself is finite and holds the last picture, except for the continuing constellation BLINK.

**Mosaic alignment:** independently rounded 22-pixel fields and explicit row positions produced hairline seams. The finished mosaic uses an exact field height of 74/2048 unit-screen (22.2 design pixels), matching origins, and an exact field width of 58/2048 (18.125 design pixels). No remaining seams were visible. This is a coordinate-rounding workaround, not a confirmed standards defect.

No malformed-stream errors, processing-limit messages, or other suspected renderer faults were observed. The standard's fill, glyph and arc approximations remain implementation-dependent. All previews use the command's default 8-bit DAC output; they are not claimed to be VGA-register-exact PP3 oracle captures.

## Validation and visual review

Every final 640 x 480 PNG was viewed, revised, and viewed again. Every named animation moment was viewed. The fern and menu were additionally inspected at 1280 x 960; those `-detail.png` files are included. The contact sheet was inspected after assembly.

`validate.py` checks known coordinate and pure-colour encodings, ten deterministic generators, streams below 8,192 bytes, all bytes below 128, explicit initial RESET, sixteen initial palette entries, 640 x 480 output, at most sixteen visible colours, and clean renderer stderr. Every page is also rendered after a different predecessor page and compared byte-for-byte as RGB pixels against its standalone render. All ten reset-independence checks passed. Named WAIT stages differ, and the constellation's two BLINK phases differ and return to the first phase after a full period. SHA-256 hashes, byte sizes, visible-colour counts and stage counts are in [manifest.tsv](out/manifest.tsv).

## 01 — Tide-clock harbour

[Preview](out/01-tide-clock.png) · [NAPLPS](out/01-tide-clock.nap) · [Animation](out/01-tide-clock.gif) · **1,670 bytes**

**Concept.** A dusk harbour composed as a three-ink coastal travel poster. The large title rests in the warm sky, with the lighthouse, cutter and short horizontal reflections counterbalancing it.

**Palette.** Peach and dusty mauve above blue slate and sea green; cream is saved for sails, the tower and navigation light.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#18293B` | 01 `#F6E7C5` | 02 `#ED9471` | 03 `#C96667` |
| 04 `#704C68` | 05 `#304762` | 06 `#436078` | 07 `#2F777E` |
| 08 `#6EAAA2` | 09 `#F3C98B` | 10 `#101F30` | 11 `#AEC4B1` |
| 12 `#DFAD84` | 13 `#466D7A` | 14 `#34566A` | 15 `#B9D1B7` |

**Techniques.** Filled RECTANGLE and relative POLYGON primitives; polygonal sun; fine LINE detail; palette animation with WAIT and SET COLOR. Water and both beam triangles are drawn once. The animation then changes only colour-map entries.

**Visual iteration.** The first title touched the top of the picture. I lowered both lines, separated the harbour caption from the title, and inspected all three light states.

**Timing.** Initial dusk at 0; east beam at 12; west beam at 24 tenths. East/west alternate three times, ending at 84 tenths. East overrides: 07 `#28646F`, 08 `#A5C9B6`, 11 `#F3C98B`, 13 `#34566A`, 14 `#6EAAA2`. West overrides: 07 `#2F777E`, 08 `#6EAAA2`, 11 `#466D7A`, 13 `#B9D1B7`, 14 `#AEC4B1`.

**With more time.** Give the reflections a second spatial rhythm, and introduce a more convincing shoreline behind the lighthouse.

## 02 — Botanical plate

[Preview](out/02-botanical.png) · [NAPLPS](out/02-botanical.nap) · **4,265 bytes**

**Concept.** A herbarium sheet: one large frond, a circular analytical detail, a Latin caption and an economical double rule. The asymmetric leaf lengths prevent the scientific layout from feeling mechanical.

**Palette.** Warm ivory paper, deep green ink and sage shading. The reserve colours stay within an aged botanical-print palette.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#EFE9D6` | 01 `#233E35` | 02 `#64765A` | 03 `#A5AD8A` |
| 04 `#D9DBC1` | 05 `#B2A478` | 06 `#8C7957` | 07 `#476353` |
| 08 `#F6F0DF` | 09 `#D0C8AE` | 10 `#7C8B6B` | 11 `#364C3F` |
| 12 `#9B9E76` | 13 `#CECBA8` | 14 `#EEE5C8` | 15 `#867F67` |

**Techniques.** Thirty serrated filled polygons; native INCREMENTAL LINE veins, twelve diagonal steps per pinna; vertical TEXTURE hatching on selected pinnae and the enlarged detail; proportional Latin caption; ruled border. The frond outline is deliberately stylised.

**Visual iteration.** I varied the opposing leaf positions, lengths and angles, replaced bright veins with quieter sage, introduced hatching, and enlarged the Latin caption. I also inspected the 1280 x 960 render.

**With more time.** Subdivide the pinnae into finer pinnules and add several locally curved veins while keeping the stream below 8 KB.

## 03 — After dark / constellation map

[Preview](out/03-constellation.png) · [NAPLPS](out/03-constellation.nap) · [Animation](out/03-constellation.gif) · **5,083 bytes**

**Concept.** A fictional navigation atlas, with a large circular sky balanced by a narrow text column. The Voyager, Echo and Lantern are invented figures; this is an illustration rather than an observing chart.

**Palette.** Midnight blue, restrained blue-grey construction lines, parchment stars and old-brass routes.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#0D192E` | 01 `#EDE7CE` | 02 `#33465F` | 03 `#66788B` |
| 04 `#C0A775` | 05 `#90BDC7` | 06 `#21344E` | 07 `#F2B874` |
| 08 `#F6F1DD` | 09 `#526B80` | 10 `#869DA6` | 11 `#B8B6A1` |
| 12 `#1B2A43` | 13 `#667B8C` | 14 `#D6C793` | 15 `#283E57` |

**Techniques.** Concentric vector rings, small polygonal stars, fine LINE routes, nine successive WAIT reveals, and a native BLINK process on three bright stars. BLINK uses entry 8 -> 5, ON 4 / OFF 12 tenths. Four cardinal labels sit around the ring.

**Visual iteration.** I checked the empty sky, the first four routes, the completed constellation and both blink phases. The final star overprint retains the blinking colour index instead of covering it with a static colour.

**Timing.** Stars alone for 8 tenths, then one additional route every 3 tenths; all nine routes exist at 32 tenths. The final star overprint follows the last wait at 35 tenths. BLINK uses source 08 `#F6F1DD` and destination 05 `#90BDC7`: destination visible for 4 tenths, source for 12, repeating every 16. Named PNGs show 0, 17 and 32 tenths; `-blink-000`, `-004` and `-012` show full-stream blink samples.

**With more time.** Introduce additional small peripheral labels and make a more expressive second fictional constellation.

## 04 — Common ground / isometric city

[Preview](out/04-city-block.png) · [NAPLPS](out/04-city-block.nap) · [Animation](out/04-city-block.gif) · **2,508 bytes**

**Concept.** Four modest buildings share a little paved block. The illustration is about a neighbourhood rather than a skyline, with a roof garden and a street tree supplying scale.

**Palette.** Day: warm paper, sand paving, sage roofs and terracotta walls. Night: ink blue, muted teal and plum, with amber and cream windows.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#E9DFC6` | 01 `#26394B` | 02 `#D6C498` | 03 `#B9AD86` |
| 04 `#648F88` | 05 `#3D6F71` | 06 `#97B7A1` | 07 `#BC765E` |
| 08 `#814C50` | 09 `#E5AD7C` | 10 `#E1CA88` | 11 `#8BA4A0` |
| 12 `#F7E9BD` | 13 `#D8C9A6` | 14 `#B19E7A` | 15 `#26394B` |

**Techniques.** Three filled polygon faces per building; two relative window macros, one for each face orientation, invoked across the grids; fine roof and paving lines. A WAIT followed by a colour-map swap turns the existing image to night without redrawing it.

**Visual iteration.** The first night version made the roads almost white because roads shared the text index. I reserved entry 15 for asphalt, lifted the city ten pixels, and moved the day/night caption clear of the roof.

**Timing.** Day for 20 tenths, then night for another 20. Night overrides: 00 `#182539`, 01 `#E9DFC6`, 02 `#354456`, 03 `#495666`, 04 `#36636B`, 05 `#243F52`, 06 `#6C938E`, 07 `#754E5B`, 08 `#4F384E`, 09 `#B98271`, 10 `#EDBF6C`, 12 `#FFE4A1`, 15 `#101D2E`.

**With more time.** Add a second window macro with a partly lit curtain, and distinguish one roof with a low parapet.

## 05 — Form follows frequency

[Preview](out/05-form.png) · [NAPLPS](out/05-form.nap) · **569 bytes**

**Concept.** An all-type Swiss poster. FORM is the image; a red rule supplies the only geometric accent. The large pale page number and a quiet body column create a second reading distance.

**Palette.** Almost-black on warm paper, a vermilion rule and a grey-green numeral.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#EFECE2` | 01 `#202726` | 02 `#D8332F` | 03 `#C2C3B9` |
| 04 `#9D9E96` | 05 `#DEDBD1` | 06 `#4F5650` | 07 `#B05A49` |
| 08 `#E5C4AD` | 09 `#D9CBB7` | 10 `#ACB8AF` | 11 `#7F9086` |
| 12 `#F7F1DE` | 13 `#BBB3A5` | 14 `#6A706A` | 15 `#DBAD8B` |

**Techniques.** Native Microstar stroke typography at three scales, proportional body text, fixed spaced subheading and a single red RECTANGLE. The giant word remains text bytes, not hand-traced letter polygons.

**Visual iteration.** The initial word ended too early. I expanded its character field from 152 to 185 design pixels so the final M aligns with the rule. The body copy remains deliberately small and open.

**With more time.** Refine optical spacing around R/M with individually positioned native glyphs and compare that display size against a period terminal.

## 06 — One bird, two languages

[Preview](out/06-two-languages.png) · [NAPLPS](out/06-two-languages.nap) · [Animation](out/06-two-languages.gif) · **3,166 bytes**

**Concept.** The same original kingfisher silhouette is shown as chunky mosaic cells and as smooth vector shapes. A neutral paper background keeps attention on the different visual languages.

**Palette.** Petrol ink, kingfisher teal, blue wing, burnt-orange breast and a small golden beak.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#EFE7CF` | 01 `#153F50` | 02 `#288B9A` | 03 `#2F677E` |
| 04 `#D86C49` | 05 `#E7B24E` | 06 `#F8EDCA` | 07 `#7EB6AD` |
| 08 `#BB503C` | 09 `#9ABCA7` | 10 `#D3C59F` | 11 `#41606B` |
| 12 `#D99A68` | 13 `#B5D3BA` | 14 `#7B8E85` | 15 `#F4D9A4` |

**Techniques.** Actual G3 2 x 3 mosaic characters through SS3, layered by foreground colour; the right bird uses filled relative polygons. A WAIT reveals the vector version. Both versions derive from the same original shape list; the mosaic side samples that geometry into six-block cells.

**Visual iteration.** I enlarged both birds. The first enlargement left one-pixel row seams; I aligned the mosaic character fields and origins to exact coordinate fractions, then re-rendered until the rows joined cleanly.

**Timing.** The mosaic is alone for 18 tenths, then the vector bird is drawn. A further 18-tenth wait holds the comparison.

**With more time.** Give the wing a more calligraphic outline and use a little separated-mosaic texture in a second comparison.

## 07 — Southern season

[Preview](out/07-weather.png) · [NAPLPS](out/07-weather.nap) · **1,799 bytes**

**Concept.** An editorial weather graphic: a simplified Australian silhouette in broad temperature bands, with a forecast column aligned to a clean vertical rule. All temperatures and conditions are illustrative.

**Palette.** Paper and slate with a warm progression from pale ochre to terracotta; sage rain hatching and cream cloud silhouettes.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#EEE8D4` | 01 `#243F47` | 02 `#F2CD84` | 03 `#DF9A5C` |
| 04 `#C86C4B` | 05 `#9BB8AA` | 06 `#6A918D` | 07 `#C1CDBB` |
| 08 `#FAF0D2` | 09 `#8DA29A` | 10 `#E1B36F` | 11 `#B65943` |
| 12 `#476D74` | 13 `#BFCCBA` | 14 `#7E8B79` | 15 `#C8B38D` |

**Techniques.** A hand-drawn coast, clipped horizontal band polygons, a native horizontal TEXTURE rain band, and reusable relative cloud and rain macros. Proportional condition labels contrast with fixed spaced city names.

**Visual iteration.** I softened the coastal hatching after the first render so it reads as weather texture rather than a heavy outline. All symbols and tiny forecasts were checked at 640 x 480.

**With more time.** Refine the coast, particularly the northern gulfs and southern peninsulas, and position the symbols with more geographic precision.

## 08 — Chromatic bloom

[Preview](out/08-kaleidoscope.png) · [NAPLPS](out/08-kaleidoscope.nap) · [Animation](out/08-kaleidoscope.gif) · **2,482 bytes**

**Concept.** A twelve-fold flower made of nested kites. Small cream inlays, floating diamonds and corner brackets introduce a second scale around the central bloom.

**Palette.** Deep petrol, ochre, coral, dusty rose and jade, with parchment used for the small inlays.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#132F39` | 01 `#F0E2BD` | 02 `#E7A650` | 03 `#D66C4E` |
| 04 `#B44D60` | 05 `#477F87` | 06 `#81AAA0` | 07 `#D4C593` |
| 08 `#2D555D` | 09 `#D78F64` | 10 `#DDC37F` | 11 `#9CB7A0` |
| 12 `#E2BAA0` | 13 `#6E7473` | 14 `#AB806B` | 15 `#F4DCB1` |

**Techniques.** Twelve oriented variants of one relative wedge macro, each invoked twice at different positions and selected colour entries; inner polygon kites and diamond inlays. WAIT plus five palette-entry updates cycles the flower through three colour arrangements.

**Visual iteration.** The first bloom had a weak centre. I added the small cream inlaid diamonds, then inspected ochre, jade and rose phases; the larger silhouette and centre remain legible in all three.

**Timing.** Three arrangements at 8-tenth intervals, repeated four times after the initial hold; 104 tenths total. Jade overrides: 02 `#81AAA0`, 03 `#E7A650`, 04 `#D66C4E`, 05 `#B44D60`, 06 `#477F87`. Rose overrides: 02 `#B44D60`, 03 `#81AAA0`, 04 `#E7A650`, 05 `#477F87`, 06 `#D66C4E`. Ochre restores initial entries 02–06.

**With more time.** Explore a second macro tile that tessellates between the flowers, and make the cycling slightly less regular.

## 09 — Lumiere / the evening room

[Preview](out/09-evening-menu.png) · [NAPLPS](out/09-evening-menu.nap) · **1,316 bytes**

**Concept.** An Art Deco supper card: a symmetrical sunburst crown above a three-course menu, framed by stepped architecture and small diamond ornaments.

**Palette.** Charcoal, old gold, restrained bronze and warm cream; only four colours are visible in the final card.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#171F22` | 01 `#D7BD7C` | 02 `#8E7A50` | 03 `#394346` |
| 04 `#B09B69` | 05 `#F0DFAD` | 06 `#6D684E` | 07 `#C6AA68` |
| 08 `#213031` | 09 `#A48E5B` | 10 `#DDC894` | 11 `#4E5548` |
| 12 `#BEA77A` | 13 `#E0CA94` | 14 `#7F775A` | 15 `#EFDDB0` |

**Techniques.** Thin filled triangle rays, two native three-point ARC commands, stepped outlined polygons, diamond ornaments, and a tracked title with proportionally spaced, stroke-measured menu descriptions. The arcs remain native ARC instructions rather than polygon approximations.

**Visual iteration.** I moved the small course-count line below the inner rule after it touched the frame. I measured the actual glyph extents to centre the proportional descriptions. The crown and menu were also inspected at 1280 x 960.

**With more time.** Compare the menu spacing against PP3, and add a second, finer gold ray between the broad rays.

## 10 — Signal / collection cover

[Preview](out/10-signal.png) · [NAPLPS](out/10-signal.nap) · **1,835 bytes**

**Concept.** A welcome page for the complete collection. A rainbow portal and receding wire floor evoke a 1980s videotex service, while the directory gives the other nine pictures a readable, orderly home.

**Palette.** Indigo, parchment, muted salmon, mauve, sea glass and a golden half-sun.

| Entry / RGB | Entry / RGB | Entry / RGB | Entry / RGB |
|---|---|---|---|
| 00 `#24273E` | 01 `#F2DFB6` | 02 `#DE8F82` | 03 `#AC5D80` |
| 04 `#688E98` | 05 `#9EC5B3` | 06 `#D9BC83` | 07 `#414563` |
| 08 `#C8757F` | 09 `#335D70` | 10 `#B5C6B2` | 11 `#E8BDA0` |
| 12 `#6E758C` | 13 `#879F9C` | 14 `#D7A179` | 15 `#EEE3C7` |

**Techniques.** Native large stroke type, a set of ARC arches with matching straight legs, thin vector perspective lines, a small outlined badge and a proportional nine-entry directory. No unsupported interaction or form commands are needed.

**Visual iteration.** I widened the masthead and added a small ten-page badge to balance the open upper-right corner. The directory rules and portal floor were checked for clear separation from text.

**With more time.** Add a short introductory reveal, with the portal appearing before the directory, while keeping the completed cover immediately readable.

