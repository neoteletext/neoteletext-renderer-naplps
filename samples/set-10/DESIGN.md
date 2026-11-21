# NAPLPS typography / 156–165

[Contact sheet](out/contact-sheet.png) · [Manifest](out/manifest.json)

The pages use independent layouts and palettes. The native captions and mastheads use the repository's NeoTeletext stroke font. Display glyphs drawn for this set use programmable DRCS masks, filled polygons or layered vector strokes. The layouts use a 640 × 480 design grid, and the renderer samples the same NAPLPS display area directly at 480 × 460 for the channel previews. The aspect ratio change makes a native circle look elliptical at channel size. Both shapes suit the dial in Quarter Turn.

## 156 · Silt

Four individually fitted DRCS capitals sit between continuous upper beds and a lower sequence offset by a fault.

## 157 · Quarter Turn

Native TEXT sets the four sides with matching cursor paths and rotations. The directional arc runs outside the graduated dial, with a four-sided frame around the rotated text.

## 158 · The Quireline

The masthead and issue line sit over a two-column cover. A tapered DRCS Q leaves the contrasting planes of the fold visible through its counter. Exposed leaf edges define the stack.

## 159 · Ink and Air

One DRCS mask shows a B with cleared counters. The other prints only those two shapes at the same scale, with numbered guides through the clear counters and behind their solid counterparts.

## 160 · Low Water

The proportional verse descends toward a bent shoreline. Its last phrase reverses to pale ink against dark water among five tapering tidal traces.

## 161 · Register 258

Three original DRCS numerals use fitted outlines and individual stencil cuts. A smaller, reordered second line shares the same column centers, showing that the outlines can trade places on the tabular grid.

## 162 · Oblique Assembly

LEAN uses filled polygons sheared around a common baseline. Blue construction guides share the same shear. Superimposed stems show the 30-unit run over a 100-unit rise.

## 163 · Three Voices

Three sizes of the same DRCS word enter at different positions on a shared typographic score. The display word keeps the same proportions at all three sizes. The entries start at different beats and end at one release line.

## 164 · The Fi Join

A vermilion DRCS ligature sits on three construction rules. Anchored leaders point to the hook and join. The separate f and i use contours shared with the combined form, with an arrow between the two settings.

## 165 · A Room After Dark

Two tiers of fitted inline vector lettering share an axis inside a recessed chamfered marquee. Two lamp circuits alternate with palette BLINK while the lettering holds steady.

## Reproduce and check

Run `python3 set-10/validate.py` from `samples/`. Each numbered script can also regenerate its own stream independently. The validator runs each generator twice and compares the streams, checks the full RESET, all sixteen initial palette definitions and the 7-bit range, and runs the renderer's diagnostics. It regenerates both native preview sizes and checks that the animated page changes between palette phases. Stream byte counts are recorded in the manifest for reference. The validator and generators use the Python standard library. The final individual images were reviewed at both sizes.
